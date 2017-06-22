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
vnc = vn.get_verb_class("spank-18.3")
#vnc_old = vn_3_2.get_verb_class("spank-18.3")
print(search.find_members(vn.get_all_members(), class_ID="register-54.1"))
print(search.find_members(vn.get_all_members(), name=["come"]))
print(search.find_members(vn.get_all_members(), class_ID="register-54.1", name=["come"]))
#print(vn.verb_classes[0].version())
#members = vn.get_all_members()
#print(search.find_members(members, name=["absorb"]))