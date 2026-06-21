#!/usr/bin/python3
import sys
import os
import math
from itertools import chain, combinations
import copy


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def create_maze_pre(budget, target, sizex, sizey, threshold, det, pre):
	
	states_obs = pre.split('|')

	obs = {} #mapping states observables

	total = {} #total number of observables and which ones

	if det == 0:
		file = open('ssp_maze_' + str(sizex) + 'x' + str(sizey)  +'_ran_z3.py', 'w')
	else:
		file = open('ssp_maze_' + str(sizex) + 'x' + str(sizey) +'_det_z3.py', 'w')

	for sub in states_obs:
		sub = sub.strip()
		spl = sub.split(' ')
		observales = spl[1].split(',')
		obs[spl[0]] = observales
		for i in observales:
			if i in total:
				pass
			else:
				total[i] = ''

	file.write('from z3 import *\n\n')

	power = []

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

	size = len(numbers)

	for i in range(0, size):
		if(str(i) in obs):
			power.append(list(powerset(obs[str(i)])))


	file.write('# Expected cost/reward of reaching the goal.\n')
	for i in range(0, size):
		file.write('pi' + str(i) + ' = Real(\'pi' + str(i) + '\')\n')

	file.write('\n# Choice of observations\n')

	keep_power = copy.deepcopy(power)


	used = {}
	y = []

	for i in range(0, size):
		if i == target:
			continue
		for o in obs[str(i)]:
			if 'y' + str(o) in used:
				continue
			file.write('y' + str(o) + ' = Real(\'y' + str(o) + '\')\n')
			used['y' + str(o)] = ''
			y.append('y' + str(o))



	file.write('\n# Rates of randomized strategies\n')

	for state in range(0,len(power)):
		for o in power[state]:
			if len(o) == 0:
				continue
			if 'xo' + ''.join([str(ele) + '' for ele in o]) in used:
				continue
			file.write('xo' + ''.join([str(ele) + '' for ele in o]) + 'l' + ' = Real(\'xo' + ''.join([str(ele) + '' for ele in o]) + 'l' + '\')\n')
			file.write('xo' + ''.join([str(ele) + '' for ele in o]) + 'r' + ' = Real(\'xo' + ''.join([str(ele) + '' for ele in o]) + 'r' + '\')\n')
			file.write('xo' + ''.join([str(ele) + '' for ele in o]) + 'u' + ' = Real(\'xo' + ''.join([str(ele) + '' for ele in o]) + 'u' + '\')\n')
			file.write('xo' + ''.join([str(ele) + '' for ele in o]) + 'd' + ' = Real(\'xo' + ''.join([str(ele) + '' for ele in o]) + 'd' + '\')\n')
			used['xo' + ''.join([str(ele) + '' for ele in o]) + 'l'] = ''



	file.write('xol = Real(\'xol\')\n')
	file.write('xor = Real(\'xor\')\n')
	file.write('xod = Real(\'xod\')\n')
	file.write('xou = Real(\'xou\')\n')

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

	save = {}

	power.clear()
	for i in range (0, size):
		if str(i) in obs:
			state_obs = obs[str(i)]
			power.append(list(powerset(state_obs)))
			for a in ['l', 'r', 'u', 'd']:
				constraint = ''
				for j in range (0, len(power[0])):
					con = {}
					tot = ''
					if len(power[0][j]) > 0:
						for element in power[0][j]:
							constraint = constraint + 'y' + element + '*'
							con[element] = ''
							tot = tot + element

					for o in state_obs:
						if o in con:
							pass
						else:
							constraint = constraint + '(1 - y' + o + ')*'
					if j == len(power[0]) - 1:
						constraint = constraint + 'xo' + tot + str(a)
					else:
						constraint = constraint + 'xo' + tot + str(a) + ' + '
				save[str(i) + str(a)] = constraint
		power.clear()


	for i in range(0, size):
		if i == target:
			file.write('pi' + str(i) + ' == 0, \n')
			continue

		if i < sizey:
			file.write('pi' + str(i) + '== (' + save[str(i) + 'l'] + ') * (1 + pi' + str(max(i-1, 0)) + ') + ')
			file.write('(' + save[str(i) + 'r'] + ') * (1 + pi' + str(min(i+1, sizey-1)) + ') + ')
			file.write('(' + save[str(i) + 'u'] + ') * (1 + pi' + str(i) + ') + ')
			if i == (sizey-1)//2:
				file.write('(' + save[str(i) + 'd'] + ') * (1 + pi' + str(sizey + 1) + '),\n')
			elif i == sizey-1:
				file.write('(' + save[str(i) + 'd'] + ') * (1 + pi' + str(sizey + 2) + '),\n')
			elif i ==0:
				file.write('(' + save[str(i) + 'd'] + ') * (1 + pi' + str(sizey) + '),\n')
			else:
				file.write('(' + save[str(i) + 'd'] + ') * (1 + pi' + str(i) + '),\n')
		else:
			file.write('pi' + str(i) + '== (' + save[str(i) + 'l'] + ') * (1 + pi' + str(i) + ') + ')
			file.write('(' + save[str(i) + 'r'] + ') * (1 + pi' + str(i) + ') + ')
			if i  <= sizey + 2:
				if i == sizey:
					file.write('(' + save[str(i) + 'u'] + ') * (1 + pi' + str((i - sizey)) + ') + ')
				elif i == sizey + 1:
					file.write('(' + save[str(i) + 'u'] + ') * (1 + pi' + str((sizey-1)//2) + ') + ')
				else:
					file.write('(' + save[str(i) + 'u'] + ') * (1 + pi' + str(sizey-1) + ') + ')
			else:
				file.write('(' + save[str(i) + 'u'] + ') * (1 + pi' + str(i - 3) + ') + ')
			if i + 3 <= numbers[-1]:
				file.write('(' + save[str(i) + 'd'] + ') * (1 + pi' + str(i + 3) + '),\n')
			else:
				file.write('(' + save[str(i) + 'd'] + ') * (1 + pi' + str(i) + '), \n')

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
	used.clear()

	for state in range(0,len(keep_power)):
		for o in keep_power[state]:
			if len(o) == 0:
				continue
			if 'xo' + ''.join([str(ele) + '' for ele in o]) in used:
				continue
			file.write('xo' + ''.join([str(ele) + '' for ele in o]) + 'l <= 1,\n')
			file.write('xo' + ''.join([str(ele) + '' for ele in o])+ 'l >= 0,\n')
			file.write('xo' + ''.join([str(ele) + '' for ele in o]) + 'r <= 1,\n')
			file.write('xo' + ''.join([str(ele) + '' for ele in o]) + 'r >= 0,\n')
			file.write('xo' + ''.join([str(ele) + '' for ele in o]) + 'u <= 1,\n')
			file.write('xo' + ''.join([str(ele) + '' for ele in o])+ 'u >= 0,\n')
			file.write('xo' + ''.join([str(ele) + '' for ele in o]) + 'd <= 1,\n')
			file.write('xo' + ''.join([str(ele) + '' for ele in o]) + 'd >= 0,\n')
			file.write('xo' + ''.join([str(ele) + '' for ele in o]) + 'l' + ' + xo' + ''.join([str(ele) + '' for ele in o]) + 'r'
			+ ' + xo' + ''.join([str(ele) + '' for ele in o]) + 'u' + ' + xo' + ''.join([str(ele) + '' for ele in o]) + 'd == 1,\n')
			
			used['xo' + ''.join([str(ele) + '' for ele in o]) + 'l'] = ''

	file.write('xol <= 1,\n')
	file.write('xol >= 0,\n')
	file.write('xor <= 1,\n')
	file.write('xor >= 0,\n')

	file.write('xou <= 1,\n')
	file.write('xou >= 0,\n')
	file.write('xod <= 1,\n')
	file.write('xod >= 0,\n')
	file.write('xol + xor + xou + xod == 1,\n')

	if det == 1:
		file.write('#Deterministic strategies activated\n')
		used.clear()
		for state in range(0,len(keep_power)):
			for o in keep_power[state]:
				if len(o) == 0:
					continue
				if 'xo' + ''.join([str(ele) + '' for ele in o]) in used:
					continue
				file.write('Or(xo' + ''.join([str(ele) + '' for ele in o]) + 'l == 0 , xo' + ''.join([str(ele) + '' for ele in o]) + 'l == 1),\n')
				file.write('Or(xo' + ''.join([str(ele) + '' for ele in o]) + 'r == 0 , xo' + ''.join([str(ele) + '' for ele in o]) + 'r == 1),\n')
				file.write('Or(xo' + ''.join([str(ele) + '' for ele in o]) + 'u == 0 , xo' + ''.join([str(ele) + '' for ele in o]) + 'u == 1),\n')
				file.write('Or(xo' + ''.join([str(ele) + '' for ele in o]) + 'd == 0 , xo' + ''.join([str(ele) + '' for ele in o]) + 'd == 1),\n')
				used['xo' + ''.join([str(ele) + '' for ele in o]) + 'l'] = ''
		file.write('Or(xol == 0 , xol == 1),\n')
		file.write('Or(xor == 0 , xor == 1),\n')
		file.write('Or(xou == 0 , xou == 1),\n')
		file.write('Or(xod == 0 , xod == 1),\n')


	used.clear()
	file.write('# y is a function that should map every state N to some observable class M\n')
	
	for i in range(0, size):
		if i == target:
			continue
		for o in obs[str(i)]:
			if 'y' + str(o) in used:
				continue
			file.write('Or (y' + str(o) + ' == 0 , y' +  str(o) + ' == 1 ),\n')
			used['y' + str(o)] = ''

	for i in range (0, len(y)):
		if i == len(y) - 1:
			file.write(y[i] + ' == ' + str(budget))
		else:
			file.write(y[i] + ' + ')

	file.write('\n)\n')

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
pre = sys.argv[7]

if pre == 'predefined.txt':
	file = open(pre, 'r')
	pre = file.readlines()[0].strip('\'')


create_maze_pre(budget, target, sizex, sizey, threshold, det, pre)
