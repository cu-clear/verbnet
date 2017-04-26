"""verbnetgl.py

This file contains the classes for the form of Verbnet that has been enhanced
with GL event and qualia structures. The classes themselves do all conversions
necessary given a VerbClass from verbnetparser.py.

To run this do the following:

First copy config.sample.txt into config.txt and edit it if needed by changing
the verbnet location. The file config.txt is needed so the VerbNet parser can
find the VerbNet directory.

Then run this script in one of the following ways:

$ python verbnetgl.py

    Runs the main code in create_verbnet_gl() on all of VerbNet. Results are
    written to html/index.html.

$ python verbnetgl.py -d

    Runs the main code in create_verbnet_gl() in debug mode, that is, on just
    the first 50 verb classes. Results are written to html/index.html.

$ python verbnetgl.py -f list-motion-classes.txt

    Runs the main code in create_verbnet_gl(), but now only n the classes listed
    in list-motion-classes.txt. Results are written to html/index.html.

$ python verbnetgl.py -t
$ python verbnetgl.py -td

   Runs a couple of tests, either using all of VerbNet or just the first 50
   classes. You will need to hit return before each test.

"""

import os, sys, itertools, getopt
from bs4 import BeautifulSoup as soup
from verbnetparser import VerbNetParser
from writer import HtmlGLWriter, HtmlClassWriter
from search import search_by_predicate, search_by_argtype
from search import search_by_ID, search_by_subclass_ID
from search import search_by_themroles, search_by_POS, search_by_cat_and_role
from search import reverse_image_search, image_schema_search, image_schema_search2

class GLVerbClass(object):

    """VerbClass analogue, with an update mostly to frames"""

    def __init__(self, verbclass):
        self.verbclass = verbclass
        self.ID = verbclass.ID
        self.members = verbclass.members
        self.names = verbclass.names
        self.roles = verbclass.themroles
        self.frames = self.frames()
        self.subclasses = [GLSubclass(sub, self.roles) for sub in verbclass.subclasses]

    def __repr__(self):
        return str(self.ID) + " = {\n\nroles = " + str(self.roles) + \
               "\n\nframes = " + str(self.frames) + "\n}" + \
               "\n Subclasses = " + str(self.subclasses)

    def is_motion_class(self):
        """Return True if one of the frames is a motion frame."""
        for f in self.frames:
            if f.is_motion_frame():
                return True
        return False

    def is_change_of_state_class(self):
        """Return True if the class is a change-of-state class, which is defined as
        having an argtype that contains ch_of in one of the frames."""
        return True if [t for t in self.argtypes() if 'ch_of_' in t] else False

    def is_change_of_info_class(self):
        """Return True if the class is a change-of-info class, which is defined as
        having an argtype that contains ch_of_info in one of the frames."""
        return True if [t for t in self.argtypes() if 'tr_of_info' in t] else False

    def frames(self):
        return [GLFrame(self, frame) for frame in self.verbclass.frames]

    def argtypes(self):
        """Return a set of all the argtypes found in all frames."""
        argtypes = set()
        for frame in self.frames:
            for pred in frame.vnframe.predicates:
                for arg, arg_type in pred.argtypes:
                    argtypes.add(arg_type)
        return list(argtypes)



class GLSubclass(GLVerbClass):

    """Represents a subclass to a GLVerbClass. This needs to be different from
    GLVerbClass because VerbNet seems to change the THEMROLES section of the
    subclass to only include thematic roles that differ from the main class,
    but does not list all the roles that stay the same. Since we need to update
    self.roles, we can't call __init__ on the superclass because that would call
    self.frames and self.subclasses before we updated our roles properly."""

    # TODO: check this for proper nesting

    def __init__(self, verbclass, parent_roles):
        self.verbclass = verbclass
        self.ID = verbclass.ID
        self.members = verbclass.members
        self.names = verbclass.names
        self.parent_roles = parent_roles
        self.subclass_only_roles = verbclass.themroles
        self.roles = self.themroles()
        self.frames = self.frames()
        self.subclasses = [GLSubclass(sub, self.roles) for sub in verbclass.subclasses]

    def themroles(self):
        """Combines the thematic roles of the parent class and the current
        subclass. Replaces any version of the parent class's role with one from
        the subclass."""
        final_roles = self.subclass_only_roles
        for parent_role in self.parent_roles:
            duplicate = False
            for sub_role in self.subclass_only_roles:
                if parent_role.role_type == sub_role.role_type:
                    duplicate = True
            if not duplicate:
                final_roles.append(parent_role)
        return final_roles

class GLFrame(object):
    """GL enhanced VN frame that adds qualia and event structure, and links
    syn/sem variables in the subcat to those in the event structure."""

    def __init__(self, glverbclass, frame):
        self.glverbclass = glverbclass
        self.vnframe = frame                    # instance of verbnetparser.Frame

        self.class_roles = glverbclass.roles    # list of verbnetparser.ThematicRoles
        self.pri_description = frame.primary    # list of unicode strings
        self.sec_description = frame.secondary  # list of unicode strings
        self.example = frame.examples           # list of unicode strings
        self.subcat = Subcat(self)
        self.qualia = None
        self.events = EventStructure(self)
        self.add_oppositions()
        self.add_gl_to_xml()

    def __str__(self):
        return "<GLFrame %s [%s] '%s'>" % \
            (self.glverbclass.ID, ' '.join(self.pri_description), self.example[0])

    def __repr__(self):
        return "\n\n{ description = " + str(" ".join(self.pri_description)) + \
            "\nexample = " + str(self.example[0]) + \
            "\nsubcat = " + str(self.subcat) + \
            "\nqualia = " + str(self.qualia) + \
            "\nevents = {" + str(self.events) + "\t}\n"



    def find_predicates(self, pred_value):
        """Returns the list of Predicates where the value equals pred_value."""
        # TODO: should forward to self.vnframe
        return [p for p in self.vnframe.predicates if p.value[0] == pred_value]

    def find_arguments(self, pred, arg):
        """Return all arguments in pred where arg matches one of the argument's elements
        (note that arguments are tuples of two strings, like <Event,during(E)>
        or <ThemRole,Theme>)."""
        # TODO: should be defined on Predicate
        return [a for a in pred.argtypes if arg in a]

    def is_motion_frame(self):
        """Returns True if one of the predicates is 'motion', returns False otherwise."""
        return True if self.find_predicates('motion') else False

    def add_oppositions(self):
        """Add oppositions for each frame to event and qualia structure."""
        # TODO: maybe pull this all out and add it to a OppositionFactory class.
        # Use an auxiliary dictionary that has mappings from role names to
        # variables, taken from the subcat frame.
        self.role2var = self._get_variables()
        # So for now we just do motion verbs, will add more, but need to decide
        # whether the groups of classes we do this for are disjoint or not.
        if self.is_motion_frame():
            self._add_motion_opposition()

    def _get_variables(self):
        """Returns a dictionary of roles and variables from all elements of the
        subcategorisation frame. The dictionary is indexed on the roles and
        variables are integers, for example {'Beneficiary': 0, 'Agent': 1}."""
        member_vars = {}
        for submember in self.subcat:
            # skip the event and skip prepositions
            if submember.var not in [None, "e"]:
                member_vars[submember.role[0]] = submember.var
        return member_vars

    def _add_motion_opposition(self):
        """Add motion opposition to wualia and event structure of motion frames."""
        initial_location, destination = None, None
        moving_object = self._get_moving_object()
        agent = self._get_agent()
        initial_location = self._get_initial_location()
        destination = self._get_destination()
        self._add_default_opposition(initial_location, destination)
        initial_state = State(self, moving_object[1], initial_location[1])
        final_state = State(self, moving_object[1], destination[1])
        opposition = Opposition(self, 'loc', [[initial_state, final_state]])
        self.events = EventStructure(self, [[initial_state, final_state]])
        self.qualia = Qualia(self, 'motion', opposition)
        #self._debug1(agent, moving_object, initial_location, destination,
        #             initial_state, final_state)

    def _get_moving_object(self):
        """Get the role and the index of the moving object. Assumes that the moving
        object is always the theme."""
        # check whether there actually is a motion predicate
        if not self.find_predicates('motion'):
            print("WARNING: no Motion predicate found in", self)
        return ['Theme', str(self.role2var.get('Theme', '?'))]

    def _get_agent(self):
        """Get the role and index of the agent of the movement. Assumes the
        cause is the agent."""
        # check whether there is an agent if there is a cause predicate
        cause_predicates = self.find_predicates('cause')
        if cause_predicates:
            args = self.find_arguments(cause_predicates[0], 'Agent')
            if not args:
                print('WARNING: missing Agent in Cause predicate')
        return ['Agent', str(self.role2var.get('Agent', '?'))]

    def _get_initial_location(self):
        """For now just return the Initial_Location role and the index of it, if any. No
        checking of predicates and no bitchy messages on missing roles."""
        # TODO: we are using list of strings, should perhaps use some class, this
        # same issue holds for the three other _get_X methods.
        return ['Initial_Location', str(self.role2var.get('Initial_Location', '?'))]

    def _get_destination(self):
        """For now just return the Destination role and the index of it, if any. No
        checking of predicates and no bitchy messages on missing roles."""
        return ['Destination', str(self.role2var.get('Destination', '?'))]

    def _add_default_opposition(self, initial_location, destination):
        """Sneaky way of adding in the opposition in case one or both of the locations
        are anonymous. Overgenerates for those cases where motion is in-place."""
        if initial_location[1] == '?' or destination[1] == '?':
            if initial_location[1] == '?' and destination[1] == '?':
                destination[1] = '-?'
            elif initial_location[1] == '?':
                initial_location[1] = '-' + destination[1]
            elif destination[1] == '?':
                destination[1] = '-' + initial_location[1]

    def pp_predicates(self, indent=0):
        print("%spredicates" % (indent * ' '))
        for p in self.vnframe.predicates:
            print("%s   %s" % (indent * ' ', p))

    def pp_subcat(self, indent=0):
        print("%ssubcat" % (indent * ' '))
        for sc in self.subcat:
            print("%s   %s" % (indent * ' ', sc))

    def pp_variables(self, indent=0):
        print("%svariables = { %s }") \
            % (indent * ' ',
               ', '.join(["%s(%s)" % (r, v) for r, v in self.role2var.items()]))

    def _debug1(self, agent, moving_object, initial_location, destination,
                initial_state, final_state):
        if self.glverbclass.ID in ('run-51.3.2', 'slide.11.2', 'snooze-40.4'):
            print(self)
            self.pp_predicates(3); self.pp_subcat(3), self.pp_variables(3)
            print('   agent  =', agent)
            print('   object =', moving_object)
            print('   start  =', initial_location)
            print('   end    =', destination)
            print('  ', initial_state)
            print('  ', final_state)


    def add_gl_to_xml(self):
        # Dummy soup object for generating new tags.
        # self.glverbclass.verbclass.soup is sometimes a tag object, which throws an error.
        # Added content to dummy so that no warnings throw
        dummy_soup = soup('dummy', 'lxml')

        # Generate tags, and add the GL content as strings
        gl_tag = dummy_soup.new_tag("GL")
        qualia_tag = dummy_soup.new_tag("QUALIA")
        qualia_tag.string = self.qualia.__repr__()
        event_structure_tag = dummy_soup.new_tag("EVENT_STRUCTURE")
        event_structure_tag.string = self.events.__repr__()
        subcat_tag = dummy_soup.new_tag("SUBCATEGORISATION")
        subcat_tag.string = self.subcat.__repr__()

        # Add each tag into the new <GL> tag
        gl_tag.append(qualia_tag)
        gl_tag.append(event_structure_tag)
        gl_tag.append(subcat_tag)

        # Insert into frame XML
        self.vnframe.soup.SEMANTICS.insert_after(gl_tag)
        return gl_tag


class Subcat(object):

    """Class that contains the GL subcategorisation for the frame, which is
    basically taken from the Verbnet frame except that it adds variables to some
    of the subcat elements."""

    def __init__(self, glframe):
        """Creates the subcat frame structure with unique variables assigned to
        different phrases/roles"""
        self.glframe = glframe
        self.members = []
        i = 0
        for synrole in self.glframe.vnframe.syntax:
            if synrole.POS in ["ADV", "PREP", "ADJ"]:
                self.members.append(SubcatMember(None, synrole, None))
                continue
            elif synrole.POS == "VERB":
                self.members.append(SubcatMember("e", synrole, None))
                continue
            added = False
            for themrole in self.glframe.class_roles:
                if str(synrole.value[0]).lower() == str(themrole.role_type).lower():
                    if str(synrole.POS) == "NP":
                        self.members.append(SubcatMember(i, synrole, themrole))
                        i += 1
                        added = True
                    else:
                        self.members.append(SubcatMember(None, synrole, themrole))
                        added = True
            if not added:
                self.members.append(SubcatMember(None, synrole, None))

    def __iter__(self):
        return iter(self.members)

    def __len__(self):
        return len(self.members)

    def __repr__(self):
        return '\n\t'.join([member.__repr__() for member in self.members])


class SubcatMember(object):

    """A combination of SyntacticRole and ThematicRole."""

    def __init__(self, var, synrole, themrole):
        self.var = var
        self.cat = synrole.POS
        self.role = synrole.value   #themrole.role_type won't work
        if themrole is not None:
            self.sel_res = themrole.sel_restrictions
        else:
            self.sel_res = synrole.restrictions

    def __repr__(self):
        return "{ var = %s, cat = %s, role = %s } / %s " \
            % (self.var, self.cat, self.role, self.sel_res)


class State(object):

    """Represents a state in the event structure For motion verbs, this gives the
    variable assignment of the mover, and its location. For transfer verbs, this
    gives the variable assignment of the object being transferred, and what
    currently owns the object."""

    # TODO. Should probably have several kinds of states, this one really is the
    # state of an object being at a position (or being owned). Should als make a
    # State a list of assignments rather than just the one.

    def __init__(self, glframe, obj_var, pos_var):
        self.glframe = glframe
        self.object = obj_var
        self.position = pos_var

    def __repr__(self):
        return "{ objects.%s.location = %s }" % (self.object, self.position)


class EventStructure(object):

    """Defines the event structure for a particular frame of a verb"""

    # TODO: adopt a list of states instead of just initial and final.

    def __init__(self, glframe, states=None):
        self.glframe = glframe
        if states is None:
            states = []
        self.var = "e"
        self.initial_state = [state1 for state1, state2 in states]
        self.final_state = [state2 for state1, state2 in states]

    def __repr__(self):
        return "{ var = %s, initial_state = %s, final_state = %s }" \
            % (self.var, self.initial_state, self.final_state)


class Opposition(object):

    """Represents the opposition structure of the frame. Right now only tailored for
    locations. Technically, an opposition should perhaps only have two states,
    but we allow there to be a longer list."""

    # define opposition operator used give the type of change predicate
    operator_mappings = { 'loc': 'At', 'pos': 'Has', 'info': 'Knows', 'state': 'State' }

    def __init__(self, glframe, type_of_change, states):
        self.glframe = glframe
        self.type_of_change = type_of_change
        self.states = states

    def __repr__(self):
        op = Opposition.operator_mappings.get(self.type_of_change, 'Op')
        return ' '.join(["(%s(%s, %s), %s(%s, %s))" % \
                         (op, start.object, start.position, op, end.object, end.position)
                         for start, end in self.states])


class Qualia(object):

    """Represents the qualia structure of a verbframe, including opposition
    structure."""

    def __init__(self, glframe, pred_type, opposition):
        self.glframe = glframe
        self.formal = pred_type
        self.opposition = opposition

    def __repr__(self):
        return "{ formal = " + str(self.formal) + "(e) AND Opposition" + \
               str(self.opposition) + "}"


## THE MAIN FUNCTION

def create_verbnet_gl(vn_classes):
    """This is what produces the output with motion classes, possession classes,
    change of state classes and change of info classes. Only th efirst class is
    currently properly implemented."""
    # TODO. We have three ways of finding classes: doing a search, setting a
    # list manually, and checking a test method on the classes. Should probably
    # use only one way of doing this and for this method that should probably be
    # using the is_motion_class() method.
    # TODO: write a test that compares results of using is_motion_class() versus
    # search_by_predicate(vn_classes, "transfer")
    motion_vcs = [vc for vc in vn_classes if vc.is_motion_class()]
    transfer_vcs = search_by_predicate(vn_classes, "transfer")
    # possession_results = search(vn_classes, "has_possession")
    # print len(possession_results), [vc.ID for vc in possession_results]
    # we only find three with the above so define them manually
    possession = ['berry-13.7', 'cheat-10.6', 'contribute-13.2', 'equip-13.4.2',
                 'exchange-13.6.1', 'fulfilling-13.4.1', 'get-13.5.1', 'give-13.1',
                 'obtain-13.5.2', 'steal-10.5']
    possession_vcs = [vc for vc in vn_classes if vc.ID in possession]
    ch_of_state_vcs = [vc for vc in vn_classes if vc.is_change_of_state_class()]
    ch_of_info_vcs = [vc for vc in vn_classes if vc.is_change_of_info_class()]
    writer = HtmlGLWriter()
    writer.write(motion_vcs + transfer_vcs, 'VN Motion Classes', 'motion')
    writer.write(possession_vcs, 'VN Posession Classes', 'poss')
    writer.write(ch_of_state_vcs, 'VN Change of State Classes', 'ch_of_x')
    writer.write(ch_of_info_vcs, 'VN Change of Info Classes', 'ch_of_info')
    writer.finish()
    # Regenerate the XML for the modified classes
    generate_verbnet_xml(motion_vcs + transfer_vcs)
    generate_verbnet_xml(possession_vcs)
    generate_verbnet_xml(ch_of_state_vcs)
    generate_verbnet_xml(ch_of_info_vcs)

def generate_verbnet_xml(gl_classes):
    for gl_class in gl_classes:
        vn_class = gl_class.verbclass
        # Write to xml
        try:
            os.makedirs("xml")
        except OSError:
            if not os.path.isdir("xml"):
                raise

        output = open(os.path.join("xml", vn_class.ID + '.xml'), 'w')
        output.write(vn_class.pp())
        output.close()

## TEST FUNCTIONS

def test_print_first_class(vn_classes):
    """Just print the first class to stdout."""
    print("\n%s" % (">" * 80))
    print(">>> RUNNING test_print_first_class")
    print(">>> Hit return to proceed...")
    raw_input()
    vn_classes[0].pp()


def test_print_some_classes(vn_classes):
    """Print a list of classes that match a couple of hand-picked predicates. The
    results are written to the html directory."""
    print("\n%s" % (">" * 80))
    print(">>> RUNNING test_print_first_class")
    print(">>> Hit return to proceed...")
    raw_input()
    preds = ["motion", "transfer", "adjust", "cause", "transfer_info",
             "emotional_state", "location", "state", "wear"]
    results = { p: search_by_predicate(vn_classes, p) for p in preds }
    result_classes = [i for i in itertools.chain.from_iterable(results.values())]
    result_classes = sorted(set(result_classes))
    writer = HtmlGLWriter()
    writer.write(result_classes, "VN Classes")
    print("Results are written to html/index.html")


def test_search_by_ID(vn_classes):
    print("\n%s" % (">" * 80))
    print(">>> RUNNING test_search_by_ID")
    print(">>> Hit return to proceed...")
    raw_input()
    try:
        print(search_by_ID(vn_classes, "absorb-39.8"))
    except:
        print("WARNING: could not find absorb-39.8")
    try:
        print(search_by_ID(vn_classes, "swarm-47.5.1").subclasses[1])
    except AttributeError:
        print("WARNING: could not find swarm-47.5.1")


def test_ch_of_searches(vn_classes):
    # find all 'ch_of_' verb classes
    print("\n%s" % (">" * 80))
    print(">>> RUNNING test_ch_of_searches")
    print(">>> Hit return to proceed...")
    raw_input()
    for argtype in ('ch_of_', 'ch_of_info', 'ch_of_pos', 'ch_of_poss',
                    'ch_of_state', 'ch_of_loc', 'ch_of_location'):
        results = search_by_argtype(vn_classes, argtype)
        print("%s %s %s\n" % (len(results), argtype, ' '.join(results)))
    path_rel_results = search_by_argtype(vn_classes, "path_rel")
    print('number of path_rel classes:', len(path_rel_results))
    path_less_ch = [vc.ID for vc in path_rel_results if vc.ID not in ch_of_results]
    print('path_rel classes with no ch_of:', path_less_ch, "\n")


def test_new_searches(vn_classes):
    print("\n%s" % (">" * 80))
    print(">>> RUNNING test_new_searches")
    print(">>> Hit return to proceed...")
    raw_input()
    for print_string, function, role_list, boolean in [
        ("Verbclasses with Agent and Patient thematic roles:", search_by_themroles, ['Agent', 'Patient'], False),
        ('Agent and Patient only classes:', search_by_themroles, ['Agent', 'Patient'], True),
        ("Verbclasses with frames with NP and VERB syntactic roles:", search_by_POS, ['NP', 'VERB'], False),
        ('NP and VERB only classes:', search_by_POS, ['NP', 'VERB'], True),
        ("Verbclasses with frames with (NP, Agent) subcat members:", search_by_cat_and_role, [('NP', 'Agent')], False),
        ('(NP, Agent) and (PREP, None) classes:', search_by_cat_and_role, [('NP', 'Agent'), ('PREP', 'None')], False),
        ('(NP, Agent) and (VERB, None) only classes:', search_by_cat_and_role, [('NP', 'Agent'), ('VERB', 'None')],
         True)]:
        results = function(vn_classes, role_list, boolean)
        ids = []
        if results:
            ids = [vc.ID for vc in results] if isinstance(results[0], GLVerbClass) \
                else [ID for frame, ID in results]
            ids = sorted(list(set(ids)))
        print("\nThere are %s cases of %s" % (len(ids), print_string))
        print('  ', "\n   ".join([id for id in ids]))


## SOME UTILITIES

def print_motion_classes():
    """Print(a list of all classes that have a motion frame.)"""
    vn = VerbNetParser()
    vn_classes = [GLVerbClass(vc) for vc in vn.verb_classes]
    motion_classes = [c for c in vn_classes if c.is_motion_class()]
    print(len(motion_classes))
    for c in motion_classes:
        print(c.ID)


def read_options():
    debug_mode = False
    filelist = None
    run_tests = False
    opts, arg = getopt.getopt(sys.argv[1:], 'dtf:', [])
    for opt, arg in opts:
        if opt == '-t':
            run_tests = True
        if opt == '-d':
            debug_mode = True
        if opt == '-f':
            filelist = arg
    return debug_mode, filelist, run_tests


def run_verbnetparser(debug_mode, filelist):
    """Return the result of running the verbnet parser, using the options to
    determine what to run it over."""
    if debug_mode:
        vn = VerbNetParser(max_count=50)
    elif filelist is not None:
        vn = VerbNetParser(file_list=filelist)
    else:
        vn = VerbNetParser()
    return vn


if __name__ == '__main__':

    debug_mode, filelist, run_tests = read_options()
    vn = run_verbnetparser(debug_mode, filelist)
    gl_classes = [GLVerbClass(vc) for vc in vn.verb_classes]

    if run_tests:
        test_print_first_class(gl_classes)
        test_print_some_classes(gl_classes)
        test_search_by_ID(gl_classes)
        test_ch_of_searches(gl_classes)
        test_new_searches(gl_classes)
    else:
        create_verbnet_gl(gl_classes)
