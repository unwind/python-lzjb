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

NBBY = 8
MATCH_BITS = 6
MATCH_MIN = 3
MATCH_MAX = (1 << MATCH_BITS) + (MATCH_MIN - 1)
OFFSET_MASK = (1 << (16 - MATCH_BITS)) - 1
LEMPEL_SIZE = 1024


def encode_size(size, dst = None):
	"""
	Encodes the given size in little-endian variable-length encoding.

	The dst argument can be an existing bytearray to append the size.
	"""
	if not dst: dst = bytearray()
	done = False
	while not done:
		dst.append(size & 0x7f)
		size >>= 7
		done = size == 0
	dst[-1] |= 0x80
	return dst


def compress(s, dst = None):
	"""
	Compresses s, the source bytearray.

	If dst is not None, it's assumed to be the output bytearray and bytes are appended to it.
	If it is None, a new bytearray is created.

	The destination bytearray is returned.
	"""

	if dst is None: dst = bytearray()

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


def decode_size(s):
	"""
	Decodes a size (encoded with encode_size()) from the start of s.

	Returns a tuple (size, len) where size is the size that was decoded,
	and len is the number of bytes from s that were consumed.
	"""
	dstSize = 0
	src = 0
	# Extract prefixed encoded size, if present.
	val = 1
	while True:
		c = s[src]
		src += 1
		if c & 0x80:
			dstSize += val * (c & 0x7f)
			break
		dstSize += val * c
		val <<= 7
	return (dstSize, src)


def decompress(s, dst = None):
	"""
	Decompresses a bytearray of compressed data.

	The dst argument can be an optional bytearray which will have the output appended.
	If it's None, a new bytearray is created.

	The output bytearray is returned.
	"""

	src = 0
	if dst is None: dst = bytearray()
	copymask = 1 << (NBBY - 1)
	while src < len(s):
		copymask <<= 1
		if copymask == (1 << NBBY):
			copymask = 1
			print("reading copymap at %u" % src)
			copymap = s[src]
			print(" got 0x%02x" % copymap)
			src += 1
		if copymap & copymask:
			mlen = (s[src] >> (NBBY - MATCH_BITS)) + MATCH_MIN
			offset = ((s[src] << NBBY) | s[src + 1]) & OFFSET_MASK
			src += 2
			cpy = len(dst) - offset
			if cpy < 0:
				return None
			print("src=%lu: %u from cpy=%lu to dst=%lu" % (src, mlen, cpy, len(dst)));
			while mlen > 0:
				dst.append(dst[cpy])
				cpy += 1
				mlen -= 1
		else:
			print("src=%lu: 1 to dst=%lu" % (src, len(dst)));
			dst.append(s[src])
			src += 1
	print("decompressed %u, header said %u, src=%u, input %u" % (len(dst), dstSize, src, len(s)))
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
		print " Compressed to %u bytes, %.2f%% in %s s [%.2f MB/s]" % (len(compr), 100.0 * len(compr) / len(data), elapsed, rate)
		decompr = decompress(compr)
		if decompr != data:
			print "**Decompression failed!"

	def save(filename, data):
		out = open(outname, "wb")
		out.write(data)
		out.close()

	DECOMPRESS = 0
	COMPRESS = 1
	mode = None
	outname = None

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
			else:
				print "**Ignoring unknown option '%s'" % a
		else:
			try:
				inf = open(a, "rb")
				data = inf.read()
				inf.close()
				data = bytearray(data)
			except:
				print "**Failed to open '%s'" % a
				continue
			print "Loaded %u bytes from '%s'" % (len(data), a)
			if mode == COMPRESS:
				dst = encode_size(len(data))
				save(outname, compress(data, dst))
			elif mode == DECOMPRESS:
				size, slen = decode_size(data)
				save(outname, decompress(data[slen:]))
			else:
				loop(data)
