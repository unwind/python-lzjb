#
# Simplistic Makefile to build the README, by running docbuilder to extract Python docstrings.
#

.PHONY:	clean

# ----------------------------------------------------------------------

README.md:	README-header.md API.html README-footer.md
		cat $^  >$@

API.html:	lzjb.py docbuilder.py
		./docbuilder.py lzjb "Size encoding:encode_size,decode_size" "Data compression:compress,decompress" > $@

# ----------------------------------------------------------------------

clean:
	rm -f README README.md API.htm
