import os, sys, itertools, getopt

from verbnetparser import VerbNetParser
import search

# Looks for config.txt for dir to VN XML
# Then instantiates parser with the files in that dir
vn = VerbNetParser()
#vn_3_2 = VerbNetParser(version="3.2")

vnc = vn.get_verb_class("invest-13.5.4")
print(vnc.themroles[0].compare_selres_with(vn.get_verb_class("remove-10.1").themroles[0]))
#vn_3_2.parse_files()
# A list of all the verb classes, as python objects
# There is a printable representation of it