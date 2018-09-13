from update_gl_semantics import update_gl_semantics
from verbnet import *
from sys import argv, stderr
from bs4 import BeautifulSoup as soup

def get_updated_classes(vn):
  # Change of location Predicate
  col_pred = Predicate(
    soup('<PRED value="path_rel"><ARGS><ARG type="Constant" value="ch_of_loc"/></ARGS></PRED>', 'lxml-xml').PRED)
  # If there’s a CAUSE predicate:
  cause_pred = Predicate(soup('<PRED value="cause"></PRED>', 'lxml-xml').PRED)

  initial_location = Predicate(
    soup(
      '<PRED value="has_location"><ARGS><ARG type="Event" value="e1"></ARG><ARG type="ThemRole" value="Theme "></ARG><ARG type="ThemRole" value="Initial_Location"></ARG></ARGS></PRED>',
      'lxml-xml').PRED)
  motion = Predicate(
    soup(
      '<PRED value="motion"><ARGS><ARG type="Event" value="e3"></ARG><ARG type="ThemRole" value="Theme"></ARG><ARG type="ThemRole" value="Trajectory"></ARG></ARGS></PRED>',
      'lxml-xml').PRED)
  destination = Predicate(
    soup(
      '<PRED value="has_location"><ARGS><ARG type="Event" value="e4"></ARG><ARG type="ThemRole" value="Theme"></ARG><ARG type="ThemRole" value="Destination"></ARG></ARGS></PRED>',
      'lxml-xml').PRED)

  # Mappings are each triples of ([preds to remove], [preds to replace with], [(argtype, argval), ...
  # to be discarded from the old_predicate args in the resulting new predicate])
  mappings = [
    ([col_pred, Predicate(soup('<PRED value="motion"><ARGS></ARGS></PRED>', 'lxml-xml').PRED)],
     [initial_location, motion, destination], []),
    ([Predicate(soup(
      '<PRED value="cause"><ARG type="ThemRole" value="Agent"></ARG><ARG type="Event" value="E"/></ARG></ARGS></PRED>',
      'lxml-xml').PRED)],
     [Predicate(soup(
       '<PRED value="do"><ARGS><ARG type="Event" value="e2"></ARG><ARG type="ThemRole" value="Agent"></ARGS></PRED>',
       'lxml-xml').PRED),
      Predicate(soup(
        '<PRED value="cause"><ARGS><ARG type="Event" value="e2"></ARG><ARG type="Event" value="e3"></ARG></ARGS></PRED>',
        'lxml-xml').PRED)], []),
    ([Predicate(soup(
      '<PRED value="cause"><ARG type="ThemRole" value="Agent"></ARG><ARG type="Event" value="E0"/></ARG></ARGS></PRED>',
      'lxml-xml').PRED)], [Predicate(soup(
      '<PRED value="do"><ARGS><ARG type="Event" value="e2"></ARG><ARG type="ThemRole" value="Agent"></ARGS></PRED>',
      'lxml-xml').PRED),
      Predicate(soup(
      '<PRED value="cause"><ARGS><ARG type="Event" value="e2"></ARG><ARG type="Event" value="e3"></ARG></ARGS></PRED>',
      'lxml-xml').PRED)], [])

  ]

  classes = update_gl_semantics([col_pred, cause_pred], vn=vn, gl_semantics_mappings=mappings)

  initial_location2 = Predicate(
    soup(
      '<PRED value="has_location"><ARGS><ARG type="Event" value="e1"></ARG><ARG type="ThemRole" value="Theme "></ARG><ARG type="ThemRole" value="Initial_Location"></ARG></ARGS></PRED>',
      'lxml-xml').PRED)
  motion2 = Predicate(
    soup(
      '<PRED value="motion"><ARGS><ARG type="Event" value="e2"></ARG><ARG type="ThemRole" value="Theme"></ARG><ARG type="ThemRole" value="Trajectory"></ARG></ARGS></PRED>',
      'lxml-xml').PRED)
  destination2 = Predicate(
    soup(
      '<PRED value="has_location"><ARGS><ARG type="Event" value="e3"></ARG><ARG type="ThemRole" value="Theme"></ARG><ARG type="ThemRole" value="Destination"></ARG></ARGS></PRED>',
      'lxml-xml').PRED)

  # Do the same thing without cause, and a simpler update, to catch all other ch_of_location
  mappings = [
    ([col_pred, Predicate(soup('<PRED value="motion"><ARGS></ARGS></PRED>', 'lxml-xml').PRED)],
     [initial_location2, motion2, destination2], [])]

  classes += update_gl_semantics([col_pred], vn=vn, gl_semantics_mappings=mappings)

  return classes

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

  updated_classes = get_updated_classes(vn)

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