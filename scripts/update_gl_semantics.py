import sys
import copy
import bs4
local_verbnet_api_path = "/Users/ajwieme/verbs-projects/VerbNet/verbnet/api"
sys.path.append(local_verbnet_api_path)

from verbnet import *

def update_event_args(predicate):
  """
  ad-hoc method to change args of type Event to the format of "e1"..."e3"
  according to a mapping
  """
  EVENT_MAPPING = {
                    "start(e)": "e1",
                    "during(e)": "e2",
                    "result(e)": "e3",
                    "end(e)": "e3"
                  }
  for argtype, value in predicate.argtypes:
    if argtype == "Event":
      e = EVENT_MAPPING.get(value.lower())
      old_argsoup = bs4.BeautifulSoup('<ARG type="%s" value="%s"/></ARG>' % (argtype, value), 'lxml-xml').ARG
      new_argsoup = bs4.BeautifulSoup('<ARG type="%s" value="%s"/></ARG>' % (argtype, e), 'lxml-xml').ARG
      if e:
        predicate.remove_args([old_argsoup])
        predicate.add_args([new_argsoup])

  return predicate

def order_predicates(frame):
  """
  ad-hoc method to order predicates by event number, and add event numbers to events without them
  """
  predicates = frame.predicates.copy()
  preds_dict = {}
  removes = []
  for predicate in predicates:
    # Check for event in e1 - e10, to be safe (although doubtful theres any predicates with close to 10 events)
    events = list(set([value for type, value in predicate.argtypes if type == "Event"]).intersection(set(["e" + str(i) for i in range(10)])))
    if events:
      # Store the predicates that need to be sorted, and therefore removed (to be readded later)
      removes.append(predicate)
      # Get the int part of, e.g. e1 for the key
      e = tuple([int(event[1:]) for event in events])
      # point to lists, in case of duplicate event numbers
      if preds_dict.get(e):
        preds_dict[e].append(predicate)
      else:
        preds_dict[e] = [predicate]

  # Remove the event preds that need to be sorted from the predicates list, so they can be readded below, in sorted order
  for r in removes:
    predicates.remove(r)
  # Sort by event number, with predicates describing a single event first, and preds describing relationship between events after
  # In python 3, .items() should sort by key
  sorted_events = [val for k in sorted(preds_dict) for val in preds_dict[k] if len(list(preds_dict.keys())) < 2]
  sorted_events += [val for k in sorted(preds_dict) for val in preds_dict[k] if len(list(preds_dict.keys())) > 1]

  frame.remove_predicates(frame.predicates)
  frame.add_predicates(sorted_events)
  frame.add_predicates(predicates)


def update_frame_with_gl(frame, gl_semantics_mappings=[]):

  updated = False

  for mapping in gl_semantics_mappings:
    old_preds, new_preds, discard_args = mapping
    new_preds = [copy.deepcopy(new_pred) for new_pred in new_preds]

    if frame.contains(old_preds):
      updated = True
      print("Removing %s predicate for %s" % (",".join([p.value[0] for p in old_preds]), frame.class_id()))
      removed_preds = frame.remove_predicates(old_preds)
      print("Adding %s predicate for %s" % (",".join([p.value[0] for p in new_preds]), frame.class_id()))

      if discard_args:
        # We can only know which args to keep if there is only one 'old_pred' being removed
        if len(old_preds) == 1 and len(new_preds) == 1:
          removed_pred = removed_preds[0]
          # Add back the args that are not being discarded, AND are not event types (those should always be replaced by the new arg)
          new_preds[0].add_args([arg for arg in removed_pred.args if (arg["type"], arg["value"]) not in discard_args and arg["type"] != "Event"], order="last")
        else:
          raise Exception("Cannot transfer args if a single mapping is not a one to one relationship, empty the discard_args list in the ,mapping")

      frame.add_predicates(new_preds)

  print("Updating names of event ARGS")
  [update_event_args(predicate) for predicate in frame.predicates]
  print("Ordering Predicates...")
  order_predicates(frame)
  return updated


def update_gl_semantics(matching_semantics, vn, gl_semantics_mappings=[], gold=[]):
  '''
  matching_semantics: list of lists of preds, or a list of frames, or both, which determine whether this class
  is one that requires the update
  gl_semantics_mappings: List of tuples of predicates to remove, and what to replace it with
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
          if update_frame_with_gl(frame, gl_semantics_mappings):
            updated_class = True

      # Otherwise, check if frame.contains any of the multiple matches
      # (Or this could just be a single frame, which should work the same)
      else:
        if any([frame.contains(m) for m in matching_semantics]):
          matches.append((frame.class_id(), frame.examples))
          if update_frame_with_gl(frame, gl_semantics_mappings):
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