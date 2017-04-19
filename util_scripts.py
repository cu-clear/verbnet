from verbnetparser import *

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


vn = VerbNetParser()
all_verb_classes = vn.get_verb_classes()

all_features = get_verb_specific_feature_set(all_verb_classes)
classes_and_members_with_features = get_classes_and_members_by_features(all_verb_classes, all_features)

with open('/Users/ajwieme/Desktop/CU Boulder Classes/Spring 2017/Semantics/final project/data/manner_verbs_from_verbnet.txt', 'w') as outfile:
  print "WRITING..."
  write_str = "ALL FEATURES: [%s]\n\n" % ' '.join(all_features)
  for vn_class_name in classes_and_members_with_features:
    write_str += "CLASS: %s\n\n" % vn_class_name
    members = classes_and_members_with_features[vn_class_name]
    write_str += ''.join([member.pp() for member in members])

  print "IT IS WRITTEN, SO IT BEGINS..."

  outfile.write(write_str)
