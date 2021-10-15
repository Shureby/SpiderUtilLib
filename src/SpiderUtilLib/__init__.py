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
# SpiderUtilLib
This is a package containing multiple utilities that are
useful for web crawling and related data processing.
It has two major class: WebUtils and FileUtils.

* WebUtils contains functions that are useful for web spiders,
* FileUtils contains functions that are useful for processing locally stored data files.
"""
from .FileUtils import FileUtils as FU
from .WebUtils import WebUtils as WU

if __name__ == '__main__':
	print(__doc__)
	print(FU.search_file_by_name('.py', '', return_all_files=True, allow_partial_name=True,
										return_path_only=False))
	print(WU.md5_hash('I ❤ Python'))