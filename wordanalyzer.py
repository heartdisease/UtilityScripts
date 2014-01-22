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

import wordlist

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

class Wordanalyzer:
	#(0, 'Formas basicas')
	#(1, 'Imperativo')
	#(2, 'negativo')
	#(3, 'Presente')
	#(4, u'Pret\xe9rito perfecto')
	#(5, u'Pret\xe9rito imperfecto')
	#(6, u'Pret\xe9rito pluscuamperfecto')
	#(7, u'Pret\xe9rito indefinido')
	#(8, u'Pret\xe9rito anterior')
	#(9, 'Futuro imperfecto')
	#(10, 'Futuro perfecto')
	#(11, 'Condicional simple')
	#(12, 'Condicional compuesto')
	#(13, 'Presente')
	#(14, u'Pret\xe9rito perfecto')
	#(15, u'Pret\xe9rito imperfecto')
	#(16, u'Pret\xe9rito pluscuamperfecto')
	#(17, u'Pret\xe9rito imperfecto II')
	#(18, u'Pret\xe9rito pluscuamperfecto II')
	#(19, 'Futuro imperfecto')
	#(20, 'Futuro perfecto')

	PRESENTE = 3
	PRETERITO_IMPERFECTO = 5
	PRETERITO_PLUSCUAMPERFECTO = 6
	PRETERITO_INDEFINIDO = 7
	FUTURO_IMPERFECTO = 9
	CONDICIONAL_SIMPLE = 11
	PRESENTE_SUBJUNTIVO = 13
	
	CSV_SEPARATOR = ','
	TEXT_DELIMITER = '"'
	WORD_SPLIT_REGEX = ur'[ \t-\.,:;!\?\(\)"\'“”]'
	WORD_PATTERN = re.compile(r'(?:(el/la|el|la) )?(\w[\w ]+)(?:, -(\w+))?')
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
	
	# Strips all extras like annotations, articles etc.
	@staticmethod
	def normalize_word(word):
		components = Wordanalyzer.WORD_PATTERN.findall(re.sub(r' ?\[[\w\.]*\]', '', word), re.UNICODE)
		return components[0][1] if len(components) > 0 else word
	#end def
	
	# Converts a vocabulary list-style string into a list of separate words.
	#
	# Example: 'el/la jugador, -a' turns into ['el jugador', 'la jugadora']
	@staticmethod
	def resolve_word_list(string):
		words = []
		word_groups = Wordanalyzer.WORD_PATTERN.findall(re.sub(r' ?\[[\w\.]*\]', '', string), re.UNICODE)
		
		for group in word_groups:
			words.append(group[1])
			
			if len(group[2]) > 0: # generate female version if available
				if group[1][-1] == 'o': # last letter is vowel 'o'
					words.append(group[1][:-len(group[2])] + group[2])
				else:
					words.append(group[1][:-len(group[2]) + 1] + group[2])
				#end if
			#end if
		#end for
		
		return set(words)
	#end def
	
	# Returns content of a given URL as a text object
	@staticmethod
	def get_content_from_url(url, encoding = 'utf-8', headers = STD_HEADERS):
		response = urllib2.urlopen(urllib2.Request(url, headers=headers))
		
		try:
			return unicode(response.read(), encoding).replace('\n', ' ')
		except UnicodeDecodeError, e:
			print(str(e))
		#end try
		
		return None
	#end def
	
	##
	# Returns a dictionary that contains the normalized version of the word, the translation and the word type (e.g. noun).
	# 
	# @param word to be looked up on SpanishDict.com
	# @return dictionary with information about the word
	##
	@staticmethod
	def get_translation_es(word):
		word = Wordanalyzer.normalize_word(word)
		url = u'http://www.spanishdict.com/translate/' + urllib.quote(word)
		normalized  = None
		translation = None
		wordtype    = None
		
		content = Wordanalyzer.get_content_from_url(url)
		if content != None:
			p = pq(url=None, opener=lambda url: content)
	
			result_block = p('div.results-block')
			normalized   = result_block.find('h1.word').text()
			translation  = result_block.find('h2.quick_def').text()
			wordtype     = result_block.find('div.hw-block > span.quick_pos').text()
			partofspeach = result_block.find('span.part_of_speech:first-child').text()
			head_word    = result_block.find('div.dictionary_word > span.head_word').text()
			
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
			
			# head_word offers more detailed description of the noun (like 'chico, -a')
			if head_word != None and len(head_word) > 0:
				normalized = head_word.strip()
			#end if
			
			if wordtype == u'noun':
				if partofspeach == None: # special case where gender declaration is missing
					normalized = u'?? ' + normalized
				else:
					is_masculine = u'masculine' in partofspeach
					is_feminine  = u'feminine' in partofspeach
				
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
			#end if
	
			if translation != None:
				translation = translation.replace(';', ',').replace(' , ', ', ')
			#end if
		else:
			print(u'Invalid response for "' + unicode(word, 'utf-8') + '".')
		#end if
	
		return { 'normalized' : normalized if normalized != None else unicode(word, 'utf-8'), 'translation' : translation, 'wordtype' : wordtype }
	#end def
	
	##
	# Returns a dictionary that contains the normalized version of the word, the translation and the word type (e.g. noun).
	# 
	# @param word to be looked up on diccionario-ingles.info
	# @return dictionary with information about the word
	##
	@staticmethod
	def get_translation_es_2(word):
		word = Wordanalyzer.normalize_word(word)		
		url = u'http://www.diccionario-ingles.info/index.php?search=' + urllib2.quote(word)
		normalized  = None
		translation = None
		wordtype    = None
		
		content = Wordanalyzer.get_content_from_url(url, 'latin-1')
		if content != None:
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
						translation += u', ' + english_row
					#end if
				else:
					break # found all translations
				#end if
			#end for
		else:
			print(u'Invalid response for "' + unicode(word, 'utf-8') + '".')
		#end if
	
		return { 'normalized' : normalized, 'translation' : translation, 'wordtype' : wordtype }
	#end def
	
	@staticmethod
	def get_conjugation_es(verb, tense):
		urlencoded = urllib2.quote(verb.encode('iso-8859-1'))
		verb = verb.encode('utf-8')
		url = u'http://dix.osola.com/v.php?search=' + urlencoded.encode('utf-8')
		
		content = Wordanalyzer.get_content_from_url(url, 'iso-8859-1')
		if content != None:
			p = pq(url=None, opener=lambda url: content)
			
			table_headers = p('td.contentheadcenter')
			if len(table_headers) > tense:
				conjugation_table = p(table_headers[tense]).parent().parent()
				conjugation_cells = conjugation_table.find('td:last-child')
			
				conjugations = []
			
				for cell in conjugation_cells:
					conjugations.append(p(cell).text())
				#end for
			
				return conjugations
			else:
				print(u'Cannot find conjugations for verb "' + unicode(verb, 'utf-8') + u'"')
			#end if
		#end if
		
		return None
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
				p = Processable(lambda word: Wordanalyzer.get_translation_es(word), word, [word])
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
				p = Processable(lambda word: Wordanalyzer.get_translation_es(word), row[0], row)
				p.start()
				
				thread_pool.add(p)
			#end if
		#end for
		
		thread_pool.finish()
	#end def
	
	def print_conjugation_table(self, tenses):
		thread_pool = ThreadPool(self.__print_conjugation_table)
		rows = Wordanalyzer.READER.parse(self.src)

		self.print_csv_row([u'[Infinitive]', u'[Tense]', u'[yo]', u'[tú]', u'[el/ella/usted]', u'[nosotros, -as]', u'[vosotros, -as]', u'[ellos/ellas/ustedes]']) # print header
		for row in rows:
			if len(row) < 1:
				print('Skip incomplete row')
			else:
				for tense in tenses:
					p = Processable(lambda word: Wordanalyzer.get_conjugation_es(word, tense), row[0], row)
					p.start()
				
					thread_pool.add(p)
				#end for
			#end if
		#end for
		
		thread_pool.finish()
	#end def
	
	def print_word_array(self):
		rows = Wordanalyzer.READER.parse(self.src)

		self.out.write('#!/usr/bin/python\n# -*- coding: utf-8 -*-\nWORD_COLLECTION = [\n') # print header
		first_row = True
		for row in rows:
			for word in Wordanalyzer.resolve_word_list(row[0]):
				if first_row:
					self.out.write('\t  u\'')
					first_row = False
				else:
					self.out.write('\t, u\'')
				#end if
				
				self.out.write(word)
				self.out.write('\'\n')
			#end for
		#end for
		self.out.write(']\n')
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
	
	def __print_conjugation_table(self, result, row):
		if result != None:
			row.extend(result)
		#end if
		
		self.print_csv_row(row)
	#end def
#end class

def main(argv):
	if len(argv) != 4:
		print('Argument is missing!')
		print('wordanalyzer [option] [inputfile] [outputfile]')
		print('\t--wordlist\tprints list of words contained in [file]')
		print('\t--check-csv\tprints enhanced version of cvs file [file]')
		print('\t--conjugate-verbs\tprints table with conjugated verbs from cvs file [file]')
		print('\t--word-array\tprints python code with list of words from cvs file [file]')
		
		#word = u'el/la líder'
		#print(word)
		#print(Wordanalyzer.get_translation_es_2(word))
		
		#PRESENTE = 3
		#PRETERITO_IMPERFECTO = 5
		#PRETERITO_PLUSCUAMPERFECTO = 6
		#PRETERITO_INDEFINIDO = 7
		#FUTURO_IMPERFECTO = 9
		#CONDICIONAL_SIMPLE = 11
		#PRESENTE_SUBJUNTIVO = 13
		
		#for entry in Wordanalyzer.get_conjugation_es('comprender', Wordanalyzer.PRESENTE_SUBJUNTIVO):
			#print(entry)
		
		#for row in Wordanalyzer.READER.parse('csv/new.words.csv'):
		#	word = Wordanalyzer.normalize_word(row[0])
		#	if word not in wordlist.WORD_COLLECTION:
		#		print(word)
		#	#end if
		##end if
		
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
		elif mode.startswith('--conjugate-verbs='):
			tense = getattr(Wordanalyzer, mode[18:]) # 18 = length of mode string
			analyzer.print_conjugation_table([tense])
		elif mode == '--word-array':
			analyzer.print_word_array()		
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
			elif mode.startswith('--conjugate-verbs='):
				tense = getattr(Wordanalyzer, mode[18:]) # 18 = length of mode string
				analyzer.print_conjugation_table([tense])
			elif mode == '--word-array':
				analyzer.print_word_array()
			else:
				print('Invalid mode!')
				exit(1)
			#end if
		#end with
	#end if
#end def

main(sys.argv)
