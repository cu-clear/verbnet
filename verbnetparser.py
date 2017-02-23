"""verbnetparser.py

This program takes in VerbNet XML files and creates several classes for easy
manipulation of the data, for eventual inclusion of GL features to individual
verb frames.

"""

import os
from bs4 import BeautifulSoup as soup

__author__ = ["Todd Curcuru & Marc Verhagen"]
__date__ = "3/15/2016"
__email__ = ["tcurcuru@brandeis.edu, marc@cs.brandeis.edu"]


def get_verbnet_directory():
    for line in open('config.txt'):
        if line.startswith('VERBNET_PATH'):
            return line.split('=')[1].strip()
    exit('WARNING: could not find a value for VERBNET_PATH')


VERBNET_PATH = get_verbnet_directory()


class VerbNetParser(object):
    """Parse VerbNet XML files, and turn them into a list of BeautifulSoup 
    objects"""
    
    def __init__(self, max_count=None, file_list=None):
        """Take all verbnet files, if max_count is used then take the first max_count
        files, if file_list is used, read the filenames from the file."""
        fnames = [f for f in os.listdir(VERBNET_PATH) if f.endswith(".xml")]
        if max_count is not None:
            fnames = fnames[:max_count]
        if file_list is not None:
            fnames = ["%s.xml" % f for f in open(file_list).read().split()]
        self.filenames = [os.path.join(VERBNET_PATH, fname) for fname in fnames]
        self.parsed_files = self.parse_files()
        self.verb_classes = [VerbClass(parse) for parse in self.parsed_files]

    def parse_files(self):
        """Parse a list of XML files using BeautifulSoup. Returns list of parsed
        soup objects"""
        parsed_files = []
        for fname in self.filenames:
            parsed_files.append(soup(open(fname), "lxml-xml"))
        return parsed_files


class AbstractXML(object):
    """Abstract class to be inherited by other classes that share the same 
    features"""
    
    def __init__(self, soup):
        self.soup = soup
        
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


class VerbClass(AbstractXML):
    """Represents a single class of verbs in VerbNet (all verbs from the same 
    XML file)."""
    # TODO: Check if nested subclasses have issues

    def __init__(self, soup):
        self.soup = soup
        try:
            self.ID = self.get_category("ID", self.soup.VNCLASS)[0]
        except IndexError:
            print self.get_category("ID", self.soup.VNSUBCLASS), self.soup
            self.ID = self.get_category("ID", self.soup.VNSUBCLASS)[0]
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
        return [Member(mem_soup) for mem_soup in self.soup.MEMBERS.find_all("MEMBER")]
    
    def frames(self):
        """Get all frames for a verb class, seems to be shared by all members
        of the class."""
        return [Frame(frame_soup, self.ID) for frame_soup in self.soup.FRAMES.find_all("FRAME")]
        
    def themroles(self):
        """Get all the thematic roles for a verb class ans their selectional 
        restrictions."""
        return [ThematicRole(them_soup) for them_soup in 
                self.soup.THEMROLES.find_all("THEMROLE")]
    
    def subclass(self):
        """Get every subclass listed, if any"""
        subclasses_soup = self.soup.find_all("SUBCLASSES")
        if len(subclasses_soup[0].text) < 1:
            return []
        return [VerbClass(sub_soup) for sub_soup in \
                self.soup.SUBCLASSES.find_all("VNSUBCLASS", recursive=False)]


class Member(AbstractXML):
    """Represents a single member of a VerbClass, with associated name, WordNet
    category, and PropBank grouping."""
    
    def __init__(self, soup):
        self.soup = soup
        self.name = self.get_category('name')
        self.wn = self.get_category('wn')
        self.grouping = self.get_category('grouping')
                
    def __repr__(self):
        return str(self.name + self.wn + self.grouping)


class Frame(AbstractXML):
    """Represents a single verb frame in VerbNet, with a description, examples,
    syntax, and semantics """

    def __init__(self, soup, class_ID):
        self.soup = soup
        self.class_ID = class_ID
        self.description_num = self.get_category('descriptionNumber', 
                                                 self.soup.DESCRIPTION)
        self.primary = self.get_category('primary', self.soup.DESCRIPTION)
        self.secondary = self.get_category('secondary', self.soup.DESCRIPTION)
        self.xtag = self.get_category('xtag', self.soup.DESCRIPTION)
        self.examples = [example.text for example in self.soup.EXAMPLES.find_all("EXAMPLE")]
        self.syntax = self.get_syntax()
        self.predicates = [Predicate(pred) for pred in self.soup.SEMANTICS.find_all("PRED")]
    
    def __repr__(self):
        return "\nDN: " + str(self.description_num) + \
               "\nPrimary: " + str(self.primary) + \
               "\nSecondary: " + str(self.secondary) + \
               "\nXtag: " + str(self.xtag) + \
               "\nExamples: " + str(self.examples) + \
               "\nSyntax: " + str(self.syntax) + \
               "\nPredicates: " + str(self.predicates) + "\n"

    def get_syntax(self):
        raw_roles = [SyntacticRole(role) for role in self.soup.SYNTAX.children]
        roles = []
        for role in raw_roles:
            if role.POS != None:
                roles.append(role)
        return roles


class ThematicRole(AbstractXML):
    """Represents an entry in the "Roles" section in VerbNet, which is basically 
    a list of all roles for a given verb class, with possible selectional 
    restrictions"""
    
    def __init__(self, soup):
        self.soup = soup
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
        
    def __repr__(self):
        return "\n\t" + str(self.role_type) + " / " + str(self.sel_restrictions)
        

class Predicate(AbstractXML):
    """Represents the different predicates assigned to a frame"""
    
    def __init__(self, soup):
        self.soup = soup
        self.value = self.get_category('value')
        self.args = self.soup.find_all('ARG')
        self.argtypes = [(self.get_category('type', arg)[0],
                          self.get_category('value', arg)[0]) for arg in self.args]

    def __str__(self):
        return "%s(%s)" % (self.value[0], ', '.join([at[1] for at in self.argtypes]))

    def __repr__(self):
        return "Value: " + str(self.value[0]) + " -- " + str(self.argtypes)


class SyntacticRole(AbstractXML):
    """Represents a syntactic role assigned to a frame"""
    
    def __init__(self, soup):
        self.soup = soup
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
    print count, 'classes'
    vc = vnp.verb_classes[-1]
    mems = vnp.parsed_files[-1].MEMBERS
    print
    print vc.ID
    print '   names', ' '.join(vc.names)
    print'   members'
    for m in mems.find_all("MEMBER"):
        print '     ', m
    #results = search(vnp.verb_classes, "motion")
    #print len(results)
    #for frame in results:
    #    print frame
    print
    for vc in vnp.verb_classes:
        if len(vc.subclasses) >= 1:
            print vc.ID
            for subclass in vc.subclasses:
                if len(subclass.subclasses) > 0:
                    print '  ', subclass.ID


if __name__ == '__main__':

    test()
