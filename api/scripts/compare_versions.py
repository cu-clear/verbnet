import sys

local_verbnet_api_path = "../"

sys.path.append(local_verbnet_api_path)
from verbnet import *
import search
import itertools


class Change():
  """
  Class to represent a change, this will be the value pointed to by a class name key
  """

  def __init__(self, element_name, element_type, change_type, old_class=None, notes=""):
    if element_type not in ['member', 'role', 'frame']:
      raise Exception(element_type + " is not a valid element type")
    if change_type not in ['insert', 'delete', 'move', 'update']:
      raise Exception(change_type + " is not a valid change type")
    if change_type == 'move' and element_type != 'member':
      raise Exception('cannot have a  \'move\' type on an element that is not a member')
    # also should probably fail on invalid old_class, but would require VN class lookup (strict) or regex matching (loose)

    self.element_name = element_name
    self.element_type = element_type
    self.change_type = change_type
    self.old_class = old_class
    self.notes = notes

  def __eq__(self, other):
    if type(self) == type(other):
      return (
      self.element_name == other.element_name and self.element_type == other.element_type and self.change_type == other.change_type and self.old_class == other.old_class)
    else:
      return False

  def __hash__(self):
    return (hash(self.element_name) + hash(self.element_type) + hash(self.change_type) + hash(self.old_class))

  def __str__(self):
    return str(
      self.element_name + " " + self.element_type + " " + self.change_type + " " + self.old_class + " " + self.notes).strip()


def compare_members(from_vn_members, to_vn_members):
  '''
    returns a dict of {to_vn_class: [Change objects]}

    update: member still in class, but attributes changed
    delete: member removed from class, and not moved to a new VN class
    insert: member inserted to the class, and is newly added to VN
    move: member moved from the class to a new vn class
  '''
  all_changes = {}

  for from_vn_member in from_vn_members:
    # Find that member in to_vn_members, and if there are differences, record them
    possible_to_vn_members = search.find_members(to_vn_members, name=from_vn_member.name, wn=from_vn_member.wn)
    changes = []
    to_vn_member = None
    attr_diffs = None

    # First case is that this member is in the same class in to_vn
    possible_match = [m for m in possible_to_vn_members if m.class_id() == from_vn_member.class_id()]

    if possible_match:  # If member is in the same class
      to_vn_member = possible_match[0]
      attr_diffs = from_vn_member.compare_attrs(to_vn_member)
    # If there are many possible members, none of which are in the same class
    elif len(possible_to_vn_members) > 1:
      # Then try to see if any of those ALSO exist in from_vn
      # This is to identify an instance of this member in a NEW class
      # to say that this is where it moved to
      for possible_to_vn_member in possible_to_vn_members:
        if len(search.find_members(from_vn_members, class_ID=possible_to_vn_member.class_id(),
                                   name=from_vn_member.name)) == 0:
          to_vn_member = possible_to_vn_member
          changes.append(Change(from_vn_member.name, "member", "move", from_vn_member.class_id()))
          # Compare the attributes
          attr_diffs = from_vn_member.compare_attrs(to_vn_member)
    elif len(possible_to_vn_members) == 1:
      to_vn_member = possible_to_vn_members[0]
      changes.append(Change(from_vn_member.name, "member", "move", from_vn_member.class_id()))
      # Compare the attributes
      attr_diffs = from_vn_member.compare_attrs(to_vn_member)
    else:
      changes.append(Change(from_vn_member.name, "member", "delete", from_vn_member.class_id()))

    if attr_diffs:  # If member has updates to its attributes
      changes.append(Change(from_vn_member.name, "member", "update", from_vn_member.class_id(),
                            ', '.join(["%s: %s" % (attr, diff) for attr, diff in attr_diffs.items()])))

    if changes:
      all_changes[to_vn_member.class_id() if to_vn_member else to_vn_member] = changes

  '''
    Lastly, we have to get all to_vn_members that did not exist in
    from_vn_members to record all of the rest of the insert operations
    Get string name in order to hash it for the set,
    and then change it back to a list in order to work with search.find_members
  '''
  for name, class_ID in list(set([(m.name, m.class_id()) for m in to_vn_members]) - set(
      [(m.name, m.class_id()) for m in from_vn_members])):
    inserted_member = search.find_members(to_vn_members, class_ID=class_ID, name=[name])
    if inserted_member:
      all_changes.setdefault(inserted_member[0].class_id(), []).append(
        Change(inserted_member[0].name, "member", "insert", notes=inserted_member[0].pp()))

  return all_changes


def compare_themroles(from_vn_themroles, to_vn_themroles):
  '''
    returns a dict of {to_vn_class: [Change objects]}

    update: themrole still in class, but selectional restrictions changed
    delete: themrole removed from class
    insert: themrole inserted to the class
  '''
  all_changes = {}

  for from_themrole in from_vn_themroles:
    changes = []
    diff = None

    possible_to_themrole = search.find_themroles(to_vn_themroles, role_type=from_themrole.role_type,
                                                 class_ID=from_themrole.class_id())
    if possible_to_themrole:  # If themrole is in the same class
      to_themrole = possible_to_themrole[0]
      diff = from_themrole.compare_selres_with(to_themrole)
    else:
      changes.append(Change(from_themrole.role_type, "role", "delete", from_themrole.class_id()))

    if diff:  # If member has updates to its attributes
      changes.append(Change(from_themrole.role_type, "role", "update", from_themrole.class_id(), diff))

    if changes:
      all_changes[to_themrole.class_id() if to_themrole else to_themrole] = changes

  # Find insertions
  for type, class_ID in list(set([(t.role_type, t.class_id()) for t in to_vn_themroles]) - set(
      [(t.role_type, t.class_id()) for t in from_vn_themroles])):
    inserted_themrole = search.find_themroles(to_vn_themroles, class_ID=class_ID, role_type=type)
    if inserted_themrole:
      all_changes.setdefault(inserted_themrole[0].class_id(), []).append(
        Change(inserted_themrole[0].role_type, "role", "insert", None, inserted_themrole[0].pp()))

  return all_changes


def compare_frames(from_vn_frames, to_vn_frames):
  """
  Same idea, but with frames, but frames have nested
  that can undergo the same operations
  """
  all_changes = {}

  for to_vn_frame in to_vn_frames:
    to_vn_frame

  return True


def compare_semantics(from_vn_semantics, to_vn_semantics):
  """
  Same idea, but with semantics
  """
  semantic_comparisons = {}

  # A predicate has been deleted from the semantic frame
  if len(from_vn_semantics) > len(to_vn_semantics):
    for from_predicate, to_predicate in zip(from_vn_semantics, to_vn_semantics):
      attr_diffs = from_predicate.compare_attrs(to_role)
      if attr_diffs:
        semantic_comparisons[(from_role.POS, from_role.value[0])] = [("update", attr_diffs)]
    for deleted_role in from_vn_syntax[len(to_vn_syntax):]:
      # Role key represented with tuple of (POS, value)
      semantic_comparisons[(deleted_role.POS, deleted_role.value[0])] = [("delete", None)]
  return True


def compare_predicates(from_predicate, to_predicate):
  predicate_comparisons = {}

  if from_predicate.value != to_predicate.value:
    # predicate_comparisons[]
    return True


def compare_syntax(from_vn_syntax, to_vn_syntax):
  syntax_comparisons = {}

  # A role has been deleted from the syntactic frame
  if len(from_vn_syntax) > len(to_vn_syntax):
    for from_role, to_role in zip(from_vn_syntax, to_vn_syntax):
      attr_diffs = from_role.compare_attrs(to_role)
      if attr_diffs:
        syntax_comparisons[(from_role.POS, from_role.value[0])] = [("update", attr_diffs)]
    for deleted_role in from_vn_syntax[len(to_vn_syntax):]:
      # Role key represented with tuple of (POS, value)
      syntax_comparisons[(deleted_role.POS, deleted_role.value[0])] = [("delete", None)]

  # A role has been inserted into the syntactic frame
  elif len(to_vn_syntax) > len(from_vn_syntax):
    for from_role, to_role in zip(from_vn_syntax, to_vn_syntax):
      attr_diffs = from_role.compare_attrs(to_role)
      if attr_diffs:
        syntax_comparisons[(from_role.POS, from_role.value[0])] = [("update", attr_diffs)]
    for inserted_role in to_vn_syntax[len(from_vn_syntax):]:
      # Role key represented with tuple of (POS, value)
      syntax_comparisons[(inserted_role.POS, inserted_role.value[0])] = [("insert", None)]

  # No insertions/deletions
  else:
    for from_role, to_role in zip(from_vn_syntax, to_vn_syntax):
      attr_diffs = from_role.compare_attrs(to_role)
      if attr_diffs:
        syntax_comparisons[(from_role.POS, from_role.value[0])] = [("update", attr_diffs)]

  return syntax_comparisons


from_vn = VerbNetParser(version="3.2")
to_vn = VerbNetParser(version="3.4")

# from_vn = to_vn

# print(compare_syntax(from_vn.get_verb_class("hold-15.1").frames[0].syntax, to_vn.get_verb_class("hurt-40.8.3").subclasses[0].frames[0].syntax))

from_vn_members = from_vn.get_members()
to_vn_members = to_vn.get_members()
x = compare_members(from_vn_members=from_vn_members, to_vn_members=to_vn_members)

for k, v in x.items():
  print({k: [change.__dict__ for change in v]})

# from_vn_themroles = from_vn.get_themroles()
# to_vn_themroles = to_vn.get_themroles()

# x = compare_themroles(from_vn_themroles, to_vn_themroles)

# for k, v in x.items():
#  print({k: [change.__dict__ for change in v]})
