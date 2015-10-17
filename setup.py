#!/usr/bin/env python
#
# Setup script for python-lzjb.
#

from distutils.core import setup

setup(name = "lzjb",
	version = "1.1",
	description = "A pure Python implementation of LZJB compression/decompression",
	author = "Emil Brink",
	author_email = "emil@obsession.se",
	url = "https://github.com/unwind/python-lzjb",
	license = "BSD 2-clause",
	py_modules = ["lzjb"],

	classifiers = [
	"License :: OSI Approved :: BSD License",
	],
)
