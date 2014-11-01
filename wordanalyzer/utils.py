#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from multiprocessing import Process, Queue
import codecs

class CsvRow(object):

	def __init__(self, values, format_str):
		self._values = values
		self._format = format_str.split('|')
		
		for n in range(len(self._format) - len(self._values)):
			self._values.append('') # fill up non-existing columns
		#end for
	#end def
	
	@property
	def original_word(self):
		return self._values[self._format.index('O')]
	#end def
	
	@original_word.setter
	def original_word(self, value):
		self._values[self._format.index('O')] = value
	#end def
	
	@property
	def ipa(self):
		return self._values[self._format.index('P')]
	#end def
	
	@ipa.setter
	def ipa(self, value):
		self._values[self._format.index('P')] = value
	#end def
	
	@property
	def synonyms(self):
		return self._values[self._format.index('S')]
	#end def
	
	@synonyms.setter
	def synonyms(self, value):
		self._values[self._format.index('S')] = value
	#end def
	
	@property
	def antonyms(self):
		return self._values[self._format.index('A')]
	#end def
	
	@antonyms.setter
	def antonyms(self, value):
		self._values[self._format.index('A')] = value
	#end def
	
	@property
	def example_sentence(self):
		return self._values[self._format.index('E')]
	#end def
	
	@example_sentence.setter
	def example_sentence(self, value):
		self._values[self._format.index('E')] = value
	#end def
	
	@property
	def definition(self):
		return self._values[self._format.index('D')]
	#end def
	
	@definition.setter
	def definition(self, value):
		self._values[self._format.index('D')] = value
	#end def
	
	@property
	def translation(self):
		return self._values[self._format.index('M')]
	#end def
	
	@translation.setter
	def translation(self, value):
		self._values[self._format.index('M')] = value
	#end def
	
	@property
	def word_type(self):
		return self._values[self._format.index('W')]
	#end def
	
	@word_type.setter
	def word_type(self, value):
		self._values[self._format.index('W')] = value
	#end def
	
	@property
	def level(self):
		return self._values[self._format.index('L')]
	#end def
	
	@level.setter
	def level(self, value):
		self._values[self._format.index('L')] = value
	#end def
	
	@property
	def tags(self):
		return self._values[self._format.index('T')]
	#end def
	
	@tags.setter
	def tags(self, value):
		self._values[self._format.index('T')] = value
		print('Debug: set value %s at index %d' % (value, self._format.index('T')))
	#end def
	
	### SPECIAL PROPERTIES ###
	
	@property
	def normalized_word(self):
		return self._values[self._format.index('N')]
	#end def
	
	@normalized_word.setter
	def normalized_word(self, normalized):
		if 'N' in self._format:
			self._values[self._format.index('N')] = normalized
		else:
			index = self._format.index('O') + 1
			
			if len(self._values) > index:
				self._format.insert(index, 'N') # N = normalized
				self._values.insert(index, normalized)
			#end if
		#end if
	#end def
	
	@property
	def new_translation(self):
		return self._values[self._format.index('N')]
	#end def
	
	@new_translation.setter
	def new_translation(self, translation):
		if 'NM' in self._format:
			self._values[self._format.index('NM')] = translation
		else:
			index = self._format.index('M') + 1
		
			if len(self._values) > index:
				self._format.insert(index, 'NM') # NM = new meaning/translation
				self._values.insert(index, translation)
			#end if
		#end if
	#end def
	
	@property
	def new_wordtype(self):
		return self._values[self._format.index('NW')]
	#end def
	
	@new_wordtype.setter
	def new_wordtype(self, wordtype):
		if 'NW' in self._format:
			self._values[self._format.index('NW')] = normalized
		else:
			index = self._format.index('W') + 1
		
			if len(self._values) > index:
				self._format.insert(index, 'NW') # NW = new word type
				self._values.insert(index, wordtype)
			#end if
		#end if
	#end def
	
	def extend(self, array):
		self._values.extend(array)
	#end def
	
	def __len__(self):
		return len(self._values)
	#end def
	
	def __getitem__(self, index):
		return self._values[index]
	#end def
#end def

class CsvReader(object):

	# @param separator character that separates columns
	# @param delimiter for text (e.g. " or ')
	def __init__(self, separator, delimiter, column_format, encoding = 'utf-8'):
		self._separator = separator
		self._delimiter = delimiter
		self._column_format = column_format
		self._encoding = encoding
	#end def
	
	# Parses CSV table according to the column format rules.
	# Whitespcases at the beginning or end of columns are automatically removed.
	def parse(self, csvfile):
		rows = []
		
		with codecs.open(csvfile, 'r', self._encoding) as f:
			text = f.read()
			row = []
			col = ''
			quoted = False
			escaped = False
			
			for c in text: # TODO create row objects with column names!
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
						row.append(col.strip())
						col = ''
					#end if
				elif c == '\n' and not quoted: # detected end of row
					row.append(col.strip())
					rows.append(CsvRow(row, self._column_format))
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

class Processable(object):

	def __init__(self, target, word, row):
		self.__queue   = Queue()
		self.__process = Process(target=lambda q, word: q.put(target(word)), args=(self.__queue, word,))
		self.row       = row
	#end def
	
	def result(self):
		self.__process.join()
		return self.__queue.get()
	#end def
	
	def start(self):
		self.__process.start()
	#end def
#end class

class ThreadPool(object):

	POOL_SIZE = 8

	def __init__(self, process):
		self.pool = []
		self.process = process
	#end def
	
	def add(self, processable):
		self.pool.append(processable)
		
		if len(self.pool) == ThreadPool.POOL_SIZE: 
			self.__process_thread_pool()
		#end if
	#end def
	
	def finish(self):
		self.__process_thread_pool()
	#end def
	
	def __process_thread_pool(self):
		for thread in self.pool:
			self.process(thread.result(), thread.row) # thread.result() is a blocking call
		#end for
		del self.pool[:] # clear thread pool
	#end def
#end class

