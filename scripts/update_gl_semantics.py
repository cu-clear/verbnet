import sys
local_verbnet_api_path = "/Users/ajwieme/verbs-projects/VerbNet/verbnet/api"
sys.path.append(local_verbnet_api_path)

from verbnet import *

def udpate_frame_with_gl(frame, gl_semantics=[]):
  return True


def update_gl_semantics(matching_semantics, gl_semantics=[]):
  '''

  :param frame:
  :param matching_semantics: list of lists of preds, or a list of frames, or both, which determine whether this class
    is one that requires the update
  :param gl_semantics: The predicates to update to, in order to change to gl representation. Might we need a mapping?
  :return:
  '''

  vn = VerbNetParser()
  # Use get_verb_classes_and_subclasses() so we can check all classes and subclasses in one list
  for vnc in vn.get_verb_classes():
    for frame in vnc.frames:
      # If its one flat list of predicates, just check if frame.contains that list of preds
      if matching_semantics and type(matching_semantics[0]) == Predicate:
        if frame.contains(matching_semantics):
          print(frame.class_id(), frame.examples)
          udpate_frame_with_gl(frame, gl_semantics)
      # Otherwise, check if frame.contains any of the multiple matches
      # (Or this could just be a single frame, which should work the same)
      else:
        if any([frame.contains(m) for m in matching_semantics]):
          print(frame.class_id(), frame.examples)
          udpate_frame_with_gl(frame, gl_semantics)

  return True