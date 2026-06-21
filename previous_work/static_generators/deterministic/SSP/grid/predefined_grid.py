import sys

def predefined(size):
	file = open('predefined'+ 'txt', 'w')
	file.write('\'')
	for i in range(0,size):
		if i == (size-1):
			continue
		if i == size-2:
			file.write(' ' + str(i) + ' ' + str(i) + '\'')
		else:
			file.write(' ' + str(i) + ' ' + str(i) + ' |')


size = int(sys.argv[1])

predefined(size)
