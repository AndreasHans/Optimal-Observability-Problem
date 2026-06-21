#!/usr/bin/python3
import sys

def create_grid_constrained(budget: int, target: int, size: int, threshold: int, det: int):
	strat = "det" if det == 1 else "ran"
	file = open(f'grid_{size}x{size}_{strat}_z3.py', 'w')

	file.write('from z3 import *\n\n')

	side = size

	# Dictionary to keep the values
	var = {}

	actions = ['l', 'r', 'u', 'd']

	column = target % size

	size = size * size

	file.write('# Expected cost/reward of reaching the goal.\n')
	pi_vars = '\n'.join([f'pi{s} = Real(\'pi{s}\')' for s in range(size)])
	file.write(pi_vars + '\n')

	file.write('\n# Choice of observations (e.g. ys0o1 = 1 means that in state 0, observable 1 is observed)\n')
	obs_vars = '\n'.join([f'ys{s}o{o} = Real(\'ys{s}o{o}\')'
	                     for s in range(size) if s != target
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
	count = 0
	for s in range(size):
		if s % target == column:
			bound_value = abs(target - s) // side
			bounds_constraints.append(f'pi{s}>={bound_value}')
			count += bound_value
		else:
			bound_value = abs(column - s % side) + (abs(target - s) // side)
			bounds_constraints.append(f'pi{s}>={bound_value}')
			count += bound_value

	file.write(', '.join(bounds_constraints) + ', \n')
	file.write('# Expected cost/reward equations\n')

    # For optimal rewards: print(count)

	# Generate optimized cost equations for grid
	cost_equations = []
	for s in range(size):
		if s == target:
			cost_equations.append(f'pi{s} == 0')
			continue

		# Calculate next states for each direction
		left_next = s if s % side == 0 else s - 1
		right_next = s if s % side == side - 1 else s + 1
		up_next = s if s - side < 0 else s - side
		down_next = s if s + side >= size else s + side

		# Build action terms using efficient action-to-next-state mapping
		next_states = {'l': left_next, 'r': right_next, 'u': up_next, 'd': down_next}

		action_terms = []
		for act in actions:
			obs_strategy_terms = [f'ys{s}o{o}*xo{o}{act}' for o in range(1, budget + 1)]
			obs_strategy_sum = ' + '.join(obs_strategy_terms)
			next_state = next_states[act]
			action_terms.append(f'({obs_strategy_sum}) * (1 + pi{next_state})')

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
	bounds_constraints = [f'xo{o}{act}>= 0,\nxo{o}{act}<= 1,'
	                     for o in range(1, budget + 1)
	                     for act in actions]
	file.write('\n'.join(bounds_constraints) + '\n')

	# Generate probability sum constraints for all actions
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

	file.write('# ysNoM is a function that should map every state N to some observable class M\n')
	obs_binary_constraints = [f'Or(ys{s}o{o}== 0 , ys{s}o{o}== 1),'
	                         for s in range(size) if s != target
	                         for o in range(1, budget + 1)]
	file.write('\n'.join(obs_binary_constraints) + '\n')

	file.write('# Every state should be mapped to exactly one equivalence class\n')
	equiv_class_constraints = []
	for s in range(size):
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


size = int(sys.argv[1])
target = int(sys.argv[2])
budget = int(sys.argv[3])
threshold = sys.argv[4]
det = int(sys.argv[5])


create_grid_constrained(budget, target, size, threshold, det)
