#!/usr/bin/python3
import os
import time
import csv

timeout = 900


with open('table_1.csv', mode='w') as table_file:
	table_writer = csv.writer(table_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

	table_writer.writerow(['POP - Randomised strategies'])

	table_writer.writerow(['Model', 'Threshold', 'Budget', 'Time (s)', 'Reward'])

	os.system('python3 createLinePOP.py 249 124 2 \'<= Q(250,2)\' 0')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 line_249_ran_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		file.seek(0)
		lines = file.readlines()
		if len(lines) > 0:
			rew = lines[0]
		else:
			rew = 'N/A'
		file.close()

	table_writer.writerow(['L(249)', '<= 250/2', '2', str(total), str(rew)])

	os.system('python3 createLinePOP.py 249 124 2 \'<= Q(125,2)\' 0')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 line_249_ran_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'

	if total == 't.o.':
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		file.seek(0)
		lines = file.readlines()
		if len(lines) > 0:
			rew = lines[0]
		else:
			rew = 'N/A'
		file.close()
		if eval(rew) == eval('125/2'):
			rew = '125/2'

	table_writer.writerow(['L(249)', '<= 125/2', '2', str(total), str(rew)])

	os.system('python3 createLinePOP.py 249 124 2 \'< Q(125,2)\' 0')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 line_249_ran_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		file.seek(0)
		lines = file.readlines()
		if len(lines) > 0:
			rew = lines[0]
		else:
			rew = 'N/A'
		file.close()

	table_writer.writerow(['L(249)', '< 125/2', '2', str(total), str(rew)])


	os.system('python3 createGridPOP.py 20 399 2 \'<= Q(15200,399)\' 0')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 grid_20x20_ran_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		file.seek(0)
		lines = file.readlines()
		if len(lines) > 0:
			rew = lines[0]
		else:
			rew = 'N/A'
		file.close()

	table_writer.writerow(['G(20)', '<= 15200/399', '2', str(total), str(rew)])

	os.system('python3 createGridPOP.py 20 399 2 \'<= Q(7600,399)\' 0')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 grid_20x20_ran_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'

	if total == 't.o.':
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		file.seek(0)
		lines = file.readlines()
		if len(lines) > 0:
			rew = lines[0]
		else:
			rew = 'N/A'
		file.close()
		if eval(rew) == eval('7600/399'):
				rew = '7600/399'

	table_writer.writerow(['G(20)', '<= 7600/399', '2', str(total), str(rew)])

	os.system('python3 createGridPOP.py 20 399 2 \'< Q(7600,399)\' 0')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 grid_20x20_ran_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		file.seek(0)
		lines = file.readlines()
		if len(lines) > 0:
			rew = lines[0]
		else:
			rew = 'N/A'
		file.close()

	table_writer.writerow(['G(20)', '< 7600/399', '2', str(total), str(rew)])


	os.system('python3 createMazePOP.py 4 7 14 4 \'<= Q(168,15)\' 0')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 maze_4x7_ran_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		file.seek(0)
		lines = file.readlines()
		if len(lines) > 0:
			rew = lines[0]
		else:
			rew = 'N/A'
		file.close()

	table_writer.writerow(['M(7)', '<= 168/15', '4', str(total), str(rew)])

	os.system('python3 createMazePOP.py 4 7 14 4 \'<= Q(84,15)\' 0')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 maze_4x7_ran_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'

	if total == 't.o.':
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		file.seek(0)
		lines = file.readlines()
		if len(lines) > 0:
			rew = lines[0]
		else:
			rew = 'N/A'
		file.close()
		if eval(rew) == eval('84/15'):
			rew = '84/15'

	table_writer.writerow(['M(7)', '<= 84/15', '4', str(total), str(rew)])

	os.system('python3 createMazePOP.py 4 7 14 4 \'< Q(84,15)\' 0')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 maze_4x7_ran_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		file.seek(0)
		lines = file.readlines()
		if len(lines) > 0:
			rew = lines[0]
		else:
			rew = 'N/A'
		file.close()

	table_writer.writerow(['M(7)', '< 84/15', '4', str(total), str(rew)])

	table_writer.writerow([' '])

	table_writer.writerow(['SSP - Randomised strategies'])

	table_writer.writerow(['Model', 'Threshold', 'Budget', 'Time (s)', 'Reward'])

	os.system('python3 predefined_line.py 61')

	os.system('python3 createLineSSP.py 61 30 30 \'<= 31\' 0 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_line_61_ran_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		file.seek(0)
		lines = file.readlines()
		if len(lines) > 0:
			rew = lines[0]
		else:
			rew = 'N/A'
		file.close()

	table_writer.writerow(['L(61)', '<= 31', '30', str(total), str(rew)])


	os.system('python3 predefined_line.py 61')

	os.system('python3 createLineSSP.py 61 30 30 \'<= Q(31,2)\' 0 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_line_61_ran_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
	if total == 't.o.':
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		file.seek(0)
		lines = file.readlines()
		if len(lines) > 0:
			rew = lines[0]
		else:
			rew = 'N/A'
		file.close()
		if eval(rew) == eval('31/2'):
			rew = '31/2'


	table_writer.writerow(['L(61)', '<= 31/2', '30', str(total), str(rew)])

	os.system('python3 predefined_line.py 61')

	os.system('python3 createLineSSP.py 61 30 30 \'< Q(31,2)\' 0 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_line_61_ran_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		file.seek(0)
		lines = file.readlines()
		if len(lines) > 0:
			rew = lines[0]
		else:
			rew = 'N/A'
		file.close()


	table_writer.writerow(['L(61)', '< 31/2', '30', str(total), str(rew)])


	os.system('python3 predefined_grid.py 36')

	os.system('python3 createGridSSP.py 6 35 5 \'<= Q(360,35)\' 0 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_grid_6x6_ran_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		file.seek(0)
		lines = file.readlines()
		if len(lines) > 0:
			rew = lines[0]
		else:
			rew = 'N/A'
		file.close()


	table_writer.writerow(['G(6)', '<= 360/35', '5', str(total), str(rew)])


	os.system('python3 predefined_grid.py 36')

	os.system('python3 createGridSSP.py 6 35 5 \'<= Q(180,35)\' 0 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_grid_6x6_ran_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
	if total == 't.o.':
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		file.seek(0)
		lines = file.readlines()
		if len(lines) > 0:
			rew = lines[0]
		else:
			rew = 'N/A'
		file.close()
		if eval(rew) == eval('180/35'):
			rew = '180/35'


	table_writer.writerow(['G(6)', '<= 180/35', '5', str(total), str(rew)])


	os.system('python3 predefined_grid.py 36')

	os.system('python3 createGridSSP.py 6 35 5 \'< Q(180,35)\' 0 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_grid_6x6_ran_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		file.seek(0)
		lines = file.readlines()
		if len(lines) > 0:
			rew = lines[0]
		else:
			rew = 'N/A'
		file.close()


	table_writer.writerow(['G(6)', '< 180/35', '5', str(total), str(rew)])

	os.system('python3 predefined_maze.py 8 15')

	os.system('python3 createMazeSSP.py 8 15 34 21 \'<= Q(868,35)\' 0 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_maze_8x15_ran_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		file.seek(0)
		lines = file.readlines()
		if len(lines) > 0:
			rew = lines[0]
		else:
			rew = 'N/A'
		file.close()


	table_writer.writerow(['M(15)', '<= 868/35', '21', str(total), str(rew)])


	os.system('python3 predefined_maze.py 8 15')

	os.system('python3 createMazeSSP.py 8 15 34 21 \'<= Q(434,35)\' 0 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_maze_8x15_ran_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'

	if total == 't.o.':
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		file.seek(0)
		lines = file.readlines()
		if len(lines) > 0:
			rew = lines[0]
		else:
			rew = 'N/A'
		file.close()
		if eval(rew) == eval('434/35'):
			rew = '434/35'


	table_writer.writerow(['M(15)', '<= 434/35', '21', str(total), str(rew)])


	os.system('python3 predefined_maze.py 8 15')

	os.system('python3 createMazeSSP.py 8 15 34 21 \'< Q(434,35)\' 0 predefined.txt')

	start = time.time()
	os.system('timeout ' + str(timeout) + 's python3 ssp_maze_8x15_ran_z3.py')
	end = time.time()
	total = end - start

	if total > timeout:
		total = 't.o.'
		rew = 'N/A'
	else:
		file = open('reward.txt', 'r')
		file.seek(0)
		lines = file.readlines()
		if len(lines) > 0:
			rew = lines[0]
		else:
			rew = 'N/A'
		file.close()


	table_writer.writerow(['M(15)', '< 434/35', '21', str(total), str(rew)])
