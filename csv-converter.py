#!/usr/bin/python3
import sys

if len(sys.argv) != 2:
	print("Argument is missing!")
	exit(1)

filename=sys.argv[1]

with open(filename, "r") as f:
	i = 0	
	cell0 = None
	cell1 = None
	
	for line in f:
		if i == 0:
			cell0 = line.strip()
			i = 1
		elif i == 1:
			cell1 = line.strip()
			i = 2
			print(cell0 + ';' + cell1)
		else:
			i = 0
