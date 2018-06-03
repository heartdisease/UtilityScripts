######################
### Python 3 only! ###
######################

class CsvReader:
	# @param separator character that separates columns
	# @param delimiter for text (e.g. " or ')
	def __init__(self, separator, delimiter):
		self._separator = separator
		self._delimiter = delimiter
	#end def
	
	def parse(self, csvfile):
		rows = []
		
		with open(csvfile, 'r') as f:
			text = f.read()
			row = []
			col = ''
			quoted = False
			escaped = False
			
			for c in text:
				if escaped: # add any character to column text if escaped
					col += c
					escaped = False
				elif c == '\\': # next character is escaped
					escaped = True
				elif c == self._delimiter: # found text delimiter, quoted text starts or ends here
					quoted = not quoted # enable or disable quote mode
				elif c == self._separator: # found column separator
					if quoted: # within quotes column separators belong to column text
						col += c
					else: # found end of column
						row.append(col)
						col = ''
					#end if
				elif c == '\n' and not quoted: # detected end of row
					row.append(col)
					rows.append(row)
					row = []
					col = ''
				else: # normal character
					col += c
				#end if
			#end for
		#end with
		
		return rows
	#end def
#end class
