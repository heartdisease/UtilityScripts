#!/usr/bin/python3
from csvreader import CsvReader
import re

reader = CsvReader(',', '"')
original = reader.parse('latin.gerald.original.csv')
modified = reader.parse('latin.gerald.modified.csv')

if len(original) != len(modified):
	print('Both documents don\'t have equal number of rows')
	exit(1)
else:
	for i in range(0, len(original)):
		normalized_original = re.sub(r'[ \n\t\.,;:\(\)]', '', original[i][1].lower())
		normalized_modified = re.sub(r'[ \n\t\.,;:\(\)]', '', (modified[i][1] + modified[i][2]).lower())
	
		if original[i][0] != modified[i][0]:
			print('row', (i + 1), ': latin column does not match (' + original[i][0] + ' <-> ' + modified[i][0] + ')')
		#end if 
		if normalized_original != normalized_modified:
			print('row', (i + 1), ': translation column was altered (' + original[i][1].replace('\n', '\\n') + ' <-> ' + modified[i][1].replace('\n', '\\n') + ' [' + modified[i][2].replace('\n', '\\n') + '])')
		#end if 
	#end for
	
	print('Checked documents')
	exit(0)
#end if

