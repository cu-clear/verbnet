from verbnet.api.verbnet import *
from verbnet.api.annotation import *
#import search

# Looks for config.txt for dir to VN XML
# Then instantiates parser with the files in that dir
vn = VerbNetParser()
#vn_3_2 = VerbNetParser(version="3.2")

def test_update_pred(frame, predA, predR):
  frame.add_predicates([predA])
  frame.remove_predicates([predR])

'''
test_p = Predicate(soup('<PRED value="cause"><ARGS><ARG type="ThemRole" value="Agent"></ARG><ARG type="Event" value="E0"></ARG></ARGS></PRED>', 'lxml-xml').PRED)
other_r_p = Predicate(soup('<PRED value="motion"><ARGS><ARG type="Event" value="during(E1)"/><ARG type="ThemRole" value="Theme"/></ARGS></PRED>', 'lxml-xml').PRED)
add_p = Predicate(soup('<PRED value="test"><ARGS><ARG type="ThemRole" value="test"></ARG><ARG type="test" value="E0"></ARG></ARGS></PRED>', 'lxml-xml').PRED)
vc = vn.verb_classes_dict["accompany-51.7"]
frame1 = vc.frames[0]
test_update_pred(frame1, add_p, test_p)
print(vc.pp())
'''

vn.get_members()

def test_frame_contains(containing_frame, contained_frame, preds_list):
  '''
    Test if containing_frame contains contained_frame,
    and also if it contains a list of predicates
  '''
  print(containing_frame.contains(contained_frame))
  print(containing_frame.contains(preds_list))

#test_frame_contains(vnc.frames[0], vnc.frames[0], vnc.frames[0].predicates)