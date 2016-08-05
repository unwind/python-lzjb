#!/usr/bin/env python
#
# An attempt at re-implementing LZJB compression in native Python.
#
# Created in May 2014 by Emil Brink <emil@obsession.se>. See LICENSE.
#
# ---------------------------------------------------------------------
#
# Copyright (c) 2014-2016, Emil Brink
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


BYTE_BITS = 8
MATCH_BITS = 6
MATCH_MIN = 3
MATCH_MAX = (1 << MATCH_BITS) + (MATCH_MIN - 1)
MATCH_RANGE = range(MATCH_MIN, MATCH_MAX + 1)	# Length 64, fine on 2.x.
OFFSET_MASK = (1 << (16 - MATCH_BITS)) - 1
LEMPEL_SIZE = 1024


def size_encode(size, dst = None):
	"""
	Encodes the given size in little-endian variable-length encoding.

	The dst argument can be an existing bytearray to append the size. If it's
	omitted (or None), a new bytearray is created and used.

	Returns the destination bytearray.
	"""
	if dst is None: dst = bytearray()
	done = False
	while not done:
		dst.append(size & 0x7f)
		size >>= 7
		done = size == 0
	dst[-1] |= 0x80
	return dst


def size_decode(src):
	"""
	Decodes a size (encoded with size_encode()) from the start of src.

	Returns a tuple (size, len) where size is the size that was decoded,
	and len is the number of bytes from src that were consumed.
	"""
	dstSize = 0
	pos = 0
	# Extract prefixed encoded size, if present.
	val = 1
	while True:
		c = src[pos]
		pos += 1
		if c & 0x80:
			dstSize += val * (c & 0x7f)
			break
		dstSize += val * c
		val <<= 7
	return (dstSize, pos)


def compress(src, dst = None):
	"""
	Compresses src, the source bytearray.

	If dst is not None, it's assumed to be the output bytearray and bytes are appended to it using dst.append().
	If it is None, a new bytearray is created.

	The destination bytearray is returned.
	"""

	if dst is None: dst = bytearray()

	lempel = [0] * LEMPEL_SIZE
	copymask = 1 << (BYTE_BITS - 1)
	pos = 0 # Current input offset.
	while pos < len(src):
		copymask <<= 1
		if copymask == (1 << BYTE_BITS):
			copymask = 1
			copymap = len(dst)
			dst.append(0)
		if pos > len(src) - MATCH_MAX:
			dst.append(src[pos])
			pos += 1
			continue
		hsh = (src[pos] << 16) + (src[pos + 1] << 8) + src[pos + 2]
		hsh += hsh >> 9
		hsh += hsh >> 5
		hsh &= LEMPEL_SIZE - 1
		offset = (pos - lempel[hsh]) & OFFSET_MASK
		lempel[hsh] = pos
		cpy = pos - offset
		if cpy >= 0 and cpy != pos and src[pos:pos + 3] == src[cpy:cpy + 3]:
			dst[copymap] |= copymask
			for mlen in MATCH_RANGE:
				if src[pos + mlen] != src[cpy + mlen]:
					break
			dst.append(((mlen - MATCH_MIN) << (BYTE_BITS - MATCH_BITS)) | (offset >> BYTE_BITS))
			dst.append(offset & 255)
			pos += mlen
		else:
			dst.append(src[pos])
			pos += 1
	return dst


def decompress(src, dst = None):
	"""
	Decompresses src, a bytearray of compressed data.

	The dst argument can be an optional bytearray which will have the output appended.
	If it's None, a new bytearray is created.

	The output bytearray is returned.
	"""

	if dst is None: dst = bytearray()
	pos = 0
	copymask = 1 << (BYTE_BITS - 1)
	while pos < len(src):
		copymask <<= 1
		if copymask == (1 << BYTE_BITS):
			copymask = 1
			copymap = src[pos]
			pos += 1
		if copymap & copymask:
			mlen = (src[pos] >> (BYTE_BITS - MATCH_BITS)) + MATCH_MIN
			offset = ((src[pos] << BYTE_BITS) | src[pos + 1]) & OFFSET_MASK
			pos += 2
			cpy = len(dst) - offset
			if cpy < 0:
				return None
			while mlen > 0:
				dst.append(dst[cpy])
				cpy += 1
				mlen -= 1
		else:
			dst.append(src[pos])
			pos += 1
	return dst


if __name__ == "__main__":
	import cProfile
	import os
	import sys
	import time

	def loop(data):
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
		print(" Compressed to %u bytes, %.2f%% in %s s [%.2f MB/s]" % (len(compr), 100.0 * len(compr) / len(data), elapsed, rate))
		decompr = decompress(compr)
		if decompr != data:
			print("**Decompression failed!")

	def save(filename, data):
		out = open(outname, "wb")
		out.write(data)
		out.close()

	DECOMPRESS = 0
	COMPRESS = 1
	mode = None
	outname = None
	quiet = False

	profile = False
	for a in sys.argv[1:]:
		if a.startswith("-"):
			if a[1:] == "profile":
				profile = True
			elif a[1:2] == "o":
				outname = a[2:]
			elif a[1:] == "c":
				mode = COMPRESS
				if outname is None:
					print("**Use -oNAME to set output name, before -c")
			elif a[1:] == "x":
				mode = DECOMPRESS
				if outname is None:
					print("**Use -oNAME to set output name, before -x")
			elif a[1:] == "q":
				quiet = True
			else:
				print("**Ignoring unknown option '%s'" % a)
		else:
			try:
				inf = open(a, "rb")
				data = inf.read()
				inf.close()
				data = bytearray(data)
			except:
				print("**Failed to open '%s'" % a)
				continue
			if not quiet: print("Loaded %u bytes from '%s'" % (len(data), a))
			if mode == COMPRESS:
				dst = size_encode(len(data))
				save(outname, compress(data, dst))
			elif mode == DECOMPRESS:
				size, slen = size_decode(data)
				save(outname, decompress(data[slen:]))
			else:
				loop(data)
