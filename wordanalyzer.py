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

import wordlist_es

### TODO fix verb conjugation bug (yo is always last column)

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

class Translator(object):
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
	# removes duplicates (e.g. 'principal principal')
	@staticmethod
	def remove_duplicates(string):
		if string == None or len(string) == 0:
			return None
		else:
			parts = [word.strip() for word in string.split(' ')]
		
			if len(parts) >= 2:
				for word in parts:
					if parts[0] != word:
						return string
					#end if
				#end if
			else:
				return string
			#end if
		
			return parts[0] # if string only consists of the same words, strip all redundant ones
		#end if
	#end def
	
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
			result_block = p('.main-container .translate .card')
			normalized   = result_block.find('div.quickdef > div.source > h1').text()
			translation  = result_block.find('div.quickdef > div.lang > div.el').text()
			partofspeach = result_block.find('span.part_of_speech:first').text()
			wordtype     = None
			head_word    = result_block.find('div.dictionary_word > span.head_word').text()
			
			if partofspeach == None or not u' ' in partofspeach:
				wordtype = partofspeach
			else:				
				if u'sustantivo' in partofspeach:
					wordtype = u'sustantivo'
				elif u'verbo' in partofspeach:
					wordtype = u'verbo'
				elif u'adverbio' in partofspeach:
					wordtype = u'adverbio'
				elif u'adjetivo' in partofspeach:
					wordtype = u'adjetivo'
				else:
					wordtype = partofspeach.split(u' ')[0]
				#end if
			#end if
			
			if partofspeach != None:
				partofspeach = partofspeach.strip() # remove trailing white spaces
			#end if
			
			# head_word offers more detailed description of the noun or adjective (like 'chico, -a')
			if head_word != None and len(head_word) > 0:
				normalized = head_word.strip()
			elif normalized != None:
				normalized = normalized.strip()
			#end if
			#normalized = SpanishdictCom.remove_duplicates(normalized)
			
			if wordtype == u'sustantivo' or wordtype == u'noun':
				if partofspeach == None: # special case where gender declaration is missing
					normalized = u'?? ' + normalized
				else:
					is_masculine = u'masculine' in partofspeach or u'masculino' in partofspeach
					is_feminine  = u'feminine' in partofspeach or u'femenino' in partofspeach
				
					if is_masculine and is_feminine:
						normalized = u'el/la ' + normalized
					elif is_masculine:
						normalized = u'el ' + normalized
					elif is_feminine:
						# use article 'el' if noun starts with a-sound (still buggy!)
						if normalized.startswith(u'a') or normalized.startswith(u'ha'):
							normalized = u'el ' + normalized + ' {f}'
						else:
							normalized = u'la ' + normalized
						#end if
					else: # special case where gender declaration is missing (add manually)
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
		
		# translate english word type to spanish (outdated)
		#if wordtype == u'noun':
		#	wordtype = u'sustantivo'
		#elif wordtype == u'verb':
		#	wordtype = u'verbo'
		#elif wordtype == u'adjective':
		#	wordtype = u'adjetivo'
		#elif wordtype == u'adverb':
		#	wordtype = u'adverbio'
		#elif wordtype == u'pronoun':
		#	wordtype = u'pronombre'
		#endif
	
		return { 'normalized' : normalized if normalized != None else word, 'translation' : translation, 'wordtype' : wordtype }
	#end def
#end class

class DixOsolaComDe(Translator):
	def __init__(self):
		Translator.__init__(self, u'http://dix.osola.com/index.php?search=%s', 'iso-8859-1')
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
			german_rows = p('tr[id^="row_"] > td:nth-child(2)')
			spanish_rows = p('tr[id^="row_"] > td:nth-child(3)')
			
			for i in range(len(spanish_rows)):
				spanish_row = pq(spanish_rows[i]).text().strip()
				
				if normalized == None:
					print('word: %s [%s]' % (word, type(word)))
					print('spanish_row: %s [%s]' % (spanish_row, type(spanish_row)))
					
					if word == spanish_row: # word is sole translation in this row
						word_info = pq(info_rows[i]).attr('onmouseover')
						wordtype_match = re.match(r"showinfomenu\([0-9]+,'DE','de_es',this,'\w+','[0-9]+',[0-9]+,'\w+','(\w+)'", word_info)
						
						if wordtype_match != None:
							wordtype = wordtype_match.group(1)
						normalized = spanish_row
					#end if
				elif spanish_row == normalized:
					german_row = pq(german_rows[i]).text()
					
					if translation == None:
						translation = german_row
					else:
						translation += u', ' + german_row
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

class DixOsolaComEn(Translator):
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
				spanish_row = pq(spanish_rows[i]).text().strip().replace('&nbsp;', ' ')
				
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

class SpanishDictConjugator(Translator):
	def __init__(self):
		Translator.__init__(self, u'http://www.spanishdict.com/conjugate/%s')
	#end def
	
	def get_conjugation(self, verb, tense):
		return None # TODO implement
	#end def
#end class

class DixOsolaComConjugator(Translator):
	FORMAS_BASICAS = 0
	IMPERATIVO = 1
	PRESENTE = 3
	PRETERITO_IMPERFECTO = 5
	PRETERITO_PLUSCUAMPERFECTO = 6
	PRETERITO_INDEFINIDO = 7
	FUTURO_IMPERFECTO = 9
	CONDICIONAL_SIMPLE = 11
	PRESENTE_SUBJUNTIVO = 13
	PRETERITO_IMPERFECTO_SUBJUNTIVO = 15

	def __init__(self):
		Translator.__init__(self, u'http://dix.osola.com/v.php?search=%s', 'iso-8859-1')
	#end def
	
	def get_conjugation(self, verb, tense):
		p = self._pquery(verb)
		
		if p != None:
			table_headers = p('td.contentheadcenter')
			
			if len(table_headers) > tense:
				conjugation_table = p(table_headers[tense]).parent().parent()
				conjugation_cells = conjugation_table.find('td:nth-child(2)')
				
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
	
	def get_ipa(self, word):
		ipa  = None
		wordtype = None
		
		p = self._pquery(word)
		if p != None:
			ipa_spans = p('#mw-content-text span.ipa')
			ipa = p(ipa_spans[0]).text() if len(ipa_spans) > 0 else ipa_spans.text()
		#end if
	
		return ipa
	#end def
#end class

class EnWiktionaryOrg(Translator):
	def __init__(self):
		Translator.__init__(self, u'http://en.wiktionary.org/wiki/%s')
	#end def

	def get_translation(self, word):
		ipa  = None
		
		p = self._pquery(word)
		if p != None:
			result_block = p('#mw-content-text')
			ipa      = result_block.find('span.IPA')
			#wordtype = result_block.find('a[title="Hilfe:Wortart"]')
			
			ipa = p(ipa[0]).text() if len(ipa) > 0 else ipa.text()
			#wordtype = p(wordtype[0]).text() if len(wordtype) > 0 else wordtype.text()
		#end if
	
		return { 'normalized' : word, 'ipa' : ipa, 'wordtype' : None }
	#end def
	
	def get_ipa(self, word):
		ipa  = None
		
		p = self._pquery(word)
		if p != None:
			ipa_spans = p('#mw-content-text span.IPA')
			ipa = p(ipa_spans[0]).text() if len(ipa_spans) > 0 else ipa_spans.text()
		#end if
	
		return ipa
	#end def
#end class

class OxfordDictionary(Translator):
	def __init__(self):
		Translator.__init__(self, u'http://www.oxforddictionaries.com/definition/english/%s')
	#end def

	def get_info(self, word):
		ipa  = None
		wordtype = None
		
		p = self._pquery(word)
		if p != None:
			ipa_span     = p('div.headpron:first').text()
			wordtype     = p('span.partOfSpeech:first').text().strip()
			
			if ipa_span != None:
				ipa_span = re.sub(r'\s*', '', ipa_span.replace('End of DIV sound audio_play_button pron-uk icon-audio', ''))
				ipas = re.findall(r'\/(.+)\/', ipa_span)
				if len(ipas) > 0:
					ipa = ipas[0].replace(',', ', ')
				#end if
			#end if
		#end if
	
		return { 'ipa' : ipa, 'wordtype' : wordtype }
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

class SpanishWordAnalyser(object):
	SPANISH_TO_GERMAN = [ # any occurance of the letter x will not be replaced due to the unpredictability of its pronounciation (h and y need special treatment)
		(u'ch', u'tsch'), (u'cc', u'ks'), (u'j', u'ch'), (u'ñ', u'nj'), (u'll', u'j'), (u'v', u'b'), (u'z', u's'),
		(u'ca', u'ka'), (u'cá', u'ká'), (u'co', u'ko'), (u'có', u'kó'), (u'cu', u'ku'), (u'cú', u'kú'),
		(u'ce', u'se'), (u'cé', u'sé'), (u'ci', u'si'), (u'cí', u'sí'),
		(u'que', u'ke'), (u'qué', u'ké'), (u'qui', u'ki'), (u'quí', u'kí'),
		(u'ge', u'che'), (u'gé', u'ché'), (u'gi', u'chi'), (u'gí', u'chí'),
		(u'gue', u'ge'), (u'gué', u'gé'), (u'gui', u'gi'), (u'guí', u'gí'),
		(u'güe', u'gue'), (u'güé', u'gué'), (u'güi', u'gui'), (u'güí', u'guí'),
		(u'eu', u'e·u'), (u'éu', u'é·u'), (u'eú', u'e·ú'),
		(u'ei', u'e·i'), (u'éi', u'é·i'), (u'eí', u'e·í'),
		(u'ie', u'i·e'), (u'íe', u'í·e'), (u'ié', u'i·é')
	]
	ACCENT_CONVERSION = {
		u'a' : u'á', u'e' : u'é', u'i' : u'í', u'o' : u'ó', u'u' : u'ú'
	}

	def __init__(self, word):
		self._word = word
		self._syllables = None
		self._stressed = -1 # index of stressed syllable
	#end def
	
	def phonetic_de(self):
		#phonetics = u' '.join([Wordanalyzer.add_accent_es(word) for word in re.split(ur'[ \/\(\)\[\]¡!¿?;\.:_-]', re.sub(ur'(?:[^c])h', u'', word.lower())) if len(word) > 0])
		phonetics = re.sub(ur'(?:[^c])h', u'', self._word.lower())
		words_with_accents = [(self._word, SpanishWordAnalyser.__add_accent(word)) for self._word in re.findall(r'(?u)\w+', phonetics)]
		
		for word_pair in words_with_accents:
			if word_pair[0] != word_pair[1]:
				phonetics = phonetics.replace(word_pair[0], word_pair[1])
			#end if
		#end for
		
		for conversion in SpanishWordAnalyser.SPANISH_TO_GERMAN:
			phonetics = phonetics.replace(conversion[0], conversion[1])
		#end for
		
		return re.sub(ur'y ', 'i ', re.sub(ur'y$', 'i', phonetics)).replace(u'y', u'j')
	#end def
	
	def syllables(self):
		if self._syllables == None:
			self._analyse()
		#end if
		
		return self._syllables
	#end def
	
	def stressed_syllable(self):
		if self._stressed == -1:
			self._analyse()
		#end if
		
		return self._stressed
	#end def
	
	def word(self):
		return self._word
	#end def
	
	@staticmethod
	def is_vowel(char):
		return char == u'a' or char == u'e' or char == u'i' or char == u'o' or char == u'u' \
			or char == u'á' or char == u'é' or char == u'í' or char == u'ó' or char == u'ú'
	#end def
	
	@staticmethod
	def has_accent(char):
		return char == u'á' or char == u'é' or char == u'í' or char == u'ó' or char == u'ú'
	#end def
	
	@staticmethod
	def contains_accent(word):
		for char in word:
			if char == u'á' or char == u'é' or char == u'í' or char == u'ó' or char == u'ú':
				return True
			#end if
		#end for
		
		return False
	#end def
	
	# TODO implement all rules!
	def _analyse(self):
		self._syllables = []
		syllable = ''
		
		for c in self._word:
			if len(syllable) == 0:
				syllable += c
			else:
				if SpanishWordAnalyser.is_vowel(c):
					if SpanishWordAnalyser.has_accent(c):
						self._stressed = len(self._syllables)
					#end if
				
					if not SpanishWordAnalyser.is_vowel(syllable[-1]) or c == u'i' or c == u'u':
						syllable += c
					else:
						if syllable[-1] == u'u' or syllable[-2] == u'q':
							syllable += c
						else:
							self._syllables.append(syllable)
							syllable = c
						#end if
					#end if
				else: # character is a consonant
					if SpanishWordAnalyser.is_vowel(syllable[-1]):
						self._syllables.append(syllable)
						syllable = c
					else:
						syllable += c
					#end if
				#end if
			#end if
		#end for
		
		self._syllables.append(syllable)
		if self._stressed == -1: # detect accent for words without one
			if SpanishWordAnalyser.contains_accent(syllable):
				self._stressed = len(self._syllables) - 1
			elif len(self._syllables) > 1 and (syllable == u'n' or syllable == u's' or SpanishWordAnalyser.is_vowel(syllable)):
				self._stressed = len(self._syllables) - 2 # accent on penultimate syllable
			else:
				self._stressed = len(self._syllables) - 1 # accent on last syllable
			#end if
		#end if
	#end def
	
	@staticmethod
	def __add_accent(word):
		if Wordanalyzer.contains_accent(word):
			return word
		#end if
		
		last_char = word[-1]
		consonants = 0
		chars = list(word)
		for i, char in reversed(list(enumerate(chars))):
			if Wordanalyzer.is_vowel(char):
				if last_char == u'n' or last_char == u's':
					if consonants > 1:
						chars[i] = Wordanalyzer.ACCENT_CONVERSION[char]
						break
					#end if
				elif consonants > 0:
					chars[i] = Wordanalyzer.ACCENT_CONVERSION[char]
					break
				#end if
			else:
				consonants += 1
			#end if
		#end for
		
		return u''.join(chars)
	#end def
#end class

class Wordanalyzer(object):
	DEFAULT_COLUMN_FORMAT = 'O|M|T'
	SPANISH_COLUMN_FORMAT = 'O|S|A|E|M|W|L|T'
	ENGLISH_COLUMN_FORMAT = 'O|P|D|M|W|T'
	GERMAN_COLUMN_FORMAT  = 'O|M|W|T'
	CSV_SEPARATOR = ','
	TEXT_DELIMITER = '"'
	WORD_SPLIT_REGEX = ur'[ \t-\.,:;!\?\(\)"\'“”]'
	DICT_CC_MODULE = None
	SPANISH_TO_GERMAN = [ # any occurance of the letter x will not be replaced due to the unpredictability of its pronounciation (h and y need special treatment)
		(u'ch', u'tsch'), (u'cc', u'ks'), (u'j', u'ch'), (u'ñ', u'nj'), (u'll', u'j'), (u'v', u'b'), (u'z', u's'),
		(u'ca', u'ka'), (u'cá', u'ká'), (u'co', u'ko'), (u'có', u'kó'), (u'cu', u'ku'), (u'cú', u'kú'),
		(u'ce', u'se'), (u'cé', u'sé'), (u'ci', u'si'), (u'cí', u'sí'),
		(u'que', u'ke'), (u'qué', u'ké'), (u'qui', u'ki'), (u'quí', u'kí'),
		(u'ge', u'che'), (u'gé', u'ché'), (u'gi', u'chi'), (u'gí', u'chí'),
		(u'gue', u'ge'), (u'gué', u'gé'), (u'gui', u'gi'), (u'guí', u'gí'),
		(u'güe', u'gue'), (u'güé', u'gué'), (u'güi', u'gui'), (u'güí', u'guí'),
		(u'eu', u'e·u'), (u'éu', u'é·u'), (u'eú', u'e·ú'),
		(u'ei', u'e·i'), (u'éi', u'é·i'), (u'eí', u'e·í'),
		(u'ie', u'i·e'), (u'íe', u'í·e'), (u'ié', u'i·é')
	]
	ACCENT_CONVERSION = {
		u'a' : u'á', u'e' : u'é', u'i' : u'í', u'o' : u'ó', u'u' : u'ú'
	}
	
	@staticmethod
	def get_translation_es(word):
		module = SpanishdictCom()
		return module.get_translation(word)
	#end def
	
	@staticmethod
	def get_translation_es2(word):
		module = DixOsolaComDe()
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
	def get_ipa_en(word):
		module = OxfordDictionary()
		return module.get_info(word)['ipa']
	#end def
	
	@staticmethod
	def get_ipa_de(word):
		module = DeWiktionaryOrg()
		return module.get_ipa(word)
	#end def
	
	@staticmethod
	def has_accent(word):
		for char in word:
			if char == u'á' or char == u'é' or char == u'í' or char == u'ó' or char == u'ú':
				return True
			#end if
		#end for
		
		return False
	#end def
	
	@staticmethod
	def is_vowel(char):
		return char == u'a' or char == u'e' or char == u'i' or char == u'o' or char == u'u'
	#end def
	
	@staticmethod
	def add_accent_es(word):
		if Wordanalyzer.has_accent(word):
			return word
		#end if
		
		last_char = word[-1]
		consonants = 0
		chars = list(word)
		for i, char in reversed(list(enumerate(chars))):
			if Wordanalyzer.is_vowel(char):
				if last_char == u'n' or last_char == u's':
					if consonants > 1:
						chars[i] = Wordanalyzer.ACCENT_CONVERSION[char]
						break
					#end if
				elif consonants > 0:
					chars[i] = Wordanalyzer.ACCENT_CONVERSION[char]
					break
				#end if
			else:
				consonants += 1
			#end if
		#end for
		
		return u''.join(chars)
	#end def
	
	@staticmethod
	def spanish_to_phonetic_de(word):
		#phonetics = u' '.join([Wordanalyzer.add_accent_es(word) for word in re.split(ur'[ \/\(\)\[\]¡!¿?;\.:_-]', re.sub(ur'(?:[^c])h', u'', word.lower())) if len(word) > 0])
		phonetics = re.sub(ur'(?:[^c])h', u'', word.lower())
		words_with_accents = [(word, Wordanalyzer.add_accent_es(word)) for word in re.findall(r'(?u)\w+', phonetics)]
		
		for word_pair in words_with_accents:
			if word_pair[0] != word_pair[1]:
				phonetics = phonetics.replace(word_pair[0], word_pair[1])
			#end if
		#end for
		
		for conversion in Wordanalyzer.SPANISH_TO_GERMAN:
			phonetics = phonetics.replace(conversion[0], conversion[1])
		#end for
		
		return re.sub(ur'y ', 'i ', re.sub(ur'y$', 'i', phonetics)).replace(u'y', u'j')
	#end def
	
	@staticmethod
	def get_conjugation_es(verb, tense):
		module = DixOsolaComConjugator()
		return module.get_conjugation(verb, tense)
	#end def
	
	@staticmethod
	def get_normalized_words(rows):
		return set([Translator.normalize_word(row.original_word) for row in rows])
	#end def
	
	def __init__(self, src, out = None):
		self._src = src
		self._ostream = sys.stdout if out == None else codecs.open(out, 'w', 'utf-8')
		self.set_column_format(Wordanalyzer.DEFAULT_COLUMN_FORMAT)
	#end def
	
	def close(self):
		if self._ostream != sys.stdout:
			self._ostream.close()
		#end if
	#end def
	
	def set_column_format(self, column_format):
		self._column_format = column_format
		self._reader = CsvReader(Wordanalyzer.CSV_SEPARATOR, Wordanalyzer.TEXT_DELIMITER, column_format)
	#end def
	
	def _parse_src(self):
		return self._reader.parse(self._src)
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
				words = sorted(wordset - wordlist_es.WORD_COLLECTION_ES)
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
		rows = self._parse_src()
		
		self.print_csv_row( # print header
			['[Original word]', '[Normalized word]', '[Synonyms]', '[Antonyms]', '[Example sentence]', '[Translation]', '[New translation]', '[Word type]', '[New word type]', '[Level]', '[Tags]']
		)
		for row in rows:
			if len(row) < 2:
				print('Skip incomplete row')
			else:
				p = Processable(lambda word: Wordanalyzer.get_translation_es(word), row.original_word, row)
				p.start()
				
				thread_pool.add(p)
			#end if
		#end for
		
		thread_pool.finish()
	#end def
	
	def print_enhanced_table_en(self):
		thread_pool = ThreadPool(self.__print_enhanced_row_en)
		rows = self._parse_src()
		
		self.print_csv_row(['[Original word]', '[Normalized word]', '[IPA]', '[Definition]', '[Translation]', '[New translation]', '[Word type]', '[New word type]', '[Tags]']) # print header
		for row in rows:
			if len(row) < 2:
				print('Skip incomplete row')
			else:
				p = Processable(lambda word: Wordanalyzer.get_translation_en(word), row.original_word, row)
				p.start()
				
				thread_pool.add(p)
			#end if
		#end for
		
		thread_pool.finish()
	#end def
	
	def print_enhanced_table_de(self):
		thread_pool = ThreadPool(self.__print_enhanced_row_de)
		rows = self._parse_src()

		self.print_csv_row(['[Original word]', '[IPA]', '[Word type]']) # print header
		for row in rows:
			if len(row) < 2:
				print('Skip incomplete row')
			else:
				p = Processable(lambda word: Wordanalyzer.get_ipa_de(word), row[0], row)
				p.start()
				
				thread_pool.add(p)
			#end if
		#end for
		
		thread_pool.finish()
	#end def
	
	def print_table_with_ipa_en(self):
		thread_pool = ThreadPool(self.__print_row_with_ipa)
		rows = self._parse_src()

		self.print_csv_row(['[Original word]', '[IPA]', '[Word type]']) # print header
		for row in rows:
			if len(row) < 1:
				print('Skip incomplete row')
			else:
				p = Processable(lambda word: Wordanalyzer.get_ipa_en(word), row[0], row)
				p.start()
				
				thread_pool.add(p)
			#end if
		#end for
		
		thread_pool.finish()
	#end def
	
	def print_table_with_ipa_de(self):
		thread_pool = ThreadPool(self.__print_row_with_ipa)
		rows = self._parse_src()

		self.print_csv_row(['[Original word]', '[IPA]', '[Word type]']) # print header
		for row in rows:
			if len(row) < 1:
				print('Skip incomplete row')
			else:
				p = Processable(lambda word: Wordanalyzer.get_ipa_de(word), row[0], row)
				p.start()
				
				thread_pool.add(p)
			#end if
		#end for
		
		thread_pool.finish()
	#end def
	
	def print_table_with_phonetics_es(self):
		rows = self._parse_src()
		
		self.print_csv_row(['[Original word]', '[Pronounciation]', '[Translation]', '[Word type]']) # print header
		for row in rows:
			if len(row) < 1:
				print('Skip incomplete row')
			else:
				row.insert(1, Wordanalyzer.spanish_to_phonetic_de(row[0]))
				self.print_csv_row(row)
			#end if
		#end for
	#end def
	
	
	def print_conjugation_table(self, tenses):
		thread_pool = ThreadPool(self.__print_conjugation_table)
		rows = self._parse_src()
		
		self.print_csv_row([u'[Infinitive]', u'[yo]', u'[tú]', u'[el/ella/usted]', u'[nosotros, -as]', u'[vosotros, -as]', u'[ellos/ellas/ustedes]', u'[Tense]']) # print header
		for row in rows:
			if len(row) < 1:
				print('Skip incomplete row')
			else:
				for tense in tenses:
					p = Processable(lambda word: Wordanalyzer.get_conjugation_es(word, tense), row.original_word, row)
					p.start()
				
					thread_pool.add(p)
				#end for
			#end if
		#end for
		
		thread_pool.finish()
	#end def
	
	def print_word_array(self):
		rows = self._parse_src()

		self._ostream.write('#!/usr/bin/python\n# -*- coding: utf-8 -*-\nWORD_COLLECTION = set(sorted([\n') # print header
		first_row = True
		for row in rows:
			for word in Translator.resolve_word_list(row.original_word):
				if first_row:
					self._ostream.write('\t  u\'')
					first_row = False
				else:
					self._ostream.write('\t, u\'')
				#end if
				
				self._ostream.write(word.lower())
				self._ostream.write('\'\n')
			#end for
		#end for
		self._ostream.write(']))\n')
	#end def
	
	def print_new_words(self):
		for row in self._parse_src():
			words = set([Translator.normalize_word(word) for word in Translator.resolve_word_list(row.original_word)])
			
			if words <= wordlist_es.WORD_COLLECTION_ES: # words is subset from WORD_COLLECTION
				print('Removed entry %s (Normalized: %s)' % (row.original_word, ', '.join(words)))
			else:
				self.print_csv_row(row)
			#end if
		#end if
	#end def
	
	# prints rows from [newfile] that are not part of [self._src]
	def print_difference(self, newfile):
		total_count = 0
		new_count   = 0
		ignore = [(row.original_word[3:] if row.original_word.startswith('to ') else row.original_word).strip().lower() for row in self._parse_src()]
		
		for row in self._reader.parse(newfile):
			word = row.original_word.strip().lower()
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
	
	def print_commons_marked(self, diff_file):
		rows = self._parse_src()
		marked = Wordanalyzer.get_normalized_words(self._reader.parse(diff_file))
		
		self.print_csv_row( # print header
			['[Original word]', '[Synonyms]', '[Antonyms]', '[Example sentence]', '[Translation]', '[Word type]', '[Level]', '[Tags]']
		)
		for row in rows:
			normalized = Translator.normalize_word(row.original_word)
			
			if normalized in marked:
				if len(row.tags) > 0:
					row.tags = 'marked %s' % row.tags
				else:
					row.tags = 'marked'
				#end if
				
				marked.remove(normalized)
				print('Debug: tags = %s' % row.tags)
			#end if
			
			self.print_csv_row(row)
		#end for
		
		for word in marked:
			self.print_csv_row([word, '', '', '', '', '', '', 'new'])
		#end for
	#end def
	
	def print_without_duplicates(self):
		total_count = 0
		new_count   = 0
		rows = self._parse_src()
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
		normalized  = u'{unknown}' if result['normalized'] == None else result['normalized']
		translation = result['translation']
		wordtype    = u'' if result['wordtype'] == None else result['wordtype']
		
		if translation == None:
			translation = u'{unknown}'
		elif len(translation) > 0 and translation in row.translation:
			translation = u'{duplicate} ' + translation
		#endif

		row.normalized_word = normalized
		row.new_translation = translation
		row.new_wordtype    = wordtype

		self.print_csv_row(row)
	#end def
	
	def __print_enhanced_row_en(self, result, row):
		normalized  = u'{unknown}' if result['normalized'] == None else result['normalized']
		translation = result['translation']
		wordtype    = u'' if result['wordtype'] == None else result['wordtype']
		
		if translation == None:
			translation = u'{unknown}'
		elif len(translation) > 0 and translation in row.translation:
			translation = u'{duplicate} ' + translation
		#endif

		row.normalized_word = normalized
		row.new_translation = translation
		row.new_wordtype    = wordtype

		self.print_csv_row(row)
	#end def
	
	def __print_enhanced_row_de(self, result, row):
		normalized  = u'unknown' if result['normalized'] == None else result['normalized']
		ipa         = u'unknown' if result['ipa'] == None else result['ipa']
		wordtype    = u'' if result['wordtype'] == None else result['wordtype']

		row.normalized_word = normalized
		row.insert(2, ipa)
		row.new_wordtype = wordtype

		self.print_csv_row(row)
	#end def
	
	def __print_row_with_ipa(self, result, row):
		row.insert(1, result if result != None else '') # result = IPA or None
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
		print('\t--add-ipa-en              prints enhanced version of cvs file [input file] including IPA annotations (English)')
		print('\t--add-ipa-de              prints enhanced version of cvs file [input file] including IPA annotations (German)')
		print('\t--add-phonetic-es         prints enhanced version of cvs file [input file] including annotations for pronounciation in German (Spanish)')
		print('\t--conjugate-verbs=[TENSE] prints table with conjugated verbs from cvs file [input file] (Spanish)')
		print('\t--word-array              prints python code with list of words from cvs file [input file]')
		print('\t--check-new               prints words from cvs file [input file] that are not yet part of the vocublary collection (see wordlist_es.py) (Spanish)')
		print('\t--diff-csv                prints words from cvs file [diff file] that are not part of csv file [input file]')
		print('\t--mark-common             prints words from cvs file [input file] and marks those that also exist in [diff file] with a tag')
		print('\t--remove-dupl             prints words from cvs file [input] without duplicate rows')
		print
		print('Column identifiers: [TODO implement]')
		print('\tO - original language (e.g. Spanish)')
		print('\tP - phonetic transcription in IPA')
		print('\tS - synonyms')
		print('\tA - antonyms')
		print('\tE - example sentence')
		print('\tD - definition (alternative to plain translation)')
		print('\tM - meaning/translation (e.g. English)')
		print('\tW - word type (e.g. verb, noun, etc.)')
		print('\tL - Level of relevance (0, 1, ... Smaller number = higher relevance)')
		print('\tT - Tags (Anki)')
		print
		print('\t[[ Standard column identifiers for Spanish: %s ]]' % Wordanalyzer.SPANISH_COLUMN_FORMAT)
		print('\t[[ Standard column identifiers for English: %s ]]' % Wordanalyzer.ENGLISH_COLUMN_FORMAT)
		print('\t[[ Standard column identifiers for German:  %s ]]' % Wordanalyzer.GERMAN_COLUMN_FORMAT)
		print
		print('Conjugation modes:')
		print('\tFORMAS_BASICAS')
		print('\tIMPERATIVO')
		print('\tPRESENTE')
		print('\tPRETERITO_IMPERFECTO')
		print('\tPRETERITO_PLUSCUAMPERFECTO')
		print('\tPRETERITO_INDEFINIDO')
		print('\tFUTURO_IMPERFECTO')
		print('\tCONDICIONAL_SIMPLE')
		print('\tPRESENTE_SUBJUNTIVO')
		print('\tPRETERITO_IMPERFECTO_SUBJUNTIVO')
		
		#analyser = SpanishWordAnalyser(u'bloqueó')
		#print(' - '.join(analyser.syllables()))
		#print(analyser.stressed_syllable())
		
		#trans = Wordanalyzer.get_translation_en('ludicrous')
		#print(trans['normalized'], trans['translation'], trans['wordtype'])
		
		#print Wordanalyzer.get_ipa_en('gullible')
		
		#print(Wordanalyzer.add_accent_es('mojado'))
		
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
		analyzer.set_column_format(Wordanalyzer.SPANISH_COLUMN_FORMAT)
		analyzer.print_word_list('es')
	elif mode == '--wordlist-en':
		analyzer.set_column_format(Wordanalyzer.ENGLISH_COLUMN_FORMAT)
		analyzer.print_word_list('en')
	elif mode == '--wordlist-de':
		analyzer.set_column_format(Wordanalyzer.GERMAN_COLUMN_FORMAT)
		analyzer.print_word_list('de')
	elif mode == '--check-csv-es':
		analyzer.set_column_format(Wordanalyzer.SPANISH_COLUMN_FORMAT)
		analyzer.print_enhanced_table()
	elif mode == '--check-csv-en':
		analyzer.set_column_format(Wordanalyzer.ENGLISH_COLUMN_FORMAT)
		analyzer.print_enhanced_table_en()
	elif mode == '--check-csv-de':
		analyzer.set_column_format(Wordanalyzer.GERMAN_COLUMN_FORMAT)
		analyzer.print_enhanced_table_de()
	elif mode == '--add-ipa-en':
		analyzer.print_table_with_ipa_en()
	elif mode == '--add-ipa-de':
		analyzer.set_column_format(Wordanalyzer.GERMAN_COLUMN_FORMAT)
		analyzer.print_table_with_ipa_de()
	elif mode == '--add-phonetic-es':
		analyzer.set_column_format(Wordanalyzer.SPANISH_COLUMN_FORMAT)
		analyzer.print_table_with_phonetics_es()
	elif mode.startswith('--conjugate-verbs='):
		identifier = mode[18:] # 18 = length of mode string
		tense = getattr(DixOsolaComConjugator, identifier) # retrieve constant with reflection
		
		analyzer.set_column_format(Wordanalyzer.SPANISH_COLUMN_FORMAT)
		analyzer.print_conjugation_table([tense])
	elif mode == '--word-array':
		analyzer.print_word_array()
	elif mode == '--check-new':
		analyzer.print_new_words()
	elif mode == '--diff-csv':
		analyzer.print_difference(diff_file)
	elif mode == '--mark-common': # only works for spanish so far
		analyzer.set_column_format(Wordanalyzer.SPANISH_COLUMN_FORMAT)
		analyzer.print_commons_marked(diff_file)
	elif mode == '--remove-dupl':
		analyzer.print_without_duplicates()
	else:
		print('Invalid mode!')
		exit(1)
	#end if
	
	analyzer.close()
#end def

main(sys.argv)
