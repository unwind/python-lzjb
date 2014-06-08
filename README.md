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

##Size encoding##
<dl>

Original Code
-------------
This was ported to Python based on:
- [The original C code](http://web.archive.org/web/20100807223517/http://cvs.opensolaris.org/source/xref/onnv/onnv-gate/usr/src/uts/common/fs/zfs/lzjb.c)
- [The JavaScript port](https://code.google.com/p/jslzjb/source/browse/trunk/Iuppiter.js), which adds the inclusion of the uncompressed data size as a prefix

Thanks of course to these authors for contributing their code as open source.
