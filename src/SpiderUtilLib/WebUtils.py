#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Copyright 2021 Wei WANG of Ezy App Co. Pty Ltd, Australia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
# WebUtils
This module contains a few utilities that can help you crawling the web .

## Update History
* Version 1.0.0: [20210906]
	* Initial version
"""

import os
import itertools
import string
import sys
import hashlib
import random

import requests
from requests.sessions import CaseInsensitiveDict

# from .FileUtils import FileUtils
from FileUtils import FileUtils

class WebUtils:
	__user_agent_list = [
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
		'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
		'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
	]

	BASE64MAP_dict = {
		'default': tuple(
			itertools.chain(string.ascii_uppercase, string.ascii_lowercase, string.digits, ['+', '/', '='])),
		'RFC3501': tuple(
			itertools.chain(string.ascii_uppercase, string.ascii_lowercase, string.digits, ['+', ',', '='])),
		'RFC4648': tuple(
			itertools.chain(string.ascii_uppercase, string.ascii_lowercase, string.digits, ['-', '_', '='])),
	}

	@classmethod
	def get_remote_file(cls, url: str, size_only: bool = False,
						path: str = '.', filename='', stream_mode=True,
						silent_mode=False) -> CaseInsensitiveDict():
		"""
		Download file from any given url

		:param cls: Current Class
		:param url: The url where your file is remotely
		:param size_only: Only get the size of file without retrieve the file for real, default is your current directory
		:param path: Where you want to store the downloaded file
		:param filename: The name of your downloaded file, if set to empty,  it will try to get the file name from the
						end of the url (e.g. http://www.abc.xyz/file.pdf will means your file name will be file.pdf).
		:param stream_mode: Download the file in as a stream, which is friendlier for large file
		:param silent_mode: Show no visible information
		:return: A caseInsensitiveDict of all the request response information, plus extra information on the location of
				the downloaded file {'file': filename, 'dir': path, 'fullpath':full_path, } etc if download is successful;
				or { 'download_success': False, 'status_code': request.status_code, 'error_message': What is wrong message}
				to tell you download failed and help you to identify what is wrong
		"""

		__file_url = url
		__params = {}

		def get_url_params(url):
			url_parts = url.split('?')
			if len(url_parts)==2:  # Url carries Parameters
				file_url = url_parts[0]
				param_str = url_parts[-1]

		def get_unique_filename(path: str = '.', extension='.tmp'):
			count = 0
			while True:
				filename = 'WUDL{}.{}'.format(str(count).zfill(4), extension.lstrip('.'))
				if not os.path.exists(os.path.join(path, filename)):
					break
				count += 1
			return filename

		headers = {
			"User-Agent": random.choice(cls.__user_agent_list),
		}

		try:
			head_response = requests.head(url, headers=headers)
			file_info = head_response.headers.copy()
			head_response.raise_for_status()
		except Exception as e:
			print('Failed to acquire information remotely with error of {}'.format(e))
			file_info['status_code'] = head_response.status_code
			file_info['error_message'] = e
			file_info['download_success'] = False

		if not size_only and not file_info.get('download_success') == False:
			if not os.path.exists(path):
				os.makedirs(path)
			if not filename:
				filename = FileUtils.file_name_cleanup(url.split('/')[-1])
				if not filename:
					filename = get_unique_filename(path)

				while True:
					full_path = os.path.join(path, filename)
					if not os.path.exists(full_path):
						break
					else:
						if silent_mode:
							filename = get_unique_filename(path, extension=url.split('/')[-1].rsplit('.')[-1])
						else:
							choice = input(
								'File "{}" is already existed at [{}], do you want to overwrite (y/n)? '.format(
									filename, os.path.abspath(path)))
							if choice.lower().startswith('y'):
								break
							else:
								filename = input('Please enter a new name for your file (Enter for a random one): ')
								if not filename:
									filename = get_unique_filename(path, extension=url.split('/')[-1].rsplit('.')[-1])
								print('Downloaded file name will be named {}'.format(filename))

				try:
					if not silent_mode:
						print('Downloading {} [{:.2f}Mb]...'.format(filename,
																	int(file_info['content-length']) / 1024 / 1024),
							  end='')
					if not stream_mode:
						data = requests.get(url, headers=headers)
						dl_status = data.status_code
						data.raise_for_status()
						with open(full_path, mode='wb') as file_writer:
							file_info['download_length'] = str(len(data.content))
							file_writer.write(data.content)
					else:
						with requests.get(url, headers=headers, stream=True) as data_stream:
							file_length = int(data_stream.headers["Content-length"])
							dl_status = data_stream.status_code
							data_stream.raise_for_status()
							chunk_size = 65536
							dl_size = 0
							with open(full_path, 'wb') as stream_writer:
								for chunk in data_stream.iter_content(chunk_size=chunk_size):
									stream_writer.write(chunk)
									dl_size += len(chunk)
									if not silent_mode:
										print('\rDownloading {} [{:.2f}Mb]: {:.1f}%'.format(filename,
																							int(file_length) / 1024 / 1024,
																							dl_size * 100 / file_length),
											  end='')
							file_info['download_length'] = str(dl_size)
							if not silent_mode:
								print('\rDownloading {} [{:.2f}Mb]...'.format(filename,
																			  int(file_info[
																					  'content-length']) / 1024 / 1024),
									  end='')

					file_info['status_code'] = dl_status
					file_info['download_success'] = True
					file_info['file'] = filename
					file_info['dir'] = os.path.abspath(path)
					file_info['fullpath'] = os.path.abspath(full_path)
					if not silent_mode:
						print('Accomplished.')
				except Exception as e:
					print(e)
					if os.path.exists(full_path):
						os.remove(full_path)
					file_info['status_code'] = dl_status
					file_info['error_message'] = e
					file_info['download_success'] = False

		return file_info

	@classmethod
	def md5_hash(cls, origin, salt_prefix, salt_suffix, encoding: str = 'utf-8',
				 double_md5: bool = False) -> str:
		"""
		Use MD5 various hash for original text or bytes with salts

		:param cls: Current Class
		:param origin: The text that need to get MD5 hashed, str or bytes are acceptable
		:param salt_prefix: The prefix Salt for the hash, str or bytes are acceptable
		:param salt_suffix:The suffix Salt for the hash, str or bytes are acceptable
		:param encoding: The encoding of the str, as MD5 hash only takes bytes, different encoding matteres
		:param double_md5: Use double_md5 algorithm if set to true:
		:return: The MD5 hash digest in str format
		"""
		if double_md5:
			origin = cls.md5_hash(origin, salt_prefix=salt_prefix, salt_suffix=salt_suffix, encoding=encoding,
								  double_md5=False)
		md5_hashed_obj = hashlib.md5(salt_prefix.encode(encoding) if type(salt_prefix) is str else salt_prefix)
		md5_hashed_obj.update(origin.encode(encoding) if type(origin) is str else origin)
		md5_hashed_obj.update(salt_suffix.encode(encoding) if type(salt_suffix) is str else salt_suffix)

		return md5_hashed_obj.hexdigest()

	@classmethod
	def base64_encoder(cls, text, encoding: str = 'utf-8', base64_encoding_map='default') -> str:
		"""
		Base64 Encoder, can take either str (of above encoding) or bytes as input and output according to
		base64_encoding_map standard.

		:param text: The text (or bytes) to be encoded
		:param encoding: The text's original encoding if text is a str
		:param base64_encoding_map: Can choose between default standard, RFC3501 standard, or RFC4648 standard.
		:return: The base64 encoded text or bytes
		"""
		BASE64MAP = cls.BASE64MAP_dict.get(base64_encoding_map)
		if not BASE64MAP:
			raise ValueError('Invalid base64_encoding_map: only ["default", "RFC3501", "RFC4648"] are allowed')
		text_encoded = text.encode(encoding) if type(text) is str else text
		str_encoded = ''
		text_in_block_of_three = (
			''.join([bin(character).lstrip('0b').zfill(8) for character in text_encoded[i: i + 3]])
			for i in range(0, len(text_encoded), 3))
		text_in_base64_block = (['00' + block[index:index + 6] for index in range(0, 24, 6)] for block in
								text_in_block_of_three)
		for b64block in text_in_base64_block:
			for character in b64block:
				c_length = len(character)

				if c_length == 6:
					character += '00'
				elif c_length == 4:
					character += '0000'
				elif c_length == 2:
					character += '01' + '0' * 6

				characterToAppend = BASE64MAP[int(character, base=2)]
				if characterToAppend == '=' and base64_encoding_map == 'RFC3501':
					characterToAppend = ''
				str_encoded += characterToAppend

		return str_encoded

	@classmethod
	def base64_decoder(cls, encrypted_text, encoding: str = 'utf-8', base64_encoding_map='default') -> str:
		"""
		Base64 Decoder, can take either str (of above encoding) or bytes of base64_encoding_map standard as input,
		and output the decoded original text

		:param encrypted_text: The text (or bytes) to be decoded using based64 algorithm
		:param encoding: The original encoding for the returned result
		:param base64_encoding_map: Can choose between default standard, RFC3501 standard, or RFC4648 standard.
		:return: The decoded original text (of above encoding)
		"""
		BASE64MAP = cls.BASE64MAP_dict.get(base64_encoding_map)
		if not BASE64MAP:
			raise ValueError('Invalid base64_encoding_map: only ["default", "RFC3501", "RFC4648"] are allowed')

		if base64_encoding_map == 'RFC3501' or base64_encoding_map == 'RFC4648':
			while not len(encrypted_text) % 4 == 0:
				encrypted_text += '=' if type(encrypted_text) is str else b'='

		encrypted_text = encrypted_text.rstrip().decode(encoding) if type(encrypted_text) is bytes else encrypted_text

		b64blocks = (
			''.join([bin(BASE64MAP.index(character))[2:].zfill(6)[-6:] for character in encrypted_text[i: i + 4]])
			for i in range(0, len(encrypted_text), 4))

		decoded_text_block = [int(block[i: i + 8], base=2).to_bytes(1, sys.byteorder) for block in b64blocks for i in
							  range(0, 24, 8) if int(block[i:i + 8], base=2)]

		decoded_text_bytes = b''.join(decoded_text_block)

		decoded_text_str = decoded_text_bytes.decode(encoding)

		return decoded_text_str


if __name__ == '__main__':
	print(__doc__)
	# print(WebUtils.md5_hash(b'\xe6\xb1\xaa\xe5\xb7\x8d'))  # 91f3e094c26c06f25e00ae1ae2b8038d
	# print(WebUtils.md5_hash(123))  # 91f3e094c26c06f25e00ae1ae2b8038d

	# result = WebUtils.get_remote_file('https://www.win-rar.com/fileadmin/winrar-versions/winrar/winrar-x64-602.exe',
	# 								  size_only=False, stream_mode=True, silent_mode=False)
	# print(result)
	# input('Enter to remove downloaded file')
	# os.remove(result.get('fullpath'))

	# print(WebUtils.base64_encoder('Python❤'))
	# print(WebUtils.base64_decoder('UHl0aG9u4p2k'))
	# print(WebUtils.base64_encoder('I ❤ Python'.encode('utf-8')))  # Normally take str as input, but bytes also works
	# print(WebUtils.base64_decoder(b'SSDinaQgUHl0aG9u'))  # Can also decode bytes directly

	# print(
	# 	WebUtils.base64_encoder('A', base64_encoding_map='RFC3501'))  # RFC3501 has no padding
	# print(WebUtils.base64_decoder('QQ',
	# 							  base64_encoding_map='RFC3501'))   # RFC3501 has no padding
	# print(
	# 	WebUtils.base64_encoder('A'))  # default has padding
	# print(WebUtils.base64_decoder('QQ=='))   # default has padding
	# print(WebUtils.BASE64MAP_dict)


	pass
