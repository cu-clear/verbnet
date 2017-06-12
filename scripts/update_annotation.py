'''
VN Version that produces updates is dependent on what config.txt is pointed to

INPUTS: annotation_file.ann member_name, new_vn_version (i.e the version that you want to find the annotation in)
OUTPUTS: updated_annotation_file_with_version_specific_updates, log_file
'''
#TODO update search to also look in subclasses
# There may be an issue where presence of subclasses appears as duplicate classes?
import sys
import os
sys.path.append("../")
import codecs
from verbnetparser import *
from annotation import *
from sys import argv, stderr
import argparse
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


def find_in_old_versions(ann, old_vns):
  for old_vn in old_vns:
    all_old_members = old_vn.get_all_members()

    if ann.exists_in(old_vn):
      return search.find_members(all_old_members, class_ID=ann.class_ID, name=ann.verb.split())
    else:
      return search.find_members(all_old_members, name=ann.verb.split())

def update_annotation_line(ann_line, new_vn, old_vns, log):
  ann = Annotation(ann_line)

  # If the verb in this annotation is not mapped directly to desired "new" version of VN
  if not ann.exists_in(new_vn):
    vn_members = find_in_old_versions(ann, old_vns)

    all_new_members = new_vn.get_all_members()
    updated_vn_members = []
    for vn_member in vn_members:
      # search these members for the lookup member by name and wordnet mapping
      updated_vn_members += search.find_members(all_new_members, name=vn_member.name, wn=vn_member.wn)

    # Ambiguities in previous versions may all point to the same verb in new version
    # so we need to remove the duplicate members from this list
    unique_members = []
    for updated_member in updated_vn_members:
      if (updated_member.name, updated_member.class_id()) not in [u[1] for u in unique_members]:
        unique_members.append([updated_member, (updated_member.name, updated_member.class_id())])

    updated_vn_members = [u[0] for u in unique_members]

    if len(updated_vn_members) == 1: # The verb maps to new version in a new class
      ann.update_vn_info(updated_vn_members[0])
      log.write("SUCCESS: Found %s in %s in VerbNet version %s" % (ann.verb, ann.class_ID, updated_vn_members[0].version()))
    elif len(updated_vn_members) > 1: # Otherwise there is ambiguity
      log.write("ERROR: %s no longer belongs to %s and could belong to %s" % (ann.verb, ann.class_ID, ' OR '.join([u.class_id() for u in updated_vn_members])))
      return None
    else: # Otherwise this verb no longer exists in VN
      log.write("ERROR: %s no longer exists in VerbNet" % ann.verb)
      return None
  else:
    log.write("SUCCESS: %s is still a reference to %s in %s" % (ann.verb, ann.verb, ann.class_ID))

  return str(ann)

def generate_updated_annotations(fn, lines, new_vn, old_vns):
  log = Log(fn.split("/")[-1] + ".log")
  # Directory for new annotations + JUST the annotation filename (no other path info)
  new_fn = new_anns_dir + "/" + fn.split('/')[-1]
  with codecs.open(new_fn, "w", encoding="utf-8") as out:
    x = [update_annotation_line(line, new_vn, old_vns, log) for line in lines]
    # Remove the lines wherein it was removed and thus returned None
    x = [l for l in x if l != None]
    out.write('\n'.join(x))

if __name__ == '__main__':
  global logs_dir
  global new_anns_dir

  # DEFINE ARGS
  parser = argparse.ArgumentParser()
  parser.add_argument('-v', '--version', help='The version of verbnet to update the annotation members to', required=True)
  parser.add_argument('-l', '--logs_dir', help='the directory to output the logs to. Default is ./logs_versionNum', required=False)
  parser.add_argument('-n', '--new_anns_dir', help='The directory to put the new updated annotations. Default is ./new_anns_versionNum', required=False)
  parser.add_argument('-f', '--files', help="Annotation files to update", nargs='+', required=True)
  args = vars(parser.parse_args())

  # GET VARIABLES FROM ARGS
  new_vn_version = args.get("version")
  ann_fns = args.get("files")
  if args.get("logs_dir"):
    logs_dir = args.get("logs_dir")
  else:
    logs_dir = "./logs_%s" % new_vn_version
  if args.get("new_anns_dir"):
    new_anns_dir = args.get("new_anns_dir")
  else:
    new_anns_dir = "./new_anns_%s" % new_vn_version

  new_vn = VerbNetParser(version=new_vn_version)
  new_vn.parse_files()

  # Make sure the these dirs exist, or create them
  os.makedirs(logs_dir, exist_ok=True)
  os.makedirs(new_anns_dir, exist_ok=True)

  # Old versions of VN to look through,
  # just hard coding 3.2 for now, can add others as needed
  old_vns = []
  for version in ["3.2"]:
    old_vns.append(VerbNetParser(version=version))

  for fn in ann_fns:
    lines = [line.strip() for line in codecs.open(fn, "r", encoding="utf-8")]
    generate_updated_annotations(fn, lines, new_vn, old_vns)
