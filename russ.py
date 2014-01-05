#!/usr/bin/python3
import re
import sys

def is_cyrillic(char):	
	return 0x0400 <= ord(char) <= 0x04FF # http://en.wikipedia.org/wiki/List_of_Unicode_characters#Cyrillic
#end def

def is_neutral_character(char):
	return char == ' ' or char == '\t' or char == '!' or char == '?' or char == '/' or char == '.' or char == '-'
#end def

def random2csv(filename):
	with open(filename, 'r') as f:
		text = f.read().replace('\n', '')
		russian = None
		pronounciation = None
		translation = None
	
		for char in text:		
			if russian == None: # found first russian word in document
				if is_neutral_character(char) or is_cyrillic(char):
					russian = char
			elif pronounciation == None:
				if is_neutral_character(char) or is_cyrillic(char):
					russian += char
				elif char == '[':
					pronounciation = ''
			elif translation == None:
				if char == ']':
					translation = ''
				else:
					pronounciation += char
			else:
				if is_cyrillic(char): # found next row
					print(russian.strip() + ';' + pronounciation.strip() + ';' + re.sub(r'[ ]+[\w ]+\:$', '', translation.strip()))
				
					russian = char
					pronounciation = None
					translation = None
				else:
					translation += char
		#end for
	#end with
#end def

if len(sys.argv) != 2:
	print("Argument is missing!")
	exit(1)
#end if

inputfile = sys.argv[1]

random2csv(inputfile)
