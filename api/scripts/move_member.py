import sys
local_verbnet_api_path = "/Users/ajwieme/verbs-projects/VerbNet/verbnet/api"
sys.path.append(local_verbnet_api_path)

from verbnet import *
import search
import argparse

def move_member(member_name, current_classname, new_classname):
  '''
    :return: (current_class_xml, new_class_xml)
  '''
  current_member_search = search.find_members(name=member_name, class_ID=current_classname)
  if current_member_search:
    # Should only ever be one unique member name per class
    current_member = current_member_search[0]
  else:
    raise Exception("%s is not in the class %s in VerbNet version %s" % (member_name, current_classname, vn.version))

  new_class = vn.get_verb_class(new_classname)
  current_class = vn.get_verb_class(current_classname)

  if new_class:
    current_class.remove_member(current_member)
    new_class.add_member(current_member)
    return (current_class.pp(), new_class.pp())
  else:
    raise Exception("%s is not a class in VerbNet version %s" % (new_classname, vn.version))

if __name__ == '__main__':

  # DEFINE ARGS
  parser = argparse.ArgumentParser()
  parser.add_argument('-m', '--member', help='The name of the member to move', required=True)
  parser.add_argument('-c', '--current_class', help='The name of the class where that member currently resides', required=True)
  parser.add_argument('-n', '--new_class', help="The new class to move that member to", required=True)
  args = vars(parser.parse_args())

  # GET VARIABLES FROM ARGS
  member_name = args.get("member")
  current_class = args.get("current_class")
  new_class = args.get("new_class")

  global vn

  vn = VerbNetParser()

  # Get the two updated xml's for the insertion/removal
  current_class_xml, new_class_xml = move_member(member_name, current_class, new_class)
  doctype = '<!DOCTYPE VNCLASS SYSTEM "vn_class-3.dtd">'

  for class_file in vn.filenames:
    if class_file.endswith(current_class + ".xml"):
      with open(class_file, "w") as f:
        print("saving %s" % class_file)
        f.write(current_class_xml)
    elif class_file.endswith(new_class + ".xml"):
      with open(class_file, "w") as f:
        print("saving %s" % class_file)
        f.write(new_class_xml)