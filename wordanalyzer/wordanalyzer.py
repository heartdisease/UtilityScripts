#!/usr/bin/env python3
import re
import sys
import codecs

from utils import CsvReader, ThreadPool, Processable
from arguments import CommandLineParser
from translators import Translator, SpanishdictCom, DixOsolaComDe, DixOsolaComEn, SpanishDictConjugator, DixOsolaComConjugator, DeWiktionaryOrg, EnWiktionaryOrg, OxfordDictionary, DictCc

import wordlist_es
import wordlist_en

### TODO fix verb conjugation bug (yo is always last column)

class SpanishWordAnalyzer(object):

	SPANISH_TO_GERMAN = [ # any occurance of the letter x will not be replaced due to the unpredictability of its pronounciation (h and y need special treatment)
		('ch', 'tsch'), ('cc', 'ks'), ('j', 'ch'), ('ñ', 'nj'), ('ll', 'j'), ('v', 'b'), ('z', 's'),
		('ca', 'ka'), ('cá', 'ká'), ('co', 'ko'), ('có', 'kó'), ('c', 'k'), ('cú', 'kú'),
		('ce', 'se'), ('cé', 'sé'), ('ci', 'si'), ('cí', 'sí'),
		('que', 'ke'), ('qué', 'ké'), ('qui', 'ki'), ('quí', 'kí'),
		('ge', 'che'), ('gé', 'ché'), ('gi', 'chi'), ('gí', 'chí'),
		('gue', 'ge'), ('gué', 'gé'), ('gui', 'gi'), ('guí', 'gí'),
		('güe', 'gue'), ('güé', 'gué'), ('güi', 'gui'), ('güí', 'guí'),
		('e', 'e·'), ('é', 'é·'), ('eú', 'e·ú'),
		('ei', 'e·i'), ('éi', 'é·i'), ('eí', 'e·í'),
		('ie', 'i·e'), ('íe', 'í·e'), ('ié', 'i·é')
	]
	ACCENT_CONVERSION = {
		'a' : 'á', 'e' : 'é', 'i' : 'í', 'o' : 'ó', '' : 'ú'
	}

	def __init__(self, word):
		self._word = word
		self._syllables = None
		self._stressed = -1 # index of stressed syllable
	#end def
	
	def phonetic_de(self):
		#phonetics = ' '.join([Wordanalyzer.add_accent_es(word) for word in re.split(r'[ \/\(\)\[\]¡!¿?;\.:_-]', re.sub(r'(?:[^c])h', '', word.lower())) if len(word) > 0])
		phonetics = re.sub(r'(?:[^c])h', '', self._word.lower())
		words_with_accents = [(self._word, SpanishWordAnalyzer.__add_accent(word)) for self._word in re.findall(r'(?u)\w+', phonetics)]
		
		for word_pair in words_with_accents:
			if word_pair[0] != word_pair[1]:
				phonetics = phonetics.replace(word_pair[0], word_pair[1])
			#end if
		#end for
		
		for conversion in SpanishWordAnalyzer.SPANISH_TO_GERMAN:
			phonetics = phonetics.replace(conversion[0], conversion[1])
		#end for
		
		return re.sub(r'y ', 'i ', re.sub(r'y$', 'i', phonetics)).replace('y', 'j')
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
		return char == 'a' or char == 'e' or char == 'i' or char == 'o' or char == '' \
			or char == 'á' or char == 'é' or char == 'í' or char == 'ó' or char == 'ú'
	#end def
	
	@staticmethod
	def has_accent(char):
		return char == 'á' or char == 'é' or char == 'í' or char == 'ó' or char == 'ú'
	#end def
	
	@staticmethod
	def contains_accent(word):
		for char in word:
			if char == 'á' or char == 'é' or char == 'í' or char == 'ó' or char == 'ú':
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
				if SpanishWordAnalyzer.is_vowel(c):
					if SpanishWordAnalyzer.has_accent(c):
						self._stressed = len(self._syllables)
					#end if
				
					if not SpanishWordAnalyzer.is_vowel(syllable[-1]) or c == 'i' or c == '':
						syllable += c
					else:
						if syllable[-1] == '' or syllable[-2] == 'q':
							syllable += c
						else:
							self._syllables.append(syllable)
							syllable = c
						#end if
					#end if
				else: # character is a consonant
					if SpanishWordAnalyzer.is_vowel(syllable[-1]):
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
			if SpanishWordAnalyzer.contains_accent(syllable):
				self._stressed = len(self._syllables) - 1
			elif len(self._syllables) > 1 and (syllable == 'n' or syllable == 's' or SpanishWordAnalyzer.is_vowel(syllable)):
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
				if last_char == 'n' or last_char == 's':
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
		
		return ''.join(chars)
	#end def
#end class

class Wordanalyzer(object):
	"""Main class."""
	CSV_SEPARATOR = ','
	TEXT_DELIMITER = '"'
	WORD_SPLIT_REGEX = r'[ \t-\.,:;!\?\(\)"\'“”]'
	DICT_CC_MODULE = None
	SPANISH_TO_GERMAN = [ # any occurance of the letter x will not be replaced due to the unpredictability of its pronounciation (h and y need special treatment)
		('ch', 'tsch'), ('cc', 'ks'), ('j', 'ch'), ('ñ', 'nj'), ('ll', 'j'), ('v', 'b'), ('z', 's'),
		('ca', 'ka'), ('cá', 'ká'), ('co', 'ko'), ('có', 'kó'), ('c', 'k'), ('cú', 'kú'),
		('ce', 'se'), ('cé', 'sé'), ('ci', 'si'), ('cí', 'sí'),
		('que', 'ke'), ('qué', 'ké'), ('qui', 'ki'), ('quí', 'kí'),
		('ge', 'che'), ('gé', 'ché'), ('gi', 'chi'), ('gí', 'chí'),
		('gue', 'ge'), ('gué', 'gé'), ('gui', 'gi'), ('guí', 'gí'),
		('güe', 'gue'), ('güé', 'gué'), ('güi', 'gui'), ('güí', 'guí'),
		('e', 'e·'), ('é', 'é·'), ('eú', 'e·ú'),
		('ei', 'e·i'), ('éi', 'é·i'), ('eí', 'e·í'),
		('ie', 'i·e'), ('íe', 'í·e'), ('ié', 'i·é')
	]
	ACCENT_CONVERSION = {
		'a' : 'á', 'e' : 'é', 'i' : 'í', 'o' : 'ó', '' : 'ú'
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
			if char == 'á' or char == 'é' or char == 'í' or char == 'ó' or char == 'ú':
				return True
			#end if
		#end for
		
		return False
	#end def
	
	@staticmethod
	def is_vowel(char):
		return char == 'a' or char == 'e' or char == 'i' or char == 'o' or char == ''
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
				if last_char == 'n' or last_char == 's':
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
		
		return ''.join(chars)
	#end def
	
	@staticmethod
	def spanish_to_phonetic_de(word):
		#phonetics = ' '.join([Wordanalyzer.add_accent_es(word) for word in re.split(r'[ \/\(\)\[\]¡!¿?;\.:_-]', re.sub(r'(?:[^c])h', '', word.lower())) if len(word) > 0])
		phonetics = re.sub(r'(?:[^c])h', '', word.lower())
		words_with_accents = [(word, Wordanalyzer.add_accent_es(word)) for word in re.findall(r'(?u)\w+', phonetics)]
		
		for word_pair in words_with_accents:
			if word_pair[0] != word_pair[1]:
				phonetics = phonetics.replace(word_pair[0], word_pair[1])
			#end if
		#end for
		
		for conversion in Wordanalyzer.SPANISH_TO_GERMAN:
			phonetics = phonetics.replace(conversion[0], conversion[1])
		#end for
		
		return re.sub(r'y ', 'i ', re.sub(r'y$', 'i', phonetics)).replace('y', 'j')
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
	
	def __init__(self, column_format, src, out = None):
		self._src = src
		self._ostream = sys.stdout if out == None else codecs.open(out, 'w', 'utf-8')
		self._column_format = column_format
		
		self._reader = CsvReader(Wordanalyzer.CSV_SEPARATOR, Wordanalyzer.TEXT_DELIMITER, column_format)
	#end def
	
	def close(self):
		if self._ostream != sys.stdout:
			self._ostream.close()
		#end if
	#end def
	
	def _parse_src(self):
		"""TODO decribe what this method does."""
		return self._reader.parse(self._src)
	#end def
	
	def print_csv_row(self, cols):
		"""TODO decribe what this method does.
	
		Keyword arguments:
		cols -- TODO describe what this argument is about
		"""	
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
	
	def print_header_row(self, column_format):
		"""TODO decribe what this method does.
		
		Keyword arguments:
		column_format -- column format as array which is used for the current table
		"""
		header_columns = []
		
		for col in column_format:
			header_columns.append('[%s]' % {
				'O': 'Original word',
				'P': 'IPA',
				'S': 'Synonyms',
				'A': 'Antonyms',
				'E': 'Example sentence',
				'D': 'Definition',
				'M': 'Translation',
				'W': 'Word type',
				'L': 'Level',
				'T': 'Tags',
				# special column identifiers
				'N': 'Normalized word',
				'NM': 'New translation',
				'NW': 'New word type',
				'NP': 'New IPA'
			}[col])
		#end for
	
		self.print_csv_row(header_columns)
	#end def

	def print_word_list(self, lang = None):
		"""Parses text file containing standard text and generates vocabulary list without translations from it.
	
		Keyword arguments:
		src -- path to input file
		out -- output stream
		"""
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
	
	def print_enhanced_table(self):
		"""Parses CSV table already containing at least two columns with Spanish/English word pairs. The third column is optional and usually contains a 'checked' flag, which
		declares whether a word has been already validated. The generated table will contain an extra row for a normalized version of the original Spanish word, an extra row
		for translation (from SpanishDict.com) and an extra column for the word type (e.g. noun).
		
		Keyword arguments:
		src -- path to input CSV file
		out -- output stream
		"""
		thread_pool = ThreadPool(self.__print_enhanced_row)
		rows = self._parse_src()
		
		self.print_header_row(rows[0].get_column_format() if len(rows) > 0 else self._column_format.split('|'))
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
		"""TODO decribe what this method does."""
		thread_pool = ThreadPool(self.__print_enhanced_row_en)
		rows = self._parse_src()
		
		self.print_header_row(rows[0].get_column_format() if len(rows) > 0 else self._column_format.split('|'))
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
		"""TODO decribe what this method does."""
		thread_pool = ThreadPool(self.__print_enhanced_row_de)
		rows = self._parse_src()

		self.print_header_row(rows[0].get_column_format() if len(rows) > 0 else self._column_format.split('|'))
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
		"""TODO decribe what this method does."""
		thread_pool = ThreadPool(self.__print_row_with_ipa)
		rows = self._parse_src()

		self.print_header_row(rows[0].get_column_format() if len(rows) > 0 else self._column_format.split('|'))
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
		"""TODO decribe what this method does."""
		thread_pool = ThreadPool(self.__print_row_with_ipa)
		rows = self._parse_src()

		self.print_header_row(rows[0].get_column_format() if len(rows) > 0 else self._column_format.split('|'))
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
		"""TODO decribe what this method does."""
		rows = self._parse_src()
		
		self.print_header_row(rows[0].get_column_format() if len(rows) > 0 else self._column_format.split('|'))
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
		"""TODO decribe what this method does.
	
		Keyword arguments:
		tenses -- TODO describe what this argument is about
		"""	
		thread_pool = ThreadPool(self.__print_conjugation_table)
		rows = self._parse_src()
		
		self.print_csv_row(['[Infinitive]', '[yo]', '[tú]', '[el/ella/usted]', '[nosotros, -as]', '[vosotros, -as]', '[ellos/ellas/ustedes]', '[Tense]']) # print header
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
	
	def print_word_array(self, lang_code):
		"""TODO decribe what this method does.
	
		Keyword arguments:
		lang_code -- TODO describe what this argument is about
		"""
		rows = self._parse_src()

		self._ostream.write('#!/usr/bin/env python3\n\nWORD_COLLECTION_%s = set(sorted([\n' % lang_code) # print header
		first_row = True
		if lang_code == 'es':
			for row in rows:
				for word in Translator.resolve_word_list(row.original_word):
					word = word.lower() # normalize entry
			
					if first_row:
						self._ostream.write('\t  u\'')
						first_row = False
					else:
						self._ostream.write('\t, u\'')
					#end if
					
					self._ostream.write(word.replace('\'', '\\\''))
					self._ostream.write('\'\n')
				#end for
			#end for
		else:
			for row in rows:
				word = Translator.strip_annotations(row.original_word).lower() # normalize entry
			
				if first_row:
					self._ostream.write('\t  u\'')
					first_row = False
				else:
					self._ostream.write('\t, u\'')
				#end if
			
				self._ostream.write(word.replace('\'', '\\\''))
				self._ostream.write('\'\n')
			#end for
		#end if
		
		self._ostream.write(']))\n')
	#end def
	
	def print_new_words_es(self):
		"""TODO decribe what this method does."""
		for row in self._parse_src():
			words = set([Translator.normalize_word(word) for word in Translator.resolve_word_list(row.original_word)])
			
			if words <= wordlist_es.WORD_COLLECTION_ES: # words is subset from WORD_COLLECTION
				print('Removed entry %s (Normalized: %s)' % (row.original_word, ', '.join(words)))
			else:
				self.print_csv_row(row)
			#end if
		#end if
	#end def
	
	def print_new_words_en(self):
		"""TODO decribe what this method does."""
		for row in self._parse_src():
			word = Translator.strip_annotations(row.original_word).lower() # normalize entry
			
			if word in wordlist_en.WORD_COLLECTION_EN: # words is subset from WORD_COLLECTION
				print('Removed entry %s (Normalized: %s)' % (row.original_word, word))
			else:
				self.print_csv_row(row)
			#end if
		#end if
	#end def
	
	def print_difference(self, newfile):
		"""Prints rows from [newfile] that are not part of [self._src].
	
		Keyword arguments:
		newfile -- path string to the file which should be compared to the other one
		"""
		total_count = 0
		new_count   = 0
		ignore = [row.original_word.strip().lower() for row in self._parse_src()] # [(row.original_word[3:] if row.original_word.startswith('to ') else row.original_word).strip().lower() for row in self._parse_src()]
		
		for row in self._reader.parse(newfile):
			word = row.original_word.strip().lower()
			normalized = word # word[3:] if word.startswith('to ') else word
			
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
		"""TODO decribe what this method does.
	
		Keyword arguments:
		diff_file -- TODO describe what this argument is about
		"""	
		rows = self._parse_src()
		marked = Wordanalyzer.get_normalized_words(self._reader.parse(diff_file))
		
		self.print_header_row(rows[0].get_column_format() if len(rows) > 0 else self._column_format.split('|'))
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
		"""TODO decribe what this method does."""	
		total_count = 0
		new_count   = 0
		rows = self._parse_src()
		checked_words = []
		
		for row in rows:
			word = row[0].strip()
			normalized = word.lower() # word[3:].lower() if word.startswith('to ') else word.lower()
			
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
		"""TODO decribe what this method does.
	
		Keyword arguments:
		result -- TODO describe what this argument is about
		row -- TODO describe what this argument is about
		"""
		row.append('unknown' if result['normalized'] == None else result['normalized'])
		row.append('unknown' if result['translation'] == None else result['translation'])
		row.append('' if result['wordtype'] == None else result['wordtype'])
		
		self.print_csv_row(row)
	#end def
	
	def __print_enhanced_row(self, result, row):
		"""TODO decribe what this method does.
	
		Keyword arguments:
		result -- TODO describe what this argument is about
		row -- TODO describe what this argument is about
		"""
		normalized  = '{unknown}' if result['normalized'] == None else result['normalized']
		translation = result['translation']
		wordtype    = '' if result['wordtype'] == None else result['wordtype']
		
		if translation == None:
			translation = '{unknown}'
		elif len(translation) > 0 and translation in row.translation:
			translation = '{duplicate} ' + translation
		#endif

		row.normalized_word = normalized
		row.new_translation = translation
		row.new_wordtype    = wordtype

		self.print_csv_row(row)
	#end def
	
	def __print_enhanced_row_en(self, result, row):
		"""TODO decribe what this method does.
	
		Keyword arguments:
		result -- TODO describe what this argument is about
		row -- TODO describe what this argument is about
		"""
		normalized  = '{unknown}' if result['normalized'] == None else result['normalized']
		translation = result['translation']
		wordtype    = '' if result['wordtype'] == None else result['wordtype']
		
		if translation == None:
			translation = '{unknown}'
		elif len(translation) > 0 and translation in row.translation:
			translation = '{duplicate} ' + translation
		#endif

		row.normalized_word = normalized
		row.new_translation = translation
		row.new_wordtype    = wordtype

		self.print_csv_row(row)
	#end def
	
	def __print_enhanced_row_de(self, result, row):
		"""TODO decribe what this method does.
	
		Keyword arguments:
		result -- TODO describe what this argument is about
		row -- TODO describe what this argument is about
		"""
		normalized  = '{unknown}' if result['normalized'] == None else result['normalized']
		ipa         = '{unknown}' if result['ipa'] == None else result['ipa']
		wordtype    = '' if result['wordtype'] == None else result['wordtype']

		row.normalized_word = normalized
		row.new_ipa         = ipa
		row.new_wordtype    = wordtype

		self.print_csv_row(row)
	#end def
	
	def __print_row_with_ipa(self, result, row):
		"""TODO decribe what this method does.
	
		Keyword arguments:
		result -- TODO describe what this argument is about
		row -- TODO describe what this argument is about
		"""
		if result != None:
			row.new_ipa = result
		#end if
		
		self.print_csv_row(row)
	#end def
	
	def __print_conjugation_table(self, result, row):
		"""TODO decribe what this method does.
	
		Keyword arguments:
		result -- TODO describe what this argument is about
		row -- TODO describe what this argument is about
		"""
		if result != None:
			row.extend(result)
		#end if
		
		self.print_csv_row(row)
	#end def
#end class

def main(argv):
	arguments = CommandLineParser(argv)
	
	analyzer = Wordanalyzer(arguments.column_format(), arguments.input_file()) if arguments.output_file() == '-' \
		else Wordanalyzer(arguments.column_format(), arguments.input_file(), arguments.output_file())
	
	if arguments.wordlist():
		analyzer.print_word_list(arguments.lang())
	elif arguments.check_csv():
		if arguments.lang() == 'es':
			analyzer.print_enhanced_table()
		elif arguments.lang() == 'en':
			analyzer.print_enhanced_table_en()
		elif arguments.lang() == 'de':
			analyzer.print_enhanced_table_de()
		#end if
	elif arguments.add_ipa():
		if arguments.lang() == 'en':
			analyzer.print_table_with_ipa_en()
		elif arguments.lang() == 'de':
			analyzer.print_table_with_ipa_de()
		#end if
	elif arguments.add_phonetic():
		if arguments.lang() == 'es':
			analyzer.print_table_with_phonetics_es()
		#end if
	elif arguments.conjugate_verbs():
		analyzer.print_conjugation_table([arguments.tense()])
	elif arguments.word_array():
		analyzer.print_word_array(arguments.lang())
	elif arguments.check_new():
		if arguments.lang() == 'es':
			analyzer.print_new_words_es()
		elif arguments.lang() == 'en':
			analyzer.print_new_words_en()
		#end if
	elif arguments.diff_csv():
		analyzer.print_difference(arguments.diff_file())
	elif arguments.mark_common(): # only works for spanish so far
		analyzer.print_commons_marked(arguments.diff_file())
	elif arguments.remove_dupl():
		analyzer.print_without_duplicates()
	else:
		print('No mode was selected!')
		CommandLineParser.print_help()
		exit(1)
	#end if
	
	analyzer.close()
#end def

main(sys.argv)
