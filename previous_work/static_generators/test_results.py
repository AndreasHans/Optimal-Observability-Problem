#!/usr/bin/python3
import sys

################################################
# This code is checking the results            #
# where the given threshold is the optimal one #
# or the strategy is deterministic             #
################################################

def check_line(size):


	# For the line we have 2 solutions:

	# -> all the states on the left of the target are assigned observation 1
	#    and all the states on the right of the target are assigned observation 2
	#    depicted in correct_solution_1

	# -> all the states on the left of the target are assigned observation 2
	#    and all the states on the right of the target are assigned observation 1
    #    depicted in correct_solution_2

	correct_solution_1 = {}

	correct_solution_2 = {}

	found_solution = {}

	for i in range(0, size):

		if i == (size - 1)/2:
			continue

		if i < (size - 1)/2:
			correct_solution_1['ys' + str(i) + '1'] = '1'
			correct_solution_1['ys' + str(i) + '2'] = '0'
			correct_solution_2['ys' + str(i) + '1'] = '0'
			correct_solution_2['ys' + str(i) + '2'] = '1'
		else:
			correct_solution_1['ys' + str(i) + '1'] = '0'
			correct_solution_1['ys' + str(i) + '2'] = '1'
			correct_solution_2['ys' + str(i) + '1'] = '1'
			correct_solution_2['ys' + str(i) + '2'] = '0'


	# Read the result produced by Z3

	file = open('../results.txt', 'r')
	lines = file.readlines()

	# Save the values in found solution

	for line in lines:
		if list(line.split()[0])[0] == 'y':
			found_solution[line.split()[0]] = line.split()[2].split(',')[0].split(']')[0]
		if list(line.split()[0])[1] == 'y':
			found_solution[line.split()[0].split('[')[1]] = line.split()[2].split(',')[0].split(']')[0]

	# Check if found solution matches one of the correct solutions above

	if found_solution == correct_solution_1 or found_solution == correct_solution_2:
		print('The solution found matches the hypothesis')
	else:
		print('Wrong solution')

def check_grid(size):


	# For the grid we have 4 solutions:
	# We symbolise the position in the grid with (i, j), where i indicates the row
	# and j the column

	# -> all the states with the same i of the target are assigned observation 1
	#    and all other states are assigned observation 2
	#    depicted in correct_solution_1

	# -> all the states with the same i of the target are assigned observation 2
	#    and all other states are assigned observation 1
	#    depicted in correct_solution_2

	# -> all the states with the same j of the target are assigned observation 2
	#    and all other states are assigned observation 1
    #    depicted in correct_solution_3

    # -> all the states with the same j of the target are assigned observation 1
	#    and all other states are assigned observation 2
    #    depicted in correct_solution_4

	correct_solution_1 = {}

	correct_solution_2 = {}

	correct_solution_3 = {}

	correct_solution_4 = {}

	found_solution = {}

	for i in range(0, size):
		for j in range(0, size):

			if i == j and i == size-1:
				continue

			if i < size-1 and j < size-1:
				correct_solution_1['ys' + str(i* size + j) + '1'] = '0'
				correct_solution_1['ys' + str(i* size + j) + '2'] = '1'
				correct_solution_2['ys' + str(i* size + j) + '1'] = '1'
				correct_solution_2['ys' + str(i* size + j) + '2'] = '0'
				correct_solution_3['ys' + str(i* size + j) + '1'] = '1'
				correct_solution_3['ys' + str(i* size + j) + '2'] = '0'
				correct_solution_4['ys' + str(i* size + j) + '1'] = '0'
				correct_solution_4['ys' + str(i* size + j) + '2'] = '1'
			elif i == size - 1:
				print('mpika')
				correct_solution_1['ys' + str(i* size + j) + '1'] = '1'
				correct_solution_1['ys' + str(i* size + j) + '2'] = '0'
				correct_solution_2['ys' + str(i* size + j) + '1'] = '0'
				correct_solution_2['ys' + str(i* size + j) + '2'] = '1'
				correct_solution_3['ys' + str(i* size + j) + '1'] = '1'
				correct_solution_3['ys' + str(i* size + j) + '2'] = '0'
				correct_solution_4['ys' + str(i* size + j) + '1'] = '0'
				correct_solution_4['ys' + str(i* size + j) + '2'] = '1'
			elif j == size - 1:
				correct_solution_1['ys' + str(i* size + j) + '1'] = '0'
				correct_solution_1['ys' + str(i* size + j) + '2'] = '1'
				correct_solution_2['ys' + str(i* size + j) + '1'] = '1'
				correct_solution_2['ys' + str(i* size + j) + '2'] = '0'
				correct_solution_3['ys' + str(i* size + j) + '1'] = '0'
				correct_solution_3['ys' + str(i* size + j) + '2'] = '1'
				correct_solution_4['ys' + str(i* size + j) + '1'] = '1'
				correct_solution_4['ys' + str(i* size + j) + '2'] = '0'


	# Read the result produced by Z3

	file = open('../results.txt', 'r')
	lines = file.readlines()

	# Save the values in found solution

	for line in lines:
		if list(line.split()[0])[0] == 'y':
			found_solution[line.split()[0]] = line.split()[2].split(',')[0].split(']')[0]
		if list(line.split()[0])[1] == 'y':
			found_solution[line.split()[0].split('[')[1]] = line.split()[2].split(',')[0].split(']')[0]

	# Check if found solution matches one of the correct solutions above

	if found_solution == correct_solution_1 or found_solution == correct_solution_2 or found_solution == correct_solution_3 or found_solution == correct_solution_4:
		print('The solution found matches the hypothesis')
	else:
		print('Wrong solution')

def check_maze(size):

	# For the maze we have 16 solutions:
	# We symbolise the position in the grid with (i, j), where i indicates the row
	# and j the column

	# We know that the states with the same optimal action should get the same observation.
	# We divide the states based on the optimal action

	sizex = int(3 + (size - 5)/2)

	sizey = size

	up = []
	down = []
	left = []
	right = []

	# Find the nodes, since it is not  a compete grid

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

	# Group nodes based on the optimal action

	for i in numbers:

			if i == numbers[-2]:
				continue

			if i  < (size-1)/2:
				right.append('ys' + str(i))

			elif i  > (size-1)/2 and i < size:
				left.append('ys' + str(i))

			elif i >= size and (i - size)%3 == 0:
				up.append('ys' + str(i))

			elif i >= size and (i - size)%3 == 2:
				up.append('ys' + str(i))

			elif (i > size and (i - size)%3 == 1) or i  == (size-1)/2:
				down.append('ys' + str(i))

	# Read the result produced by Z3

	file = open('../results.txt', 'r')
	lines = file.readlines()

	# Save the values in found solution

	found_solution = {}

	for line in lines:
		if list(line.split()[0])[0] == 'y':
			found_solution[line.split()[0]] = line.split()[2].split(',')[0].split(']')[0]
		if list(line.split()[0])[1] == 'y':
			found_solution[line.split()[0].split('[')[1]] = line.split()[2].split(',')[0].split(']')[0]


	# Group states based on the activated observation

	o1 = []
	o2 = []
	o3 = []
	o4 = []

	for i in numbers:

		if i == numbers[-2]:
			continue

		if found_solution['ys' + str(i) + str(1)] == str(1):
			o1.append('ys' + str(i))

		if found_solution['ys' + str(i) + str(2)] == str(1):
			o2.append('ys' + str(i))

		if found_solution['ys' + str(i) + str(3)] == str(1):
			o3.append('ys' + str(i))

		if found_solution['ys' + str(i) + str(4)] == str(1):
			o4.append('ys' + str(i))

	# Check if we get the same result as in the hypothesis

	check_equality = {}
	check_equality[str(o1)] = '1'
	check_equality[str(o2)] = '1'
	check_equality[str(o3)] = '1'
	check_equality[str(o4)] = '1'

	flag = True

	if str(up) in check_equality:
		flag = flag and True
		check_equality.pop(str(up))
	else:
		flag = False

	if str(down) in check_equality:
		flag = flag and True
		check_equality.pop(str(down))
	else:
		flag = False

	if str(left) in check_equality:
		flag = flag and True
		check_equality.pop(str(left))
	else:
		flag = False

	if str(right) in check_equality:
		flag = flag and True
		check_equality.pop(str(right))
	else:
		flag = False

	if flag:
		print('The solution found matches the hypothesis')
	else:
		print('Wrong solution')


# Size of the model
size = int(sys.argv[1])

# Type of the model
model = sys.argv[2]

#select corresponding function
if model == 'line':
	check_line(size)
elif model == 'grid':
	check_grid(size)
elif model == 'maze':
	check_maze(size)
else:
	print('This model is not supported')
