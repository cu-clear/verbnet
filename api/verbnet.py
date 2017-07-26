"""verbnetparser.py

This program takes in VerbNet XML files and creates several classes for easy
manipulation of the data, for eventual inclusion of GL features to individual
verb frames.

"""

import os
import bs4
from bs4 import BeautifulSoup as soup
from itertools import chain
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
            # (currently 3.3, pointed to in config.txt)
            VERBNET_PATH = get_verbnet_directory("3.3")

        fnames = [f for f in os.listdir(VERBNET_PATH) if f.endswith(".xml")]
        self.filenames = [os.path.join(VERBNET_PATH, fname) for fname in fnames]

        if max_count is not None:
            fnames = fnames[:max_count]
        if file_list is not None:
            fnames = ["%s.xml" % f for f in open(file_list).read().split()]

        self.version = version
        self.parsed_files = self.parse_files()
        self.verb_classes_dict = {}

        for parse in self.parsed_files:
            vc = VerbClass(parse.VNCLASS, version)
            self.verb_classes_dict[vc.ID] = vc
            # Add a key for this verb_class that is JUST the numerical part of the string, as well
            self.verb_classes_dict[vc.ID.split("-")[1]] = vc
            for sub in vc.get_all_subclasses():
                self.verb_classes_dict[sub.ID] = sub
                self.verb_classes_dict["-".join(sub.ID.split("-")[1:])] = sub


    def parse_files(self):
        """Parse a list of XML files using BeautifulSoup. Returns list of parsed
        soup objects"""
        parsed_files = []
        for fname in self.filenames:
            parsed_files.append(soup(open(fname), "lxml-xml"))
        return parsed_files


    def get_verb_classes(self, class_list=[]):
        """Return a list of all classes, which can be scoped by a list of class_ID's,
        each of which can optionally be just the numerical ID.
        look through subclasses too depending on the flag"""
        if class_list:
            return [self.verb_classes_dict[c] for c in class_list]
        else:
            return list(self.verb_classes_dict.values())

    def get_members(self, class_list=[]):
        """Return a list of members from all VerbNet classes
           optionally scoped by a list of classes, and with addition
           a subclass flag to also look in all subclasses"""
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

    def __init__(self, soup, version="3.3"):
        self.soup = soup
        try:
            self.ID = self.get_category("ID", self.soup)[0]
        except IndexError:
            print(self.get_category("ID", self.soup), self.soup)
            self.ID = self.get_category("ID", self.soup.VNSUBCLASS)[0]
        self.version = version
        self.numerical_ID = "-".join(self.ID.split("-")[1:])
        self.members = self.members()
        self.frames = self.frames()
        self.names = [mem.get_category('name')[0] for mem in self.members]
        self.themroles = self.themroles()
        self.subclasses = self.subclass()
        
    def __repr__(self):
        return str(self.ID) + "\n" + str([mem.__repr__() for mem in self.members]) \
               + "\nThemRoles: " + str(self.themroles) \
               + "\nNames: " + str(self.names) \
               + "\nFrames: " + str(self.frames) \
               + "\nSubclasses: " + str(self.subclasses)

    def members(self):
        """Get all members of a verb class"""
        return [Member(mem_soup, self.version) for mem_soup in self.soup.MEMBERS.find_all("MEMBER")]

    #TODO Adam: add and remove are implemented to just work with the soup,
    #TODO it may be cleaner to write the API so that the object can be updated directly
    #TODO and the soup be updated form the object
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

    
    def frames(self):
        """Get all frames for a verb class, seems to be shared by all members
        of the class."""
        return [Frame(frame_soup, self.ID, self.version) for frame_soup in self.soup.FRAMES.find_all("FRAME")]
        
    def themroles(self):
        """Get all the thematic roles for a verb class ans their selectional 
        restrictions."""
        return [ThematicRole(them_soup, self.version) for them_soup in self.soup.THEMROLES.find_all("THEMROLE")]
    
    def subclass(self):
        """Get every subclass listed, if any"""
        subclasses_soup = self.soup.find_all("SUBCLASSES")
        if len(subclasses_soup[0].text) < 1:
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
    
    def __init__(self, soup, version="3.3"):
        self.soup = soup
        self.version = version
        self.name = self.get_category('name')[0]
        self.wn = self.get_category('wn')
        self.grouping = self.get_category('grouping')
        self.features = self.get_category('features')
        
    def __repr__(self):
        return str(self.name + str(self.wn) + str(self.grouping))


class Frame(AbstractXML):
    """Represents a single verb frame in VerbNet, with a description, examples,
    syntax, and semantics """

    def __init__(self, soup, class_ID, version="3.3"):
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




class ThematicRole(AbstractXML):
    """Represents an entry in the "Roles" section in VerbNet, which is basically 
    a list of all roles for a given verb class, with possible selectional 
    restrictions"""
    
    def __init__(self, soup, version="3.3"):
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
    
    def __init__(self, soup, version="3.3"):
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


class SyntacticRole(AbstractXML):
    """Represents a syntactic role assigned to a frame"""
    
    def __init__(self, soup, version="3.3"):
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
    vnp = VerbNetParser(max_count=50)
    count =  len(vnp.parsed_files)
    #print count, 'classes'
    vc = vnp.verb_classes[-1]
    mems = vnp.parsed_files[-1].MEMBERS
    #print
    #print vc.ID
    #print '   names', ' '.join(vc.names)
    #print'   members'
    #for m in mems.find_all("MEMBER"):
    #    print '     ', m
    #results = search(vnp.verb_classes, "motion")
    #print len(results)
    #for frame in results:
    #    print frame
    #print
    for vc in vnp.verb_classes:
#        vc.pp()
        if len(vc.subclasses) >= 1:
            #print vc.ID
            for subclass in vc.subclasses:
                if len(subclass.subclasses) > 0:
                    pass
                    #print '  ', subclass.ID


if __name__ == '__main__':

    test()
