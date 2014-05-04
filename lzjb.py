#!/usr/bin/env python
#
# An attempt at re-implementing LZJB compression in native Python.
#

import math

NBBY = 8
MATCH_BITS = 6
MATCH_MIN = 3
MATCH_MAX = ((1 << MATCH_BITS) + (MATCH_MIN - 1))
OFFSET_MASK = ((1 << (16 - MATCH_BITS)) - 1)
LEMPEL_SIZE_BASE = 1024


def compress(s, with_size = True):
	LEMPEL_SIZE = LEMPEL_SIZE_BASE

	# During compression, treat output string as list of code points.
	dst = []

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
		if (copymask == (1 << NBBY)):
			copymask = 1
			copymap = len(dst)
			dst.append(0)
		if src > len(s) - MATCH_MAX:
			dst.append(ord(s[src]))
			src += 1
			continue
		hsh = (ord(s[src]) << 16) + (ord(s[src + 1]) << 8) + ord(s[src + 2])
		hsh += hsh >> 9
		hsh += hsh >> 5
		hsh &= LEMPEL_SIZE - 1
		offset = (src - lempel[hsh]) & OFFSET_MASK
		print "src=%u hsh=0x%04x offset=%u" % (src, hsh, offset)
		lempel[hsh] = src
		cpy = src - offset
		if cpy >= 0 and cpy != src and s[src:src+3] == s[cpy:cpy+3]:
			dst[copymap] = dst[copymap] | copymask
			for mlen in xrange(MATCH_MIN, MATCH_MAX):
				if s[src + mlen] != s[cpy + mlen]:
					break
			dst.append(((mlen - MATCH_MIN) << (NBBY - MATCH_BITS)) | (offset >> NBBY))
			dst.append(offset & 0xff)
			src += mlen
		else:
			dst.append(ord(s[src]))
			src += 1
	# Now implode the list of codepoints into an actual string.
	return "".join(map(chr, dst))


def decompressed_size(s):
	dstSize = 0
	src = 0
	# Extract prefixed encoded size, if present.
	while True:
		c = ord(s[src])
		src += 1
		if (c & 0x80):
			dstSize |= c & 0x7f
			break
		dstSize = (dstSize | c) << 7
	dstSize -= 1	# -1 means "not known".		
	return (dstSize, src)


def decompress(s, with_size = True):
	src = 0
	dstSize = 0
	if with_size:
		dstSize, src = decompressed_size(s)
		if dstSize < 0:
			return None

	dst = ""
	copymask = 1 << (NBBY - 1)
	while src < len(s):
		copymask <<= 1
		if copymask == (1 << NBBY):
			copymask = 1
			copymap = ord(s[src])
			src += 1
		if copymap & copymask:
			mlen = (ord(s[src]) >> (NBBY - MATCH_BITS)) + MATCH_MIN
			offset = ((ord(s[src]) << NBBY) | ord(s[src + 1])) & OFFSET_MASK
			src += 2
			cpy = len(dst) - offset
			print "src=%u mlen=%u offset=%u cpy=%u" % (src, mlen, offset, cpy)
			if cpy < 0:
				print "Decompression failed"
				return None
			while mlen > 0:
				dst += dst[cpy]
				cpy += 1
				mlen -= 1
		else:
			dst += s[src]
			src += 1
	return dst


if __name__ == "__main__":
	data = 18 * "whatever ever is what this ever?"
	compressed = compress(data)
	print "%u -> %u (%.2f%%)" % (len(data), len(compressed), 100.0 * len(compressed) / len(data))
	print "data size was %u (encoded in %u bytes)" % decompressed_size(compressed)
	decompressed = decompress(compressed)
	print len(decompressed)
	print data == decompressed
