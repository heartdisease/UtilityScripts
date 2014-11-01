#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import re
import sys

import utils
import translators
import wordlist_es
import wordlist_en

### TODO fix verb conjugation bug (yo is always last column)

class SpanishWordAnalyzer(object):

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
		words_with_accents = [(self._word, SpanishWordAnalyzer.__add_accent(word)) for self._word in re.findall(r'(?u)\w+', phonetics)]
		
		for word_pair in words_with_accents:
			if word_pair[0] != word_pair[1]:
				phonetics = phonetics.replace(word_pair[0], word_pair[1])
			#end if
		#end for
		
		for conversion in SpanishWordAnalyzer.SPANISH_TO_GERMAN:
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
				if SpanishWordAnalyzer.is_vowel(c):
					if SpanishWordAnalyzer.has_accent(c):
						self._stressed = len(self._syllables)
					#end if
				
					if not SpanishWordAnalyzer.is_vowel(syllable[-1]) or c == u'i' or c == u'u':
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
			elif len(self._syllables) > 1 and (syllable == u'n' or syllable == u's' or SpanishWordAnalyzer.is_vowel(syllable)):
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
	ENGLISH_COLUMN_FORMAT = 'O|P|E|M|W|T'
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
	
	def print_word_array(self, lang_code):
		rows = self._parse_src()

		self._ostream.write('#!/usr/bin/python\n# -*- coding: utf-8 -*-\nWORD_COLLECTION_%s = set(sorted([\n' % lang_code) # print header
		first_row = True
		if lang_code == 'ES':
			for row in rows:
				for word in Translator.resolve_word_list(row.original_word):
					word = Translator.strip_annotations(word).lower() # normalize entry
			
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
		for row in self._parse_src():
			word = Translator.strip_annotations(row.original_word).lower() # normalize entry
			
			if word in wordlist_en.WORD_COLLECTION_EN: # words is subset from WORD_COLLECTION
				print('Removed entry %s (Normalized: %s)' % (row.original_word, word))
			else:
				self.print_csv_row(row)
			#end if
		#end if
	#end def
	
	# prints rows from [newfile] that are not part of [self._src]
	def print_difference(self, newfile):
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
		normalized  = u'{unknown}' if result['normalized'] == None else result['normalized']
		ipa         = u'{unknown}' if result['ipa'] == None else result['ipa']
		wordtype    = u'' if result['wordtype'] == None else result['wordtype']

		row.normalized_word = normalized
		row.ipa             = ipa
		row.new_wordtype    = wordtype

		self.print_csv_row(row)
	#end def
	
	def __print_row_with_ipa(self, result, row):
		if result != None:
			row.ipa = result
		#end if
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
		print('\t--word-array-es           prints python code with list of words from cvs file [input file] (Spanish)')
		print('\t--word-array-en           prints python code with list of words from cvs file [input file] (English)')
		print('\t--check-new-es            prints words from cvs file [input file] that are not yet part of the vocabulary collection (see wordlist_es.py) (Spanish)')
		print('\t--check-new-en            prints words from cvs file [input file] that are not yet part of the vocabulary collection (see wordlist_en.py) (English)')
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
		
		#analyser = SpanishWordAnalyzer(u'bloqueó')
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
		analyzer.set_column_format(Wordanalyzer.ENGLISH_COLUMN_FORMAT)
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
	elif mode == '--word-array-es':
		analyzer.print_word_array('ES')
	elif mode == '--word-array-en':
		analyzer.print_word_array('EN')
	elif mode == '--check-new-es':
		analyzer.print_new_words_es()
	elif mode == '--check-new-en':
		analyzer.print_new_words_en()
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
