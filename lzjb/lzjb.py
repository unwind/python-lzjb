#!/usr/bin/env python
#
# An attempt at re-implementing LZJB compression in native Python.
#
# Created in May 2014 by Emil Brink <emil@obsession.se>. See LICENSE.
#
# ---------------------------------------------------------------------
#
# Copyright (c) 2014, Emil Brink
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided
# that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and
# the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions
# and the following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import cProfile
import math
import sys
import time

NBBY = 8
MATCH_BITS = 6
MATCH_MIN = 3
MATCH_MAX = ((1 << MATCH_BITS) + (MATCH_MIN - 1))
OFFSET_MASK = ((1 << (16 - MATCH_BITS)) - 1)
LEMPEL_SIZE_BASE = 1024


def compress(s, with_size = True):
	"""
	Compresses the source bytearray, returning a new bytearray holding the compressed data.

	If the input is not a bytearray, an attempt to convert it by passing it to the bytearray()
	constructor is made. This will of course fail for objects that bytearray() doesn't accept.

	If with_size is not false, the length of the input is prepended to the result,
	in a special variable-length binary encoding.
	"""

	LEMPEL_SIZE = LEMPEL_SIZE_BASE

	# Make sure the input is a byte array. If it's not, convert.
	if not isinstance(s, bytearray):
		s = bytearray(s)

	# During compression, treat output string as list of code points.
	dst = bytearray()

	# Encode input size. This uses a variable-length encoding.
	if with_size:
		size = len(s)
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
				dst.append(sb)

	lempel = [0] * LEMPEL_SIZE
	copymask = 1 << (NBBY - 1)
	src = 0 # Current input offset.
	while src < len(s):
		copymask <<= 1
		if copymask == (1 << NBBY):
			copymask = 1
			copymap = len(dst)
			dst.append(0)
		if src > len(s) - MATCH_MAX:
			dst.append(s[src])
			src += 1
			continue
		hsh = (s[src] << 16) + (s[src + 1] << 8) + s[src + 2]
		hsh += hsh >> 9
		hsh += hsh >> 5
		hsh &= LEMPEL_SIZE - 1
		offset = (src - lempel[hsh]) & OFFSET_MASK
		lempel[hsh] = src
		cpy = src - offset
		if cpy >= 0 and cpy != src and s[src:src + 3] == s[cpy:cpy + 3]:
			dst[copymap] |= copymask
			for mlen in xrange(MATCH_MIN, MATCH_MAX):
				if s[src + mlen] != s[cpy + mlen]:
					break
			dst.append(((mlen - MATCH_MIN) << (NBBY - MATCH_BITS)) | (offset >> NBBY))
			dst.append(offset & 255)
			src += mlen
		else:
			dst.append(s[src])
			src += 1
	return dst


def decompressed_size(s):
	"""
	Returns a tuple (original length, length of size) from a bytearray of compressed data.

	The original length is the length of the data passed to compress(), and length of
	size is the number of bytes that are used in s to express this size.
	"""
	dstSize = 0
	src = 0
	# Extract prefixed encoded size, if present.
	while True:
		c = s[src]
		src += 1
		if (c & 0x80):
			dstSize |= c & 0x7f
			break
		dstSize = (dstSize | c) << 7
	dstSize -= 1	# -1 means "not known".
	return (dstSize, src)


def decompress(s, with_size = True):
	"""
	Decompresses a bytearray of compressed data, returning the original array.

	The return value is always a bytearray, the Python type of the input to
	compress() is not encoded.

	The value of with_size must match the value given when s was generated
	by compress().
	"""

	src = 0
	dstSize = 0
	if with_size:
		dstSize, src = decompressed_size(s)
		if dstSize < 0:
			return None

	dst = bytearray()
	copymask = 1 << (NBBY - 1)
	while src < len(s):
		copymask <<= 1
		if copymask == (1 << NBBY):
			copymask = 1
			copymap = s[src]
			src += 1
		if copymap & copymask:
			mlen = (s[src] >> (NBBY - MATCH_BITS)) + MATCH_MIN
			offset = ((s[src] << NBBY) | s[src + 1]) & OFFSET_MASK
			src += 2
			cpy = len(dst) - offset
			if cpy < 0:
				return None
			while mlen > 0:
				dst.append(dst[cpy])
				cpy += 1
				mlen -= 1
		else:
			dst.append(s[src])
			src += 1
	return dst


if __name__ == "__main__":
	profile = False
	for a in sys.argv[1:]:
		if a.startswith("-"):
			if a[1:] == "profile":
				profile = True
			else:
				print "**Ignoring unknown option '%s'" % a
		else:
			try:
				inf = open(a, "rb")
				data = inf.read()
				inf.close()
			except:
				print "**Failed to open '%s'" % a
				continue
			print "Loaded %u bytes from '%s'" % (len(data), a)
			t0 = time.clock()
			if profile:
				pr = cProfile.Profile()
				pr.enable()
			compr = compress(data)
			if profile:
				pr.disable()
				pr.print_stats()
			elapsed = time.clock() - t0
			rate = len(data) / (1024 * 1024 * elapsed)
			print " Compressed to %u bytes, %.2f%% in %s s [%.2f MB/s]" % (len(compr), 100.0 * len(compr) / len(data), elapsed, rate)
			decompr = decompress(compr)
			if decompr != data:
				print "**Decompression failed!"
