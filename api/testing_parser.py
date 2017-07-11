import os, sys, itertools, getopt

from verbnetparser import VerbNetParser
import search

# Looks for config.txt for dir to VN XML
# Then instantiates parser with the files in that dir
vn = VerbNetParser()
#vn_3_2 = VerbNetParser(version="3.2")

# Returns a list of the XML as beautiful Soup objects
vn.parse_files()
#vn_3_2.parse_files()
# A list of all the verb classes, as python objects
# There is a printable representation of it
vnc = vn.get_verb_class("put-9.1")
print([t.sel_restrictions for t in vnc.themroles])