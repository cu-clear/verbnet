local_scripts_path = "../"
local_verbnet_api_path = "/Users/ajwieme/verbs-projects/VerbNet/verbnet/api"

import sys
sys.path.append(local_verbnet_api_path)
sys.path.append(local_scripts_path)

from update_gl_semantics import update_gl_semantics
from verbnetparser import *
from bs4 import BeautifulSoup as soup

'''
  Just instantiate 3 predicates with an xml string parsed with BeautifulSoup
  Adding .PRED to end of soup instantiation to account for default xml added by lxml-xml parser
'''
# Motion pred
p1 = Predicate(soup('<PRED value="motion"><ARGS><ARG type="Event" value="during(E)"/><ARG type="ThemRole" value="Theme"/></ARGS></PRED>', 'lxml-xml').PRED)
# path_rel start pred
p2 = Predicate(soup('<PRED value="path_rel"><ARGS><ARG type="Event" value="start(E)"/><ARG type="ThemRole" value="?Initial_Location"/><ARG type="Constant" value="ch_of_loc"/></ARGS></PRED>', 'lxml-xml').PRED)
# path_rel end pred
p3 = Predicate(soup('<PRED value="path_rel"><ARGS><ARG type="Event" value="end(E)"/><ARG type="ThemRole" value="?Destination"/><ARG type="Constant" value="ch_of_loc"/></ARGS></PRED>', 'lxml-xml').PRED)

update_gl_semantics([p1, p2, p3])