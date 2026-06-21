import sys

def predefined(sizex, sizey):
	file = open('predefined'+ '.txt', 'w')
	file.write('\'')
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
					
	for i in range(0,len(numbers)):
		if i == len(numbers)-1:
			file.write(' ' + str(numbers[i]) + ' ' + str(numbers[i]) + '\'')
		else:
			file.write(' ' + str(numbers[i]) + ' ' + str(numbers[i]) + ' |')


sizex = int(sys.argv[1])
sizey = int(sys.argv[2])

predefined(sizex, sizey)
