import sys
local_verbnet_api_path = "/Users/ajwieme/verbs-projects/VerbNet/verbnet/api"
sys.path.append(local_verbnet_api_path)

from verbnetparser import *

def udpate_frame_with_gl(frame, gl_semantics=[]):
  return True


def update_gl_semantics(matching_semantics, gl_semantics=[]):
  '''

  :param frame:
  :param matching_semantics: list of preds, can also be a frame, which determine whether this class is one that requires the update
  :param gl_semantics: The predicates to update to, in order to change to gl representation. Might we need a mapping?
  :return:
  '''

  vn = VerbNetParser()
  for vnc in vn.get_verb_classes():
    for frame in vnc.frames:
      if frame.contains(matching_semantics):
        print(frame.class_id(), frame.primary)
        udpate_frame_with_gl(frame, gl_semantics)

  return True