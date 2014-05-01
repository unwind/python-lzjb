#!/usr/bin/env python
#
# An attempt at re-implementing LZJB compression in native Python.
#

import cStringIO
import math

NBBY = 8
MATCH_BITS = 6
MATCH_MIN = 3
MATCH_MAX = ((1 << MATCH_BITS) + (MATCH_MIN - 1))
OFFSET_MASK = ((1 << (16 - MATCH_BITS)) - 1)
LEMPEL_SIZE_BASE = 1024

class Instream(object):
	def __init__(self, s):
		self._string = s
		self._pos = 0
		self._unbuffer = []

	def size(self):
		return len(self._string)

	def get(self):
		if len(self._unbuffer) > 0:
			return self._unbuffer.pop()
		if self._pos < len(self._string):
			r = self._string[self._pos]
			self._pos += 1
			return r
		return None

	def push(self, char):
		self._unbuffer.extend(char)


def compress(s, compression = 1, c_compatible = True):
	LEMPEL_SIZE = LEMPEL_SIZE_BASE
	EXPAND = True
	if compression != 1:
		LEMPEL_SIZE *= 2
		compression = max(1, min(compression, 9)) - 1
		EXPAND = 1 << int(math.floor(compression / 2))
		if compression & 1:
			EXPAND = round(EXPAND * 1.5)
		if compression >= 2 and compression <= 4:
			EXPAND += 1

	out = cStringIO.StringIO()
	src = Instream(s)

	# Encode input size.
	size = src.size()
	if size:
		sbytes = []
		size += 1
		while True:
			sbytes.append(size & 0x7f)
			size = int(math.floor(size / 128))
			if size == 0:
				break
		sbytes[0] |= 0x80
		for sb in reversed(sbytes):
			out.write(chr(sb))
		print out.getvalue()

if __name__ == "__main__":
	compress(18 * "whatever ever is what this ever?")
