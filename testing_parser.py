import os, sys, itertools, getopt

from verbnetparser import VerbNetParser

# Looks for config.txt for dir to VN XML
# Then instantiates parser with the files in that dir
vn = VerbNetParser()

# Returns a list of the XML as beautiful Soup objects
vn.parse_files()

# A list of all the verb classes, as python objects
# There is a printable representation of it
vn.verb_classes

a = vn.find_class("accept-77")
print a.ID
for t in a.themroles:
  for s in t.sel_restrictions:
    print s