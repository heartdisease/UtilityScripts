#!/usr/bin/python3
import sys

SEPARATOR = ";"

def first_col(line):
	return line.strip().split(SEPARATOR, 1)[0].strip("\"'")
#end def

def adjust_row(line):
	return line.strip().replace("(to)", "to") + SEPARATOR + "unchecked"
#end def

def get_words(src):
	words = []

	with open(src, "r") as f:	
		for line in f:
			word = first_col(line)
			
			if len(word) > 0:
				words.append(word)
			#end if
		#end for
	#end with
	
	return words
#end def

def print_diff(src, ignore):
	count = 0
	exists = ignore[:] # array with words already parsed

	with open(src, "r") as f:	
		for line in f:
			word = first_col(line)
			
			if word not in exists:
				exists.append(word) # avoid doubles
				print(adjust_row(line))
				count += 1
			#end if
		#end for
	#end with
	
	print(count, "new rows")
#end def

def main():
	if len(sys.argv) != 3:
		print("Argument is missing!")
		exit(1)
	#end if

	oldfile=sys.argv[1]
	newfile=sys.argv[2]

	existing_words = get_words(oldfile)
	print_diff(newfile, existing_words)
#end def

main()
