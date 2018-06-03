#!/usr/bin/env python3

class CommandLineParser:
	DEFAULT_COLUMN_FORMAT = 'O|M|T'
	SPANISH_COLUMN_FORMAT = 'O|S|A|E|M|W|L|T'
	ENGLISH_COLUMN_FORMAT = 'O|P|E|M|W|T'
	GERMAN_COLUMN_FORMAT  = 'O|M|W|T'
	
	@staticmethod
	def print_help():
		print('Invalid parameter count!')
		print('wordanalyzer.py [options] [input file] [output file]|[[diff file] [output file]]')
		print('Options:')
		print('\t--columns="[COLS]"        specifies column order (see column identifiers)')
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
		print()
		print('Column identifiers:')
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
		print()
		print('\t[[ Standard column identifiers for Spanish: %s ]]' % CommandLineParser.SPANISH_COLUMN_FORMAT)
		print('\t[[ Standard column identifiers for English: %s ]]' % CommandLineParser.ENGLISH_COLUMN_FORMAT)
		print('\t[[ Standard column identifiers for German:  %s ]]' % CommandLineParser.GERMAN_COLUMN_FORMAT)
		print()
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
	#end def
	
	def __init__(self, argv):
		if not 4 <= len(argv) <= 6:
			CommandLineParser.print_help()
			
			#analyser = SpanishWordAnalyzer(u'bloqueó')
			#print(' - '.join(analyser.syllables()))
			#print(analyser.stressed_syllable())
			
			#trans = Wordanalyzer.get_translation_en('ludicrous')
			#print(trans['normalized'], trans['translation'], trans['wordtype'])
			
			#print Wordanalyzer.get_ipa_en('gullible')
			
			#print(Wordanalyzer.add_accent_es('mojado'))
			
			exit(1)
		#end if
		
		self._column_format = None
		self._lang = None
		self._tense = None
		
		self._wordlist = False
		self._check_csv = False
		self._add_ipa = False
		self._add_phonetic = False
		self._conjugate_verbs = False
		self._word_array = False
		self._check_new = False
		self._diff_csv = False
		self._mark_common = False
		self._remove_dupl = False
		
		self._input_file = None
		self._output_file = None
		self._diff_file = None
		
		for i, arg in enumerate(argv):
			if arg.startswith('--columns='):
				self._column_format = arg[10:]
			elif arg == '--wordlist-es':
				if self._column_format == None:
					self._column_format = CommandLineParser.SPANISH_COLUMN_FORMAT
				#end if
				self._wordlist = True
				self._lang = 'es'
			elif arg == '--wordlist-en':
				if self._column_format == None:
					self._column_format = CommandLineParser.ENGLISH_COLUMN_FORMAT
				#end if
				self._wordlist = True
				self._lang = 'en'
			elif arg == '--wordlist-de':
				if self._column_format == None:
					self._column_format = CommandLineParser.GERMAN_COLUMN_FORMAT
				#end if
				self._wordlist = True
				self._lang = 'de'
			elif arg == '--check-csv-es':
				if self._column_format == None:
					self._column_format = CommandLineParser.SPANISH_COLUMN_FORMAT
				#end if
				self._check_csv = True
				self._lang = 'es'
			elif arg == '--check-csv-en':
				if self._column_format == None:
					self._column_format = CommandLineParser.ENGLISH_COLUMN_FORMAT
				#end if
				self._check_csv = True
				self._lang = 'en'
			elif arg == '--check-csv-de':
				if self._column_format == None:
					self._column_format = CommandLineParser.GERMAN_COLUMN_FORMAT
				#end if
				self._check_csv = True
				self._lang = 'de'
			elif arg == '--add-ipa-en':
				if self._column_format == None:
					self._column_format = CommandLineParser.ENGLISH_COLUMN_FORMAT
				#end if
				self._add_ipa = True
				self._lang = 'en'
			elif arg == '--add-ipa-de':
				if self._column_format == None:
					self._column_format = CommandLineParser.GERMAN_COLUMN_FORMAT
				#end if
				self._add_ipa = True
				self._lang = 'de'
			elif arg == '--add-phonetic-es':
				if self._column_format == None:
					self._column_format = CommandLineParser.SPANISH_COLUMN_FORMAT
				#end if
				self._add_phonetic = True
				self._lang = 'es'
			elif arg.startswith('--conjugate-verbs='):
				identifier = arg[18:] # 18 = length of mode string
				self._tense = getattr(DixOsolaComConjugator, identifier) # retrieve constant with reflection
				if self._column_format == None:
					self._column_format = CommandLineParser.SPANISH_COLUMN_FORMAT
				#end if
				self._conjugate_verbs = True
			elif arg == '--word-array-es':
				if self._column_format == None:
					self._column_format = CommandLineParser.DEFAULT_COLUMN_FORMAT
				#end if
				self._word_array = True
				self._lang = 'es'
			elif arg == '--word-array-en':
				if self._column_format == None:
					self._column_format = CommandLineParser.DEFAULT_COLUMN_FORMAT
				#end if
				self._word_array = True
				self._lang = 'en'
			elif arg == '--check-new-es':
				if self._column_format == None:
					self._column_format = CommandLineParser.DEFAULT_COLUMN_FORMAT
				#end if
				self._check_new = True
				self._lang = 'es'
			elif arg == '--check-new-en':
				if self._column_format == None:
					self._column_format = CommandLineParser.DEFAULT_COLUMN_FORMAT
				#end if
				self._check_new = True
				self._lang = 'en'
			elif arg == '--diff-csv':
				if self._column_format == None:
					self._column_format = CommandLineParser.DEFAULT_COLUMN_FORMAT
				#end if
				self._diff_csv = True
			elif arg == '--mark-common': # only works for spanish so far
				if self._column_format == None:
					self._column_format = CommandLineParser.SPANISH_COLUMN_FORMAT
				#end if
				self._mark_common = True
			elif arg == '--remove-dupl':
				if self._column_format == None:
					self._column_format = CommandLineParser.DEFAULT_COLUMN_FORMAT
				#end if
				self._remove_dupl = True
			elif i > 1:				
				if self._input_file == None:
					self._input_file = arg
				elif self._diff_file == None and self._diff_csv or self._mark_common:
					self._diff_file = arg
				else:
					self._output_file = arg
				#end if
			elif i > 0: # arg[0] is the name of the script
				print('Invalid option "%s"!' % arg)
				exit(1)
			#end if
		#end for
		
		## test ##
		#print('Input file: %s' % self.input_file())
		#print('Output file: %s' % self.output_file())
		#print('Diff file: %s' % self.diff_file())
		#print('Columns: %s' % self.column_format())
		#print('Language: %s' % self.lang())
		#exit(0)
	#end def
	
	def lang(self):
		return self._lang
	#end def
	
	def column_format(self):
		return self._column_format
	#end def
	
	def tense(self):
		return self._tense
	#end def
	
	def wordlist(self):
		return self._wordlist
	#end def
	
	def check_csv(self):
		return self._check_csv
	#end def
	
	def add_ipa(self):
		return self._add_ipa
	#end def
	
	def add_phonetic(self):
		return self._add_phonetic
	#end def
	
	def conjugate_verbs(self):
		return self._conjugate_verbs
	#end def
	
	def word_array(self):
		return self._word_array
	#end def
	
	def check_new(self):
		return self._check_new
	#end def
	
	def diff_csv(self):
		return self._diff_csv
	#end def
	
	def mark_common(self):
		return self._mark_common
	#end def
	
	def remove_dupl(self):
		return self._remove_dupl
	#end def
	
	def input_file(self):
		return self._input_file
	#end def
	
	def output_file(self):
		return self._output_file
	#end def
	
	def diff_file(self):
		return self._diff_file
	#end def
#end class
