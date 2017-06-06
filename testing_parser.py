import os, sys, itertools, getopt

from verbnetparser import VerbNetParser
import search

# Looks for config.txt for dir to VN XML
# Then instantiates parser with the files in that dir
vn = VerbNetParser()

# Returns a list of the XML as beautiful Soup objects
vn.parse_files()

# A list of all the verb classes, as python objects
# There is a printable representation of it
#print(vn.verb_classes[0].version())
print(vn.get_verb_class("waltz-51.5").members)
#members = vn.get_all_members()
#print(search.find_members(members, name=["absorb"]))