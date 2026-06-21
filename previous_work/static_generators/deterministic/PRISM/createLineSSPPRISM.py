#!/usr/bin/python3
import more_itertools as mit
import sys
import os
import itertools
import math
from six.moves import input
from itertools import chain, combinations


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))




def create_line(budget, target, size, pre):
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

	file = open('line_PRE_' + str(size) + '_prism.sm', 'w')
	file.write('mdp\n\n')
	file.write('formula target = s =' + str(target) + ';\n\n\n')

	power = []

	for i in range(0, size):
		if(str(i) in obs):
			power.append(list(powerset(obs[str(i)])))


	pol = {} #observables with corresponding variable

	file.write('formula initialized = \n')

	used = {}
	y = []


	for state in range(0,len(power)):
		for o in power[state]:
			if len(o) == 0:
				continue
			if 'x' + ''.join([str(ele) + '' for ele in o]) in used:
				continue
			file.write('x' + ''.join([str(ele) + '' for ele in o]) + '0 >= 0 &\n')
			file.write('x' + ''.join([str(ele) + '' for ele in o]) + '1 >= 0 &\n')
			used['x' + ''.join([str(ele) + '' for ele in o])] = ''

	file.write('x0 >= 0 &\n')
	file.write('x1 >= 0 &\n')

	for i in range(0, size):
		if i == target:
			continue
		for o in obs[str(i)]:
			if 'y' + str(o) in used:
				continue
			file.write('y' + str(o) + ' >= 0 &\n')
			used['y' + str(o)] = ''
			y.append('y' + str(o))
	file.write('true;\n\n')


	file.write('\nmodule line\n')
	file.write('\t\ts : [0..' + str(size-1) + '];\n')
	file.write('\t\tstarted : bool;\n');

	used.clear()

	for state in range(0,len(power)):
		for o in power[state]:
			if len(o) == 0:
				continue
			if 'x' + ''.join([str(ele) + '' for ele in o]) in used:
				continue
			file.write('\t\tx' + ''.join([str(ele) + '' for ele in o]) + '0 : [-1..1] init -1;\n')
			file.write('\t\tx' + ''.join([str(ele) + '' for ele in o]) + '1 : [-1..1] init -1;\n')
			used['x' + ''.join([str(ele) + '' for ele in o])] = ''

	file.write('\t\tx0 : [-1..1] init -1;\n')
	file.write('\t\tx1 : [-1..1] init -1;\n')

	for i in range(0, size):
		if i == target:
			continue
		for o in obs[str(i)]:
			if 'y' + str(o) in used:
				continue
			file.write('\t\ty' + str(o) + ': [-1..1] init -1;\n')
			used['y' + str(o)] = ''



	file.write('\n\n')
	file.write('\n\t\t// CHOICE OF OBSERVATIONS\n\t\t')
	possible_comb = list(itertools.combinations(y, budget))

	temp = {}

	for obj in possible_comb:
		file.write('[' + ''.join([str(ele) + '' for ele in obj]) + '] ')
		file.write('(!initialized')
		for state in y:
			file.write(' & ')
			file.write(str(state) + ' =-1')
		file.write(') -> ')

		for ele in obj:
			temp[ele] = ''

		flag = 0

		for state in y:
			if flag != 0:
				file.write(' & ')
			if str(state) in temp:
				file.write('(' + state + '\'=1)')
				flag = 1
			else:
				file.write('(' + state + '\'=0)')
				flag = 1
		file.write(';\n\t\t')

		temp.clear()
	



	file.write('\n\t\t// CHOICE OF STRATEGY\n\t\t\n')
	used.clear()

	for state in range(0,len(power)):
		for o in power[state]:
			if len(o) == 0:
				continue
			if 'x' + ''.join([str(ele) + '' for ele in o]) in used:
				continue
			file.write('\t\t[x'+ ''.join([str(ele) + '' for ele in o]) + '0] ' +'(!initialized & x' + ''.join([str(ele) + '' for ele in o]) + '0 =-1 & x' + ''.join([str(ele) + '' for ele in o]) 
				+ '1 =-1) -> (x'+ ''.join([str(ele) + '' for ele in o]) + '0\' =1) & (x' + ''.join([str(ele) + '' for ele in o]) +'1\'=0);\n')
			file.write('\t\t[x'+ ''.join([str(ele) + '' for ele in o]) + '1] ' +'(!initialized & x' + ''.join([str(ele) + '' for ele in o]) + '0 =-1 & x' + ''.join([str(ele) + '' for ele in o]) 
				+ '1 =-1) -> (x'+ ''.join([str(ele) + '' for ele in o]) + '0\' =0) & (x' + ''.join([str(ele) + '' for ele in o]) +'1\'=1);\n')
			used['x' + ''.join([str(ele) + '' for ele in o])] = ''


	file.write('\t\t[x' + '0] ' +'(!initialized & x' + '0 =-1 & x'
		+ '1 =-1) -> (x' + '0\' =1) & (x' +'1\'=0);\n')
	
	file.write('\t\t[x'+ '1] ' +'(!initialized & x' + '0 =-1 & x' 
		+ '1 =-1) -> (x'+'0\' =0) & (x' +'1\'=1);\n')


	file.write('\n\n')


	if(target != 0):
		file.write('\t\t[] !started & initialized -> 1/' + str(size-1) + ': (started\' = true) & (s\' = 0)')
	else:
		file.write('\t\t[] !started & initialized -> 1/' + str(size-1) + ': (started\' = true) & (s\' = 1)')

	for i in range(1, size):
		if i == 0:
			continue
		else:
			if(i != target):
				file.write('\n')
				file.write('\t\t\t+ 1/'+ str(size-1) + ' : (started\'=true) & (s\'=' + str(i) +')')
	file.write(';\n')

	save = {}

	power.clear()
	for i in range (0, size):
		if str(i) in obs:
			state_obs = obs[str(i)]
			power.append(list(powerset(state_obs)))
			for a in range(0, 2):
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
						constraint = constraint + 'x' + tot + str(a)
					else:
						constraint = constraint + 'x' + tot + str(a) + ' + '
				save[str(i) + str(a)] = constraint
		power.clear()

	file.write('\n')

	for i in range(0, size):
		if i == target:
			file.write('\t\t[move] s=' + str(target) + ' & started '  +' -> (s\' = s); \n')
			continue
		if str(i) in obs:
			if i == 0:
				file.write('\t\t[move] s=0 & started  -> ' + save[str(i) + str(0)] + ': (s\'=0) + ' + save[str(i) + str(1)] + ': (s\'=1);\n')
			elif i == size-1:
				file.write('\t\t[move] s=' + str(size-1) + ' & started '  + ' -> ' + save[str(i) + str(0)] + ': (s\'='+ str(size-2) +') + ' + save[str(i) + str(1)] +  ': (s\'=' + str(size-1) + ');\n')
			else:
				file.write('\t\t[move] s=' + str(i) + ' & started '  + ' -> ' + save[str(i) + str(0)] + ': (s\'='+ str(i-1) +') + ' + save[str(i) + str(1)] +': (s\'=' + str(i+1) + ');\n')
		else:
			if i == 0:
				file.write('\t\t[move] s=0 & started -> ' + 'x0' + ': (s\'=0) + ' + 'x1' + ': (s\'=1);\n')
			elif i == size-1:
				file.write('\t\t[move] s=' + str(size-1) + ' & started '  + ' -> ' + 'x0'+ ': (s\'='+ str(size-2) +') + ' + 'x1' +  ': (s\'=' + str(size-1) + ');\n')
			else:
				file.write('\t\t[move] s=' + str(i) + ' & started '  + ' -> ' + 'x0' + ': (s\'='+ str(i-1) +') + ' + 'x1' +': (s\'=' + str(i+1) + ');\n')

	

	file.write('endmodule\n\n')

	file.write('rewards\n')
	file.write('\t\t[move] !target : 1;\n')
	file.write('endrewards')







size = int(sys.argv[1])
target = int(sys.argv[2])
budget = int(sys.argv[3])
pre = str(sys.argv[4])

create_line(budget, target, size, pre)