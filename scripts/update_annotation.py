'''
VN Version that produces updates is dependent on what config.txt is pointed to

INPUTS: annotation_file.ann member_name, new_vn_version (i.e the version that you want to find the annotation in)
OUTPUTS: updated_annotation_file_with_version_specific_updates, log_file
'''
#TODO update search to also look in subclasses
# There may be an issue where presence of subclasses appears as duplicate classes?
import sys
sys.path.append("../")
import codecs
from verbnetparser import *
from sys import argv, stderr
import search

class Log(object):
  def __init__(self, filename):
    self.filename = filename
    self.out = '/'.join([logs_dir, self.filename])
    self._generate_outfile()

  def _generate_outfile(self):
    with codecs.open(self.out, "w", encoding="utf-8") as outfile:
      outfile.write("")

  def write(self, message):
    with codecs.open(self.out, "a", encoding="utf-8") as outfile:
      outfile.write(message + "\n")


class Annotation(object):
  def __init__(self, line):
    self.string = line.strip()

    attr_list = self.string.split()

    self.source_file = attr_list[0]
    self.sentence_no = attr_list[1]
    self.token_no = attr_list[2]
    self.verb = attr_list[3]
    self.class_ID = attr_list[4]

  # Check if the ref in the annotation exists in the given version of VN
  def exists_in(self, vn):
    if self.class_ID and vn.get_verb_class(self.class_ID):
        return self.verb.split() in [member.name for member in vn.get_verb_class(self.class_ID).members]
    else:
        return False

  # return the current state of this annotation as a string in the format of the
  # self.string for the original input line
  def line(self):
    return ' '.join([self.source_file, self.sentence_no, self.token_no, self.verb, self.class_ID])

  # Update the line with info from a VN member
  def update_vn_info(self, vn_member):
    # AbstractXML method get_category() will return a list
    # But because it can only have one name, we can take index 0
    self.verb = vn_member.name[0]
    self.class_ID = vn_member.class_id()


def update_annotation_line(ann_line, new_vn, old_vns, log):
  ann = Annotation(ann_line)

  # If the verb in this annotation is not mapped directly to desired "new" version of VN
  if not ann.exists_in(new_vn):
    for old_vn in old_vns:
      all_old_members = old_vn.get_all_members()

      if ann.exists_in(old_vn):
        vn_members = search.find_members(all_old_members, class_ID=ann.class_ID, name=ann.verb.split())
      else:
        vn_members = search.find_members(all_old_members, name=ann.verb.split())

    all_new_members = new_vn.get_all_members()
    updated_vn_members = []
    for vn_member in vn_members:
      # search these members for the lookup member by name and wordnet mapping
      updated_vn_members += search.find_members(all_new_members, name=vn_member.name, wn=vn_member.wn)

    # Ambiguities in previous versions may all point to the same verb in new version
    # so we need to remove the duplicate members from this list
    unique_members = []
    for m in updated_vn_members:
      if (m.name, m.class_id()) not in [u[1] for u in unique_members]:
        unique_members.append([m, (m.name, m.class_id())])

    updated_vn_members = [u[0] for u in unique_members]

    if len(updated_vn_members) == 1:
      ann.update_vn_info(updated_vn_members[0])
      #log.write("SUCCESS: Found %s in %s in VerbNet version %s" % (ann.verb, ann.class_ID, updated_vn_members[0].version()))
      print("SUCCESS: Found %s from %s in VerbNet version %s in %s" % (ann.verb, ann.class_ID, updated_vn_members[0].version(), updated_vn_members[0].class_id()))
    elif len(updated_vn_members) > 1: # Otherwise there is ambiguity
      #log.write("ERROR: %s could belong to %s" % (ann.verb, ' OR '.join([u.class_id() for u in updated_vn_members])))
      print("ERROR: %s in %s could now belong to %s" % (ann.verb, ann.class_ID, ' OR '.join([u.class_id() for u in updated_vn_members])))
      return ''
    else: # Otherwise this verb no longer exists in VN
      # log.write("ERROR: %s no longer exists in VerbNet" % ann.verb)
      print("ERROR: No member named %s (which was previously in class %s) exists in VerbNet" % (ann.verb, ann.class_ID))
      return ''
  else:
    print("EASY PZ MAPPING")

  return ann.line()

def generate_updated_annotations(fn, lines, new_vn, old_vns):
  #log = Log(fn.split("/")[-1] + ".log")
  x = [update_annotation_line(line, new_vn, old_vns, "") for line in lines]
  #with codecs.open(fn, "w", encoding="utf-8") as out:
  #  x = [update_annotation_line(line, new_vn, old_vns, log) for line in lines]
     # Remove the empty lines
  #  x.remove("") if '' in x else None
  #  out.write('\n'.join(x))

if __name__ == '__main__':
  global logs_dir

  if len(argv) < 4:
    stderr.write("USAGE: new_verbnet_version logs_dir annotation_filenames")
    exit(1)

  if len(argv) >= 4:
    new_vn_version = argv[1]
    logs_dir = argv[2]
    ann_fns = argv[3:]

    new_vn = VerbNetParser(version=new_vn_version)
    new_vn.parse_files()

    # Old versions of VN to look through,
    # just hard coding 3.2 for now, can add others as needed
    old_vns = []
    for version in [3.2]:
      old_vns.append(VerbNetParser(version=version))

    for fn in ann_fns:
      lines = [line.strip() for line in codecs.open(fn, "r", encoding="utf-8")]

      generate_updated_annotations(fn, lines, new_vn, old_vns)
