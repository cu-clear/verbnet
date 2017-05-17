from verbnetparser import *
from framenet import *

def get_verb_specific_feature_set(vn_classes):
  all_features = []

  for vn_class in vn_classes:
    for member in vn_class.members:
      if member.features:
        all_features.append(member.features)

  return set([feature for features_list in all_features for feature in features_list])

# Given a set of VN classes, and a set of features,
# returns a dict of {class: [(member with one of those features, feature set for member)]}
def get_classes_and_members_by_features(vn_classes, features):
  classes_and_members = {}
  for verb_class in vn_classes:
    for member in verb_class.members:
      if not set(features).isdisjoint(member.features):
        classes_and_members.setdefault(verb_class.ID, []).append(member)

  return classes_and_members

def get_classes_and_members_by_exact_feature_set(vn_classes, features):
  classes_and_members = {}
  for verb_class in vn_classes:
    for member in verb_class.members:
      if set(features) == set(member.features):
        classes_and_members.setdefault(verb_class.ID, []).append(member)

  return classes_and_members


# ISSUE IS THAT SOME MAPPiNGS POINT TO SUBCLASSES, NEED TO MAP THESE CORRECTLY
def update_fn_mapping():
  fn = FrameNet()
  vn = VerbNetParser()
  num_ids_and_classes = {}

  vn.get_verb_class_by_numerical_id

  print(num_ids_and_classes.keys())

  for mapping in fn.mappings:
    parent_class_id = mapping.verbnet_class_ID.split("-")[0]
    if parent_class_id in num_ids_and_classes.keys():
      # Get node in soup
      for node in fn.soup.findAll(attrs={"fnframe": mapping.name, "class": mapping.verbnet_class_ID, "vnmember": mapping.verbnet_member_name}):
        node["class"] = num_ids_and_classes[parent_class_id].ID
    else:
      print(mapping.soup)
      for broken_mapping in fn.soup.findAll(attrs={"fnframe": mapping.name, "class": mapping.verbnet_class_ID}):
        broken_mapping.extract()

#update_fn_mapping()
vn = VerbNetParser()
print([s.ID for s in vn.get_verb_class_by_numerical_id("36.4").subclasses])
#print(sorted([verb_class.ID.split("-")[1] for verb_class in vn.get_verb_classes()]))

'''
vn = VerbNetParser()
all_verb_classes = vn.get_verb_classes()

#all_features = get_verb_specific_feature_set(all_verb_classes)
classes_and_members_with_features = get_classes_and_members_by_features(all_verb_classes, ["+orientation"])

with open('/Users/ajwieme/Desktop/CU Boulder Classes/Spring 2017/Semantics/final project/data/manner_verbs_from_verbnet_for_experiment.txt', 'w') as outfile:
  print "WRITING..."
  write_str = "" #"ALL FEATURES: [%s]\n\n" % ' '.join(all_features)
  for vn_class_name in classes_and_members_with_features:
    write_str += "CLASS: %s\n\n" % vn_class_name
    members = classes_and_members_with_features[vn_class_name]
    write_str += ''.join([member.pp() for member in members])

  print "IT IS WRITTEN, SO IT BEGINS..."

  outfile.write(write_str)
  '''
