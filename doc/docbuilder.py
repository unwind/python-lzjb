#!/usr/bin/env python
#
# Simple helper program that builds parts of the GitHub README
# by extracting text from the docstrings of the package's functions.
#
# This is all in the spirit of keeping DRY, of course. Somebody has
# probably already done this much better, somewhere.
#
# Written in June 2014 by Emil Brink <emil@obsession.se>. Public domain.
#

def doc_callable(obj):
	"""Documents obj, which we've already determined is callable."""
	code = obj.func_code
	name = code.co_name
	argnames = code.co_varnames[:code.co_argcount]
	defs = obj.__defaults__
	args = []
	if defs != None:
		fd = len(argnames) - len(defs)	# Index of first argument with a default.
	else:
		fd = len(argnames)
	for i in range(len(argnames)):
		if i < fd:
			args.append(argnames[i])
		else:
			args.append("%s = %s" % (argnames[i], defs[i - fd]))
	print "<dt><tt>%s(%s)</tt></dt>" % (name, ", ".join(list(args)))
	print "<dd>%s</dd>" % obj.__doc__

def doc_object(obj):
	if hasattr(obj, "__call__"):
		doc_callable(obj)

def doc_package(package, methods, path_prefix = None):
	if not path_prefix is None:
		sys.path = [path_prefix] + sys.path
		print "path set to '%s'" % sys.path

	temp = __import__(package)
	for g in methods:
		if g[0] is not None:
			print "##%s##" % g[0]
		print "<dl>"
		for m in g[1:]:
			doc_object(getattr(temp, m))
		print "</dl>"


if __name__ == "__main__":
	import sys
	package = None
	methods = []
	path_prefix = None
	if len(sys.argv) >= 3:
		for a in sys.argv[1:]:
			if a.startswith("-"):
				if a[1:12] == "pathprefix=":
					path_prefix = a[12:]
				else:
					print "**Unknown option '%s'" % a
			else:
				if package is None:
					package = a
				else:
					# Expect remaining arguments to be list of category-prefixed
					# function names (e.g. "category:f1,f2,f3").
					cat = a.find(":")
					if cat > 0:
						methods.append(tuple([a[:cat],] + a[cat + 1:].split(",")))

		if package is not None and len(methods) > 0:
			doc_package(package, methods, path_prefix)
