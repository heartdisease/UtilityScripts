#!/usr/bin/env python3
import re
import urllib.parse
import urllib.request

from pyquery import PyQuery as pq
from lxml import etree

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
	WORD_PATTERN = re.compile(r'(?:(el/la|el|la) )?(\w[\w\(\)/ ]+)(?:, -(\w+))?', re.UNICODE)
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
		sections = Translator.strip_annotations(string).split(';')
		
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
	
	@staticmethod
	def strip_annotations(string):
		return Translator.ANNOTATION_PATTERN.sub('', string)
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
		url = self._url_template % urllib.parse.quote(get_data.encode(self._encoding))
		content = None
		
		try:
			response = urllib.request.urlopen(urllib.request.Request(url, headers=self._headers))
			content  = response.read()
			return str(content).replace('\n', ' ') #unicode(content, self._encoding).replace('\n', ' ')
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
		Translator.__init__(self, 'http://www.spanishdict.com/translate/%s')
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
			
			if partofspeach == None or not ' ' in partofspeach:
				wordtype = partofspeach
			else:				
				if 'sustantivo' in partofspeach:
					wordtype = 'sustantivo'
				elif 'verbo' in partofspeach:
					wordtype = 'verbo'
				elif 'adverbio' in partofspeach:
					wordtype = 'adverbio'
				elif 'adjetivo' in partofspeach:
					wordtype = 'adjetivo'
				else:
					wordtype = partofspeach.split(' ')[0]
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
			
			if wordtype == 'sustantivo' or wordtype == 'noun':
				if partofspeach == None: # special case where gender declaration is missing
					normalized = '?? ' + normalized
				else:
					is_masculine = 'masculine' in partofspeach or 'masculino' in partofspeach
					is_feminine  = 'feminine' in partofspeach or 'femenino' in partofspeach
				
					if is_masculine and is_feminine:
						normalized = 'el/la ' + normalized
					elif is_masculine:
						normalized = 'el ' + normalized
					elif is_feminine:
						# use article 'el' if noun starts with a-sound (still buggy!)
						if normalized.startswith('a') or normalized.startswith('ha'):
							normalized = 'el ' + normalized + ' [fem.]'
						else:
							normalized = 'la ' + normalized
						#end if
					else: # special case where gender declaration is missing (add manually)
						normalized = '?? ' + normalized
					#end if
				#end if
			#end if
	
			if translation != None:
				translation = translation.replace(';', ',').replace(' , ', ', ')
			#end if
		else:
			print('Invalid response for "' + word + '".')
		#end if
		
		# translate english word type to spanish due to site inconsistencies
		if wordtype == 'noun':
			wordtype = 'sustantivo'
		elif wordtype == 'verb':
			wordtype = 'verbo'
		elif wordtype == 'adjective':
			wordtype = 'adjetivo'
		elif wordtype == 'adverb':
			wordtype = 'adverbio'
		elif wordtype == 'pronoun':
			wordtype = 'pronombre'
		#endif
	
		return { 'normalized' : normalized if normalized != None else word, 'translation' : translation, 'wordtype' : wordtype }
	#end def
#end class

class DixOsolaComDe(Translator):

	def __init__(self):
		Translator.__init__(self, 'http://dix.osola.com/index.php?search=%s', 'iso-8859-1')
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
						translation += ', ' + german_row
					#end if
				else:
					break # found all translations
				#end if
			#end for
		else:
			print('Invalid response for "' + word + '".')
		#end if
	
		return { 'normalized' : normalized if normalized != None else word, 'translation' : translation, 'wordtype' : wordtype }
	#end def
#end class

class DixOsolaComEn(Translator):

	def __init__(self):
		Translator.__init__(self, 'http://www.diccionario-ingles.info/index.php?search=%s', 'iso-8859-1')
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
						translation += ', ' + english_row
					#end if
				else:
					break # found all translations
				#end if
			#end for
		else:
			print('Invalid response for "' + word + '".')
		#end if
	
		return { 'normalized' : normalized if normalized != None else word, 'translation' : translation, 'wordtype' : wordtype }
	#end def
#end class

class SpanishDictConjugator(Translator):

	def __init__(self):
		Translator.__init__(self, 'http://www.spanishdict.com/conjugate/%s')
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
		Translator.__init__(self, 'http://dix.osola.com/v.php?search=%s', 'iso-8859-1')
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
				print('Cannot find conjugations for verb "%s".' % verb)
			#end if
		#end if
		
		return None
	#end def
#end class

class DeWiktionaryOrg(Translator):

	def __init__(self):
		Translator.__init__(self, 'http://de.wiktionary.org/wiki/%s')
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
		Translator.__init__(self, 'http://en.wiktionary.org/wiki/%s')
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
		Translator.__init__(self, 'http://www.oxforddictionaries.com/definition/english/%s')
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
		Translator.__init__(self, 'http://www.dict.cc/?s=%s')
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
