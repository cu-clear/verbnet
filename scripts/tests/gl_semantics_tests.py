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
# path_rel start, ch_of_loc pred
col_p2 = Predicate(soup('<PRED value="path_rel"><ARGS><ARG type="Constant" value="ch_of_loc"/></ARGS></PRED>', 'lxml-xml').PRED)
location_gold=["put-9.1", "put_spatial-9.2", "funnel-9.3", "put_direction-9.4", "pour-9.5", "coil-9.6", "spray-9.7", "fill-9.8", "butter-9.9", "pocket-9.10", "remove-10.1", "banish-10.2", "clear-10.3", "wipe_manner-10.4.1", "wipe_instr-10.4.2", "steal-10.5", "cheat-10.6", "pit-10.7", "debone-10.8", "mine-10.9", "fire-10.10", "resign-10.11", "send-11.1", "slide-11.2", "bring-11.3", "carry-11.4", "drive-11.5", "push-12", "throw-17.1", "pelt-17.2", "hit-18.1", "swat-18.2", "spank-18.3", "bump-18.4", "poke-19", "escape-51.1", "leave-51.2", "roll-51.3.1", "run-51.3.2", "vehicle-51.4.1", "nonvehicle-51.4.2", "vehicle_path-51.4.3", "waltz-51.5", "chase-51.6", "accompany-51.7", "reach-51.8"]
# path_rel end, ch_of_loc pred
#col_p3 = Predicate(soup('<PRED value="path_rel"><ARGS><ARG type="Event" value="end(E)"/><ARG type="ThemRole" value="?Destination"/><ARG type="Constant" value="ch_of_loc"/></ARGS></PRED>', 'lxml-xml').PRED)

# CHANGE_OF_POSSESSION
# path_rel source, ch_of_poss pred
cop_p1 = Predicate(soup('<PRED value="path_rel"><ARGS><ARG type="Constant" value="ch_of_poss"/></ARGS></PRED>', 'lxml-xml').PRED)
#cop_p1 = Predicate(soup('<PRED value="path_rel"><ARGS><ARG type="Event" value="start(E)"/><ARG type="ThemRole" value="Source"/><ARG type="Constant" value="ch_of_poss"/></ARGS></PRED>', 'lxml-xml').PRED)
# path_rel recipient, ch_of_poss pred
#cop_p2 = Predicate(soup('<PRED value="path_rel"><ARGS><ARG type="Event" value="end(E)"/><ARG type="ThemRole" value="Recipient"/><ARG type="Constant" value="ch_of_poss"/></ARGS></PRED>', 'lxml-xml').PRED)
# transfer pred (don't care about args)
#cop_p3 = Predicate(soup('<PRED value="transfer"><ARGS></ARGS></PRED>', 'lxml-xml').PRED)
possession_gold = ["give-13.1", "contribute-13.2", "future_having-13.3", "fulfilling-13.4.1", "equip-13.4.2", "get-13.5.1", "obtain-13.5.2", "hire-13.5.3", "exchange-13.6", "berry-13.7", "pay-68"]

# CHANGE_OF_STATE
cos_p1  = Predicate(soup('<PRED value="path_rel"><ARGS><ARG type="Constant" value="ch_of_state"/></ARGS></PRED>', 'lxml-xml').PRED)
#cos_p2 = Predicate(soup('<PRED value="path_rel"><ARGS><ARG type="Event" value="result(E)"/><ARG type="ThemRole" value="?Result"/><ARG type="Constant" value="ch_of_state"/></ARGS></PRED>', 'lxml-xml').PRED)

#cos_or_p1 = Predicate(soup('<PRED value="degradation_material_integrity"><ARGS><ARG type="Event" value="result(E)"/></ARGS></PRED>', 'lxml-xml').PRED)
state_gold = ["coloring-24", "image_impression-25.1", "scribble-25.2", "illustrate-25.3", "transcribe-25.4", "build-26.1", "grow-26.2", "preparing-26.3", "create-26.4", "knead-26.5", "turn-26.6.1", "convert-26.6.2", "snooze-40.4", "flinch-40.5", "body_internal_states-40.6", "suffocate-40.7", "pain-40.8.1", "tingle-40.8.2", "hurt-40.8.3", "change_bodily_state-40.8.4", "dress-41.1.1", "groom-41.1.2", "floss-41.2.1", "braid-41.2.2", "simple_dressing-41.3.1", "dressing_well-41.3.2", "being_dressed-41.3.3", "murder-42.1", "poison-42.2", "subjugate-42.3", "break-45.1", "bend-45.2", "cooking-45.3", "other_cos-45.4", "entity_specific_cos-45.5", "remedy-45.7", "exist-47.1", "disappearance-48.2", "complete-55.2", "confine-92", "addict-96", "become-109.1"]

# Right now, update_gl_semantics just prints the class_id/example of any frame that meets the criteria
#print("Change of Location")
#update_gl_semantics([col_p2], gold=location_gold)#col_p1, col_p2, col_p3])
#print("Change of Possession")
#update_gl_semantics([cop_p1], gold=possession_gold)
#print("Change of State")
#update_gl_semantics([cos_p1], gold=state_gold)

'''
  Note this, i.e. searching by a single framed, worked.
'''
#print("TESTTTTTT")
#vn = VerbNetParser()
#vnc = vn.get_verb_class("neglect-75.1")
#update_gl_semantics([vnc.frames[0]])