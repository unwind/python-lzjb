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


def compress(s):
	LEMPEL_SIZE = LEMPEL_SIZE_BASE

	dst = cStringIO.StringIO()

	# Encode input size. This uses a variable-length encoding.
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
			dst.write(chr(sb))

	lempel = [0] * LEMPEL_SIZE
	copymask = 1 << (NBBY - 1)
	src = 0 # Current input offset.
	while src < len(s):
		copymask <<= 1
		if (copymask == (1 << NBBY)):
			copymask = 1
			copymap = dst
			dst.write(chr(0))
		if src > len(s) - MATCH_MAX:
			out.write(s[src])
			src += 1
			continue
		hsh = (ord(s[src]) << 16) + (ord(s[src + 1]) << 8) + ord(s[src + 2])
		hsh += hsh >> 9
		hsh += hsh >> 5
		hsh &= LEMPEL_SIZE - 1
		offset = (src - lempel[hsh]) & OFFSET_MASK
		lempel[hsh] = src


if __name__ == "__main__":
	compress(18 * "whatever ever is what this ever?")
