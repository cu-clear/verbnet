import os, sys, itertools, getopt

from verbnetparser import VerbNetParser
import search

# Looks for config.txt for dir to VN XML
# Then instantiates parser with the files in that dir
vn = VerbNetParser()
#vn_3_2 = VerbNetParser(version="3.2")

# Returns a list of the XML as beautiful Soup objects
vn.parse_files()
vnc = vn.get_verb_class("invest-13.5.4")
print([t.class_id() for t in vnc.themroles])
#vn_3_2.parse_files()
# A list of all the verb classes, as python objects
# There is a printable representation of it