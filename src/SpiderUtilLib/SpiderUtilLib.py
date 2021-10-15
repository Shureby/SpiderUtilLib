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
# FileUtils
This module contains a few utilities that can help you
process local files easily.

## Update History
* Version 1.0.0: [20210906]
	* Initial version
* Version 1.0.5: [20210908]
	* Added is_folder_empty method
	* Modified the logic of text_file_cleanup method to handle case of empty value for search_for parameter
"""
import base64

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
import shutil
import re
import functools
from operator import methodcaller, sub
import codecs

import requests
from requests.sessions import CaseInsensitiveDict


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
			if len(url_parts) == 2:  # Url carries Parameters
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
	def base64_decoder(cls, encrypted_text, decode_output_as=str, encoding: str = 'utf-8',
					   base64_encoding_map='default'):
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

		decoded_text = decoded_text_bytes.decode(encoding) if decode_output_as == str else decoded_text_bytes

		return decoded_text


class FileUtils:
	@classmethod
	def is_folder_empty(cls, dir_name: str) -> bool:
		"""
		Test to see if a given folder is empty, it throws an exception if the folder is nonexistent
		:param dir_name: The folder you want to test for
		:return: True if given dir_name exists and is empty,
				False if given dir_name exists and is not empty
		"""
		if os.path.exists(dir_name) and os.path.isdir(dir_name):
			return not os.listdir(dir_name)
		else:
			raise Exception(f"Directory {dir_name} doesn't exist")

	@classmethod
	def file_name_cleanup(cls, name: str, remove_left_whitespace: bool = True,
						  remove_right_whitespace: bool = True) -> str:
		"""
		Clean up the illegal ASCII characters in the name string and return a new string
		that keeps the same format using legal unicode characters.
		:param name: a possible filename
		:param remove_left_whitespace: remove the white space from the left of above given name
		:param remove_right_whitespace: remove the white space from the right of above given name
		:return: a cleaned filename with will accepted by the OS filesystem
		"""
		new_name = name
		new_name = new_name.replace('|', '-')
		new_name = new_name.replace('?', '？')
		new_name = new_name.replace('*', '×')
		new_name = new_name.replace('/', '╱')
		new_name = new_name.replace('\\', '╲')
		new_name = new_name.replace('\n', '_')
		new_name = new_name.replace('\r', '_')
		new_name = new_name.replace(':', '：')
		new_name = new_name.replace('>', '〉')
		new_name = new_name.replace('<', '〈')
		new_name = new_name.replace('&nbsp;', ' ')
		replace_by = "“”"
		count = 0
		while new_name.find('"') > -1:
			new_name = new_name.replace('"', replace_by[count % 2], 1)
			count += 1
		if remove_left_whitespace:
			new_name = new_name.lstrip()
		if remove_right_whitespace:
			new_name = new_name.rstrip()

		return new_name

	@classmethod
	def remove_duplicates_orderly(cls, list_with_duplicates: list, preserve_first_encounter: bool = True,
								  preserve_original_list: bool = False) -> list:
		"""
		Remove duplicates from a list without change it original order
		:param list_with_duplicates: a list with duplicates
		:param preserve_first_encounter: True - when remove duplicates, keep the first encountered duplicate element; or
										False - when remove duplicates, keep the last encountered duplicate element.
		:param preserve_original_list: 	True - list_with_duplicates will remain unchanged after the execution of the function
										False - list_with_duplicates will be a duplicate-free list itself.
		:return: A new list with the duplicates removed without breaking its order

		"""
		list_set = set(list_with_duplicates)
		list_new = list_with_duplicates.copy() if preserve_original_list else list_with_duplicates
		if len(list_new) == len(list_set):  # No extra
			return list_new
		if preserve_first_encounter:
			list_new.reverse()
		for index in range(len(list_new) - 1, -1, -1):
			item = list_new[index]
			if item in list_set:
				list_set.remove(item)
			else:
				list_new.pop(index)
		if preserve_first_encounter:
			list_new.reverse()
		return list_new

	@classmethod
	def search_file_by_name(cls, name: str, root_path: str, return_path_only: bool = True,
							return_all_files: bool = False,
							allow_partial_name: bool = False):
		"""
		Search for file with  by walk through root_path and its sub directories, return
		the absolute path of the file if exists.
		:param name: File name you want to search for
		:param root_path: Search file name inside this folder and its sub folders
		:param return_path_only:  Return path include filename if set to False, return only
				path proceeds the filename if set to True
		:param return_all_files: If True, return a list of all founded files in a list
		:param allow_partial_name: If True, allow partial file name match, AND THIS WILL
				FORCE return_path_only TO BE SET TO False
		:return: return first found file's absolute path or None if not found, when return_all_files is set to False;
				otherwise, return a list of all found files
		"""

		# if allow_partial_name and return_path_only:
		# 	import warnings
		# 	warnings.warn(
		# 		'{}.{} - Due to "allow_partial_name" is set to True, "return_path_only" has been set to False '.format(
		# 			__name__, cls.search_file_by_name.__name__), RuntimeWarning)
		result_list = []
		for dirpath, dirnames, filenames in os.walk(root_path):
			for filename in filenames:
				if (name == filename and (not allow_partial_name)) or (
						(filename.find(name) != -1) and allow_partial_name):
					if return_path_only and not allow_partial_name:
						absolute_path = dirpath
					else:
						absolute_path = os.path.join(dirpath, filename)
					if not return_all_files:
						return absolute_path
					else:
						result_list.append(absolute_path)
		if result_list:
			return result_list
		return None

	@classmethod
	def text_file_cleanup(cls, file: str, search_for: str = '', replace_as: str = '', encoding: str = 'utf-8',
						  search_using_regex: bool = False,
						  preserve_original_file: bool = False, auto_replace_nbsp=True) -> bool:
		"""
		Search text inside file using pure_text or regular expression (RE) and replace it.
		:param file: File with its path
		:param search_for: The text you are searching for
		:param replace_as: The text you are replacing as
		:param encoding: The encoding of the text file
		:param search_using_regex: 	True - The search_for parameter is a RE, or
									False - The search_for parameters is a str
		:param preserve_original_file: 	True - A extra file.old file will be created after replacement completed
										False - The original file will be cleaned and gone for good
		:param auto_replace_nbsp: 	True - Find all &nbsp; and change it to space automatically,
									False - Ignore &nbsp;
		:return: return True if complete replacement successfully, or False if failed
		"""

		if search_for == '' and not auto_replace_nbsp:
			return True
		try:
			shutil.move(file, file + '.origin')
			with open(file + '.origin', mode='r', encoding=encoding) as file_reader, open(file, mode='w',
																						  encoding=encoding) as file_writer:
				for line in file_reader:
					if auto_replace_nbsp:
						line.replace('&nbsp;', ' ')
					if search_for:
						if not search_using_regex:
							file_writer.write(line.replace(search_for, replace_as))
						else:
							search_for_re = re.compile(search_for)
							file_writer.write(re.sub(search_for_re, replace_as, line))
			if not preserve_original_file:
				os.remove(file + '.origin')
		except Exception as e:
			print(e)
			return False
		return True

	@classmethod
	def reverse_file_reader(cls, file_object: object,
							lines_separator: str = '\n',
							keep_lines_separator: bool = True,
							save_memory: bool = True):
		"""
		Read text file in reversed direction, return iteration of lines
		Original idea from: https://stackoverflow.com/questions/2301789/how-to-read-a-file-in-reverse-order/
		Modified and tested for UFT-8 based Text File (in Chinese particularly), but should work for most encodings
		:param file_object: Text File Stream (file opened in 'rt' mode)
		:param lines_separator: Line separator using after file reversed
		:param keep_lines_separator: 	True - Keep above separator at the end of each line, or
										False - Remove any line separator
		:param save_memory: 	True - Save memory by reading file using bitstream, slower by works for any file
								False - Read the while file in memory and reverse it, faster but limited to small file
		:return: iteration each line of the file from the back towards the front
		"""
		f = open(filename, 'w')

		def ceil_division(left_number, right_number):
			"""
			Divides given numbers with ceiling.
			"""
			return -(-left_number // right_number)

		def split(string, separator, keep_separator):
			"""
			Splits given string by given separator.
			"""
			parts = string.split(separator)
			if keep_separator:
				*parts, last_part = parts
				parts = [part + separator for part in parts]
				if last_part:
					return parts + [last_part]
			return parts

		def read_batch_from_end(byte_stream, size, end_position):
			"""
			Reads batch from the end of given byte stream.
			"""
			if end_position > size:
				offset = end_position - size
			else:
				offset = 0
				size = end_position
			byte_stream.seek(offset)
			return byte_stream.read(size)

		def reverse_binary_stream(byte_stream, batch_size=None,
								  lines_separator=None,
								  keep_lines_separator=True):
			if lines_separator is None:
				lines_separator = (b'\r', b'\n', b'\r\n')
				lines_splitter = methodcaller(str.splitlines.__name__,
											  keep_lines_separator)
			else:
				lines_splitter = functools.partial(split,
												   separator=lines_separator,
												   keep_separator=keep_lines_separator)
			stream_size = byte_stream.seek(0, os.SEEK_END)
			if batch_size is None:
				batch_size = stream_size or 1
			batches_count = ceil_division(stream_size, batch_size)
			remaining_bytes_indicator = itertools.islice(
				itertools.accumulate(itertools.chain([stream_size],
													 itertools.repeat(batch_size)),
									 sub),
				batches_count)
			try:
				remaining_bytes_count = next(remaining_bytes_indicator)
			except StopIteration:
				return

			def read_batch(position):
				result = read_batch_from_end(byte_stream,
											 size=batch_size,
											 end_position=position)
				while result.startswith(lines_separator):
					try:
						position = next(remaining_bytes_indicator)
					except StopIteration:
						break
					result = (read_batch_from_end(byte_stream,
												  size=batch_size,
												  end_position=position)
							  + result)
				return result

			batch = read_batch(remaining_bytes_count)
			segment, *lines = lines_splitter(batch)
			yield from lines[::-1]
			for remaining_bytes_count in remaining_bytes_indicator:
				batch = read_batch(remaining_bytes_count)
				lines = lines_splitter(batch)
				if batch.endswith(lines_separator):
					yield segment
				else:
					lines[-1] += segment
				segment, *lines = lines
				yield from lines[::-1]
			yield segment

		def reverse_file(file, batch_size=None,
						 lines_separator=None,
						 keep_lines_separator=True):
			encoding = file.encoding
			if lines_separator is not None:
				lines_separator = lines_separator.encode(encoding)
			yield from map(functools.partial(codecs.decode,
											 encoding=encoding),
						   reverse_binary_stream(
							   file.buffer,
							   batch_size=batch_size,
							   lines_separator=lines_separator,
							   keep_lines_separator=keep_lines_separator))

		if save_memory:
			r_file = reverse_file(file_object)
			for line in r_file:
				if keep_lines_separator:
					yield f'{line.rstrip()}{lines_separator}'
				else:
					yield line.rstrip()
		else:
			reversed_file = file_object.readlines()
			reversed_file.reverse()
			for line in reversed_file:
				if keep_lines_separator:
					yield f'{line.rstrip()}{lines_separator}'
				else:
					yield line.rstrip()

	@classmethod
	def text_file_search_all(cls, file, search_for, encoding='utf-8', search_using_regex=False,
							 search_from_front_to_back=False, count=0):
		"""
		Search text inside file using pure_text or regular expression (RE)
		:param file: File with its path
		:param search_for: The text you are searching for
		:param search_using_regex: True: The search_for parameter is a RE, or False: The search_for parameters is a str
		:param search_from_front_to_back: 	True: Search the file from the start towards the end, or
											False: Search the file from the end towards the start
		:param count: Maximum Occurrence needed, 0 will return all
		:return: return a list of found strings, or None if not found
		"""

		if search_for == '':
			return None
		try:
			result = []
			with open(file, mode='r', encoding=encoding) as file_reader:
				for line in file_reader if search_from_front_to_back else cls.reverse_file_reader(file_reader,
																								  save_memory=True):
					if not search_using_regex:
						if not line.find(search_for) == -1:
							result.append(search_for)

					else:
						search_for_re = re.compile(search_for)
						re_result = re.search(search_for_re, line)
						if re_result:
							result.append(re_result.group())
					if 0 < count == len(result):
						break
				if not result:
					return None
				else:
					return result
		except Exception as e:
			print(e)
			return None

	@classmethod
	def text_file_search(cls, file: str, search_for: str, encoding: str = 'utf-8', search_using_regex: bool = False,
						 search_from_front_to_back: bool = False):
		"""
		Search text inside file using pure_text or regular expression (RE)
		:param file: File with its path
		:param search_for: The text you are searching for
		:param encoding: what encoding to use for the file
		:param search_using_regex: True: The search_for parameter is a RE, or False: The search_for parameters is a str
		:param search_from_front_to_back: 	True: Search the file from the start towards the end, or
											False: Search the file from the end towards the start
		:return: return the first found string, or None if not found
		"""

		result = cls.text_file_search_all(file, search_for, encoding, search_using_regex,
										  search_from_front_to_back, count=1)

		return result[0] if result else None

	@classmethod
	def encode_file_using_base64(cls, original_file, encoded_file):
		try:
			with open(original_file, mode='rb') as f_in:
				with open(encoded_file, mode='wt') as f_out:
					byte_stream = f_in.read(3)
					while byte_stream:
						f_out.write(WebUtils.base64_encoder(byte_stream))
						byte_stream = f_in.read(3)
			print('{} has been encoded successfully into {}'.format(original_file, encoded_file))
			return True
		except Exception as e:
			if os.path.exists(encoded_file):
				os.remove(encoded_file)
			print('Encode {} failed due to {}'.format(original_file, e))
			return False

	@classmethod
	def decode_file_use_base64(cls, encoded_file, decoded_file, encoding='utf-8'):
		try:
			with open(encoded_file, mode='rb') as f_in:
				with open('{}.tmp'.format(decoded_file), mode='wb+') as f_tmp:
					encoded_text = f_in.read()
					if encoded_text:
						f_tmp.write(WebUtils.base64_decoder(encoded_text, decode_output_as=str, encoding='utf-8').encode('utf-8'))
					f_tmp.seek(0)
					with open(decoded_file, mode='w', encoding=encoding) as f_out:
						f_out.write(f_tmp.read())
			print('{} has been decoded successfully into {}'.format(encoded_file, decoded_file))
			return True
		except Exception as e:
			if os.path.exists(decoded_file):
				os.remove(decoded_file)
			print('Decode {} failed due to {}'.format(encoded_file, e))
			return False


if __name__ == '__main__':
# 	ls = """Hello, world!
# I ❤ Python
#
# See you later!
#
# CSDN首页
# 博客"""
# 	print(f'{ls.encode("utf-16-le")}')
#
# 	print(base64.decodebytes('SABlAGwAbABvACwAIAB3AG8AcgBsAGQAIQAKAEkAIABkJyAAUAB5AHQAaABvAG4ACgAKAFMAZQBlACAAeQBvAHUAIABsAGEAdABlAHIAIQAKAAoAQwBTAEQATgCWmXWYCgBaU6Jb'.encode('ascii')))
# 	print(WebUtils.base64_encoder(ls, encoding='utf-16-le'))
# 	print(base64.encodebytes(ls.encode("utf-16-le")))
# 	dt = base64.decodebytes(base64.encodebytes(ls.encode("utf-16-le")))
# 	print(dt)
# 	# dt = WebUtils.base64_decoder("SABlAGwAbABvACwAIAB3AG8AcgBsAGQAIQAKAEkAIABkJyAAUAB5AHQAaABvAG4ACgAKAFMAZQBlACAAeQBvAHUAIABsAGEAdABlAHIAIQAKAAoAQwBTAEQATgCWmXWYCgBaU6Jb", encoding='utf-16-le')
# 	print()
# 	with open('ls.txt', 'w', encoding='utf-16-le') as f:
# 		f.write(dt.decode('utf-16-le'))
# 	print(bytes.decode(dt, 'utf-16-le'))

	# FileUtils.encode_file_using_base64('Test_origin.txt', 'Test_encoded.b64')
	# FileUtils.decode_file_use_base64('Test_encoded.b64', 'Test_decoded.txt')
	FileUtils.encode_file_using_base64('Test_origin_UTF-16LE.txt', 'Test_encoded_u16.b64')
	FileUtils.decode_file_use_base64('Test_encoded_u16.b64', 'Test_decoded_u16.txt', encoding='utf-16-le')
