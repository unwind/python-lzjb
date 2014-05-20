python-lzjb: lzjb in pure Python
================================
This is a port of [Jeff Bonwick's](http://en.wikipedia.org/wiki/Jeff_Bonwick) [lzjb compression algorithm](http://en.wikipedia.org/wiki/LZJB) to pure Python.
This compression scheme is used in the ZFS filesystem.

One of its main features is very small memory requirements for decompression.
This can make it a suitable choice when adding compression in memory-constrained environments, such as in embedded development.

The name is perhaps not optimal.
I didn't want to come up with a "fancy" name that has no meaning.
I know of the [pylzjb](https://code.google.com/p/pylzjb/) project, which provides Python bindings for a C implementation of lzjb.

Unlike pylzjb, the module install name for this project is simply `lzjb`, which I think makes sense (it's kind of obvious that the imported module is for Python).


Original Code
-------------
This was ported to Python based on:

- [The original C code](http://web.archive.org/web/20100807223517/http://cvs.opensolaris.org/source/xref/onnv/onnv-gate/usr/src/uts/common/fs/zfs/lzjb.c)
- [The JavaScript port](https://code.google.com/p/jslzjb/source/browse/trunk/Iuppiter.js), which adds the inclusion of the uncompressed data size as a prefix


Status
------
It's early days for this code.
There is some work to be done to bring this into anything near "production quality":

- Proper Python packaging (setup.py, and so on).
- More profiling and optimization.


Tests
-----
To ensure compatibility with the public C code for LZJB compression, automatic testing is performed.
A simple shell script runs python-lzjb against both the C code and itself, on a set of 30 files.
The test script emits [a simple matrix](https://github.com/unwind/python-lzjb/blob/master/test/test-results.txt) which quickly shows when something breaks.


Python compatibility
--------------------
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

<dl>
<dt><code>lzjb.compress(s, dst = None)</code></dt>
<dd>
Compresses the source bytearray <code>s</code>.
Accepts an optional <code>dst</code> destination bytearray.
If no destination is given, a new bytearray is allocated.
The destination is returned.
No header of any kind is emitted into the destination.
</dd>

<dt><code>lzjb.decompress(s, dst = None)</code></dt>
<dd>
Decompresses the source bytearray <code>s</code>.
Accepts an optional <code>dst</code> destination bytearray.
If no destination is given, a new bytearray is allocated.
The destination is returned.
No header of any kind is expected in the source.
</dd>

<dt><code>lzjb.encode_size(size, dst = None)</code></dt>
<dd>
Encodes the given <code>size</code> into a bytearray.
Accepts an optional <code>dst</code> destination bytearray.
If no destination is given, a new bytearray is allocated.
The destination is returned.
</dd>

<dt><code>lzjb.decode_size(s)</code></dt>
<dd>
Decodes a size from a bytearray.
Returns a tuple <code>(size, count)</code> where <code>size</code> is the size that was decoded and <code>count</code> is the number of bytes it occupied.
The remaining data, if any, is thus <code>s[count:]</code>.
</dd>

</dl>
