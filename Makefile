#
# Top-level makefile for python-lzjb.
#
# This doesn't do a whole lot.
#

.PHONY:	doc dist

# ----------------------------------------------------------------------

doc:
	cd doc && make

# ----------------------------------------------------------------------

dist:
	python ./setup.py sdist
