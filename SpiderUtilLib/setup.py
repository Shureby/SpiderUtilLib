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



"""Setup for SpiderUtilLib"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SpiderUtilLib",
    version="0.5.0",
    author="Wei WANG",
    author_email="wwang@ezyappco.com",
    description="Spider Utilities Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Shureby/SpiderUtilLib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License 2.0",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)


