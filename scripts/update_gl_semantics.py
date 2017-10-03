import sys
import copy
local_verbnet_api_path = "/Users/ajwieme/verbs-projects/VerbNet/verbnet/api"
sys.path.append(local_verbnet_api_path)

from verbnet import *

def update_frame_with_gl(frame, keep_args, gl_semantics_mappings=[]):
  updated = False

  for mapping in gl_semantics_mappings:
    old_preds, new_preds = mapping
    new_preds = [copy.deepcopy(new_pred) for new_pred in new_preds]
    if frame.contains(old_preds):
      updated = True
      print("Removing %s predicate for %s" % (",".join([p.value[0] for p in old_preds]), frame.class_id()))
      removed_preds = frame.remove_predicates(old_preds)
      print("Adding %s predicate for %s" % (",".join([p.value[0] for p in new_preds]), frame.class_id()))
      if keep_args:
        # We can only know which args to keep if there is only one 'old_pred' being removed
        if len(old_preds) == 1 and len(new_preds) == 1:
          removed_pred = removed_preds[0]
          removed_pred.remove_args(old_preds[0].args)
          print(removed_pred.args)
          new_preds[0].add_args(removed_pred.args)
        else:
          raise Exception("Cannot keep args if a single mapping is not a one to one relationship")

      frame.add_predicates(new_preds)

  return updated


def update_gl_semantics(matching_semantics, vn, keep_args=False, gl_semantics_mappings=[], gold=[]):
  '''
  matching_semantics: list of lists of preds, or a list of frames, or both, which determine whether this class
  is one that requires the update
  gl_semantics_mappings: List of tuples of predicates to remove, and what to replace it with
  keep_args: If there are args in the predicate being removed, other than those in the mapping, should they be kept or discareded?
  '''
  matches = []
  # track classes have frames that get updated
  updated_classes = []
  # Use get_verb_classes_and_subclasses() so we can check all classes and subclasses in one list
  for vnc in vn.get_verb_classes():
    """
    We do not want to end up returning subclasses, or parsing duplciate frames.
    vnc.frames_and_subclass_frames() should get ALL frames in the file, including subclass frames
    """
    if vnc.is_subclass():
      continue
    updated_class = False
    for frame in vnc.frames_and_subclass_frames():
      # If its one flat list of predicates, just check if frame.contains that list of preds
      if matching_semantics and type(matching_semantics[0]) == Predicate:
        if frame.contains(matching_semantics):
          matches.append((frame.class_id(), frame.examples))
          if update_frame_with_gl(frame, keep_args, gl_semantics_mappings):
            updated_class = True

      # Otherwise, check if frame.contains any of the multiple matches
      # (Or this could just be a single frame, which should work the same)
      else:
        if any([frame.contains(m) for m in matching_semantics]):
          matches.append((frame.class_id(), frame.examples))
          if update_frame_with_gl(frame, keep_args, gl_semantics_mappings):
            updated_class = True

    if updated_class:
      updated_classes.append(vnc)

  if gold:
    false_positives = []
    correct = 0

    for ID in unique_matches:
      if ID in gold:
        correct += 1
      else:
        false_positives.append(ID)

    print(len(gold), len(unique_matches), correct)
    print("RECALL: %.2f %%" % (correct / float(len(gold)) * 100))
    print("PRECISION: %.2f %%" % (correct / float(len(unique_matches)) * 100))
    print("FALSE POSITIVES: " + str(false_positives))

  # Return all the effected frames (remove None's)
  return updated_classes