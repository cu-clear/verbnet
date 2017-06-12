import os, sys, itertools, getopt

from verbnetparser import VerbNetParser
from xml_diff import compare
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
#print(vn.verb_classes[0].version())
c1 = vn.get_verb_class("admire-31.2")
c2 = vn.get_verb_class("addict-96")
for child in c1.etree:
  print(child.tag)
print(compare(c1.etree, c2.etree))
#members = vn.get_all_members()
#print(search.find_members(members, name=["absorb"]))