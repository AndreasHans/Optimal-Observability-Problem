#!/usr/bin/python3
import sys


def create_maze_constrained(budget, target, height, width, threshold, det):
	strat = "det" if det == 1 else "ran"
	file = open(f'maze_{height}x{width}_{strat}_z3.py', 'w')

	file.write('from z3 import *\n\n')

	actions = ['l', 'r', 'u', 'd']

	if width % 2 == 0:
		print('We need odd number for size y')
		exit(1)

	numbers = []
	counter = 0
	for i in range(0, height):
		for j in range(0, width):
			if i == 0:
				numbers.append(counter)
				counter = counter + 1
			else:
				if j == 0 or j == width - 1 or j == (width - 1) // 2:
					numbers.append(counter)
					counter = counter + 1

	file.write('# Expected cost/reward of reaching the goal.\n')
	pi_vars = '\n'.join([f'pi{s} = Real(\'pi{s}\')' for s in numbers])
	file.write(pi_vars + '\n')

	file.write('\n# Choice of observations (e.g. ys01 = 1 means that in state 0, observable 1 is observed)\n')
	obs_vars = '\n'.join([f'ys{s}o{o} = Real(\'ys{s}o{o}\')'
						  for s in numbers if s != target
						  for o in range(1, budget + 1)])
	file.write(obs_vars + '\n')

	file.write('\n# Rates of randomized strategies\n')
	strategy_vars = '\n'.join([f'xo{o}{act} = Real(\'xo{o}{act}\')'
							   for o in range(1, budget + 1)
							   for act in actions])
	file.write(strategy_vars + '\n')

	file.write('solver = Solver()\n\n\n')
	file.write('solver.add(\n')
	file.write('#We cannot do better than the fully observable case\n')

	# Generate constraints for optimal bounds on expected reward
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

	file.write(', '.join(bounds_constraints) + ', ')

	# For optimal reward: print(th)
	# For the maze goal: print(numbers[-1])

	file.write('\n')
	file.write('# Expected cost/reward equations\n')

	# Generate cost/reward equations for each state
	cost_equations = []
	for s in numbers:
		if s == target:
			cost_equations.append(f'pi{s} == 0')
			continue

		# Helper function to calculate next states for maze navigation
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
			else: # action == 'd'
				if state == 0:
					return width
				elif state == (width - 1) // 2:
					return width + 1
				elif width - 1 <= state <= numbers[-1] - 3:
					return state + 3
			return state

		# Build action terms for each direction using transition tables
		action_terms = []
		for act in actions:
			obs_strategy_terms = [f'ys{s}o{o}*xo{o}{act}' for o in range(1, budget + 1)]
			obs_strategy_sum = ' + '.join(obs_strategy_terms)
			next_state = get_next_state(s, act)
			action_terms.append(f'({obs_strategy_sum}) * (1 + pi{next_state})')

		equation = f'pi{s} == ' + ' + '.join(action_terms)
		cost_equations.append(equation)

	file.write(',\n'.join(cost_equations) + ',\n')


	file.write(f'# We are dropped uniformly in the maze\n'
			   f'# We want to check if the minimal expected cost is below some threshold {threshold}\n')

	# Generate threshold constraint using list comprehension
	pi_terms = [f'pi{i}' for i in numbers if i != target]
	pi_sum = '+'.join(pi_terms)
	threshold_constraint = f'({pi_sum}) * Q(1,{numbers[-1]}) {threshold},'
	e = f'({pi_sum}) * Q(1,{numbers[-1]}) '

	file.write(threshold_constraint + '\n')

	file.write('# Randomised strategies (proper probability distributions)\n')
	# Generate bounds constraints using list comprehension
	bounds_constraints = [f'xo{o}{act}>= 0,\nxo{o}{act}<= 1,'
	                     for o in range(1, budget + 1)
	                     for act in actions]
	file.write('\n'.join(bounds_constraints) + '\n')

	# Generate sum constraints for probability distributions
	sum_constraints = []
	for o in range(1, budget + 1):
		action_sum = ' + '.join([f'xo{o}{act}' for act in actions])
		sum_constraints.append(f'{action_sum} == 1,')
	file.write('\n'.join(sum_constraints) + '\n')

	if det == 1:
		file.write('# Deterministic Strategies activated\n')
		det_constraints = [f'Or(xo{o}{act} == 0, xo{o}{act} == 1),'
		                  for o in range(1, budget + 1)
		                  for act in actions]
		file.write('\n'.join(det_constraints) + '\n')

	file.write('# ysNM is a function that should map every state N to some observable class M\n')
	obs_binary_constraints = [f'Or(ys{s}o{o}== 0 , ys{s}o{o}== 1),'
	                         for s in numbers if s != target
	                         for o in range(1, budget + 1)]
	file.write('\n'.join(obs_binary_constraints) + '\n')

	file.write('# Every state should be mapped to exactly one equivalence class\n')
	equiv_class_constraints = []
	for s in numbers:
		if s != target:
			obs_sum = ' + '.join([f'ys{s}o{o}' for o in range(1, budget + 1)])
			equiv_class_constraints.append(f'{obs_sum} == 1')
	file.write('\n'.join([constraint + (',' if i < len(equiv_class_constraints) - 1 else '')
	                     for i, constraint in enumerate(equiv_class_constraints)]))
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

create_maze_constrained(budget, target, sizex, sizey, threshold, det)
