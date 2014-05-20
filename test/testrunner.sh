#!/usr/bin/env bash
#
# testrunner.sh - Runs testfile.sh on a bunch of files.
#
# Part of python-lzjb by Emil Brink.
#
# Copyright (c) 2014, Emil Brink
# All rights reserved.
#

PYDRIVER=../lzjb.py
CDRIVER=./cdriver
TESTFILES=/tmp/testfiles.txt

# Collect some files to test.
# Idea: text files from /etc, and binaries from /usr/bin.

find /etc     -maxdepth 1  -type f  \! -name '.*' -readable | xargs ls -S 2>/dev/null | head -15  >$TESTFILES
find /usr/bin -maxdepth 1  -type f                -readable | xargs ls -S 2>/dev/null | head -15 >>$TESTFILES

TOTBYTES=0

printf "%-30s\t%5s\t%s\t%s\t%s\n" "Filename" "Size" "Py-Py" "C-Py" "Py-C"
for f in $(cat $TESTFILES)
do
	BYTES=$(ls -l $f | cut -d ' ' -f 5)
	SIZE=$(ls -lh $f | cut -d ' ' -f 5)
	printf "%-30s\t%5s\t" $f $SIZE
	./testfile.sh $PYDRIVER $PYDRIVER $f
	echo -e -n "\t"
	./testfile.sh $CDRIVER  $PYDRIVER $f
	echo -e -n "\t"
	./testfile.sh $PYDRIVER $CDRIVER  $f
	echo ""
	TOTBYTES=$(($TOTBYTES+$BYTES))
done

rm -f $TESTFILES

echo "Done; processed $((2*3*$TOTBYTES)) bytes total."
