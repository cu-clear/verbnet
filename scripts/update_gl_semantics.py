import sys
local_verbnet_api_path = "/Users/ajwieme/verbs-projects/VerbNet/verbnet/api"
sys.path.append(local_verbnet_api_path)

from verbnetparser import *

def update_gl_semantics(frame, gl_semantics):
  return True


matching_semantics = [] # list of preds, can also be a frame
gl_semantics = [] # The predicates to update to, might we need a mapping?

for vnc in verbnetparser.get_verb_classes():
  for frame in vnc.frames:
    if frame.contains(matching_semantics):
      update_gl_semantics(frame, gl_semantics)