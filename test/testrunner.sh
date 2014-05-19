#
# testrunner.sh - Runs testfile.sh on a bunch of files.
#

DIR=$1
PYDRIVER=../lzjb.py
CDRIVER=./cdriver

find $DIR -maxdepth 1  -type f  \! -name '.*'  -readable  -print0 | while IFS= read -r -d $'\0' f; do
	./testfile.sh $PYDRIVER $PYDRIVER $f
	./testfile.sh $PYDRIVER $CDRIVER  $f
	./testfile.sh $CDRIVER  $PYDRIVER $f
done
