#!/usr/bin/python3
import sys
import os
import math
from itertools import chain, combinations
import copy


def create_maze_constrained(budget, target, sizex, sizey, threshold, det):

	if det == 0:
		file = open('maze_' + str(sizex) + 'x' + str(sizey)  +'_ran_z3.py', 'w')
	else:
		file = open('maze_' + str(sizex) + 'x' + str(sizey) +'_det_z3.py', 'w')


	file.write('from z3 import *\n\n')

	# Dictionary to keep the values
	var = {}

	actions = ['l', 'r', 'u', 'd']

	size = sizex * sizey

	if sizey%2 == 0:
		print('We need odd number for size y')
		exit(1)

	numbers = []
	counter = 0
	for i in range(0, sizex):
		for j in range(0, sizey):
			if i == 0:
				numbers.append(counter)
				counter = counter + 1
			else:
				if j == 0 or j == sizey-1 or j == (sizey-1)//2:
					numbers.append(counter)
					counter = counter + 1



	file.write('# Expected cost/reward of reaching the goal.\n')

	for i in numbers:
		file.write('pi' + str(i) + ' = Real(\'pi' + str(i) + '\')\n')


	file.write('\n# Choice of observations (e.g. ys01 = 1 means that in state 0, observable 1 is observed)\n')
	for i in numbers:
		if i == target:
			continue
		for j in range(1, budget + 1):
			file.write('ys' + str(i) + str(j) + ' = Real(\'ys' + str(i) + str(j) + '\')\n')


	file.write('\n# Rates of randomized strategies\n')
	for i in range(1, budget + 1):
		file.write('xo' + str(i) + 'l' + ' = Real(\'xo' + str(i) + 'l\')\n')
		file.write('xo' + str(i) + 'r' + ' = Real(\'xo' + str(i) + 'r\')\n')
		file.write('xo' + str(i) + 'u' + ' = Real(\'xo' + str(i) + 'u\')\n')
		file.write('xo' + str(i) + 'd' + ' = Real(\'xo' + str(i) + 'd\')\n')


	file.write('solver = Solver()\n\n\n')

	file.write('solver.add(\n')

	file.write('#We cannot do better than the fully observable case\n')

	th = 0

	for i in numbers:
		if(i < sizey):
			file.write('pi' + str(i) + '>=' + str(abs(i - sizey//2) + sizex - 1) + ', ')
			th = th + abs(i - sizey//2) + sizex - 1
		else:
			if (i - sizey)%3 == 1:
				#file.write('pi' + str(i) + '>=' + str(sizex - 1 - (i//3 - 1)) + ', ')
				file.write('pi' + str(i) + '>=' + str((target - i)//3) + ', ')
				th = th + (target - i)//3
			else:
				file.write('pi' + str(i) + '>=' + str(((i - sizey)//3) + (sizey - sizey//2) + sizex - 1) + ', ')
				th = th + ((i - sizey)//3) + (sizey - sizey//2) + sizex - 1



	#If you print th, you can find the optimal reward. And number[-1] the goal 
	#print(th)
	#print(numbers[-1])

	file.write('\n')
	file.write('# Expected cost/reward equations\n')



	for i in numbers:
		left = ''
		right = ''
		up = ''
		down = ''
		if i == target:
			file.write('pi' + str(i) + ' == 0, \n')
			continue
		file.write('pi' + str(i) + ' == ' + '(')

		for o in range(1, budget+1):
			if i < sizey:
				if o < budget:
					left = left + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'l + '
					right = right + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'r + '
					up = up + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'u + '
					down = down + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'd + '
				else:
					if i == 0:
						left = left + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'l) * (1 + pi' + str(i) + ') + ('
					else: 
						left = left + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'l) * (1 + pi' + str(i - 1) + ') + ('
					if i == sizey - 1:
						right = right + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'r) * (1 + pi' + str(i) + ') + ('
					else: 
						right = right + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'r) * (1 + pi' + str(i + 1) + ') + ('
					
					up = up + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'u) * (1 + pi' + str(i) + ') + ('
					
					if i == (sizey-1)//2:
						down = down + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'd) * (1 + pi' + str(sizey + 1) + '),\n'
					elif i == sizey-1:
						down = down + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'd) * (1 + pi' + str(sizey + 2) + '),\n'
					elif i ==0:
						down = down + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'd) * (1 + pi' + str(sizey) + '),\n'
					else: 
						down = down + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'd) * (1 + pi' + str(i) + '),\n'
			else:
				if o < budget:
					left = left + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'l + '
					right = right + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'r + '
					up = up + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'u + '
					down = down + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'd + '
				else:
					left = left + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'l) * (1 + pi' + str(i) + ') + ('
					right = right + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'r) * (1 + pi' + str(i) + ') + ('

					if i  <= sizey + 2:
						if i == sizey:
							up = up + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'u) * (1 + pi' + str(i - sizey)  + ') + ('
						elif i == sizey + 1:
							up = up + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'u) * (1 + pi' + str((sizey-1)//2)  + ') + ('
						else:
							up = up + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'u) * (1 + pi' + str(sizey-1)  + ') + ('
					else:
						up = up + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'u) * (1 + pi' + str(i - 3) + ') + ('
					
					if i + 3 <= numbers[-1]:
						down = down + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'd) * (1 + pi' + str(i + 3) + '),\n'
					else: 
						down = down + 'ys' + str(i) + str(o) + '*xo' + str(o) + 'd) * (1 + pi' + str(i) + '),\n'

		file.write(left + right + up + down)


	file.write('# We are dropped uniformly in the grid\n# We want to check if the minimal expected cost is below some threshold ' + str(threshold) + '\n')

	line = '('
	for i in numbers:
		if i == target:
			continue
		if i < numbers[-1]:
			if target == numbers[-1]:
				if i == numbers[-2] :
					line = line + 'pi' + str(i) + ')'
				else:
					line = line + 'pi' + str(i) + '+'
			else:
				line = line + 'pi' + str(i) + '+'
		else:
			line = line + 'pi' + str(i) + ')'
	e = copy.deepcopy(line + ' * Q(1,' + str(numbers[-1]) + ') ')
	line = line + ' * Q(1,' + str(numbers[-1]) + ') ' + str(threshold) + ','

	file.write(line + '\n')

	file.write('# Randomised strategies (proper probability distributions)\n')
	for i in range(1, budget + 1):
		for a in actions:
			file.write('xo' + str(i) + a + '>= 0,\n')
			file.write('xo' + str(i) + a + '<= 1,\n')
	
	
	for i in range(1, budget + 1):
		for a in actions:
			if a != 'd':
				file.write('xo' + str(i) + a + ' + ')
			else:
				file.write('xo' + str(i) + a + ' == 1,\n')

	if det == 1:
		file.write('# Deterministic Strategies activated\n')
		for i in range(1, budget + 1):
			file.write('Or(xo' + str(i) + 'l ' + '== 0, xo' + str(i) + 'l' + ' == 1),\n')
			file.write('Or(xo' + str(i) + 'r ' + '== 0, xo' + str(i) + 'r' + ' == 1),\n')
			file.write('Or(xo' + str(i) + 'u ' + '== 0, xo' + str(i) + 'u' + ' == 1),\n')
			file.write('Or(xo' + str(i) + 'd ' + '== 0, xo' + str(i) + 'd' + ' == 1),\n')

	file.write('# ysNM is a function that should map every state N to some observable class M\n')

	for i in numbers:
		if i == target:
			continue
		for j in range(1, budget + 1):
			file.write('Or(ys' + str(i) + str(j) +  '== 0 , ys' + str(i) + str(j) + '== 1),\n')

	file.write('# Every state should be mapped to exactly one equivalence class\n')

	for i in numbers:
		if i == target:
			continue
		for j in range(1, budget + 1):
			file.write('ys' + str(i) + str(j))
			if j < budget:
				file.write(' + ')
			else:
				file.write(' == 1')
		if i == numbers[-1]:
			file.write('\n)\n\n')
		else:
			if target == numbers[-1]:
				if i == numbers[-2]:
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


sizex = int(sys.argv[1])
sizey = int(sys.argv[2])
target = int(sys.argv[3])
budget = int(sys.argv[4])
threshold = sys.argv[5]
det = int(sys.argv[6])

create_maze_constrained(budget, target, sizex, sizey, threshold, det)

