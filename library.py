#!/usr/bin/env python

import os
import argparse

DEFAULT_LIBRARY_PATH = os.path.join(os.environ["HOME"], ".rfid_library.csv")

def add_cwd_to_library(path):

	identifier = raw_input("Please input the identifier for this library entry\n")
	entry = os.getcwd()

	with open(path, "a") as f:
		f.write("{},{}".format(identifier, entry))

	print "Success: {} -> {}".format(identifier, entry)


def lookup(path):
	
	with open(path, "r") as f:

		library = {}		
		for line in f.read().split("\n"):
			if not line:
				continue
			identifier = line.split(",")[0]
			entry = line.split(",")[1]
			library[identifier] = entry
		
		while True:

			identifier = raw_input("Please input an identifier (Empty line to exit)\n")
			if not len(identifier):
				break
			
			entry = library.get(identifier, None)
			if entry is None:
				print "Entry {} is not in the library".format(identifier)
			else:
				print "{} -> {}".format(identifier, entry)


def init(path):

	if os.path.exists(path):
		confirmation = raw_input("Library already exists. Overwrite? [y/n]\n")
		if confirmation != "y":
			print "Aborting."
		os.remove(path)

	open(path, "w").close()
	print "Library initialized at {}".format(path)


if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="Interact with music library")
	parser.add_argument("-f",
			    metavar="LIRBRARY",
			    action="store",
			    default=DEFAULT_LIBRARY_PATH,
			    help="Path to the library file")
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("-i",
			   "--init",
			   action="store_const",
			   dest="action",
			   const=init,
			   help="Clean initialization of library")
	group.add_argument("-a",
			   "--add",
			   action="store_const",
			   dest="action",
			   const=add_cwd_to_library,
			   help="Add an entry")
	group.add_argument("-l",
			   "--look-up",
			   action="store_const",
			   dest="action",
			   const=lookup,
			   help="Look up entries in the library")
	args = parser.parse_args()

	args.action(args.f)

