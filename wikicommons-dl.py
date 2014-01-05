#!/usr/bin/python3
import re
import os.path
import urllib.request
import urllib.parse

kanji1 = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '上', '下', '左', '右', '中', '大', '小', '月', '日', '年', '早', '木', '林', '山', '川', '土', '空', '田', '天', '生', '花', '草', '虫', '犬', '人', '名', '女', '男', '子', '目', '耳', '口', '手', '足', '見', '音', '力', '気', '円', '入', '出', '立', '休', '先', '夕', '本', '文', '字', '学', '校', '村', '町', '森', '正', '水', '火', '玉', '王', '石', '竹', '糸', '貝', '車', '金', '雨', '赤', '青', '白']

def save_url(url, path):
	response = None

	try:
		response = urllib.request.urlopen(url)

		with open(path, 'wb') as f:
			f.write(response.read())
		#end with
	except urllib.error.HTTPError as e:
		pass
		#print ("[!] Error code: ",  e.code)
	except urllib.error.URLError as e:
		pass
		#print ("[!] Reason: ",  e.reason)
	#end try
#end def

def generic_to_imageurl(generic_url):
	response = None

	try:
		response = urllib.request.urlopen(generic_url)
		html = str(response.read())
	except urllib.error.HTTPError as e:
		pass
		#print ("[!] Error code: ",  e.code)
	except urllib.error.URLError as e:
		pass
		#print ("[!] Reason: ",  e.reason)
	#end try
	
	if response != None and response.getcode() == 200:
		match = re.search(r'<div class="fullMedia"><a href="([^"]+)', str(html))
		image_url = match.group(1)
		
		if image_url.startswith('//'):
			return 'http:' + image_url
		else:
			return image_url
		#end if
	#end if
	
	return None
#end def

def fetch_hiragana():
	for code in range(12354, 12435):
		encoded_char = urllib.parse.quote(chr(code))
		image_url = generic_to_imageurl('http://commons.wikimedia.org/wiki/File:Hiragana_' + encoded_char + '_stroke_order_animation.gif')
		
		if image_url != None:
			filename = urllib.parse.unquote(image_url[image_url.rfind('/') + 1:])
			save_path = '/home/heartdisease/Documents/hiragana_animated/' + filename
			
			print('Downloading ' + image_url + ' to ' + save_path + ' ...')
			save_url(image_url, save_path)
	#end for
#end def

def fetch_katakana():
	for code in range(12449, 12531):
		encoded_char = urllib.parse.quote(chr(code))
		image_url = generic_to_imageurl('http://commons.wikimedia.org/wiki/File:Katakana_' + encoded_char + '_stroke_order_animation.gif')
		
		if image_url != None:
			filename = urllib.parse.unquote(image_url[image_url.rfind('/') + 1:])
			save_path = '/home/heartdisease/Documents/katakana_animated/' + filename
			
			print('Downloading ' + image_url + ' to ' + save_path + ' ...')
			save_url(image_url, save_path)
	#end for
#end def

def save_image(image_url, imgtype):
	filename = urllib.parse.unquote(image_url[image_url.rfind('/') + 1:])
	save_path = '/home/heartdisease/Documents/kanji_' + imgtype + '/' + filename
	
	print('Downloading ' + image_url + ' to ' + save_path + ' ...')
	if os.path.exists(save_path):
		print('File ' + save_path + ' already exists.')
	else:
		save_url(image_url, save_path)
	#end if
#end def

def fetch_kanji(kanjis, imgtype, filetype):
	for kanji in kanjis:	
		encoded_char = urllib.parse.quote(kanji)
		image_url = generic_to_imageurl('http://commons.wikimedia.org/wiki/File:' + encoded_char + '-j' + imgtype + '.' + filetype) # check for japan-specific file
		
		if image_url != None:
			print('Found Japan-specific image for kanji ' + kanji + '!')
			save_image(image_url, imgtype)
		else:
			image_url = generic_to_imageurl('http://commons.wikimedia.org/wiki/File:' + encoded_char + '-' + imgtype + '.' + filetype)
			
			if image_url != None:
				save_image(image_url, imgtype)
			else:
				print('Cannot download image for kanji ' + kanji)
			#end if
		#end if
	#end for
#end def

#fetch_hiragana()
#fetch_katakana()
fetch_kanji(kanji1, 'red', 'png') # 'order', 'red'
