#
# Makefile for automated tests of the python-lzjb code.
#
# Uses the reference C code as a ... well, reference. To
# avoid re-distributing that code needlessly, we download
# it on demand.
#

WGET  = wget
LZJBC = https://raw.githubusercontent.com/joyent/illumos-joyent/master/usr/src/uts/common/fs/zfs/lzjb.c

CFLAGS	= -std=c99 -Wall -pedantic

.PHONY:	clean

# ---------------------------------------------------------------------

test-bin:	cdriver testrunner.sh testfile.sh
	./testrunner.sh /usr/bin

test-etc:	cdriver testrunner.sh testfile.sh
	./testrunner.sh /etc

cdriver:	cdriver.c lzjb.c
	$(CC) $(CFLAGS) -o $@ $< 

lzjb.c:
	$(WGET) $(LZJBC)

# ---------------------------------------------------------------------

clean:
	rm -f cdriver lzjb.c
