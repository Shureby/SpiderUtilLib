# -*- encoding:utf-8 -*-

"""FileUtil
:cvar: 1.0.0
This module contains a few utilities that can help you
process local files easily.
"""

#  Copyright 2021 Wei WANG of Ezy App Co. Pty Ltd, Australia
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

import os
import shutil
import re
import functools
import itertools
from operator import methodcaller, sub
import codecs



class FileUtils:
	@classmethod
	def File_Name_Cleanup(cls, name: str) -> str:
		"""Clean up the illegal ASCII characters in the name
		string and return a new string that keeps the same
		format using legal unicode characters.
		"""
		new_name = name
		new_name = new_name.replace('|', '-')
		new_name = new_name.replace('?', '？')
		new_name = new_name.replace('*', '×')
		new_name = new_name.replace('/', '╱')
		new_name = new_name.replace('\\', '╲')
		new_name = new_name.replace('\n', '_')
		new_name = new_name.replace(':', '：')
		new_name = new_name.replace('>', '〉')
		new_name = new_name.replace('<', '〈')
		new_name = new_name.replace('"', '\'')
		return new_name

	@classmethod
	def Remove_Duplicates_Orderly(cls, list_with_duplicates, preserve_first_encounter=True,
								  preserve_original_list=False):
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
	def Search_File_By_Name(cls, name, root_path, return_path_only=True, return_all_files=False,
							allow_partial_name=False):
		""":cvar:1.0
		Serach for file with  by walk through root_path and its sub directories, return
		the absolute path of the file if exists.
		:param name: File name you want to search for
		:param root_path: Search file name inside this folder and its sub folders
		:param return_path_only:  Return path include filename if set to False, return only
				path proceeds the filename if set to True
		:param return_all_files: If True, return a list of all founded files in a list
		:param allow_partial_name: If True, allow partial file name match, AND THIS WILL
				FORCE return_path_only TO BE SET TO False
		:return: return first found file's absolute path or None if not found, when
				 return_all_files is set to False, otherwise, return a list of all
				 found files
		"""

		# if allow_partial_name and return_path_only:
		# 	import warnings
		# 	warnings.warn(
		# 		'{}.{} - Due to "allow_partial_name" is set to True, "return_path_only" has been set to False '.format(
		# 			__name__, cls.Search_File_By_Name.__name__), RuntimeWarning)
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
	def Text_File_Cleanup(cls, file, search_for, replace_as='', encoding='utf-8', search_using_regex=False,
						  preserve_original_file=False):
		""":cvar:1.0
		Serach text inside file using pure_text or regular expression (RE) and replace
		it.
		:param file: File with its path
		:param search_for: The text you are searching for
		:param replace_as: The text you are replacing as
		:param encoding: The encoding of the text file
		:param search_using_regex: True: The search_for parameter is a RE, or
								  False: The search_for parameters is a str
		:param preserve_original_file: True: A extra file.old file will be created
											  after replacement completed
									  False: The original file will be cleaned and
									          gone for good
		:return: return True if complete replacement successfully, or False if failed
		"""

		try:
			shutil.move(file, file + '.origin')
			with open(file + '.origin', mode='r', encoding=encoding) as file_reader, open(file, mode='w',
																						  encoding=encoding) as file_writer:
				for line in file_reader:
					if not search_using_regex:
						file_writer.write(line.replace(search_for, replace_as))
					else:
						search_for_re = re.compile(search_for)
						file_writer.write(re.sub(search_for_re, replace_as, line))
			if not preserve_original_file:
				shutil.remove(file + '.origin')
		except Exception as e:
			print(e)
			return False
		return True

	@classmethod
	def Reverse_File_Reader(cls, file_object,
							lines_separator='\n',
							keep_lines_separator=True,
							save_memory=True):
		""":cvar: 1.0.0
		   :param file_object: Text File Stream (file opened in 'rt' mode)
		   :param lines_separator: Line separator using after file reversed
		   :param keep_lines_separator: True - Keep above separator at the end of each line, or
		   							   False - Remove any line separator
		   :param save_memory: True - Save memory by reading file using bitstream, slower by works for any file
		   					  False - Read the while file in memory and reverse it, faster but limited to small file
		   :return: read file_object from the back towards the front, iterate file line by line

		Read text file in reversed direction, return iteration of lines
		Original idea from: https://stackoverflow.com/questions/2301789/how-to-read-a-file-in-reverse-order/
		Modified and tested for UFT-8 based Text File (in Chinese particularly), but should work for most encodings
		"""

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
	def Text_File_Search_All(cls, file, search_for, encoding='utf-8', search_using_regex=False,
							 search_from_front_to_back=False, count=0):
		""":cvar:1.0
		Serach text inside file using pure_text or regular expression (RE)
		:param file: File with its path
		:param search_for: The text you are searching for
		:param search_using_regex: True: The search_for parameter is a RE, or False: The search_for parameters is a str
		:param search_from_front_to_back: True: Search the file from the start towards the end, or
										 False: Search the file from the end towards the start
		:param count: Maximum Occurrence needed, 0 will return all
		:return: return a list of found strings, or None if not found
		"""

		if search_for == '':
			return None
		try:
			result = []
			with open(file, mode='r', encoding=encoding) as file_reader:
				for line in file_reader if search_from_front_to_back else cls.Reverse_File_Reader(file_reader,
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
	def Text_File_Search(cls, file, search_for, encoding='utf-8', search_using_regex=False,
						 search_from_front_to_back=False):
		""":cvar:1.0
		Serach text inside file using pure_text or regular expression (RE)
		:param file: File with its path
		:param search_for: The text you are searching for
		:param search_using_regex: True: The search_for parameter is a RE, or False: The search_for parameters is a str
		:param search_from_front_to_back: True: Search the file from the start towards the end, or
										 False: Search the file from the end towards the start
		:return: return the first found string, or None if not found
		"""

		result = cls.Text_File_Search_All(file, search_for, encoding, search_using_regex,
										  search_from_front_to_back, count=1)

		return result[0] if result else None


if __name__ == '__main__':
	print(__doc__)
	pass
