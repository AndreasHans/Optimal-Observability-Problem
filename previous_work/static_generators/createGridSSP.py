#!/usr/bin/python3
import sys


def create_grid_pre(budget, target, sizex, sizey, threshold, det, pre):

    actions = ['l', 'r', 'u', 'd']
    column = target % sizex
    size = sizex * sizey

    puzzle_type = "ssp_grid"
    strat_type = "det" if det == 1 else "ran"
    file = open(f'{puzzle_type}_{sizex}x{sizex}_{strat_type}_z3.py', 'w')

    file.write('from z3 import *\n\n')

    file.write('# Expected cost/reward of reaching the goal.\n')
    pi_vars = '\n'.join([f'pi{s} = Real(\'pi{s}\')' for s in range(size)])
    file.write(pi_vars + '\n')

    file.write('\n# Choice of observations\n')

    # Generate sensor variables - one per non-target state (sensor selection approach)
    sensor_vars = []
    sensor_states = []
    for s in range(size):
        if s != target:
            sensor_vars.append(f'ys{s} = Real(\'ys{s}\')')
            sensor_states.append(s)

    file.write('\n'.join(sensor_vars) + '\n')

    file.write('\n# Rates of randomized strategies\n')

    # Generate state-specific strategy variables (when sensor is on for that state)
    state_strategy_vars = []
    for s in sensor_states:
        for act in actions:
            state_strategy_vars.append(f'xo{s}{act} = Real(\'xo{s}{act}\')')

    file.write('\n'.join(state_strategy_vars) + '\n')

    # Default strategy variables (when no sensor observes - unknown state)
    default_strategies = [f'xo{act} = Real(\'xo{act}\')' for act in actions]
    file.write('\n'.join(default_strategies) + '\n')

    file.write('solver = Solver()\n\n\n')
    file.write('solver.add(\n')

    file.write('#We cannot do better than the fully observable case\n')

    # Optimize bounds constraints generation for grid
    bounds_constraints = []
    count = 0
    for s in range(size):
        # For optimal reward: print(count)
        if s % target == column:
            bound_value = abs(target - s) // sizex
            bounds_constraints.append(f'pi{s}>={bound_value}')
            count += bound_value
        else:
            bound_value = abs(column - s % sizex) + (abs(target - s) // sizex)
            bounds_constraints.append(f'pi{s}>={bound_value}')
            count += bound_value

    file.write(', '.join(bounds_constraints) + ', \n')


    file.write('# Expected cost/reward equations\n')

    # Generate sensor selection cost equations for grid
    cost_equations = []
    for s in range(size):
        if s == target:
            cost_equations.append(f'pi{s} == 0')
        else:
            # Calculate next states for each direction in grid
            left_next = s if s % sizex == 0 else s - 1
            right_next = s if s % sizex == sizex - 1 else s + 1
            up_next = s if s - sizex < 0 else s - sizex
            down_next = s if s + sizex >= size else s + sizex

            # Build sensor selection strategies using efficient action-to-next-state mapping
            next_states = {'l': left_next, 'r': right_next, 'u': up_next, 'd': down_next}

            action_terms = []
            for act in actions:
                strategy_term = f'((1 - ys{s})*xo{act} + ys{s}*xo{s}{act})'
                next_state = next_states[act]
                action_terms.append(f'{strategy_term} * (1 + pi{next_state})')

            equation = f'pi{s} == ' + ' + '.join(action_terms)
            cost_equations.append(equation)

    file.write(',\n'.join(cost_equations) + ',\n')

    # Optimize threshold constraint generation
    file.write(f'# We are dropped uniformly in the grid\n# We want to check if the minimal expected cost is below some threshold {threshold}\n')
    pi_terms = [f'pi{s}' for s in range(size) if s != target]
    pi_sum = '+'.join(pi_terms)
    threshold_constraint = f'({pi_sum}) * Q(1,{size-1}) {threshold},'
    e = f'({pi_sum}) * Q(1,{size-1}) '
    file.write(threshold_constraint + '\n')

    # Optimize strategy constraints
    file.write('# Randomised strategies (proper probability distributions)\n')

    # Generate strategy constraints for state-specific sensors using efficient action iteration
    strategy_constraints = []
    for s in sensor_states:
        for act in actions:
            strategy_constraints.extend([
                f'xo{s}{act} <= 1,',
                f'xo{s}{act} >= 0,'
            ])
        action_sum = ' + '.join([f'xo{s}{act}' for act in actions])
        strategy_constraints.append(f'{action_sum} == 1,')

    # Add default strategy constraints using efficient action iteration
    for act in actions:
        strategy_constraints.extend([
            f'xo{act} <= 1,',
            f'xo{act} >= 0,'
        ])

    default_action_sum = ' + '.join([f'xo{act}' for act in actions])
    strategy_constraints.append(f'{default_action_sum} == 1,')

    file.write('\n'.join(strategy_constraints) + '\n')

    if det == 1:
        file.write('#Deterministic strategies activated\n')
        det_constraints = []
        for s in sensor_states:
            for act in actions:
                det_constraints.append(f'Or(xo{s}{act} == 0, xo{s}{act} == 1),')

        # Add default deterministic constraints using efficient action iteration
        for act in actions:
            det_constraints.append(f'Or(xo{act} == 0, xo{act} == 1),')

        file.write('\n'.join(det_constraints) + '\n')

    file.write('# y is a function that should map every state N to some observable class M\n')

    # Binary constraints for sensor variables
    sensor_binary_constraints = [f'Or(ys{s} == 0, ys{s} == 1),' for s in sensor_states]
    file.write('\n'.join(sensor_binary_constraints) + '\n')

    # Budget constraint - total sensors used <= budget
    sensor_sum = ' + '.join([f'ys{s}' for s in sensor_states])
    file.write(f'{sensor_sum} == {budget}')

    file.write('\n)\n\n')

    file.write('set_option(max_args=1000000, max_lines=100000000)\n')

    file.write('file_results = open(\'results.txt\', \'w\')\n')

    file.write('file_reward = open(\'reward.txt\', \'w\')\n')

    file.write('result = solver.check()\n'
               'if result == sat:\n\t'
               'm = solver.model()\n\t'
               'print(\'Solution found\')\n\t'
               'file_results.write(str(m))\n\t'
               'file_reward.write(str(m.eval(' + str(e) + ')))\n'
               'elif result == unsat:\n\t'
               'print(\'No solution!!!\')\n\t'
               'file_reward.write(\'N/A\')\n'
               'else:\n\t'
               'print(\'Unknown\')')


size = int(sys.argv[1])
target = int(sys.argv[2])
budget = int(sys.argv[3])
threshold = sys.argv[4]
det = int(sys.argv[5])
pre = sys.argv[6]

if pre == 'predefined.txt':
    file = open(pre, 'r')
    pre = file.readlines()[0].strip('\'')


create_grid_pre(budget, target, size, size, threshold, det, pre)
