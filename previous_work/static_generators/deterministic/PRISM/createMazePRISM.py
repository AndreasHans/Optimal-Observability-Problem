#!/usr/bin/python3
import more_itertools as mit
import sys
import os
import itertools
import math
from six.moves import input
from itertools import chain, combinations




def create_maze(budget, target, sizex, sizey):

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

	file = open('maze_' + str(size) + '_prism.sm', 'w')
	file.write('mdp\n\n')

	file.write('formula target = s = ' + str(target) + ';\n\n')

	file.write('formula initialised = \n')

	for b in range (0, budget):
		for a in range (0,4):
			file.write('x' + str(b) + str(a) + ' >= 0 & \n')

	for i in numbers:
		if i == target:
				continue
		for b in range (0, budget):
			file.write('y' + str(i) + str(b) + ' >= 0 & \n')

	file.write('true;\n\n')

	file.write('module grid\n\t\t')
	file.write('s : [0..' + str(len(numbers)-1) + '];\n\t\t')
	file.write('started : bool;\n\t\t')

	for i in numbers:
		if i == target:
				continue
		for b in range (0, budget):
			file.write('y' + str(i) + str(b) + ' : [-1..1] init -1;\n\t\t')


	for b in range (0, budget):
		for a in range (0,4):
			file.write('x' + str(b) + str(a) + ' : [-1..1] init -1;\n\t\t')

	file.write('\n\t\t// CHOICE OF OBSERVATIONS\n\t\t')

	for i in numbers:
		if i == target:
				continue
		for b in range(0, budget):
			file.write('[y' + str(i) + str(b) + '] (!initialised & ')
			for j in range(0, budget):
				if j < budget-1:
					file.write('y' + str(i) + str(j) + '=-1 &')
				else:
					file.write('y' + str(i) + str(j) + '=-1) ->')
			for j in range(0, budget):
				if j == budget-1:
					if j == b:
						file.write('(y' + str(i) + str(j) + '\'=1);\n\t\t')
					else:
						file.write('(y' + str(i) + str(j) + '\'=0);\n\t\t')
				else:
					if j == b:
						file.write('(y' + str(i) + str(j) + '\'=1) & ')
					else:
						file.write('(y' + str(i) + str(j) + '\'=0) & ')

	file.write('\n\t\t// CHOICE OF STRATEGY\n\t\t')
	for b in range (0, budget):
		for a in range (0,4):
			file.write('[x' + str(b) + str(a) + '] (!initialised & ')
			for j in range(0, 4):
				if j < 3:
					file.write('x' + str(b) + str(j) + '=-1 &')
				else:
					file.write('x' + str(b) + str(j) + '=-1) ->')
			for j in range(0, 4):
				if j == 3:
					if j == a:
						file.write('(x' + str(b) + str(j) + '\'=1);\n\t\t')
					else:
						file.write('(x' + str(b) + str(j) + '\'=0);\n\t\t')
				else:
					if j == a:
						file.write('(x' + str(b) + str(j) + '\'=1) & ')
					else:
						file.write('(x' + str(b) + str(j) + '\'=0) &')

	if(target != 0):
		file.write('\n\t\t[] !started & initialised -> 1/' + str(len(numbers)-1) + ': (started\' = true) & (s\' = 0)')
	else:
		file.write('\n\t\t[] !started & initialised -> 1/' + str(len(numbers)-1) + ': (started\' = true) & (s\' = 1)')

	for i in numbers:
		if i == 0:
			continue
		else:
			if(i != target):
				file.write('\n')
				file.write('\t\t\t+ 1/'+ str(len(numbers)-1) + ' : (started\'=true) & (s\'=' + str(i) +')')
	file.write(';\n')

	save = []


	for i in numbers:
		temp = []
		for a in range(0, 4):
			constraint = ''
			for j in range(0, budget):
				constraint = constraint + 'y' + str(i) + str(j) + '*x' + str(j) + str(a)
				if j < budget - 1:
					constraint = constraint + '+'
			temp.append(constraint)
		save.append(temp)

	file.write('\n\n')

	for i in numbers:
		if i == target:
			file.write('\t\t[move] s=' + str(target) + ' & started ' + ' -> (s\' = s); \n')
			continue
		if i - (sizey) < 0:
			if i == 0:
				file.write('\t\t[move] s=' + str(i) + ' & started -> ' + save[i][0] +  ': (s\'=' + str(i) + ') +')
			else:
				file.write('\t\t[move] s=' + str(i) + ' & started -> ' + save[i][0] +  ': (s\'=' + str(i-1) + ') +')
			if i == sizey-1:
				file.write(save[i][1] + ': (s\'= ' + str(i) + ') + ')
			else:
				file.write(save[i][1] + ': (s\'= ' + str(i + 1) + ') + ')
			
			file.write(save[i][2] + ': (s\'= ' + str(i) + ') + ')

			file.write(save[i][3] + ': (s\'= ' + str(sizey + i//2) + ');\n')
		else:
			file.write('\t\t[move] s=' + str(i) + ' & started -> ' + save[i][0] +  ': (s\'=' + str(i) + ') +')
			file.write(save[i][1] + ': (s\'= ' + str(i) + ') + ')

			if i - (sizey // 2 + 1) <= sizey - 1:
				file.write(save[i][2] + ': (s\'= ' + str((i - sizey) * 2) + ') + ')
			else:
				file.write(save[i][2] + ': (s\'= ' + str(i - (sizey//2 + 1)) + ') + ')
			if i + sizey//2 + 1 <= numbers[-1]:
				file.write(save[i][3] + ': (s\'= ' + str(i + sizey//2 + 1) + ');\n')
			else:
				file.write(save[i][3] + ': (s\'= ' + str(i) + ');\n')



	file.write('endmodule\n\n')

	file.write('rewards\n')
	file.write('\t\t[move] !target : 1;\n')
	file.write('endrewards')


sizex = int(sys.argv[1])
sizey = int(sys.argv[2])
target = int(sys.argv[3])
budget = int(sys.argv[4])

create_maze(budget, target, sizex, sizey)
