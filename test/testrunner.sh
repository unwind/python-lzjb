#
# Test script for python-lzjb.
#
# Usage:
#
# test-lzjb.sh COMPRESSOR(1) TAG(2) SOURCE_DIRECTORY(3)
#
# Creates a directory named TAG, then runs COMPRESSOR on the 10
# largest files in SOURCE_DIRECTORY, saving output in TAG.
#
# COMPRESSOR is assumed to be a relative path, and to accept -c and -x
# options to compress/decompress, respectively.

mkdir -p $2
for a in $(ls -S $3 | head)
do
	cd $2 && ../$1 -c $3/$a && cd ..
done
