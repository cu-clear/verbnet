'''
VN Version that produces updates is dependent on what config.txt is pointed to

INPUTS: annotation_file.ann member_name, new_vn_version (i.e the version that you want to find the annotation in)
OUTPUTS: updated_annotation_file_with_version_specific_updates, log_file
'''
# There may be an issue where presence of subclasses appears as duplicate classes?
import codecs
import sys
import argparse
import os
local_verbnet_api_path = "../"
sys.path.append(local_verbnet_api_path)
import verbnet, annotation, search

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
    all_old_members = old_vn.get_members()
    if ann.exists_in(old_vn):
      return search.find_members(all_old_members, class_ID=ann.vn_class, name=ann.verb)
    else:
      return search.find_members(all_old_members, name=ann.verb)

def update_annotation_line(ann_line, new_vn, old_vns, log=None):
  """
  Logs changes to log if one is given

  Returns a tuple of (bool marking if the update was successful, updated_annotation)
  """
  # Semlink annotations have mappings, and thus more attributes in a line
  if len(ann_line.strip().split()) > 5:
    ann = annotation.SemLinkAnnotation(ann_line)
  else:
    ann = annotation.VnAnnotation(ann_line)

  # Flag to tell us whether or not the annotation was updated
  success = False

  stats[4] += 1
  # If the verb in this annotation is not mapped directly to desired "new" version of VN
  print("Searching for %s from %s...." % (ann.verb, ann.vn_class))
  if not ann.exists_in(new_vn):
    possible_old_vn_members = find_in_old_versions(ann, old_vns)

    all_new_members = new_vn.get_members()
    updated_vn_members = []
    for vn_member in possible_old_vn_members:
      # search these members for the lookup member by name and wordnet mapping
      updated_vn_members += search.find_members(all_new_members, name=vn_member.name, wn=vn_member.wn)

    """
    Ambiguities in previous versions may all point to the same verb in new version
    I.e one verb may appear in multiple classes in version 3.2, and so this script
    will look for n new verbs in 3.3, where n is the number of times this member
    appears in 3.2. So if all n of those points to the same member of the same class
    in 3.3, then we need to remove those duplicate members from this list
    """
    unique_members = []
    for updated_member in updated_vn_members:
      if (updated_member.name, updated_member.class_id()) not in [u[1] for u in unique_members]:
        unique_members.append([updated_member, (updated_member.name, updated_member.class_id())])

    updated_vn_members = [u[0] for u in unique_members]

    if len(updated_vn_members) == 1: # The verb maps to new version in a new class
      if log:
        log.write("SUCCESS: Found %s from %s in %s in VerbNet version %s" % (ann.verb, ann.vn_class, updated_vn_members[0].class_id(), updated_vn_members[0].version))
      stats[1] += 1
      success = True
      ann.update_vn_info(updated_vn_members[0])
    elif len(updated_vn_members) > 1: # Otherwise there is ambiguity
      if log:
        log.write("ERROR: %s no longer belongs to %s and could belong to %s in VerbNet version %s" % (ann.verb, ann.vn_class, ' OR '.join([u.class_id() for u in updated_vn_members]), updated_vn_members[0].version))
      stats[2] += 1
      success = False
    else: # Otherwise this verb no longer exists in VN
      if log:
        log.write("ERROR: %s from %s in an old version of VerbNet does not have an exact match in version %s" % (ann.verb, ann.vn_class, new_vn.version))
      stats[3] += 1
      success = False
  else:
    if log:
      log.write("SUCCESS: %s is still a reference to %s in %s in VerbNet version %s" % (ann.verb, ann.verb, ann.vn_class, new_vn.version))
    stats[0] += 1
    success = True

  return (success, str(ann))

def generate_updated_annotations(fn, lines, new_vn, old_vns):
  if simulate:
    [update_annotation_line(line, new_vn, old_vns) for line in lines]
  else:
    log = Log(fn.split("/")[-1] + ".log")
    # Directory for new annotations + JUST the annotation filename (no other path info)
    success_fn = new_anns_dir + "/" + fn.split('/')[-1]
    failed_fn = new_anns_dir + "FAILED/" + fn.split('/')[-1]

    # Get updates and organize by successsful/failed updates
    updates = [update_annotation_line(line, new_vn, old_vns, log) for line in lines]
    successful_anns = [ann for success, ann in updates if success == True]
    failed_anns = [ann for success, ann in updates if success == False]

    # Write to respective directories
    with codecs.open(success_fn, "w", encoding="utf-8") as out:
      out.writelines("\n".join(successful_anns))

    with codecs.open(failed_fn, "w", encoding="utf-8") as out:
      out.writelines("\n".join(failed_anns))

if __name__ == '__main__':
  global logs_dir
  global new_anns_dir
  global stats

  stats = [0, 0, 0, 0, 0] #[num_no_change, num_successful_change, num_ambiguous_error, num_no_longer_exist, total]

  # DEFINE ARGS
  parser = argparse.ArgumentParser()
  parser.add_argument('-v', '--version', help='The version of verbnet to update the annotation members to', required=False)
  parser.add_argument('-l', '--logs_dir', help='the directory to output the logs to. Default is ./logs_versionNum', required=False)
  parser.add_argument('-n', '--new_anns_dir', help='The directory to put the new updated annotations. Default is ./new_anns_versionNum', required=False)
  parser.add_argument('-f', '--files', help="Annotation files to update", nargs='+', required=True)
  parser.add_argument('-m', '--mode', help="Pass 'simulate' to run as simulation, which will not write any actual files", required=False)
  args = vars(parser.parse_args())

  # GET VARIABLES FROM ARGS
  ann_fns = args.get("files")
  if args.get("version"):
    new_vn_version = args.get("version")
  else:
    new_vn_version = "3.3"

  if args.get("logs_dir"):
    logs_dir = args.get("logs_dir")
  else:
    logs_dir = "./logs_%s" % new_vn_version
  if args.get("new_anns_dir"):
    new_anns_dir = args.get("new_anns_dir")
  else:
    new_anns_dir = "./new_anns_%s" % new_vn_version

  if args.get("mode") == "simulate":
    simulate = True
  else:
    simulate = False

  ##write a wrapper for testing versions
  try:
    new_vn = verbnet.VerbNetParser(version=new_vn_version)
  except Exception:
    new_vn = verbnet.VerbNetParser(directory=new_vn_version)
  except Exception:
    print ('input version is bad : ' + new_vn)
    sys.exit(2)

  # Make sure the these dirs exist, or create them
  os.makedirs(logs_dir, exist_ok=True)
  os.makedirs(new_anns_dir, exist_ok=True)
  os.makedirs(new_anns_dir + "FAILED", exist_ok=True)

  # Old versions of VN to look through,
  # just hard coding 3.2 for now, can add others as needed
  old_vns = []
  for version in ["3.2"]:
    old_vns.append(verbnet.VerbNetParser(version=version))

  for fn in ann_fns:
    lines = [line.strip() for line in codecs.open(fn, "r", encoding="utf-8")]
    generate_updated_annotations(fn, lines, new_vn, old_vns)

  print_stats = ((float(stats[0]) / float(stats[4])) * 100, (float(stats[1]) / float(stats[4])) * 100, (float(stats[2]) / float(stats[4])) * 100, (float(stats[3]) / float(stats[4])) * 100)
  print("%.2f%% of annotations unchanged, %.2f%% successfully updated, %.2f%% too ambiguous to update, %.2f%% of verbs no longer exist in VN" % print_stats)
