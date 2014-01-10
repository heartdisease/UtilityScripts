#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from pyquery import PyQuery as pq
from lxml import etree
from multiprocessing import Process, Queue
import re
import sys
import urllib
import urllib2
import codecs

class CsvReader:
	# @param separator character that separates columns
	# @param delimiter for text (e.g. " or ')
	def __init__(self, separator, delimiter):
		self._separator = separator
		self._delimiter = delimiter
	#end def
	
	def parse(self, csvfile):
		rows = []
		
		with codecs.open(csvfile, 'r', 'utf-8') as f:
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

class Processable:
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

class ThreadPool:
	def __init__(self, process):
		self.pool1 = []
		self.pool2 = []
		self.process = process
	#end def
	
	def add(self, processable):
		if len(self.pool1) == 4: # thread pool 1 is full
			if len(self.pool2) == 4: # both thread pools are full - execute all
				self.__process_thread_pool(self.pool1)
				self.__process_thread_pool(self.pool2)
			else: # thread pool 2 is not full yet
				self.pool2.append(processable)
			#end if
		else: # thread pool 1 is not full yet
			self.pool1.append(processable)			
		#end if
	#end def
	
	def finish(self):
		self.__process_thread_pool(self.pool1)
		self.__process_thread_pool(self.pool2)
	#end def
	
	def __process_thread_pool(self, pool):
		for thread in pool:
			self.process(thread.result(), thread.row)
		#end for
		del pool[:] # clear thread pool
	#end def
#end class

class Wordanalyzer:
	CSV_SEPARATOR = ','
	TEXT_DELIMITER = '"'
	WORD_SPLIT_REGEX = ur'[ \t-\.,:;!\?\(\)"\'“”]'
	EXCLUDED_WORDS = set([
		'qué', 'cuál', 'quién', 'dónde', 'adonde', 'cómo', 'que', 'como',
		'mio', 'tuyo', 'suyo', 'nuestro', 'nuestros', 'nuestra', 'nuestras', 'mis', 'tus', 'sus',
		'los', 'las', 'les', 'ella', 'ellos' 'con', 'sin', 'desde', 'nosotros', 'vosotros', 'ellos', 'ellas',
		'este', 'esta', 'está', 'una', 'uno', 'son',	'por', 'para', 'porque', 'cómo', 'soy', 'estoy',
		'nos', 'vos', 'hay', 'del', 'esto', 'han','hemos', 'más', 'pero', 'ser', 'estar'
	])
	READER = CsvReader(CSV_SEPARATOR, TEXT_DELIMITER)
	STD_HEADERS = {
		'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
		'Accept-Language' : 'es-419,es'
	}
	POST_HEADERS = {
		'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
		'Accept-Language' : 'es-419,es',
		'Content-type' : 'application/x-www-form-urlencoded; charset=utf-8'
	}
	
	##
	# Returns a dictionary that contains the normalized version of the word, the translation and the word type (e.g. noun).
	# 
	# @param word to be looked up on SpanishDict.com
	# @return dictionary with information about the word
	##
	@staticmethod
	def get_translation(word):
		# normalize input
		slash_index = word.find('/') # in case of 'el/la' pair, remove 'el/' to avoid problems with search engine
		word = word.encode('utf-8') if slash_index == -1 else word[slash_index + 1:].encode('utf-8')
		
		url = u'http://www.spanishdict.com/translate/' + urllib.quote(word)
		normalized  = None
		translation = None
		wordtype    = None
		
		response = urllib2.urlopen(urllib2.Request(url, headers=Wordanalyzer.STD_HEADERS))
		try:
			content = unicode(response.read(), 'utf-8').replace('\n', ' ')
			p = pq(url=None, opener=lambda url: content)
	
			result_block = p('div.results-block')
			normalized   = result_block.find('h1.word').text()
			translation  = result_block.find('h2.quick_def').text()
			wordtype     = result_block.find('div.hw-block > span.quick_pos').text()
			partofspeach = result_block.find('span.part_of_speech:first-child').text()
			
			is_masculine = False
			is_feminine  = False
			
			if partofspeach != None:
				partofspeach = partofspeach.strip() # remove trailing white spaces
		
				if wordtype == None or len(wordtype) == 0:
					is_probably_noun = u'noun' in partofspeach
					is_masculine = partofspeach.startswith(u'masculine') and is_probably_noun
					is_feminine  = partofspeach.startswith(u'feminine') and is_probably_noun
				
					# fix for inconsistency of the website
					if is_masculine or is_feminine: # word is a noun
						wordtype = u'noun'
					else:
						first_word = re.match(r'\w+', partofspeach) # find first word type
			
						if first_word != None:
							wordtype = first_word.group(0)
						#end if
					#end if
				else:
					wordtype = wordtype.strip() # remove trailing white spaces
				#end if
			#end if
			
			if wordtype == u'noun':
				is_masculine = u'masculine' in partofspeach
				is_feminine  = u'feminine' in partofspeach
				
				# head_word offers more detailed description of the noun (like 'chico, -a')
				head_word = result_block.find('span.head_word').text()
				if head_word != None and len(head_word) > 0:
					normalized = head_word.strip()
				#end if
				
				if is_masculine and is_feminine:
					normalized = u'el/la ' + normalized
				elif is_masculine:
					normalized = u'el ' + normalized
				elif is_feminine:
					normalized = u'la ' + normalized
				else: # special case where gender declaration is missing
					normalized = u'?? ' + normalized
				#end if
			#end if
	
			if translation != None:
				translation = translation.replace(';', ',').replace(' , ', ', ')
			#end if
		except UnicodeDecodeError, e:
			print(u'Invalid response for "' + unicode(word, 'utf-8') + '": ' + str(e))
		#end try
	
		return { 'normalized' : normalized if normalized != None else word, 'translation' : translation, 'wordtype' : wordtype }
	#end def
	
	##
	# Returns a dictionary that contains the normalized version of the word, the translation and the word type (e.g. noun).
	# 
	# @param word to be looked up on diccionario-ingles.info
	# @return dictionary with information about the word
	##
	@staticmethod
	def get_translation_2(word):
		# normalize input
		slash_index = word.find('/') # in case of 'el/la' pair, remove 'el/' to avoid problems with search engine
		word = word.encode('utf-8') if slash_index == -1 else word[slash_index + 1:].encode('utf-8')
		
		url = u'http://www.diccionario-ingles.info/index.php' #?search=' + urllib2.quote(word)
		normalized  = None
		translation = None
		wordtype    = None
		
		response = urllib2.urlopen(urllib2.Request(url, u'search=' + str(word), Wordanalyzer.POST_HEADERS))
		try:
			content = unicode(response.read(), 'latin-1').replace('\n', ' ')
			p = pq(url=None, opener=lambda url: content)
			
			normalized  = None
			translation = None
			wordtype    = None
			
			info_rows = p('tr[id^="row_"] > td:first-child a')
			spanish_rows = p('tr[id^="row_"] > td:nth-child(2)')
			english_rows = p('tr[id^="row_"] > td:nth-child(3)')
			
			for i in range(len(spanish_rows)):
				spanish_row = pq(spanish_rows[i]).text()
				
				if normalized == None:
					if word in spanish_row:
						word_info = pq(info_rows[i]).attr('onmouseover')
						wordtype_match = re.match(r"showinfomenu\([0-9]+,'ES','es_en',this,'\w+','[0-9]+',[0-9]+,'\w+','(\w+)'", word_info)
						
						if wordtype_match != None:
							wordtype = wordtype_match.group(1)
						normalized = spanish_row
					else:
						break # no translation found
					#end if
				elif spanish_row == normalized:
					english_row = pq(english_rows[i]).text()
					
					if translation == None:
						translation = english_row
					else:
						translation += ', ' + english_row
					#end if
				else:
					break # found all translations
				#end if
			#end for
		except UnicodeDecodeError, e:
			print(u'Invalid response for "' + unicode(word, 'utf-8') + '": ' + str(e))
		#end try
	
		return { 'normalized' : normalized, 'translation' : translation, 'wordtype' : wordtype }
	#end def
	
	def __init__(self, src, ostream):
		self.src = src
		self.out = ostream
	#end def
	
	def print_csv_row(self, cols):
		first_col = True
	
		for col in cols:
			if not first_col:
				self.out.write(Wordanalyzer.CSV_SEPARATOR)
			else:
				first_col = False
			#end if
		
			self.out.write('"')
			self.out.write(col)
			self.out.write('"')
		#end for
	
		self.out.write('\n')
	#end def

	##
	# Parses text file containing standard text and generates vocabulary list from it.
	#
	# @param src path to input file
	# @param out output stream
	##
	def print_word_list(self):
		with codecs.open(self.src, 'r', 'utf-8') as f:	
			thread_pool = ThreadPool(self.__print_word_row)
			text = f.read().replace('\n', ' ').lower() # ignore case and replace newlines with spaces
			wordset = set(word for word in re.split(Wordanalyzer.WORD_SPLIT_REGEX, text) if len(word) > 2 and re.match(r'[0-9@]+', word) == None)
			words = sorted(wordset - Wordanalyzer.EXCLUDED_WORDS)
		
			self.print_csv_row(['[Original word]', '[Normalized form]', '[Translation]', '[Word type]']) # print header
			for word in words:
				p = Processable(lambda word: Wordanalyzer.get_translation(word), word, [word])
				p.start()
				
				thread_pool.add(p)
			#end for
		#end with
	#end def

	##
	# Parses CSV table already containing at least two columns with Spanish/English word pairs. The third column is optional and usually contains a 'checked' flag, which
	# declares whether a word has been already validated. The generated table will contain an extra row for a normalized version of the original Spanish word, an extra row
	# for translation (from SpanishDict.com) and an extra column for the word type (e.g. noun).
	#
	# @param src path to input CSV file
	# @param out output stream
	##
	def print_enhanced_table(self):
		thread_pool = ThreadPool(self.__print_enhanced_row)
		rows = Wordanalyzer.READER.parse(self.src)

		self.print_csv_row(['[Original word]', '[Normalized form]', '[New translation]', '[Translation]', '[Word type]', '[Checked]']) # print header
		for row in rows:
			if len(row) < 2:
				print('Skip incomplete row')
			else:
				p = Processable(lambda word: Wordanalyzer.get_translation(row[0]), row[0], row)
				p.start()
				
				thread_pool.add(p)
			#end if
		#end for
		
		thread_pool.finish()
	#end def
	
	def __print_word_row(self, result, row):
		row.append(u'unknown' if result['normalized'] == None else result['normalized'])
		row.append(u'unknown' if result['translation'] == None else result['translation'])
		row.append(u'' if result['wordtype'] == None else result['wordtype'])
		
		self.print_csv_row(row)
	#end def
	
	def __print_enhanced_row(self, result, row):
		normalized  = u'unknown' if result['normalized'] == None else result['normalized']
		translation = u'unknown' if result['translation'] == None else \
								u'{duplicate} '+result['translation'] if result['translation'] in row[1] \
								else result['translation']
		wordtype    = u'' if result['wordtype'] == None else result['wordtype']

		row.insert(1, normalized)
		row.insert(2, translation)
		row.insert(4, wordtype)

		self.print_csv_row(row)
	#end def
#end class

def main(argv):
	if len(argv) != 4:
		print('Argument is missing!')
		print('wordanalyzer [option] [inputfile] [outputfile]')
		print('\t--wordlist\tprints list of words contained in [file]')
		print('\t--check-csv\tprints enhanced version of cvs file [file]')
		
		#word = u'el/la líder'
		#print(word)
		#print(Wordanalyzer.get_translation_2(word))
		
		exit(1)
	#end if

	mode = argv[1]
	inputfile = argv[2]
	outputfile = argv[3]
	
	if outputfile == '-':
		analyzer = Wordanalyzer(inputfile, sys.stdout)
	
		if mode == '--wordlist':
			analyzer.print_word_list()
		elif mode == '--check-csv':
			analyzer.print_enhanced_table()
		else:
			print('Invalid mode!')
			exit(1)
		#end if
	else:
		with codecs.open(outputfile, 'w', 'utf-8') as ostream:
			analyzer = Wordanalyzer(inputfile, ostream)
			
			if mode == '--wordlist':
				analyzer.print_word_list()
			elif mode == '--check-csv':
				analyzer.print_enhanced_table()
			else:
				print('Invalid mode!')
				exit(1)
			#end if
		#end with
	#end if
#end def

main(sys.argv)
