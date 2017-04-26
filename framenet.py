#from verbnetparser import VerbNetParser, VerbClass, Member
from bs4 import BeautifulSoup as soup
from writer import HtmlFNWriter

def get_framenet_mappings():
  for line in open('config.txt'):
    if line.startswith('FRAMENET_MAPPING_PATH'):
      return line.split('=')[1].strip()
  exit('WARNING: could not find a value for VERBNET_PATH')

FRAMENET_MAPPING_PATH = get_framenet_mappings()
'''
vn = VerbNetParser()
vn.parse_files()
'''

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

  def pp(self):
    return self.soup.prettify()


class FrameNet(AbstractXML):
  def __init__(self):
    self.soup = soup(open(FRAMENET_MAPPING_PATH), "lxml-xml")
    self.mappings = [Mapping(mapping_soup) for mapping_soup in self.soup.find_all("vncls")]
    self.frames = self._frames()

  def _frames(self):
    names_and_frames = {}

    for mapping in self.mappings:
      # If there is already a frame with this name
      if mapping.name in names_and_frames.keys():
        # Add the mapping as part of that frame
        names_and_frames[mapping.name].mappings.append(mapping)
      else:
        names_and_frames[mapping.name] = Frame([mapping])

    return list(names_and_frames.values())

  def get_pure_frames(self, threshhold=.5):
    pure_frames = []

    for frame in self.frames:
      if frame.purity() > threshhold:
        pure_frames.append(frame)

    return pure_frames


class Mapping(AbstractXML):
  def __init__(self, soup):
    self.soup = soup
    self.name = self.get_category('fnframe')[0]
    self.verbnet_class_ID = self.get_category('class')[0]
    self.verbnet_member_name = self.get_category('vnmember')[0]

class Frame(object):
  def __init__(self, mappings):
    self.mappings = mappings
    self.name = mappings[0].name

  def get_vn_members(self):
    return [Member(mapping.verbnet_member_name, mapping.verbnet_class_ID) for mapping in self.mappings]


  def get_vn_classes(self):
    class_and_members = {}

    for member in self.get_vn_members():
      class_and_members.setdefault(member.class_ID, []).append(member)

    return [VN_class(c, m) for c, m in class_and_members.items()]

  def purity(self):
    return self.biggest_vn_class().size() / len(self.get_vn_members())

  def biggest_vn_class(self):
    vn_classes = self.get_vn_classes()
    biggest = vn_classes[0]
    for vn_class in vn_classes:
      if vn_class.size() > biggest.size():
        biggest = vn_class

    return biggest


class VN_class(object):
  def __init__(self, ID, members=[]):
    self.ID = ID
    self.members = members

  def size(self):
    return len(self.members)


class Member(object):
  def __init__(self, name, class_ID):
    self.name = name
    self.class_ID = class_ID

def create_verbnet_framenet(fn):
  # If we need more VN info to go in these FN frames,
  # Add that here by importing VerbNetParser
  writer = HtmlFNWriter()
  writer.write(fn)
  writer.finish()

fn = FrameNet()
#print([(f.name, f.purity()) for f in fn.get_pure_frames()])
create_verbnet_framenet(fn)