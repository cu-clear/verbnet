"""verbnetparser.py

This program takes in VerbNet XML files and creates several classes for easy
manipulation of the data, for eventual inclusion of GL features to individual
verb frames.

"""

import os
import bs4
import re

__author__ = ["Todd Curcuru & Marc Verhagen"]
__date__ = "3/15/2016"
__email__ = ["tcurcuru@brandeis.edu, marc@cs.brandeis.edu"]


def get_verbnet_directory(version):
    for line in open(os.path.join(os.path.dirname(__file__), 'config.txt')):
        if line.startswith('VERBNET_PATH') and line.split("=")[0].strip().endswith(version):
            return line.split('=')[1].strip()
    exit('WARNING: could not find a value for VERBNET_PATH version %s' % version)


class VerbNetParser(object):
    """Parse VerbNet XML files, and turn them into a list of BeautifulSoup
    objects"""

    def __init__(self, max_count=None, directory=None, file_list=None, version=None):
        """Take all verbnet files, if max_count is used then take the first max_count
        files, if file_list is used, read the filenames from the file."""
        if directory:
            VERBNET_PATH = directory
        elif version:
            VERBNET_PATH = get_verbnet_directory(version)
        else:
            # If no files or version provided, look for the most up-to-date version
            # (currently 3.4, pointed to in config.txt)
            VERBNET_PATH = get_verbnet_directory("3.4")

        fnames = [f for f in os.listdir(VERBNET_PATH) if f.endswith(".xml")]
        self.filenames = [os.path.join(VERBNET_PATH, fname) for fname in fnames]

        if max_count is not None:
            fnames = fnames[:max_count]
        if file_list is not None:
            fnames = ["%s.xml" % f for f in open(file_list).read().split()]

        self.version = version
        self.parsed_files = self.parse_files()
        self.verb_classes_dict = {}
        # For lookup when classname is not available
        # As in the annotation files
        self.verb_classes_numerical_dict = {}

        for parse in self.parsed_files:
            vc = VerbClass(parse.VNCLASS, version)
            self.verb_classes_dict[vc.ID] = vc
            self.verb_classes_numerical_dict["-".join(vc.ID.split("-")[1:])] = vc
            for sub in vc.get_all_subclasses():
                self.verb_classes_dict[sub.ID] = sub
                self.verb_classes_numerical_dict["-".join(sub.ID.split("-")[1:])] = sub

    def parse_files(self):
        """Parse a list of XML files using BeautifulSoup. Returns list of parsed
        soup objects"""
        parsed_files = []
        for fname in self.filenames:
            parsed_files.append(bs4.BeautifulSoup(open(fname), "lxml-xml"))
        return parsed_files

    def get_verb_classes(self, class_list=[]):
        """Return a list of all classes, which can be scoped by a list of class_ID's.
        look through subclasses too depending on the flag"""
        if class_list:
            return [self.verb_classes_dict[c] for c in class_list]
        else:
            return list(self.verb_classes_dict.values())

    def get_verb_classes_by_members(self, members_list):
        """Return a list of all classes that have any members with names in the given list"""
        if type(members_list) != list:
            members_list = [members_list]

        if type(members_list[0]) == Member:
            members_list = [m.name for m in members_list]
        elif type(members_list[0]) != str:
            raise Exception("get_verb_classes_by_members requires a list of Members or strings")

        v_classes = []
        for vc in self.verb_classes_dict.values():
            if list(set(members_list) & set([m.name for m in vc.members])):
                v_classes.append(vc)
                continue
        return v_classes

    def get_members(self, class_list=[]):
        """Return a list of members from all VerbNet classes
           optionally scoped by a list of class_ID's"""
        members = []

        for vc in self.get_verb_classes(class_list=class_list):
            members += vc.members

        return members

    def get_themroles(self, class_list=[]):
        """Just like get_members, but for themroles"""
        themroles = []

        for vc in self.get_verb_classes(class_list=class_list):
            themroles += vc.themroles

        return themroles

    def get_frames(self, class_list=[]):
        """Just like get_members, but for frames"""
        frames = []

        for vc in self.get_verb_classes(class_list=class_list):
            frames += vc.frames

        return frames

    def check_vn(self, vn_class, verb, vn, update=False):
        if not vn_class:
            return False
        if vn_class in self.verb_classes_numerical_dict:
            if verb in [m.name for m in self.verb_classes_numerical_dict[vn_class].members]:
                return vn_class
        if update:
            if vn_class not in self.verb_classes_numerical_dict:
                if vn_class.split("-")[0] in self.verb_classes_numerical_dict:
                    vn_class = vn_class.split("-")[0]
                else:
                    return False

            for subclass in [self.verb_classes_numerical_dict[vn_class.split("-")[0]]] + self.verb_classes_numerical_dict[vn_class.split("-")[0]].get_all_subclasses():
                if verb in [m.name for m in subclass.get_members()]:
                    return subclass.numerical_ID
        return False

class AbstractXML(object):
    """Abstract class to be inherited by other classes that share the same
    features"""

    def __init__(self, soup):
        self.soup = soup
        self.etree = etree.fromstring(self.pp())

    def get_category(self, cat, special_soup=None):
        """Extracts the category from a soup, with the option to specify a soup.

        For MEMBERs, we have:
        name (lexeme),
        wn (WordNet category)
        grouping (PropBank grouping)"""
        if not special_soup:
            special_soup = self.soup
        try:
            return special_soup.get(cat).split()
        except AttributeError:
            return []

    # list of dicts of {attribute_name: attribute_value} for self and each child node
    # One dict per node
    def all_attrs(self):
        a = []
        for element in self.soup.find_all():
            a.append(element.attrs)

        return a

    # Assumes self and compare are both are of the same type of object
    # Return a dict of {changed_attr: new value in compare}
    def compare_attrs(self, compare):
        updates = {}
        for k, v in self.soup.attrs.items():
            compare_attrs = compare.soup.attrs
            if compare_attrs.get(k) != v:
                updates[k] = compare_attrs.get(k)

        return updates

    def class_id(self, subclasses=True):
        '''
          Recursively find the closest parent node (n nodes up)
          that is a VNCLASS or VNSUBCLASS (if subclasses flag set to True)
          in order to get the soup object, and grab the ID
        '''
        if subclasses:
            id_nodes = ["VNCLASS", "VNSUBCLASS"]
        else:
            id_nodes = ["VNCLASS"]

        def get_class_id(soup):
            if soup.name in id_nodes:
                return soup["ID"]
            else:
                return get_class_id(soup.parent)

        return get_class_id(self.soup)

    def numerical_class_id(self):
        return "-".join(self.class_id().split("-")[1:])

    def get_class(self, subclasses=True):
        '''
          Recursively find the closest parent node (n nodes up)
          that is a VNCLASS or VNSUBCLASS (if subclasses flag set to True)
          in order to get its ID
        '''
        if subclasses:
            id_nodes = ["VNCLASS", "VNSUBCLASS"]
        else:
            id_nodes = ["VNCLASS"]

        def get_class_id(soup):
            if soup.name in id_nodes:
                return soup['ID']
            else:
                return get_class_id(soup.parent)

        return get_class_id(self.soup)

    def pp(self):
        # Better indentation for more readable XML
        indent = re.compile(r'^(\s*)', re.MULTILINE)
        return indent.sub(r'\1' * 4, self.soup.prettify())


class VerbClass(AbstractXML):
    """Represents a single class of verbs in VerbNet (all verbs from the same
    XML file)."""
    # TODO: Check if nested subclasses have issues

    def __init__(self, soup, version="3.4"):
        self.soup = soup
        try:
            self.ID = self.get_category("ID", self.soup)[0]
        except IndexError:
            print(self.get_category("ID", self.soup), self.soup)
            self.ID = self.get_category("ID", self.soup.VNSUBCLASS)[0]
        self.version = version
        self.numerical_ID = "-".join(self.ID.split("-")[1:])
        self.members = self._members()
        self.frames = self._frames()
        self.names = [mem.get_category('name')[0] for mem in self.members]
        self.themroles = self._themroles()
        self.subclasses = self._subclass()

    def __repr__(self):
        return str(self.ID) + "\n" + str([mem.__repr__() for mem in self.members]) \
               + "\nThemRoles: " + str(self.themroles) \
               + "\nNames: " + str(self.names) \
               + "\nFrames: " + str(self.frames) \
               + "\nSubclasses: " + str(self.subclasses)

    def __lt__(self, other):
        return self.ID < other.ID

    def __gt__(self, other):
        return self.ID > other.ID

    def is_subclass(self):
        """
        If the highest class id of the soup object is its own ID,
        then it is not a subclass of another class.

        Return True or False
        """

        return self.class_id(subclasses=False) != self.ID

    def _members(self):
        """Get all members of a verb class"""
        return [Member(mem_soup, self.ID, self.version) for mem_soup in self.soup.MEMBERS.find_all("MEMBER")]

    #TODO Adam: add and remove are implemented to just work with the soup,
    #TODO it may be cleaner to write the API so that the object can be updated directly
    #TODO and the soup be updated from the object
    def remove_member(self, input_member):
        '''
            Remove the member object with a given name, or that matches a given member object
            from this class.

            Returns the soup for the removed member
        '''

        if type(input_member) == Member:
            input_member_name = input_member.name[0]
        elif type(input_member) == str:
            input_member_name = input_member

        # Should only ever be one member with a unique name in a class,
        # so we can search by name and use [0]
        return self.soup.MEMBERS.find_all("MEMBER", {"name": input_member_name})[0].extract()

    def add_member(self, input_member):
        '''
          Add the member object, or soup object representing the member to this class,
          may need to add validation for the soup object later,
          and support for other inputs such as XML, or dictionary of info
        '''

        if type(input_member) == Member:
            mem_soup = input_member.soup
        elif type(input_member) == bs4.element.Tag:
            mem_soup = input_member

        # Should only ever be one member with a unique name in a class,
        # so we can search by name and use [0]
        self.soup.MEMBERS.append(mem_soup)

    def get_members(self):
        return self.members


    def _frames(self):
        """Get all frames for a verb class, seems to be shared by all members
        of the class."""
        return [Frame(frame_soup, self.ID, self.version) for frame_soup in self.soup.FRAMES.find_all("FRAME")]

    def frames_and_subclass_frames(self):
        return [Frame(frame_soup, self.ID, self.version) for frame_soup in self.soup.find_all("FRAME")]

    def _themroles(self):
        """Get all the thematic roles for a verb class ans their selectional
        restrictions."""
        return [ThematicRole(them_soup, self.version) for them_soup in self.soup.THEMROLES.find_all("THEMROLE")]

    def _subclass(self):
        """Get every subclass listed, if any"""
        subclasses_soup = self.soup.find_all("SUBCLASSES")        
        if len(subclasses_soup) < 1 or len(subclasses_soup[0].text) < 1:
            return []
        return [VerbClass(sub_soup, self.version) for sub_soup in \
                self.soup.SUBCLASSES.find_all("VNSUBCLASS", recursive=False)]

    def get_all_subclasses(self):
        def get_subclasses_gen(vc):
            for sub in vc.subclasses:
                if sub.subclasses:
                    # Yield the subclass before iterating over its children
                    yield sub
                    for x in get_subclasses_gen(sub):
                        yield x
                else:
                    # termination case for a branch, use yield so function continues to iterate
                    yield sub


        return [s for s in get_subclasses_gen(self)]


class Member(AbstractXML):
    """Represents a single member of a VerbClass, with associated name, WordNet
    category, and PropBank grouping."""

    def __init__(self, soup, vnc, version="3.4"):
        self.soup = soup
        self.version = version
        self.name = self.get_category('name')[0]
        self.wn = self.get_category('wn')
        self.grouping = self.get_category('grouping')
        self.features = self.get_category('features')
        self.verbnet_key = self.get_category('verbnet_key')

    def __repr__(self):
        return str(self.name + " " + str(self.verbnet_key))

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def update_name(self, name):
        """
        Update the name of a Member, and it's soup for XML output
        """
        self.name = name
        self.soup["name"] = name


class Frame(AbstractXML):
    """Represents a single verb frame in VerbNet, with a description, examples,
    syntax, and semantics """

    def __init__(self, soup, class_ID, version="3.4"):
        self.soup = soup
        self.version = version
        self.class_ID = class_ID
        self.description_num = self.get_category('descriptionNumber',
                                                 self.soup.DESCRIPTION)
        self.primary = self.get_category('primary', self.soup.DESCRIPTION)
        self.secondary = self.get_category('secondary', self.soup.DESCRIPTION)
        self.xtag = self.get_category('xtag', self.soup.DESCRIPTION)
        self.examples = [example.text for example in self.soup.EXAMPLES.find_all("EXAMPLE")]
        self.syntax = self.get_syntax()
        self.predicates = [Predicate(pred, self.version) for pred in self.soup.SEMANTICS.find_all("PRED")]

    def __repr__(self):
        return "\nDN: " + str(self.description_num) + \
               "\nPrimary: " + str(self.primary) + \
               "\nSecondary: " + str(self.secondary) + \
               "\nXtag: " + str(self.xtag) + \
               "\nExamples: " + str(self.examples) + \
               "\nSyntax: " + str(self.syntax) + \
               "\nPredicates: " + str(self.predicates) + "\n"

    def pp_syntax(self):
        return " ".join(self.primary)

    def pp_semantics(self):
        return str(self.predicates)

    def get_syntax(self):
        raw_roles = [SyntacticRole(role, self.version) for role in self.soup.SYNTAX.children]
        roles = []
        for role in raw_roles:
            if role.POS != None:
                roles.append(role)
        return roles

    def contains(self, input):
        '''
            input: a Frame object, or a list of Predicates,
            which is also the return type of Frame.predicates
        '''
        if type(input) == list:
            search_predicates = input
        elif type(input) == Frame:
            search_predicates = input.predicates
        else:
            raise Exception(str(type(input)) + " is not a valid input type type")

        predicates = self.predicates
        matches = []

        # Updated to be O(2n) to catch cases where there are multiple preds with the same name
        for search_pred in search_predicates:
            for predicate in predicates:
                # Reset match flag
                match = False
                if predicate.value == search_pred.value and predicate.contains(search_pred):
                    # We got a match! Go to next search_pred
                    match = True
                    break

            # If this loop completes without finding a match, we must be missing a matching pred
            if not match:
                return False

        # If loop completes, all search_preds must have a match, note this also
        # Means if no search_preds are supplied, the method will return True
        return True

    def add_predicates(self, add_preds, reference_pred=None):
        '''
        add_preds: list of preds to add in this frame
        reference_pred: the existing pred to

        Add the list of predicate objects, or soup objects
        may need to add validation for the soup object later,
        and support for other inputs such as XML, or dictionary of info
        '''
        if reference_pred:
            if type(reference_pred) == Predicate:
                ref_soup = reference_pred.soup
            elif type(reference_pred) == bs4.element.Tag and reference_pred.name == PRED:
                ref_soup = reference_pred
            else:
                raise Exception("Reference predicate must be a Predicate object or soup object at the PRED node")

        for add_pred in add_preds:
            if type(add_pred) == Predicate:
                pred_soup = add_pred.soup
            elif type(add_pred) == bs4.element.Tag and add_pred.name == PRED:
                pred_soup = add_pred
            else:
                raise Exception("Add predicate requires a list of Predicate objects or soup objects at the PRED node")

            if reference_pred:
                ref_soup.insert_after(pred_soup)
            else:
                self.soup.SEMANTICS.append(pred_soup)

        self._reset_preds()

    def remove_predicates(self, remove_preds):
        '''
        Remove the predicate objects with a given name, or that matches a given member object
        from this class.

        Returns the soup for the removed member
        '''
        removed = []
        for remove_pred in remove_preds:
            if type(remove_pred) == bs4.element.Tag:
                remove_pred = Predicate(remove_pred)
            elif type(remove_pred) != Predicate:
                raise Exception("remove_predicates accepts a list of Predicate or soup objects")

            for frame_pred in self.predicates:
                if frame_pred.value == remove_pred.value and frame_pred.contains(remove_pred.args):
                    if frame_pred.soup.extract():
                        removed.append(frame_pred)
        self._reset_preds()
        return removed

    def _reset_preds(self):
        self.predicates = [Predicate(pred, self.version) for pred in self.soup.SEMANTICS.find_all("PRED")]


class ThematicRole(AbstractXML):
    """Represents an entry in the "Roles" section in VerbNet, which is basically
    a list of all roles for a given verb class, with possible selectional
    restrictions"""

    def __init__(self, soup, version="3.4"):
        self.soup = soup
        self.version = version
        self.role_type = self.get_category('type')[0]
        self.sel_restrictions = self.sel_restrictions(self.soup.SELRESTRS)

    def sel_restrictions(self, soup):
        """Finds all the selectional restrictions of the thematic roles and
        returns them as a string"""
        try:
            a = soup.contents                 # Get rid of \n noise
        except AttributeError:
            return
        if len(self.soup.contents) == 0:        # empty SELRESTRS
            return []
        elif len([child for child in soup.children]) == 0:
            return self.get_category('Value', soup) + self.get_category('type', soup)
        elif len(self.get_category('logic', soup)) > 0:
            children = ['OR'] + [self.sel_restrictions(child) for child in soup.children]
            return [child for child in children if child is not None]
        elif len([child for child in soup.children]) == 3:
            return self.sel_restrictions(soup.find_all('SELRESTR')[0])
        else:
            return ['AND'] + [self.sel_restrictions(child) for child in soup.find_all('SELRESTR')]

    def compare_selres_with(self, other_themrole):
        sel_restrictions = self.sel_restrictions
        other_sel_restrictions = other_themrole.sel_restrictions

        if len(sel_restrictions) in [2, 0] and len(other_sel_restrictions)in [2, 0]:
            '''
                Both have only one, or no restrictions
            '''
            return list(set(sel_restrictions) - set(other_sel_restrictions))
        elif len(sel_restrictions) in [2, 0] or len(other_sel_restrictions) in [2, 0]:
            '''
              One has multiple, one has only one, or no restrictions
            '''
            if len(sel_restrictions) > 1 and isinstance(sel_restrictions[1], list): # it has multiple selres
                if other_sel_restrictions in sel_restrictions:
                    sel_restrictions.pop(sel_restrictions.index(other_sel_restrictions))
                    return sel_restrictions
                else:
                    return other_sel_restrictions + sel_restrictions
            else: # other has the multiple selres
                # Just do the inverse
                if sel_restrictions in other_sel_restrictions:
                    other_sel_restrictions.pop(other_sel_restrictions.index(sel_restrictions))
                    return other_sel_restrictions
                else:
                    return sel_restrictions + other_sel_restrictions
        else:
            '''
              Both have multiple restrictions
            '''
            diffs = []
            for i, selres in enumerate(sel_restrictions):
                if isinstance(selres, list):
                    if len(other_sel_restrictions) > i:
                        if selres != other_sel_restrictions[i]:
                            diffs.append(other_sel_restrictions[i])
                    else:
                        diffs.append(selres)

            return diffs

    def identical_selres_with(self, other_themrole):
        return False if self.compare_selres_with(other_themrole) else True

    def __repr__(self):
        return str(self.role_type) + " : " + str(self.sel_restrictions)


class Predicate(AbstractXML):
    """Represents the different predicates assigned to a frame"""

    def __init__(self, soup, version="3.4"):
        self.soup = soup
        self.version = version
        self.value = self.get_category('value')
        self.args = self.soup.find_all('ARG')
        self.argtypes = [(self.get_category('type', arg)[0],
                          self.get_category('value', arg)[0]) for arg in self.args]

    def __str__(self):
        return "%s(%s)" % (self.value[0], ', '.join([at[1] for at in self.argtypes]))

    def __repr__(self):
        return "Value: " + str(self.value[0]) + " -- " + str(self.argtypes)

    def contains(self, input):
        '''
            input: a Predicate object, or a BeatifulSoup result set,
            which is the return type of predicate.args
        '''
        if type(input) == bs4.element.ResultSet:
            search_args = input
        elif type(input) == Predicate:
            search_args = input.args
        else:
            raise Exception(str(type(input)) + " is not a valid input type")

        # Hacky way to ignore question marks (?) in arg values
        argtypes = [(argtype[0].replace('?', ''), argtype[1].replace('?', '')) for argtype in self.argtypes]

        for search_arg in search_args:
            # Use the same hacky way to ignore question marks (?) in arg values
            if (self.get_category("type", search_arg)[0].replace('?', ''), self.get_category("value", search_arg)[0].replace('?', '')) not in argtypes: # one of the search_args is not an arg of this predicate
                return False

        # All args have been checked and have a match, thus not returning false
        # This will also return if there were no input preds to loop over
        return True

    def add_args(self, add_args, order="first"):
        """
        Add an ARG to a predicate

         add_args: list of soup objects corresponding with the ARG node
         order: optional, add it as the first or last arg. Default to first
        """
        for i, add_arg in enumerate(add_args):
            if type(add_arg) != bs4.element.Tag or add_arg.name != "ARG":
                raise Exception("add_args only accepts a list of soup objects at the ARG node")

            if order == "last":
                self.soup.ARGS.append(add_arg)
            elif order == "first":
                self.soup.ARGS.insert(i, add_arg)
            else:
                raise Exception("order parameter must be 'first' or 'last'")

        self._reset_args()

    def remove_args(self, remove_args):
        '''
        Remove the matching soup for args of this predicate
        Takes a list of soup objects corresponding to ARGS
        '''
        removed = []
        for remove_arg in remove_args:
            if type(remove_arg) != bs4.element.Tag or remove_arg.name != "ARG":
                raise Exception("remove_args only accepts a list of soup objects at the ARG node")

            for pred_arg in self.soup.ARGS.find_all("ARG"):
                if pred_arg["type"] == remove_arg["type"] and pred_arg["value"] == remove_arg["value"]:
                    removed.append(pred_arg.extract())
        # Reset the arg attributes to reflect the update
        self._reset_args()
        return removed

    def _reset_args(self):
        self.args = self.soup.find_all('ARG')
        self.argtypes = [(self.get_category('type', arg)[0],
                          self.get_category('value', arg)[0]) for arg in self.args]


class SyntacticRole(AbstractXML):
    """Represents a syntactic role assigned to a frame"""

    def __init__(self, soup, version="3.4"):
        self.soup = soup
        self.version = version
        self.POS = self.soup.name
        self.value = self.get_category('value')
        self.restrictions = self.restrictions()

    def restrictions(self):
        """Check for selectional restrictions
        NP has value and SYNRESTRS which have Value and type
        PREP has value sometimes and SELRESTRS with Value and type
        SYN/SELRESTRS can be empty
        VERB seems empty"""
        try:
            if str(self.POS) == "PREP":
                raw_children = self.soup.find_all('SELRESTR')
            else:
                raw_children = self.soup.find_all('SYNRESTR')
        except AttributeError:
            return None

        children = []
        for child in raw_children:
            children.append(self.get_category('Value', child)[0])
            children.append(self.get_category('type', child)[0])
        return children

    def __repr__(self):
        return "\n" + str(self.POS) + "\tValue: " + str(self.value) \
                    + "\tRestrs: " + str(self.restrictions)


def search(verbclasslist, pred_type=None, themroles=None, synroles=None, semroles=None):
    """Returns frames for verbclasses that match search parameters
    TODO: figure out what it means to search for themroles, synroles, and semroles"""
    successes = []
    for vc in verbclasslist:
        for frame in vc.frames:
            for pred in frame.predicates:
                if pred.value[0] == pred_type:
                    successes.append((vc, frame))
    return successes


def test():
    # vnp = VerbNetParser(directory='/Users/ghazalehk/codes/github/verbnet/verbnet3.4')
    #
    # for v in vnp.get_members():
    #     print(v)
    #     pass
    pass

if __name__ == '__main__':

    test()
