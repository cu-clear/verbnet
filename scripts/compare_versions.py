import sys

local_verbnet_api_path = "/Users/ajwieme/verbs-projects/VerbNet/verbnet"

sys.path.append(local_verbnet_api_path)
from verbnetparser import *
import search
import itertools


# Return the operation from self to compare,
# i.e. update, remove, move, and any other data on that operation
# such as the class moved to, or attribute updates

# update: member still in class, but attributes changed
# delete: member removed from class, and not moved to a new VN class
# move: member moved to a new vn class
def compare_members(from_vn_members, to_vn_members):
  all_changes = {}

  for from_vn_member in from_vn_members:
    # Find that member in to_vn, and if there are differences, record them
    possible_to_vn_members = search.find_members(to_vn_members, name=from_vn_member.name, wn=from_vn_member.wn)
    operations = []
    attr_diffs = None
    all_changes.setdefault(from_vn_member.class_id(), {})

    # First case is that this member is in the same class in to_vn
    possible_match = [m for m in possible_to_vn_members if m.class_id() == from_vn_member.class_id()]

    if possible_match: # If member is in the same class
      to_vn_member = possible_match[0]
      attr_diffs = from_vn_member.compare_attrs(to_vn_member)
    # If there are many possible members, none of which are in the same class
    elif len(possible_to_vn_members) > 1:
      # Then try to see if any of those ALSO exist in from_vn
      # This is to identify an instance of this member in a NEW class
      # to say that this is where it moved to
      for possible_to_vn_member in possible_to_vn_members:
        if len(search.find_members(from_vn_members, class_ID=to_vn_member.class_id(), name=from_vn_member.name)) == 0:
          to_vn_member = possible_to_vn_member
    elif len(possible_to_vn_members) == 1:
      to_vn_member = possible_to_vn_members[0]
      operations.append(("move", to_vn_member.class_id()))
      # Compare the attributes
      attr_diffs = from_vn_member.compare_attrs(to_vn_member)
    else:
      operations.append(("delete", None))

    if attr_diffs:  # If member has updates to its attributes
      operations.append(("update", attr_diffs))

    if operations:
      all_changes[from_vn_member.class_id()][from_vn_member.name[0]] = operations

  return all_changes

def compare_frames(from_vn_frames, to_vn_frames):
  return True


from_vn = VerbNetParser(version="3.2")
to_vn = VerbNetParser(version="3.3")

from_vn.parse_files()
to_vn.parse_files()

from_vn_members = from_vn.get_all_members()
to_vn_members = to_vn.get_all_members()

x = compare_members(from_vn_members, to_vn_members)
# Only print out classes that have changes in them
for k, v in {k: v for k, v in x.items() if v}.items():
  print({k: v})



