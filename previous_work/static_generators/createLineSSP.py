#!/usr/bin/python3
import sys


def create_line_pre(budget, target, size, threshold, det, pre):

	puzzle_type = "ssp_line"
	strat_type = "det" if det == 1 else "ran"

	file = open(f'{puzzle_type}_{size}_{strat_type}_z3.py', 'w')

	actions = ['l', 'r']

	file.write('from z3 import *\n\n')

	file.write('# Expected cost/reward of reaching the goal.\n')
	pi_vars = '\n'.join([f'pi{s} = Real(\'pi{s}\')' for s in range(size)])
	file.write(pi_vars + '\n')

	file.write('\n# Choice of observations\n')

	# Generate sensor variables - one per non-target state
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
	file.write('xol = Real(\'xol\')\n')
	file.write('xor = Real(\'xor\')\n')

	file.write('solver = Solver()\n\n\n')

	file.write('solver.add(\n')

	file.write('#We cannot do better than the fully observable case\n')
	bounds = ', '.join([f'pi{s}>={abs(target - s)}' for s in range(size)])
	file.write(f'{bounds}, \n')

	file.write('# Expected cost/reward equations\n')

	# Generate sensor selection cost equations
	cost_equations = []
	for s in range(size):
		if s == target:
			cost_equations.append(f'pi{s} == 0')
		else:
			# For sensor selection: if sensor y_s is on, use xo_s_act, else use default xol/xor
			left_next = max(s-1, 0)
			right_next = min(s+1, size-1)

			left_strategy = f'((1 - ys{s})*xol + ys{s}*xo{s}l)'
			right_strategy = f'((1 - ys{s})*xor + ys{s}*xo{s}r)'

			equation = f'pi{s} == {left_strategy} * (1 + pi{left_next}) + {right_strategy} * (1 + pi{right_next})'
			cost_equations.append(equation)

	file.write(',\n'.join(cost_equations) + ',\n')

	file.write(f'# We are dropped uniformly in the line\n# We want to check if the minimal expected cost is below some threshold {threshold}\n')

	# Generate sum of pi variables for non-target states
	pi_terms = [f'pi{s}' for s in range(size) if s != target]
	pi_sum = '+'.join(pi_terms)
	threshold_constraint = f'({pi_sum}) * Q(1,{size-1}) {threshold},'

	# Store for reward evaluation
	e = f'({pi_sum}) * Q(1,{size-1}) '

	file.write(threshold_constraint + '\n')

	file.write('# Randomised strategies (proper probability distributions)\n')

	# Generate strategy constraints for state-specific sensors
	strategy_constraints = []
	for s in sensor_states:
		for act in actions:
			strategy_constraints.extend([
				f'xo{s}{act} <= 1,',
				f'xo{s}{act} >= 0,'
			])
		strategy_constraints.append(f'xo{s}l + xo{s}r == 1,')

	# Add default strategy constraints
	strategy_constraints.extend([
		'xol <= 1,',
		'xol >= 0,',
		'xor <= 1,',
		'xor >= 0,',
		'xol + xor == 1,'
	])

	file.write('\n'.join(strategy_constraints) + '\n')

	if det == 1:
		file.write('#Deterministic strategies activated\n')
		det_constraints = []
		for s in sensor_states:
			for act in actions:
				det_constraints.append(f'Or(xo{s}{act} == 0, xo{s}{act} == 1),')
		det_constraints.extend([
			'Or(xol == 0, xol == 1),',
			'Or(xor == 0, xor == 1),'
		])
		file.write('\n'.join(det_constraints) + '\n')

	file.write('# y is a function that should map every state N to some observable class M\n')

	# Binary constraints for sensor variables
	sensor_binary_constraints = [f'Or(ys{s} == 0, ys{s} == 1),' for s in sensor_states]
	file.write('\n'.join(sensor_binary_constraints) + '\n')

	# Budget constraint - total sensors used <= budget
	sensor_sum = ' + '.join([f'ys{s}' for s in sensor_states])
	file.write(f'{sensor_sum} == {budget}')

	file.write('\n)\n')

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

create_line_pre(budget, target, size, threshold, det, pre)
