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

print vn.get_verb_class("exchange-13.6").pp()