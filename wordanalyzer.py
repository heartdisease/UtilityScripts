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
	def __init__(self, separator, delimiter, encoding = 'utf-8'):
		self._separator = separator
		self._delimiter = delimiter
		self._encoding = encoding
	#end def
	
	def parse(self, csvfile):
		rows = []
		
		with codecs.open(csvfile, 'r', self._encoding) as f:
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

class Translator:
	STD_HEADERS = {
		'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
		'Accept-Language' : 'es-419,es'
	}
	POST_HEADERS = {
		'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
		'Accept-Language' : 'es-419,es',
		'Content-type' : 'application/x-www-form-urlencoded; charset=utf-8'
	}
	WORD_PATTERN = re.compile(r'(?:(el/la|el|la) )?(\w[\w ]+)(?:, -(\w+))?', re.UNICODE)
	ANNOTATION_PATTERN = re.compile(r' ?\[[\w\.]*\]', re.UNICODE) # detects vocabulary annotations between brackets
	
	# Strips all extras like annotations, articles etc.
	@staticmethod
	def normalize_word(word):
		components = Translator.WORD_PATTERN.findall(Translator.ANNOTATION_PATTERN.sub('', word))
		return components[0][1] if len(components) > 0 else word
	#end def
	
	# Converts a vocabulary list-style string into a list of separate words.
	#
	# Example: 'el/la jugador, -a' turns into ['el jugador', 'la jugadora']
	@staticmethod
	def resolve_word_list(string):
		words = []
		sections = Translator.ANNOTATION_PATTERN.sub('', string).split(';')
		
		for section in sections:
			for group in Translator.WORD_PATTERN.findall(section):
				# group[0] = article (el/la, el, la) if available, otherwise empty string
				# group[1] = actual word
				# group[2] = female ending if available, otherwise empty string
				words.append(group[1])
			
				if len(group[2]) > 0: # generate female version if available
					if group[1][-1] == 'o': # last letter is vowel 'o'
						words.append(group[1][:-len(group[2])] + group[2])
					else:
						words.append(group[1][:-len(group[2]) + 1] + group[2])
					#end if
				#end if
			#end for
		#end for
		
		return set(words)
	#end def
	
	def __init__(self, url_template, encoding = 'utf-8', headers = STD_HEADERS):
		self._url_template = url_template
		self._encoding     = encoding
		self._headers      = headers
	#end def
	
	def _pquery(self, word):
		content = self.__get_content_from_url(Translator.normalize_word(word))
		return pq(url=None, opener=lambda url: content) if content != None else None
	#end def
	
	def __get_content_from_url(self, get_data):
		url = self._url_template % urllib2.quote(get_data.encode(self._encoding))
		content = None
		
		try:
			response = urllib2.urlopen(urllib2.Request(url, headers=self._headers))
			content  = response.read()
			return unicode(content, self._encoding).replace('\n', ' ')
		except UnicodeDecodeError as e:
			if content == None:
				raise
			#end if
			return content.decode(self._encoding, 'ignore').encode(self._encoding).replace('\n', ' ')
		except Exception as e:
			print('Failed to retrieve page for word "%s".' % get_data)
			print(str(e))
		#end try
		
		return None
	#end def
#end

class SpanishdictCom(Translator):
	def __init__(self):
		Translator.__init__(self, u'http://www.spanishdict.com/translate/%s')
	#end def
	
	##
	# Returns a dictionary that contains the normalized version of the word, the translation and the word type (e.g. noun).
	# 
	# @param word to be looked up on SpanishDict.com
	# @return dictionary with information about the word
	##
	def get_translation(self, word):
		normalized  = None
		translation = None
		wordtype    = None
		
		p = self._pquery(word)
		if p != None:
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
			print(u'Invalid response for "' + word + '".')
		#end if
	
		return { 'normalized' : normalized if normalized != None else word, 'translation' : translation, 'wordtype' : wordtype }
	#end def
#end class

class DixOsolaCom(Translator):
	def __init__(self):
		Translator.__init__(self, u'http://www.diccionario-ingles.info/index.php?search=%s', 'iso-8859-1')
	#end def
	
	##
	# Returns a dictionary that contains the normalized version of the word, the translation and the word type (e.g. noun).
	# 
	# @param word to be looked up on diccionario-ingles.info
	# @return dictionary with information about the word
	##
	def get_translation(self, word):
		normalized  = None
		translation = None
		wordtype    = None
		
		p = self._pquery(word)
		if p != None:
			normalized  = None
			translation = None
			wordtype    = None
			
			info_rows = p('tr[id^="row_"] > td:first-child a')
			spanish_rows = p('tr[id^="row_"] > td:nth-child(2)')
			english_rows = p('tr[id^="row_"] > td:nth-child(3)')
			
			for i in range(len(spanish_rows)):
				spanish_row = pq(spanish_rows[i]).text()
				
				if normalized == None:
					#print('word: ', word, ' ', type(word))
					#print('spanish_row: ', spanish_row, ' ', type(spanish_row))
					
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
			print(u'Invalid response for "' + word + '".')
		#end if
	
		return { 'normalized' : normalized if normalized != None else word, 'translation' : translation, 'wordtype' : wordtype }
	#end def
#end class

class DixOsolaComConjugator(Translator):
	def __init__(self):
		Translator.__init__(self, u'http://dix.osola.com/v.php?search=%s', 'iso-8859-1')
	#end def
	
	def get_conjugation(self, verb, tense):
		p = self._pquery(verb)
		if p != None:
			table_headers = p('td.contentheadcenter')
			if len(table_headers) > tense:
				conjugation_table = p(table_headers[tense]).parent().parent()
				conjugation_cells = conjugation_table.find('td:last-child')
				
				tense_name = None
				conjugations = []
			
				for cell in conjugation_cells:
					if tense_name == None:
						tense_name = p(cell).text()
					else:
						conjugations.append(p(cell).text())
					#end if
				#end for
				conjugations.append(tense_name)
				
				return conjugations
			else:
				print(u'Cannot find conjugations for verb "%s".' % verb)
			#end if
		#end if
		
		return None
	#end def
#end class

class DeWiktionaryOrg(Translator):
	def __init__(self):
		Translator.__init__(self, u'http://de.wiktionary.org/wiki/%s')
	#end def

	def get_translation(self, word):
		ipa  = None
		wordtype = None
		
		p = self._pquery(word)
		if p != None:
			result_block = p('#mw-content-text')
			ipa      = result_block.find('span.ipa')
			wordtype = result_block.find('a[title="Hilfe:Wortart"]')
			
			ipa = p(ipa[0]).text() if len(ipa) > 0 else ipa.text()
			wordtype = p(wordtype[0]).text() if len(wordtype) > 0 else wordtype.text()
		#end if
	
		return { 'normalized' : word, 'ipa' : ipa, 'wordtype' : wordtype }
	#end def
#end class

class DictCc(Translator):
	MAX_TRANSLATIONS = 5
	
	def __init__(self):
		Translator.__init__(self, u'http://www.dict.cc/?s=%s')
	#end def
	
	def get_translation(self, word):
		translation = None
		wordtype    = None
		p = self._pquery(word)
		
		if p != None:
			brackets_regex = re.compile(r'\[.*\]')
			translation_rows = p('tr[id^=tr] td.td7nl')
			translation_counter = 0
			tmp_word = word
			
			for i in range(0, len(translation_rows), 2):
				pq_english_col = pq(translation_rows[i])
				english_col = brackets_regex.sub('', pq_english_col.find('a').text()).strip()
				if pq_english_col.text().startswith('to ') and not english_col.startswith('to '):
					english_col = 'to ' + english_col
				#end if
				if english_col.startswith('to ') and not word.startswith('to ') and english_col[3:] == word:
					tmp_word = 'to ' + word
				else:
					tmp_word = word
				#end if
				
				if english_col == word:
					translation_col = pq(translation_rows[i+1]).find('a').text().strip()
					
					if translation == None:
						translation = translation_col
					else:
						translation += ', ' + translation_col
					#if
					
					translation_counter += 1
					if translation_counter == DictCc.MAX_TRANSLATIONS:
						break
					#end if
				#end if
			#end for
			
			wordtype = '' # TODO detect wordtype
		#end if
		
		return { 'normalized' : tmp_word, 'translation' : translation, 'wordtype' : wordtype }
	#end def
#end class

class Wordanalyzer:
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
	READER = CsvReader(CSV_SEPARATOR, TEXT_DELIMITER)
	DICT_CC_MODULE = None
	
	@staticmethod
	def get_translation_es(word):
		module = SpanishdictCom()
		return module.get_translation(word)
	#end def
	
	@staticmethod
	def get_translation_es_2(word):
		module = DixOsolaCom()
		return module.get_translation(word)
	#end def
	
	@staticmethod
	def get_translation_en(word):
		if Wordanalyzer.DICT_CC_MODULE == None:
			Wordanalyzer.DICT_CC_MODULE = DictCc()
		#end if
		
		return Wordanalyzer.DICT_CC_MODULE.get_translation(word)
	#end def
	
	@staticmethod
	def get_translation_de(word):
		module = DeWiktionaryOrg()
		return module.get_translation(word)
	#end def
	
	@staticmethod
	def get_conjugation_es(verb, tense):
		module = DixOsolaComConjugator()
		return module.get_conjugation(verb, tense)
	#end def
	
	def __init__(self, src, out = None):
		self._src = src
		self._ostream = sys.stdout if out == None else codecs.open(out, 'w', 'utf-8')
	#end def
	
	def close(self):
		if self._ostream != sys.stdout:
			self._ostream.close()
		#end if
	#end def
	
	def print_csv_row(self, cols):
		first_col = True
	
		for col in cols:
			if not first_col:
				self._ostream.write(Wordanalyzer.CSV_SEPARATOR)
			else:
				first_col = False
			#end if
		
			self._ostream.write('"')
			self._ostream.write(col)
			self._ostream.write('"')
		#end for
	
		self._ostream.write('\n')
	#end def

	##
	# Parses text file containing standard text and generates vocabulary list without translations from it.
	#
	# @param src path to input file
	# @param out output stream
	##
	def print_word_list(self, lang = None):
		with codecs.open(self._src, 'r', 'utf-8') as f:	
			text = f.read().replace('\n', ' ') # replace newlines with spaces to avoid cut-off words
			wordset = set(word for word in re.findall(r"(?u)[\w'-]{3,}", text) if re.match(r'(?u)^[^0-9]+$', word))
			words = None
			translation_lambda = None
			
			if lang == 'es':
				words = sorted(wordset - wordlist.WORD_COLLECTION)
			elif lang == 'de':
				words = sorted(wordset)
			elif lang == 'en':
				words = sorted(wordset)
			else:
				words = sorted(wordset)
			#end if
			
			self.print_csv_row(['[Original word]', '[Translation]']) # print header
			for word in words:
				if lang == 'en':
					# skip words that accidentially have two hyphens at the end
					# skip plurals and 3rd-person-s verbs if they exist in base form
					# skip past tense verbs if they exist in base form
					if word.endswith('--') or \
						word[-1] == 's' and word[:-1] in words or \
						word[-2:] == 'ed' and word[:-2] in words or word[:-1] in words:
						continue
					#end if
				#end if
				
				self.print_csv_row([word, ''])
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
		rows = Wordanalyzer.READER.parse(self._src)

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
	
	def print_enhanced_table_en(self):
		thread_pool = ThreadPool(self.__print_enhanced_row)
		rows = Wordanalyzer.READER.parse(self._src)

		self.print_csv_row(['[Original word]', '[Normalized form]', '[New translation]', '[Translation]', '[Word type]', '[Checked]']) # print header
		for row in rows:
			if len(row) < 2:
				print('Skip incomplete row')
			else:
				p = Processable(lambda word: Wordanalyzer.get_translation_en(word), row[0], row)
				p.start()
				
				thread_pool.add(p)
			#end if
		#end for
		
		thread_pool.finish()
	#end def
	
	def print_enhanced_table_de(self):
		thread_pool = ThreadPool(self.__print_enhanced_row_de)
		rows = Wordanalyzer.READER.parse(self._src)

		self.print_csv_row(['[Original word]', '[IPA]', '[Word type]']) # print header
		for row in rows:
			if len(row) < 2:
				print('Skip incomplete row')
			else:
				p = Processable(lambda word: Wordanalyzer.get_translation_de(word), row[0], row)
				p.start()
				
				thread_pool.add(p)
			#end if
		#end for
		
		thread_pool.finish()
	#end def
	
	def print_conjugation_table(self, tenses):
		thread_pool = ThreadPool(self.__print_conjugation_table)
		rows = Wordanalyzer.READER.parse(self._src)

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
		rows = Wordanalyzer.READER.parse(self._src)

		self._ostream.write('#!/usr/bin/python\n# -*- coding: utf-8 -*-\nWORD_COLLECTION = sorted(set([\n') # print header
		first_row = True
		for row in rows:
			for word in Translator.resolve_word_list(row[0]):
				if first_row:
					self._ostream.write('\t  u\'')
					first_row = False
				else:
					self._ostream.write('\t, u\'')
				#end if
				
				self._ostream.write(word)
				self._ostream.write('\'\n')
			#end for
		#end for
		self._ostream.write(']))\n')
	#end def
	
	def print_new_words(self):
		for row in Wordanalyzer.READER.parse(self._src):
			word = Translator.normalize_word(row[0])
			if word not in wordlist.WORD_COLLECTION:
				self._ostream.write(word)
				self._ostream.write('\n')
			#end if
		#end if
	#end def
	
	# prints rows from [newfile] that are not part of [self._src]
	def print_difference(self, newfile):
		total_count = 0
		new_count   = 0
		ignore = [(row[0][3:] if row[0].startswith('to ') else row[0]).strip().lower() for row in Wordanalyzer.READER.parse(self._src)]
		
		for row in Wordanalyzer.READER.parse(newfile):
			word = row[0].strip().lower()
			normalized = word[3:] if word.startswith('to ') else word
			
			if normalized not in ignore:
				self.print_csv_row(row)
				new_count += 1
			else:
				print('Omit "' + word + '"')
			#end if
			total_count += 1
		#end
	
		print("%d new rows" % new_count)
		print("%d rows deleted" % (total_count - new_count))
	#end def
	
	def print_without_duplicates(self):
		total_count = 0
		new_count   = 0
		rows = Wordanalyzer.READER.parse(self._src)
		checked_words = []
		
		for row in rows:
			word = row[0].strip()
			normalized = word[3:].lower() if word.startswith('to ') else word.lower()
			
			if normalized not in checked_words:
				checked_words.append(normalized)
				
				if word != row[0]: # remove trailing whitespaces
					row[0] = word
				#end if
				self.print_csv_row(row)
			else:
				new_count += 1
				print('Drop duplicate "' + word + '"')
			#end if
			
			total_count += 1
		#end for
		
		print('Removed %d duplicates from %d lines.' % (new_count, total_count))
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
	
	def __print_enhanced_row_de(self, result, row):
		normalized  = u'unknown' if result['normalized'] == None else result['normalized']
		ipa         = u'unknown' if result['ipa'] == None else result['ipa']
		wordtype    = u'' if result['wordtype'] == None else result['wordtype']

		row.insert(1, normalized)
		row.insert(2, ipa)
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
	if not 4 <= len(argv) <= 5:
		print('Invalid parameter count!')
		print('wordanalyzer.py [option] [input file] [output file]|[[diff file] [output file]]')
		print('Options:')
		print('\t--wordlist-es             prints list of words contained in [input file] (Spanish)')
		print('\t--wordlist-en             prints list of words contained in [input file] (English)')
		print('\t--wordlist-de             prints list of words contained in [input file] (German)')
		print('\t--check-csv-es            prints enhanced version of cvs file [input file] (Spanish)')
		print('\t--check-csv-en            prints enhanced version of cvs file [input file] (English)')
		print('\t--check-csv-de            prints enhanced version of cvs file [input file] (German)')
		print('\t--conjugate-verbs=[TENSE] prints table with conjugated verbs from cvs file [input file] (Spanish)')
		print('\t--word-array              prints python code with list of words from cvs file [input file]')
		print('\t--check-new               prints words from cvs file [input file] that are not yet part of the vocublary collection (see wordlist.py) (Spanish)')
		print('\t--diff-csv                prints words from cvs file [diff file] that are not part of csv file [input file]')
		print('\t--remove-dupl             prints words from cvs file [input] without duplicate rows')
		print
		print('Conjugation modes:')
		print('\tPRESENTE')
		print('\tPRETERITO_IMPERFECTO')
		print('\tPRETERITO_PLUSCUAMPERFECTO')
		print('\tPRETERITO_INDEFINIDO')
		print('\tFUTURO_IMPERFECTO')
		print('\tCONDICIONAL_SIMPLE')
		print('\tPRESENTE_SUBJUNTIVO')
		
		#trans = Wordanalyzer.get_translation_en('ludicrous')
		#print(trans['normalized'], trans['translation'], trans['wordtype'])
		
		exit(1)
	#end if

	mode = argv[1]
	input_file  = argv[2]
	output_file = None
	diff_file   = None
	if len(argv) == 5:
		diff_file   = argv[3]
		output_file = argv[4]
	else:
		output_file = argv[3]
	#end if	
	
	analyzer = Wordanalyzer(input_file) if output_file == '-' else Wordanalyzer(input_file, output_file)
	
	if mode == '--wordlist-es':
		analyzer.print_word_list('es')
	elif mode == '--wordlist-en':
		analyzer.print_word_list('en')
	elif mode == '--wordlist-de':
		analyzer.print_word_list('de')
	elif mode == '--check-csv-es':
		analyzer.print_enhanced_table()
	elif mode == '--check-csv-en':
		analyzer.print_enhanced_table_en()
	elif mode == '--check-csv-de':
		analyzer.print_enhanced_table_de()
	elif mode.startswith('--conjugate-verbs='):
		identifier = mode[18:] # 18 = length of mode string
		tense = getattr(Wordanalyzer, identifier) # retrieve constant with reflection
		analyzer.print_conjugation_table([tense])
	elif mode == '--word-array':
		analyzer.print_word_array()
	elif mode == '--check-new':
		analyzer.print_new_words()
	elif mode == '--diff-csv':
		analyzer.print_difference(diff_file)
	elif mode == '--remove-dupl':
		analyzer.print_without_duplicates()
	else:
		print('Invalid mode!')
		exit(1)
	#end if
	
	analyzer.close()
#end def

main(sys.argv)
