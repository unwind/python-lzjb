#
# testrunner.sh - Runs testfile.sh on a bunch of files.
#

DIR=$1
PYDRIVER=../lzjb.py
CDRIVER=./cdriver

for f in $(ls -S1 $DIR | head); do
	./testfile.sh $PYDRIVER $PYDRIVER $DIR/$f
done
