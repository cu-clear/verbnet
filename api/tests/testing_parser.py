from verbnet.api.verbnet import *
from verbnet.api.annotation import *
#import search

# Looks for config.txt for dir to VN XML
# Then instantiates parser with the files in that dir
vn = VerbNetParser()
#vn_3_2 = VerbNetParser(version="3.2")

'''
for test_mem in ["replace", "recognize", "vary", "know", "run"]:
  if test_mem in [m.name for m in vn.get_members()]:
    print(test_mem)
'''
mems = vn.verb_classes_numerical_dict.get("37.7-1-1").members
m = mems[[x.name for x in mems].index("say")]
s = SemLinkAnnotation("nw/wsj/00/wsj_0003.parse 1 31 gold say-v 37.7-1 IN say.01 null ----- 0:3*33:1-ARG1=Topic 30:1-ARG0=Agent 31:0-rel")
s.update_vn_info(m)
print(str(s))

#print(vnc.members[0].soup)

#print(vnc.themroles[0].compare_selres_with(vn.get_verb_class("remove-10.1").themroles[0]))
#vn_3_2.parse_files()

def test_frame_contains(containing_frame, contained_frame, preds_list):
  '''
    Test if containing_frame contains contained_frame,
    and also if it contains a list of predicates
  '''
  print(containing_frame.contains(contained_frame))
  print(containing_frame.contains(preds_list))

#test_frame_contains(vnc.frames[0], vnc.frames[0], vnc.frames[0].predicates)