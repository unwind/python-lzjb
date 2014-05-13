/*
 * This code is part of python-lzjb by Emil Brink.
 *
 *
*/

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define	EXTENSION	".lzjb"

/* This is needed since we're building ZFS code way outside of ZFS. */
typedef unsigned char uchar_t;

#include "lzjb.c"

/* Load the given file. Doesn't just use mmap() because reasons. */
static void * load_file(const char *filename, size_t *length)
{
	FILE	*in = fopen(filename, "rb");
	void	*buf = NULL;

	if(in != NULL)
	{
		if(fseek(in, 0, SEEK_END) >= 0)
		{
			const long size = ftell(in);
			if(size >= 0)
			{
				if(length != NULL)
					*length = (size_t) size;
				if(fseek(in, 0, SEEK_SET) == 0)
				{
					if((buf = malloc(size)) != NULL)
					{
						if(fread(buf, size, 1, in) != 1)
						{
							free(buf);
							buf = NULL;
						}
					}
				}
			}
		}
		fclose(in);
	}
	return buf;
}

/* Saves the given buffer. Analyzes the filename, and removes the extension
 * if found, or adds it if it isn't. Basically smarter than me.
 *
 * All filenames are made fully relative, any path components are stripped out.
*/
static bool save_file(const char *filename, const void *data, size_t length)
{
	const char *rslash = strrchr(filename, '/');
	const char *ext = strstr(filename, EXTENSION);
	char out_name[1024];
	bool wrote = false;

	if(rslash != NULL)
		filename = rslash + 1;

	if(ext != NULL)
	{
		memcpy(out_name, filename, ext - filename);
		out_name[ext - filename] = '\0';
	}
	else
		snprintf(out_name, sizeof out_name, "%s" EXTENSION, filename);

	FILE *out = fopen(out_name, "wb");
	if(out != NULL)
	{
		wrote = fwrite(data, length, 1, out) == 1;
		fclose(out);
	}
	return wrote;
}

/* Encode the size in the given buffer. The buffer is big enough. */
static void * size_put(void *buffer, size_t length)
{
	uint8_t *put = buffer;
	length += 1;
	do
	{
		*put++ = length & 0x7f;
		length >>= 7;
	} while(length != 0);
	put[-1] |= 0x80;

	return put;
}

/* Decode size from the given buffer. */
static const void * size_get(const void *buffer, size_t *size)
{
	const uint8_t *get = buffer;
	size_t out = 0, shift = 0;
	bool busy = true;

	while(busy)
	{
		uint8_t here = *get++;
		if(here & 0x80)
		{
			here &= 0x7f;
			busy = false;
		}
		out |= here << shift;
		shift += 7;
	}
	if(size != NULL)
		*size = out;
	return get;
}

static void compress(const char *filename)
{
	size_t in_size;
	void *in = load_file(filename, &in_size);
	if(in != NULL)
	{
		const size_t out_max = in_size + 128;
		void *out = malloc(out_max);
		void *put = size_put(out, in_size);
		const size_t out_left = out_max - ((unsigned char *) put - (unsigned char *) out);
		const size_t out_size = lzjb_compress(in, put, in_size, out_left, 0);
		if(save_file(filename, out, out_size))
			printf("%-20s %zu -> %zu [%.1f%%]\n", filename, in_size, out_size, 100.f * out_size / in_size);
		free(out);
		free(in);
	}
}

static void decompress(const char *filename)
{
	size_t in_size;
	void *in = load_file(filename, &in_size);
	if(in != NULL)
	{
		size_t out_size;
		void *get = (void *) size_get(in, &out_size);
		void *out = malloc(out_size);
		lzjb_decompress(get, out, in_size, out_size, 0);
		if(save_file(filename, out, out_size))
			printf("%-20s %zu -> %zu [%.1f%%]\n", filename, in_size, out_size, 100.f * in_size / out_size);
		free(out);
		free(in);
	}
}

int main(int argc, char *argv[])
{
	enum { DECOMPRESS, COMPRESS } mode = COMPRESS;

	for(int i = 1; argv[i] != NULL; ++i)
	{
		if(argv[i][0] == '-')
		{
			if(argv[i][1] == 'c')
				mode = COMPRESS;
			else if(argv[i][1] == 'x')
				mode = DECOMPRESS;
			else
			{
				fprintf(stderr, "**Unknown option '%s', aborting.\n", argv[i]);
				return EXIT_FAILURE;
			}
		}
		else if(mode == COMPRESS)
			compress(argv[i]);
		else if(mode == DECOMPRESS)
			decompress(argv[i]);
	}
	return EXIT_SUCCESS;
}
