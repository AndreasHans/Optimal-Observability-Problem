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




def create_maze(budget, target, sizex, sizey, pre):
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
				if j%2 == 0:
					numbers.append(counter)
					counter = counter + 1


	file = open('maze_PRE_' + str(size) + '_prism.sm', 'w')
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
			file.write('x' + ''.join([str(ele) + '' for ele in o]) + '2 >= 0 &\n')
			file.write('x' + ''.join([str(ele) + '' for ele in o]) + '3 >= 0 &\n')
			used['x' + ''.join([str(ele) + '' for ele in o])] = ''

	file.write('x0 >= 0 &\n')
	file.write('x1 >= 0 &\n')
	file.write('x2 >= 0 &\n')
	file.write('x3 >= 0 &\n')

	for i in numbers:
		if i == target:
			continue
		for o in obs[str(i)]:
			if 'y' + str(o) in used:
				continue
			file.write('y' + str(o) + ' >= 0 &\n')
			used['y' + str(o)] = ''
			y.append('y' + str(o))
	file.write('true;\n\n')


	file.write('\nmodule grid\n')
	file.write('\t\ts : [0..' + str(len(numbers)-1) + '];\n')
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
			file.write('\t\tx' + ''.join([str(ele) + '' for ele in o]) + '2 : [-1..1] init -1;\n')
			file.write('\t\tx' + ''.join([str(ele) + '' for ele in o]) + '3 : [-1..1] init -1;\n')
			used['x' + ''.join([str(ele) + '' for ele in o])] = ''

	file.write('\t\tx0 : [-1..1] init -1;\n')
	file.write('\t\tx1 : [-1..1] init -1;\n')
	file.write('\t\tx2 : [-1..1] init -1;\n')
	file.write('\t\tx3 : [-1..1] init -1;\n')

	for i in numbers:
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
				+ '1 =-1 & x' + ''.join([str(ele) + '' for ele in o]) + '2 =-1 & x' + ''.join([str(ele) + '' for ele in o]) + '3 =-1) -> (x'
				+ ''.join([str(ele) + '' for ele in o]) + '0\' =1) & (x' + ''.join([str(ele) + '' for ele in o]) +'1\'=0) & (x' + ''.join([str(ele) + '' for ele in o]) 
				+'2\'=0) & (x' + ''.join([str(ele) + '' for ele in o]) +'3\'=0);\n')
			file.write('\t\t[x'+ ''.join([str(ele) + '' for ele in o]) + '1] ' +'(!initialized & x' + ''.join([str(ele) + '' for ele in o]) + '0 =-1 & x' + ''.join([str(ele) + '' for ele in o]) 
				+ '1 =-1 & x' + ''.join([str(ele) + '' for ele in o]) + '2 =-1 & x' + ''.join([str(ele) + '' for ele in o]) + '3 =-1) -> (x'
				+ ''.join([str(ele) + '' for ele in o]) + '0\' =0) & (x' + ''.join([str(ele) + '' for ele in o]) +'1\'=1) & (x' + ''.join([str(ele) + '' for ele in o]) 
				+'2\'=0) & (x' + ''.join([str(ele) + '' for ele in o]) +'3\'=0);\n')
			file.write('\t\t[x'+ ''.join([str(ele) + '' for ele in o]) + '2] ' +'(!initialized & x' + ''.join([str(ele) + '' for ele in o]) + '0 =-1 & x' + ''.join([str(ele) + '' for ele in o]) 
				+ '1 =-1 & x' + ''.join([str(ele) + '' for ele in o]) + '2 =-1 & x' + ''.join([str(ele) + '' for ele in o]) + '3 =-1) -> (x'
				+ ''.join([str(ele) + '' for ele in o]) + '0\' =0) & (x' + ''.join([str(ele) + '' for ele in o]) +'1\'=0) & (x' + ''.join([str(ele) + '' for ele in o]) 
				+'2\'=1) & (x' + ''.join([str(ele) + '' for ele in o]) +'3\'=0);\n')
			file.write('\t\t[x'+ ''.join([str(ele) + '' for ele in o]) + '3] ' +'(!initialized & x' + ''.join([str(ele) + '' for ele in o]) + '0 =-1 & x' + ''.join([str(ele) + '' for ele in o]) 
				+ '1 =-1 & x' + ''.join([str(ele) + '' for ele in o]) + '2 =-1 & x' + ''.join([str(ele) + '' for ele in o]) + '3 =-1) -> (x'
				+ ''.join([str(ele) + '' for ele in o]) + '0\' =0) & (x' + ''.join([str(ele) + '' for ele in o]) +'1\'=0) & (x' + ''.join([str(ele) + '' for ele in o]) 
				+'2\'=0) & (x' + ''.join([str(ele) + '' for ele in o]) +'3\'=1);\n')

			used['x' + ''.join([str(ele) + '' for ele in o])] = ''


	file.write('\t\t[x' + '0] ' +'(!initialized & x0 =-1 & x1 =-1 & x2=-1 & x3=-1) -> (x0\' =1) & (x1\'=0) & (x2\'=0) & (x3\'=0);\n')
	file.write('\t\t[x' + '1] ' +'(!initialized & x0 =-1 & x1 =-1 & x2=-1 & x3=-1) -> (x0\' =0) & (x1\'=1) & (x2\'=0) & (x3\'=0);\n')
	file.write('\t\t[x' + '2] ' +'(!initialized & x0 =-1 & x1 =-1 & x2=-1 & x3=-1) -> (x0\' =0) & (x1\'=0) & (x2\'=1) & (x3\'=0);\n')
	file.write('\t\t[x' + '3] ' +'(!initialized & x0 =-1 & x1 =-1 & x2=-1 & x3=-1) -> (x0\' =0) & (x1\'=0) & (x2\'=0) & (x3\'=1);\n')


	file.write('\n\n')


	if(target != 0):
		file.write('\t\t[] !started & initialized -> 1/' + str(len(numbers)-1) + ': (started\' = true) & (s\' = 0)')
	else:
		file.write('\t\t[] !started & initialized -> 1/' + str(len(numbers)-1) + ': (started\' = true) & (s\' = 1)')

	for i in numbers:
		if i == 0:
			continue
		else:
			if(i != target):
				file.write('\n')
				file.write('\t\t\t+ 1/'+ str(len(numbers)-1) + ' : (started\'=true) & (s\'=' + str(i) +')')
	file.write(';\n')

	save = {}

	power.clear()
	for i in numbers:
		if str(i) in obs:
			state_obs = obs[str(i)]
			power.append(list(powerset(state_obs)))
			for a in range(0, 4):
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


	for i in numbers:
		if i == target:
			file.write('\t\t[move] s=' + str(target) + ' & started ' + ' -> (s\' = s); \n')
			continue
		if i - (sizey) < 0:
			if i == 0:
				file.write('\t\t[move] s=' + str(i) + ' & started -> ' + save[str(i) + str(0)] +  ': (s\'=' + str(i) + ') +')
			else:
				file.write('\t\t[move] s=' + str(i) + ' & started -> ' + save[str(i) + str(0)] +  ': (s\'=' + str(i-1) + ') +')
			if i == sizey-1:
				file.write(save[str(i) + str(1)] + ': (s\'= ' + str(i) + ') + ')
			else:
				file.write(save[str(i) + str(1)] + ': (s\'= ' + str(i + 1) + ') + ')
			
			file.write(save[str(i) + str(2)]  + ': (s\'= ' + str(i) + ') + ')

			file.write(save[str(i) + str(3)]  + ': (s\'= ' + str(sizey + i//2) + ');\n')
		else:
			file.write('\t\t[move] s=' + str(i) + ' & started -> ' + save[str(i) + str(0)] +  ': (s\'=' + str(i) + ') +')
			file.write(save[str(i) + str(1)]  + ': (s\'= ' + str(i) + ') + ')

			if i - (sizey // 2 + 1) <= sizey - 1:
				file.write(save[str(i) + str(2)]  + ': (s\'= ' + str((i - sizey) * 2) + ') + ')
			else:
				file.write(save[str(i) + str(2)]  + ': (s\'= ' + str(i - (sizey//2 + 1)) + ') + ')
			if i + sizey//2 + 1 <= numbers[-1]:
				file.write(save[str(i) + str(3)]  + ': (s\'= ' + str(i + sizey//2 + 1) + ');\n')
			else:
				file.write(save[str(i) + str(3)]  + ': (s\'= ' + str(i) + ');\n')


	

	file.write('endmodule\n\n')

	file.write('rewards\n')
	file.write('\t\t[move] !target : 1;\n')
	file.write('endrewards')







sizex = int(sys.argv[1])
sizey = int(sys.argv[2])
target = int(sys.argv[3])
budget = int(sys.argv[4])
pre = str(sys.argv[5])

create_maze(budget, target, sizex, sizey, pre)