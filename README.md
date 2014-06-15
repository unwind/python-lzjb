python-lzjb: lzjb in pure Python
================================
This is a port of [Jeff Bonwick's](http://en.wikipedia.org/wiki/Jeff_Bonwick) [lzjb compression algorithm](http://en.wikipedia.org/wiki/LZJB) to pure Python.
This compression scheme is used in the ZFS filesystem.

One of its main features is very small memory requirements for decompression.
This can make it a suitable choice when adding compression in memory-constrained environments, such as in embedded development.

The name is perhaps not optimal.
I didn't want to come up with a "fancy" name that has no meaning.
I know of the [pylzjb](https://code.google.com/p/pylzjb/) project, which provides Python bindings for a C implementation of lzjb.


Status
------
This code is starting to feel quite mature and polished.
The only thing I can think of to do would be more profiling/optimization, but it does seem to *work* already.


Installation
------------
Like any Python package, `setup.py` is used.
Installation is a two-step process:

1. `$ ./setup.py build`
2. `$ ./setup.py install`

Unlike pylzjb, the module install name for this project is simply `lzjb`.
I think this makes sense, it should be kind of obvious that the imported module is for Python.


License
-------
This is open source, distributed under the [BSD 2-clause license](http://opensource.org/licenses/BSD-2-Clause).


Tests
-----
To ensure compatibility with the public C code for LZJB compression, automatic testing is performed.
A simple shell script runs python-lzjb against both the C code and itself, on a set of 30 files.
The test script emits [a simple matrix](https://github.com/unwind/python-lzjb/blob/master/test/test-results.txt) which quickly shows when something breaks.

This package is designed to work with both Python 2.x and 3.x from the same source.
It has been tested on Python 2.7.6 and Python 3.4, by running the test script.


Performance
-----------
The main goal when implementing this has been correctness and (sort of) clarity by closely following the original C code.
On my not-so-hot laptop (Intel® Core™ i5 M 480 @ 2.67GHz) it currently achieves around 1.1 MB/s when compressing.


API
===
The package's API is extremely simple.
Data is managed as Python [`bytearray`](https://docs.python.org/2.7/library/functions.html#bytearray) objects.

path set to '['..', '/home/emil/data/workspace/python-lzjb/doc', '/usr/lib/python2.7', '/usr/lib/python2.7/plat-x86_64-linux-gnu', '/usr/lib/python2.7/lib-tk', '/usr/lib/python2.7/lib-old', '/usr/lib/python2.7/lib-dynload', '/home/emil/.local/lib/python2.7/site-packages', '/usr/local/lib/python2.7/dist-packages', '/usr/lib/python2.7/dist-packages', '/usr/lib/python2.7/dist-packages/PILcompat', '/usr/lib/python2.7/dist-packages/gst-0.10', '/usr/lib/python2.7/dist-packages/gtk-2.0', '/usr/lib/pymodules/python2.7', '/usr/lib/python2.7/dist-packages/ubuntu-sso-client']'
##Size encoding##
<dl>
<dt><tt>size_encode(size, dst = None)</tt></dt>
<dd>
	Encodes the given size in little-endian variable-length encoding.

	The dst argument can be an existing bytearray to append the size. If it's
	omitted (or None), a new bytearray is created and used.

	Returns the destination bytearray.
	</dd>
<dt><tt>size_decode(src)</tt></dt>
<dd>
	Decodes a size (encoded with size_encode()) from the start of src.

	Returns a tuple (size, len) where size is the size that was decoded,
	and len is the number of bytes from src that were consumed.
	</dd>
</dl>
##Data compression##
<dl>
<dt><tt>compress(src, dst = None)</tt></dt>
<dd>
	Compresses src, the source bytearray.

	If dst is not None, it's assumed to be the output bytearray and bytes are appended to it.
	If it is None, a new bytearray is created.

	The destination bytearray is returned.
	</dd>
<dt><tt>decompress(src, dst = None)</tt></dt>
<dd>
	Decompresses src, a bytearray of compressed data.

	The dst argument can be an optional bytearray which will have the output appended.
	If it's None, a new bytearray is created.

	The output bytearray is returned.
	</dd>
</dl>

Original Code
-------------
This was ported to Python based on:
- [The original C code](http://web.archive.org/web/20100807223517/http://cvs.opensolaris.org/source/xref/onnv/onnv-gate/usr/src/uts/common/fs/zfs/lzjb.c)
- [The JavaScript port](https://code.google.com/p/jslzjb/source/browse/trunk/Iuppiter.js), which adds the inclusion of the uncompressed data size as a prefix

Thanks of course to these authors for contributing their code as open source.
