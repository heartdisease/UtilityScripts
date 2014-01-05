#!/usr/bin/python3
import sys

if len(sys.argv) != 3:
	print("Argument is missing!")
	exit(1)

lineno=int(sys.argv[1])
filename=sys.argv[2]

with open(filename, "r") as f:
	i = 2
	
	for line in f:
		if i % lineno != 0:
			print(line.strip())
		i += 1
