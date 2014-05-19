#
# testrunner.sh - Runs testfile.sh on a bunch of files.
#

DIR=$1
PYDRIVER=../lzjb.py
CDRIVER=./cdriver

for f in $(find $DIR -type f -maxdepth 1 2> /dev/null | xargs ls -rS1 | head); do
	./testfile.sh $PYDRIVER $PYDRIVER $f
	./testfile.sh $PYDRIVER $CDRIVER  $f
	./testfile.sh $CDRIVER  $PYDRIVER $f
done
