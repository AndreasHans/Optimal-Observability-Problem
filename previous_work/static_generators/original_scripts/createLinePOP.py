#!/usr/bin/python3
import sys
import os
import math
import copy


def create_line_constrained(budget, target, size, threshold, det):

	if det == 0:
		file = open('line_' + str(size) +'_ran_z3.py', 'w')
	else:
		file = open('line_' + str(size) +'_det_z3.py', 'w')

	file.write('from z3 import *\n\n')

	# Dictionary to keep the values
	var = {}

	actions = ['l', 'r']

	file.write('# Expected cost/reward of reaching the goal.\n')
	for i in range(0, size):
		file.write('pi' + str(i) + ' = Real(\'pi' + str(i) + '\')\n')


	file.write('\n# Choice of observations (e.g. ys01 = 1 means that in state 0, observable 1 is observed)\n')
	for i in range(0, size):
		if i == target:
			continue
		for j in range(1, budget + 1):
			file.write('ys' + str(i) + str(j) + ' = Real(\'ys' + str(i) + str(j) + '\')\n')


	file.write('\n# Rates of randomized strategies\n')
	for i in range(1, budget + 1):
		file.write('xo' + str(i) + 'l' + ' = Real(\'xo' + str(i) + 'l\')\n')
		file.write('xo' + str(i) + 'r' + ' = Real(\'xo' + str(i) + 'r\')\n')


	file.write('solver = Solver()\n\n\n')

	file.write('solver.add(\n')

	file.write('#We cannot do better than the fully observable case\n')

	for i in range(0, size):
		file.write('pi' + str(i) + '>=' + str(abs(target - i)) + ', ')

	file.write('\n')
	file.write('# Expected cost/reward equations\n')

	for i in range(0, size):
		if i == target:
			file.write('pi' + str(i) + ' == 0, \n')
		line = 'pi' + str(i) + ' == ' + '(ys' + str(i)
		if i == int(target):
			continue
		for a in actions:
			for o in range(1, budget + 1):
				line = line  + str(o) + '*xo' + str(o) + a
				if o < budget:
					line = line + '+ ys' + str(i)
				else:
					if a == 'l':
						line = line + ')*(1 + pi' + str(max(i-1, 0)) + ') + (ys' + str(i)
					else:
						line = line + ')*(1 + pi' + str(min(i+1, size-1)) + ')'
		file.write(line + ',\n')

	file.write('# We are dropped uniformly in the line\n# We want to check if the minimal expected cost is below some threshold ' + str(threshold) + '\n')

	line = '('
	for i in range(0, size):
		if i == target:
			continue
		if i < size - 1:
			if target == size - 1:
				if i == size - 2 :
					line = line + 'pi' + str(i) + ')'
				else:
					line = line + 'pi' + str(i) + '+'
			else:
				line = line + 'pi' + str(i) + '+'
		else:
			line = line + 'pi' + str(i) + ')'

	e = copy.deepcopy(line + ' * Q(1,' + str(size-1) + ') ')
	
	line = line + ' * Q(1,' + str(size-1) + ') ' + str(threshold) + ','

	file.write(line + '\n')

	file.write('# Randomised strategies (proper probability distributions)\n')
	for i in range(1, budget + 1):
		for a in actions:
			file.write('xo' + str(i) + a + '>= 0,\n')
			file.write('xo' + str(i) + a + '<= 1,\n')
	
	
	for i in range(1, budget + 1):
		for a in actions:
			if a == 'l':
				file.write('xo' + str(i) + a + ' + ')
			else:
				file.write('xo' + str(i) + a + ' == 1,\n')

	if det == 1:
		file.write('# Deterministic Strategies activated\n')
		for i in range(1, budget + 1):
			file.write('Or(xo' + str(i) + 'l ' + '== 0, xo' + str(i) + 'l' + ' == 1),\n')
			file.write('Or(xo' + str(i) + 'r ' + '== 0, xo' + str(i) + 'r' + ' == 1),\n')

	file.write('# ysNM is a function that should map every state N to some observable class M\n')

	for i in range(0, size):
		if i == target:
			continue
		for j in range(1, budget + 1):
			file.write('Or(ys' + str(i) + str(j) +  '== 0 , ys' + str(i) + str(j) + '== 1),\n')

	file.write('# Every state should be mapped to exactly one equivalence class\n')

	for i in range(0, size):
		if i == target:
			continue
		for j in range(1, budget + 1):
			file.write('ys' + str(i) + str(j))
			if j < budget:
				file.write(' + ')
			else:
				file.write(' == 1')
		if i == size - 1:
			file.write('\n)\n\n')
		else:
			if i == size - 2:
				if target == size - 1:
					file.write('\n)\n\n')
				else:
					file.write(',\n')
			else:
				file.write(',\n')

	file.write('set_option(max_args=1000000, max_lines=100000000)\n')

	file.write('file_results = open(\'results.txt\', \'w\')\n')

	file.write('file_reward = open(\'reward.txt\', \'w\')\n')


	file.write('if solver.check() == sat:\n\t')
	file.write('m = solver.model()\n\t')
	file.write('print(\'Solution found\')\n\t')
	file.write('file_results.write(str(m))\n\t')
	file.write('file_reward.write(str(m.eval(' + str(e) + ')))\n')
	file.write('elif solver.check() == unsat:\n\t')
	file.write('print(\'No solution!!!\')\n\t')
	file.write('file_reward.write(\'N/A\')\n')
	file.write('else:\n\t')
	file.write('print(\'Unknown\')')


size = int(sys.argv[1])
target = int(sys.argv[2])
budget = int(sys.argv[3])
threshold = sys.argv[4]
det = int(sys.argv[5])

create_line_constrained(budget, target, size, threshold, det)

