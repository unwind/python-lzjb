pylzjb: lzjb in pure Python
======================
This is a port of [Jeff Bonwick's](http://en.wikipedia.org/wiki/Jeff_Bonwick) [lzjb compression algorithm](http://en.wikipedia.org/wiki/LZJB) to pure Python.
This compression scheme is used in the ZFS filesystem.

One of its main features is very small memory requirements for decompression.
This can make it a suitable choice when adding compression in memory-constrained environments, such as in embedded development.


Original Code
-------------
This was ported to Python based on:

- [The original C code](http://web.archive.org/web/20100807223517/http://cvs.opensolaris.org/source/xref/onnv/onnv-gate/usr/src/uts/common/fs/zfs/lzjb.c)
- [The JavaScript port](https://code.google.com/p/jslzjb/source/browse/trunk/Iuppiter.js), which adds the inclusion of the uncompressed data size as a prefix


Status
------
It's very early days for this code.
There is a lot of work to be done to bring this into anything near "production quality":

- Proper Python packaging (setup.py, and so on).
- Test framework (including two-way testing against the C code).
- More profiling and optimization.
- An idea about Python 2.x/3.x compatibility and targeting; currently written against 2.7.6.

Performance
-----------
The main goal when implementing this has been correctness and (sort of) clarity by closely following the original C code.
On my not-so-hot laptop (Intel® Core™ i5 M 480 @ 2.67GHz) it currently achieves around 1.1 MB/s when compressing.


API
===
The package's API is extremely simple.
Data is managed as Python [`bytearray`](https://docs.python.org/2.7/library/functions.html#bytearray).

To compress a bytearray, call `lzjb.compress()`.
This returns a new bytearray holding the compressed data.

There are two things you can do with a bytearray of compressed data:

1. Decompress it, using `lzjb.decompress()`.
2. Find out about its decompressed size, and the header length, using `lzjb.decompressed_size()`.
