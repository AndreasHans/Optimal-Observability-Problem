#!/usr/bin/python3
import sys
import os
import math
from itertools import chain, combinations
import copy


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def create_line_pre(budget, target, size, threshold, det, pre):
	
	states_obs = pre.split('|')

	obs = {} #mapping states observables

	total = {} #total number of observables and which ones

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
	if det == 0:
		file = open('ssp_line_' + str(size)  +'_ran_z3.py', 'w')
	else:
		file = open('ssp_line_' + str(size) +'_det_z3.py', 'w')

	file.write('from z3 import *\n\n')

	power = []

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
			used['xo' + ''.join([str(ele) + '' for ele in o]) + 'l'] = ''



	file.write('xol = Real(\'xol\')\n')
	file.write('xor = Real(\'xor\')\n')

	file.write('solver = Solver()\n\n\n')

	file.write('solver.add(\n')

	file.write('#We cannot do better than the fully observable case\n')

	for i in range(0, size):
		file.write('pi' + str(i) + '>=' + str(abs(target - i)) + ', ')

	file.write('\n')

	file.write('# Expected cost/reward equations\n')

	save = {}

	power.clear()
	for i in range (0, size):
		if str(i) in obs:
			state_obs = obs[str(i)]
			power.append(list(powerset(state_obs)))
			for a in ['l', 'r']:
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
		file.write('pi' + str(i) + '== (' + save[str(i) + 'l'] + ') * (1 + pi' + str(max(i-1, 0)) + ') + ')
		file.write('(' + save[str(i) + 'r'] + ') * (1 + pi' + str(min(i+1, size-1)) + '), \n')

	file.write('# We are dropped uniformly in the line\n# We want to check if the minimal expected cost is below some threshold ' + str(threshold) + '\n')

	line = '('
	for i in range(0, size):
		if i == target:
			continue
		if i < size - 1:
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
			file.write('xo' + ''.join([str(ele) + '' for ele in o]) + 'l' + ' + xo' + ''.join([str(ele) + '' for ele in o]) + 'r == 1,\n')
			
			used['xo' + ''.join([str(ele) + '' for ele in o]) + 'l'] = ''

	file.write('xol <= 1,\n')
	file.write('xol >= 0,\n')
	file.write('xor <= 1,\n')
	file.write('xor >= 0,\n')
	file.write('xol + xor == 1,\n')

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
				used['xo' + ''.join([str(ele) + '' for ele in o]) + 'l'] = ''
		file.write('Or(xol == 0 , xol == 1),\n')
		file.write('Or(xor == 0 , xor == 1),\n')


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
