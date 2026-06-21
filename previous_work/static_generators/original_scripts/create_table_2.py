#!/usr/bin/python3
import os
import time
import csv

timeout = 900

# path_to_prism = '/bin/'


with open('table_2.csv', mode='w') as table_file:
	table_writer = csv.writer(table_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

	table_writer.writerow(['PDOOP - Deterministic Strategies'])

	table_writer.writerow(['Model', 'Threshold', 'Budget', 'Time (s)', 'Reward'])

	os.system('python3 createLinePOP.py 9 4 2 \'<= 5\' 1')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 line_9_det_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()
		if eval(rew) == eval('5/2'):
			rew = '5/2'

	table_writer.writerow(['L(9)', '<= 5', '2', str(total), str(rew)])


	os.system('python3 createLinePOP.py 9 4 2 \'<= Q(5,2)\' 1')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 line_9_det_z3.py')
	end = time.time()
	total = end - start


	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()
		if eval(rew) == eval('5/2'):
			rew = '5/2'

	# os.system('python3 createLinePRISM.py 9 4 2')
	#
	# start = time.time()
	# os.system('timeout ' + str(timeout) + 's ' + path_to_prism + './prism -pf \'Rmin=? [F \'target\']\' line_9_prism.sm -exact > results.txt')
	# end = time.time()
	# total_p = end - start
	#
	# if total_p > timeout:
	# 	total_p = 't.o.'
	#
	# if total_p == 't.o.':
	# 	rew_p = 'N/A'
	# else:
	# 	file = open('results.txt', 'r')
	# 	lines = file.readlines()
	# 	for line in lines:
	# 		if (len(line.split()) > 0):
	# 			if line.split()[0] == 'Result:':
	# 				rew_p = line.split()[1]
	# 	file.close()

	table_writer.writerow(['L(9)', '<= 5/2', '2', str(total), str(rew)]) # str(total_p), str(rew_p)])

	os.system('python3 createLinePOP.py 9 4 2 \'< Q(5,2)\' 1')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 line_9_det_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()


	table_writer.writerow(['L(9)', '< 5/2', '2', str(total), str(rew)])


	os.system('python3 createLinePOP.py 377 188 2 \'<= 189\' 1')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 line_377_det_z3.py')
	end = time.time()
	total = end - start


	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()
		if eval(rew) == eval('189/2'):
			rew = '189/2'

	table_writer.writerow(['L(377)', '<= 189', '2', str(total), str(rew)])


	os.system('python3 createLinePOP.py 377 188 2 \'<= Q(189,2)\' 1')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 line_377_det_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()
		if eval(rew) == eval('189/2'):
			rew = '189/2'

	table_writer.writerow(['L(377)', '<= 189/2', '2', str(total), str(rew)])


	os.system('python3 createLinePOP.py 377 188 2 \'< Q(189,2)\' 1')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 line_377_det_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()

	table_writer.writerow(['L(377)', '< 189/2', '2', str(total), str(rew)])


	os.system('python3 createGridPOP.py 24 575 2 \'<= Q(26496,575)\' 1')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 grid_24x24_det_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()
		if eval(rew) == eval('13248/575'):
			rew = '13248/575'


	table_writer.writerow(['G(24)', '<= 26496/575', '2', str(total), str(rew)])

	os.system('python3 createGridPOP.py 24 575 2 \'<= Q(13248,575)\' 1')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 grid_24x24_det_z3.py')
	end = time.time()
	total = end - start


	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()
		if eval(rew) == eval('13248/575'):
			rew = '13248/575'

	table_writer.writerow(['G(24)', '<= 13248/575', '2', str(total), str(rew)])


	os.system('python3 createGridPOP.py 24 575 2 \'< Q(13248,575)\' 1')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 grid_24x24_det_z3.py')
	end = time.time()
	total = end - start


	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()


	table_writer.writerow(['G(24)', '< 13248/575', '2', str(total), str(rew)])



	os.system('python3 createMazePOP.py 20 39 94 4 \'<= Q(6232,95)\' 1')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 maze_20x39_det_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()
		if eval(rew) == eval('3116/95'):
			rew = '3116/95'

	table_writer.writerow(['M(39)', '<= 6232/95', '4', str(total), str(rew)])

	os.system('python3 createMazePOP.py 20 39 94 4 \'<= Q(3116,95)\' 1')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 maze_20x39_det_z3.py')
	end = time.time()
	total = end - start


	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()
		if eval(rew) == eval('3116/95'):
			rew = '3116/95'

	table_writer.writerow(['M(39)', '<= 3116/95', '4', str(total), str(rew)])


	os.system('python3 createMazePOP.py 20 39 94 4 \'< Q(3116,95)\' 1')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 maze_20x39_det_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()


	table_writer.writerow(['M(39)', '< 3116/95', '4', str(total), str(rew)])



	table_writer.writerow(['SSP - Deterministic strategies'])

	table_writer.writerow(['Model', 'Threshold', 'Budget', 'Time (s)', 'Reward'])

	os.system('python3 predefined_line.py 7')


	os.system('python3 createLineSSP.py 7 3 3 \'<= 4\' 1 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_line_7_det_z3.py')
	end = time.time()
	total = end - start


	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()
		if eval(rew) == eval('2'):
			rew = '2'

	table_writer.writerow(['L(7)', '<= 4', '3', str(total), str(rew)])


	os.system('python3 predefined_line.py 7')


	os.system('python3 createLineSSP.py 7 3 3 \'<= 2\' 1 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_line_7_det_z3.py')
	end = time.time()
	total = end - start


	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()
		if eval(rew) == eval('2'):
			rew = '2'


	os.system('python3 predefined_line.py 7')

	# os.system('python3 createLineSSPPRISM.py 7 3 3 predefined.txt')
	#
	# start = time.time()
	# os.system('timeout ' + str(timeout) + 's ' + path_to_prism + './prism -pf \'Rmin=? [F \'target\']\' line_PRE_7_prism.sm -exact > results.txt')
	# end = time.time()
	# total_p = end - start
	#
	# if total_p > timeout:
	# 	total_p = 't.o.'
	#
	# if total_p == 't.o.':
	# 	rew_p = 'N/A'
	# else:
	# 	file = open('results.txt', 'r')
	# 	lines = file.readlines()
	# 	for line in lines:
	# 		if (len(line.split()) > 0):
	# 			if line.split()[0] == 'Result:':
	# 				rew_p = line.split()[1]
	# 	file.close()

	table_writer.writerow(['L(7)', '<= 2', '3', str(total), str(rew)]) # str(total_p), str(rew_p)])

	os.system('python3 createLineSSP.py 7 3 3 \'< 2\' 1 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_line_7_det_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()


	table_writer.writerow(['L(7)', '< 2', '3', str(total), str(rew)])


	os.system('python3 predefined_line.py 193')


	os.system('python3 createLineSSP.py 193 96 96 \'<= 97\' 1 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_line_193_det_z3.py')
	end = time.time()
	total = end - start


	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()
		if eval(rew) == eval('97/2'):
			rew = '97/2'

	table_writer.writerow(['L(193)', '<= 97', '96', str(total), str(rew)])

	os.system('python3 predefined_line.py 193')


	os.system('python3 createLineSSP.py 193 96 96 \'<= Q(97,2)\' 1 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_line_193_det_z3.py')
	end = time.time()
	total = end - start


	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()
		if eval(rew) == eval('97/2'):
			rew = '97/2'

	table_writer.writerow(['L(193)', '<= 97/2', '96', str(total), str(rew)])

	os.system('python3 predefined_line.py 193')


	os.system('python3 createLineSSP.py 193 96 96 \'< Q(97,2)\' 1 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_line_193_det_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()


	table_writer.writerow(['L(193)', '< 97/2', '96', str(total), str(rew)])


	os.system('python3 predefined_grid.py 225')


	os.system('python3 createGridSSP.py 15 224 14 \'<= Q(3150,112)\' 1 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_grid_15x15_det_z3.py')
	end = time.time()
	total = end - start


	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()
		if eval(rew) == eval('3150/224'):
			rew = '3150/224'

	table_writer.writerow(['G(15)', '<= 3150/112', '14', str(total), str(rew)])


	os.system('python3 predefined_grid.py 225')


	os.system('python3 createGridSSP.py 15 224 14 \'<= Q(3150,224)\' 1 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_grid_15x15_det_z3.py')
	end = time.time()
	total = end - start


	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()
		if eval(rew) == eval('3150/224'):
			rew = '3150/224'

	table_writer.writerow(['G(15)', '<= 3150/224', '14', str(total), str(rew)])


	os.system('python3 predefined_grid.py 225')


	os.system('python3 createGridSSP.py 15 224 14 \'< Q(3150,224)\' 1 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_grid_15x15_det_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()


	table_writer.writerow(['G(15)', '< 3150/224', '14', str(total), str(rew)])



	os.system('python3 predefined_maze.py 25 49')


	os.system('python3 createMazeSSP.py 25 49 119 72 \'<= Q(9912,120)\' 1 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_maze_25x49_det_z3.py')
	end = time.time()
	total = end - start


	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()
		if eval(rew) == eval('4956/120'):
			rew = '4956/120'

	table_writer.writerow(['M(49)', '<= 9912/120', '72', str(total), str(rew)])



	os.system('python3 predefined_maze.py 25 49')


	os.system('python3 createMazeSSP.py 25 49 119 72 \'<= Q(4956,120)\' 1 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_maze_25x49_det_z3.py')
	end = time.time()
	total = end - start


	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()
		if eval(rew) == eval('4956/120'):
			rew = '4956/120'

	table_writer.writerow(['M(49)', '<= 4956/120', '72', str(total), str(rew)])


	os.system('python3 predefined_maze.py 25 49')


	os.system('python3 createMazeSSP.py 25 49 119 72 \'< Q(4956,120)\' 1 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_maze_25x49_det_z3.py')
	end = time.time()
	total = end - start


	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		rew = file.readlines()[0]
		file.close()

	table_writer.writerow(['M(49)', '< 4956/120', '72', str(total), str(rew)])
