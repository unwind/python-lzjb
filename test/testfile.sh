#
# Test script for python-lzjb. Compresses and decompresses a single file
# using configurable programs. Handy to test interoperability.
#
# Usage:
#
# testfile.sh COMPRESSOR DECOMPRESSOR FILENAME1 ...
#
# Compresses and decompresses each FILENAME using the indicated tools.
#
# Tool names are assumed to use relative path, and to accept the
# -o, -c and -x options to set output and to compress/decompress.

TMPDIR=/tmp

COMPRESSOR=$1
shift
DECOMPRESSOR=$1
shift


for f in $*
do
	BASE=$(basename $f)
	echo "Compressing ${BASE} ..."
	TMPF=${TMPDIR}/${BASE}
	$COMPRESSOR   -o${TMPF}.lzjb -c $f
	echo "Decompressing ..."
	$DECOMPRESSOR -o${TMPF}.orig -x ${TMPF}.lzjb
	if cmp $f ${TMPF}.orig; then
		echo "${f}: SUCCESS"
		rm -f ${TMPF}.{lzjb,orig}
	else
		echo "${f}: FAILED"
	fi
done
