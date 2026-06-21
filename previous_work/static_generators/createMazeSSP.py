#!/usr/bin/python3
import sys


def create_maze_pre(budget, target, height, width, threshold, det, pre):
	actions = ['l', 'r', 'u', 'd']

	puzzle_type = "ssp_maze"
	strat_type = "det" if det == 1 else "ran"
	file = open(f'{puzzle_type}_{height}x{width}_{strat_type}_z3.py', 'w')

	file.write('from z3 import *\n\n')

	if width % 2 == 0:
		print('We need odd number for size y')
		exit(1)

	# Generate maze state numbers
	numbers = []
	counter = 0
	for i in range(height):
		for j in range(width):
			if i == 0:
				numbers.append(counter)
				counter += 1
			else:
				if j == 0 or j == width-1 or j == (width - 1)//2:
					numbers.append(counter)
					counter += 1

	size = len(numbers)

	file.write('# Expected cost/reward of reaching the goal.\n')
	pi_vars = '\n'.join([f'pi{s} = Real(\'pi{s}\')' for s in range(size)])
	file.write(pi_vars + '\n')

	file.write('\n# Choice of observations\n')

	# Generate sensor variables - one per non-target state (sensor selection approach)
	sensor_states = [s for s in range(size) if s != target]
	sensor_vars = [f'y{s} = Real(\'y{s}\')' for s in sensor_states]
	file.write('\n'.join(sensor_vars) + '\n')

	file.write('\n# Rates of randomized strategies\n')

	# Generate state-specific strategy variables (when sensor is on for that state)
	state_strategy_vars = [f'xo{s}{act} = Real(\'xo{s}{act}\')'
	                      for s in sensor_states
	                      for act in actions]
	file.write('\n'.join(state_strategy_vars) + '\n')

	# Default strategy variables (when no sensor observes - unknown state)
	default_strategies = [f'xo{act} = Real(\'xo{act}\')' for act in actions]
	file.write('\n'.join(default_strategies) + '\n')

	file.write('solver = Solver()\n\n\n')
	file.write('solver.add(\n')
	file.write('#We cannot do better than the fully observable case\n')

	# Generate bounds constraints for maze
	bounds_constraints = []
	th = 0
	for i in numbers:
		if i < width:
			bound_value = abs(i - width // 2) + height - 1
			bounds_constraints.append(f'pi{i}>={bound_value}')
			th += bound_value
		else:
			if (i - width) % 3 == 1:
				bound_value = (target - i) // 3
				bounds_constraints.append(f'pi{i}>={bound_value}')
				th += bound_value
			else:
				bound_value = ((i - width) // 3) + (width - width // 2) + height - 1
				bounds_constraints.append(f'pi{i}>={bound_value}')
				th += bound_value

	file.write(', '.join(bounds_constraints) + ',\n')

	# For optimal reward: print(th)

	file.write('# Expected cost/reward equations\n')

	# Helper function to get next state for maze navigation
	def get_next_state(state, action):
		if action == 'l':
			if 0 < state < width:
				return state - 1
		elif action == 'r':
			if 0 <= state < width - 1:
				return state + 1
		elif action == 'u':
			if state == width:
				return 0
			elif state == width + 1:
				return (width - 1) // 2
			elif state >= width + 2:
				return state - 3
		else:  # action == 'd'
			if state == 0:
				return width
			elif state == (width - 1) // 2:
				return width + 1
			elif width - 1 <= state <= numbers[-1] - 3:
				return state + 3
		return state

	# Generate cost equations for sensor selection
	cost_equations = []
	for s in range(size):
		if s == target:
			cost_equations.append(f'pi{s} == 0')
			continue

		# Build sensor selection strategies
		action_terms = []
		for act in actions:
			strategy_term = f'((1 - y{s})*xo{act} + y{s}*xo{s}{act})'
			next_state = get_next_state(s, act)
			action_terms.append(f'{strategy_term} * (1 + pi{next_state})')

		equation = f'pi{s}== ' + ' + '.join(action_terms)
		cost_equations.append(equation)

	file.write(',\n'.join(cost_equations) + ',\n')

	# Generate threshold constraint
	file.write(f'# We are dropped uniformly in the maze\n# We want to check if the minimal expected cost is below some threshold {threshold}\n')
	pi_terms = [f'pi{s}' for s in range(size) if s != target]
	pi_sum = '+'.join(pi_terms)
	threshold_constraint = f'({pi_sum}) * Q(1,{size-1}) {threshold},'
	e = f'({pi_sum}) * Q(1,{size-1}) '
	file.write(threshold_constraint + '\n')

	# Generate strategy constraints
	file.write('# Randomised strategies (proper probability distributions)\n')

	# Generate strategy constraints
	strategy_constraints = []

	# State-specific sensor constraints
	for s in sensor_states:
		strategy_constraints.extend([f'xo{s}{act} <= 1,\nxo{s}{act} >= 0,'
		                           for act in actions])
		action_sum = ' + '.join([f'xo{s}{act}' for act in actions])
		strategy_constraints.append(f'{action_sum} == 1,')

	# Default strategy constraints
	strategy_constraints.extend([f'xo{act} <= 1,\nxo{act} >= 0,'
	                           for act in actions])
	default_action_sum = ' + '.join([f'xo{act}' for act in actions])
	strategy_constraints.append(f'{default_action_sum} == 1,')

	file.write('\n'.join(strategy_constraints) + '\n')

	if det == 1:
		file.write('#Deterministic strategies activated\n')
		det_constraints = [f'Or(xo{s}{act} == 0, xo{s}{act} == 1),'
		                  for s in sensor_states
		                  for act in actions]

		# Add default deterministic constraints
		det_constraints.extend([f'Or(xo{act} == 0, xo{act} == 1),'
		                       for act in actions])

		file.write('\n'.join(det_constraints) + '\n')

	file.write('# y is a function that should map every state N to some observable class M\n')

	# Binary constraints for sensor variables
	sensor_binary_constraints = [f'Or(y{s} == 0, y{s} == 1),' for s in sensor_states]
	file.write('\n'.join(sensor_binary_constraints) + '\n')

	# Budget constraint - total sensors used <= budget
	file.write('# Budget constraint on total no. of sensors used\n')
	sensor_sum = ' + '.join([f'y{s}' for s in sensor_states])
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


sizex = int(sys.argv[1])
sizey = int(sys.argv[2])
target = int(sys.argv[3])
budget = int(sys.argv[4])
threshold = sys.argv[5]
det = int(sys.argv[6])
pre = sys.argv[7]

if pre == 'predefined.txt':
	file = open(pre, 'r')
	pre = file.readlines()[0].strip('\'')


create_maze_pre(budget, target, sizex, sizey, threshold, det, pre)
