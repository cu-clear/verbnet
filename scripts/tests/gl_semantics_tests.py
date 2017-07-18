local_scripts_path = "../"
local_verbnet_api_path = "/Users/ajwieme/verbs-projects/VerbNet/verbnet/api"

import sys
sys.path.append(local_verbnet_api_path)
sys.path.append(local_scripts_path)

from update_gl_semantics import update_gl_semantics
from verbnetparser import *
from bs4 import BeautifulSoup as soup

'''
  Just instantiate predicates with an xml string parsed with BeautifulSoup
  Adding .PRED to end of soup instantiation to account for default xml added by lxml-xml parser
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

# Right now, update_gl_semantics just prints the class_id/example of any frame that meets the criteria
print("Change of Location")
update_gl_semantics([col_p1, col_p2, col_p3])
#print("Change of Possession")
#update_gl_semantics([cop_p1, cop_p2, cop_p3])