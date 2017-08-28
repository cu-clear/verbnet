local_scripts_path = "../"

import sys
sys.path.append(local_scripts_path)

from update_gl_semantics import update_gl_semantics
from verbnet import *
from bs4 import BeautifulSoup as soup

'''
  Just instantiate predicates with an xml string parsed with BeautifulSoup
  Adding .PRED to end of soup instantiation to account for default xml added by lxml-xml parser

  NOTE this is a sort of bare bones template of easy Predicates to match on for each change category.
  All of the change classes have other, specific predicates that need to be identified for this to be more exhaustive.
'''

# CHANGE_OF_LOCATION
# Motion pred (don't care about args)
col_p1 = Predicate(soup('<PRED value="motion"></PRED>', 'lxml-xml').PRED)
# path_rel start, ch_of_loc pred
col_p2 = Predicate(soup('<PRED value="path_rel"><ARGS><ARG type="Event" value="start(E)"/><ARG type="ThemRole" value="?Initial_Location"/><ARG type="Constant" value="ch_of_loc"/></ARGS></PRED>', 'lxml-xml').PRED)
# path_rel end, ch_of_loc pred
col_p3 = Predicate(soup('<PRED value="path_rel"><ARGS><ARG type="Event" value="end(E)"/><ARG type="ThemRole" value="?Destination"/><ARG type="Constant" value="ch_of_loc"/></ARGS></PRED>', 'lxml-xml').PRED)

# CHANGE_OF_POSSESSION
# path_rel source, ch_of_poss pred
cop_p1 = Predicate(soup('<PRED value="path_rel"><ARGS><ARG type="Event" value="start(E)"/><ARG type="ThemRole" value="Source"/><ARG type="Constant" value="ch_of_poss"/></ARGS></PRED>', 'lxml-xml').PRED)
# path_rel recipient, ch_of_poss pred
cop_p2 = Predicate(soup('<PRED value="path_rel"><ARGS><ARG type="Event" value="end(E)"/><ARG type="ThemRole" value="Recipient"/><ARG type="Constant" value="ch_of_poss"/></ARGS></PRED>', 'lxml-xml').PRED)
# transfer pred (don't care about args)
cop_p3 = Predicate(soup('<PRED value="transfer"><ARGS></ARGS></PRED>', 'lxml-xml').PRED)

# CHANGE_OF_STATE
cos_p1 = Predicate(soup('<PRED value="path_rel"><ARGS><ARG type="Event" value="start(E)"/><ARG type="ThemRole" value="?Initial_State"/><ARG type="Constant" value="ch_of_state"/></ARGS></PRED>', 'lxml-xml').PRED)
cos_p2 = Predicate(soup('<PRED value="path_rel"><ARGS><ARG type="Event" value="result(E)"/><ARG type="ThemRole" value="?Result"/><ARG type="Constant" value="ch_of_state"/></ARGS></PRED>', 'lxml-xml').PRED)

cos_or_p1 = Predicate(soup('<PRED value="degradation_material_integrity"><ARGS><ARG type="Event" value="result(E)"/></ARGS></PRED>', 'lxml-xml').PRED)

# Right now, update_gl_semantics just prints the class_id/example of any frame that meets the criteria
print("Change of Location")
update_gl_semantics([col_p1, col_p2, col_p3])
#print("Change of Possession")
#update_gl_semantics([cop_p1, cop_p2, cop_p3])
#print("Change of State")
#update_gl_semantics([[cos_p1, cos_p2], [cos_or_p1]])


'''
  Note this, i.e. searching by a single framed, worked.
'''
#print("TESTTTTTT")
#vn = VerbNetParser()
#vnc = vn.get_verb_class("neglect-75.1")
#update_gl_semantics([vnc.frames[0]])