import os, sys, itertools, getopt
local_verbnet_api_path = "/Users/ajwieme/verbs-projects/VerbNet/verbnet/api"

sys.path.append(local_verbnet_api_path)

from verbnetparser import *
import search

# Looks for config.txt for dir to VN XML
# Then instantiates parser with the files in that dir
vn = VerbNetParser()
#vn_3_2 = VerbNetParser(version="3.2")

vnc_list = vn.get_verb_classes_and_subclasses()

#print(vnc.members[0].soup)

#print(vnc.themroles[0].compare_selres_with(vn.get_verb_class("remove-10.1").themroles[0]))
#vn_3_2.parse_files()

#vnclasses = vn.get_verb_classes_and_subclasses()

#print(vnc.frames[0].predicates[0].argtypes)

def test_frame_contains(containing_frame, contained_frame, preds_list):
  '''
    Test if containing_frame contains contained_frame,
    and also if it contains a list of predicates
  '''
  print(containing_frame.contains(contained_frame))
  print(containing_frame.contains(preds_list))

#test_frame_contains(vnc.frames[0], vnc.frames[0], vnc.frames[0].predicates)