from update_gl_semantics import update_gl_semantics
from verbnet import *
from sys import argv, stderr
from bs4 import BeautifulSoup as soup

if __name__ == '__main__':
  if len(argv) == 2:
    output_dir = argv[1]
    input_dir = None
  elif len(argv) == 3:
    input_dir = argv[1]
    output_dir = argv[2]
  else:
    stderr.write(("USAGE: python %s (optional) input_dir output_dir") % argv[0])
    exit(1)

  if input_dir:
    vn = VerbNetParser(directory=input_dir)
  else:
    vn = VerbNetParser()

  """
  ch_of_state:
  """
  cos_pred = Predicate(soup('<PRED value="path_rel"><ARGS><ARG type="Constant" value="ch_of_state"/></ARGS></PRED>', 'lxml-xml').PRED)
  # If there’s a CAUSE predicate:
  cause_pred = Predicate(soup('<PRED value="cause"></PRED>', 'lxml-xml').PRED)

  # Mappings are each triples of ([preds to remove], [preds to replace with], [(argtype, argval), ... to be discarded from the old_predicate args in the resulting new predicate])
  mappings = [
    # Path_rel(Start(E), Role1, Role2…) -> has_state (e1, Role1, Role2…)
    ([Predicate(soup('<PRED value="path_rel"><ARG type="Event" value="start(E)"/></ARG></ARGS></PRED>', 'lxml-xml').PRED)],
     [Predicate(soup('<PRED value="has_state"><ARGS><ARG type="Event" value="e1"></ARG></ARGS></PRED>', 'lxml-xml').PRED)],
     [("VerbSpecific", "prep"), ("Constant", "ch_of_state")]),
     # Path_rel(Result(E), Role1…) -> has_state (e3, Role1…)
    ([Predicate(soup('<PRED value="path_rel"><ARG type="Event" value="result(E)"/></ARG></ARGS></PRED>', 'lxml-xml').PRED)],
     [Predicate(soup('<PRED value="has_state"><ARGS><ARG type="Event" value="e3"></ARG></ARGS></PRED>', 'lxml-xml').PRED)],
     [("VerbSpecific", "prep"), ("Constant", "ch_of_state")]),
    ([Predicate(soup('<PRED value="path_rel"><ARG type="Event" value="end(E)"/></ARG></ARGS></PRED>', 'lxml-xml').PRED)],
     [Predicate(soup('<PRED value="has_state"><ARGS><ARG type="Event" value="e3"></ARG></ARGS></PRED>', 'lxml-xml').PRED)],
     [("VerbSpecific", "prep"), ("Constant", "ch_of_state")]),
    # Cause(Agent, E) -> Do(e2, Agent) and Cause(e2, e3)
    ([Predicate(soup(
      '<PRED value="cause"><ARG type="ThemRole" value="Agent"></ARG><ARG type="Event" value="E"/></ARG></ARGS></PRED>',
      'lxml-xml').PRED)],
     [Predicate(soup(
       '<PRED value="do"><ARGS><ARG type="Event" value="e2"></ARG><ARG type="ThemRole" value="Agent"></ARGS></PRED>',
       'lxml-xml').PRED),
      Predicate(soup(
        '<PRED value="cause"><ARGS><ARG type="Event" value="e2"></ARG><ARG type="Event" value="e3"></ARG></ARGS></PRED>',
        'lxml-xml').PRED)], [])
  ]
  updated_classes = update_gl_semantics([cos_pred, cause_pred], vn=vn, gl_semantics_mappings=mappings)

  # Do the same thing without cause, and a simpler update, to catch all other ch_of_state
  mappings = [
    # Path_rel(Start(E), Role1, Role2…) -> has_state (e1, Role1, Role2…)
    ([Predicate(
      soup('<PRED value="path_rel"><ARG type="Event" value="start(E)"/></ARG></ARGS></PRED>', 'lxml-xml').PRED)],
     [Predicate(
       soup('<PRED value="has_state"><ARGS><ARG type="Event" value="e1"></ARG></ARGS></PRED>', 'lxml-xml').PRED)],
     [("VerbSpecific", "prep"), ("Constant", "ch_of_state")]),
    # Path_rel(Result(E), Role1…) -> has_state (e3, Role1…)
    ([Predicate(
      soup('<PRED value="path_rel"><ARG type="Event" value="result(E)"/></ARG></ARGS></PRED>', 'lxml-xml').PRED)],
     [Predicate(
       soup('<PRED value="has_state"><ARGS><ARG type="Event" value="e3"></ARG></ARGS></PRED>', 'lxml-xml').PRED)],
     [("VerbSpecific", "prep"), ("Constant", "ch_of_state")]),
    ([Predicate(soup('<PRED value="path_rel"><ARG type="Event" value="end(E)"/></ARG></ARGS></PRED>', 'lxml-xml').PRED)],
    [Predicate(
      soup('<PRED value="has_state"><ARGS><ARG type="Event" value="e3"></ARG></ARGS></PRED>', 'lxml-xml').PRED)],
    [("VerbSpecific", "prep"), ("Constant", "ch_of_state")])
  ]
  updated_classes = update_gl_semantics([cos_pred], vn=vn, gl_semantics_mappings=mappings)

  for vnc in updated_classes:
    #print(vnc.ID)
    #print(frame.pp())
    with open(output_dir + vnc.ID + ".xml", "w") as outfile:
      outfile.write(str(vnc.pp()))

  """
  If there’s another predicate with Result(E):
    Pred_name(Result(E), Role1…)  Pred_name(e3, Role1…)
  If there’s Utilize(During(E), Agent, Instrument)  Utilize(e2, Agent, Instrument)
  """