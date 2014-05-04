lzjb
====
This is a port, or re-implementation, of [Jeff Bonwick's](http://en.wikipedia.org/wiki/Jeff_Bonwick) [lzjb compression algorithm](http://en.wikipedia.org/wiki/LZJB) in pure Python.
The compression is used in the ZFS filesystem.

One of its main features is very small memory requirements for de-compression.
This can make it a suitable choice when adding compression in memory-constrained environments, such as in embedded development.
