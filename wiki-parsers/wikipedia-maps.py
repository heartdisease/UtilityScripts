#!/usr/bin/python3
import urllib
import json

from pyquery import PyQuery as pq

def download_maps(prefectures):
	for prefecture in prefectures:
		d = pq(url=urllib.parse.urlparse('https://de.wikipedia.org/wiki/Datei:' + prefecture + '_in_Japan.svg').geturl())
		anchor = d('a[href$="Japan.svg.png"]:first')

		url = anchor.attr('href')
		if url:
			full_url = 'https:' + url
			file_name = url[url.rfind('/') + 1:]
			print('Download from URL: "' + full_url + '" to "./' + file_name + '"')
			urllib.request.urlretrieve(full_url, file_name)
		else:
			print('Cannot find URL for ' + prefecture)
		#end if
	#end for
#end def

download_maps([
	'Hokkaido',
	'Akita',
	'Aomori',
	'Fukushima',
	'Iwate',
	'Miyagi',
	'Yamagata',
	'Chiba',
	'Gunma',
	'Ibaraki',
	'Kanagawa',
	'Saitama',
	'Tochigi',
	'Tokyo',
	'Hyogo',
	'Kyoto',
	'Mie',
	'Nara',
	'Osaka',
	'Shiga',
	'Wakayama',
	'Hiroshima',
	'Okayama',
	'Shimane',
	'Tottori',
	'Yamaguchi',
	'Aichi',
	'Fukui',
	'Gifu',
	'Ishikawa',
	'Nagano',
	'Niigata',
	'Shizuoka',
	'Toyama',
	'Yamanashi',
	'Fukuoka',
	'Kagoshima',
	'Kumamoto',
	'Miyazaki',
	'Nagasaki',
	'Oita',
	'Saga',
	'Okinawa',
	'Ehime',
	'Kagawa',
	'Kochi',
	'Tokushima'
])
