#!/usr/bin/env python

import os
import argparse

DEFAULT_LIBRARY_PATH = os.path.join(os.environ["HOME"], ".rfid_library.csv")
DEFAULT_DELIMETER = ","

class Library:
	"""
	Persistent (music) library
	"""

	def __init__(self, path, mode="r", delimeter=None):
		"""
		Any mode other than "w" and "w+" should work ok
		"""

		self.path = DEFAULT_LIRBRARY_PATH if path is None else path
		
		self.mode = mode
		self.delimeter = DEFAULT_DELIMETER if delimeter is None else delimeter

		self.file = None
		self.entries = {}

	def __enter__(self):
		self.file = open(self.path, self.mode)

		if self.readable():
			lines = self.file.read().split("\n")
			for line in lines:
				if not len(line):
					continue
				key, value = line.split(self.delimeter)
				self.entries[key] = value
		
		if not self.writeable():
			self.file.close()

		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		if self.writeable():
			self.file.close()

	def readable(self):
		return self.mode == "r" or "+" in self.mode

	def writeable(self):
		return self.mode != "r"

	def __getitem__(self, key):
		if not self.readable():
			raise IOError("Can't read from write-only Library instance")
		return self.entries[key]

	def __contains__(self, key):
		if not self.readable():
			raise IOError("Can't read from write-only Library instance")
		return key in self.entries

	def __setitem__(self, key, value):
		if not self.writeable():
			raise IOError("Can't write to read-only Library instance")
	
		if key in self.entries:
			raise IOError("Key already exists")
	
		self.file.write("{},{}\n".format(key, value))
		self.entries[key] = value


def add_cwd_to_library(path, delimeter=None):

	identifier = raw_input("Please input the identifier for this library entry\n")
	entry = os.getcwd()

	with Library(path, "a", delimeter) as library:
		library[identifier] = entry

	print "Success: {} -> {}".format(identifier, entry)


def lookup(path, delimeter=None):

	identifier = raw_input("Please input the identifier\n")
	
	with Library(path, "r", delimeter) as library:
		entry = None
		if identifier in library:
			entry = library[identifier]

	if entry is None:
		print "Entry {} is not in the library".format(identifier)
	else:
		print "{} -> {}".format(identifier, entry)

def init(path, delimeter=None):


	if os.path.exists(path):
		confirmation = raw_input("Library already exists. Delete? [y/n]\n")
		if confirmation != "y":
			print "Aborting."
		os.path.remove(path)

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
			   help="Look up an entry")
	args = parser.parse_args()

	args.action(args.f)
