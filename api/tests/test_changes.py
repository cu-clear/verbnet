import sys

local_verbnet_api_path = "../"

sys.path.append(local_verbnet_api_path)
from verbnet import *
import search


class Change():
    def __init__(self, element_name, element_type, change_type, old_class=None, notes=""):
        if element_type not in ['member','role','frame']:
            raise Exception(element_type + " is not a valid element type")
        if change_type not in ['insert','delete','move','update']:
            raise Exception(change_type + " is not a valid change type")
        if change_type == 'move' and element_type != 'member':
            raise Exception('cannot have a \'move\' type on an element that is not a member')
        #also should probably fail on invalid old_class, but would require VN class lookup (strict) or regex matching (loose)

        self.element_name = element_name
        self.element_type = element_type
        self.change_type = change_type
        self.old_class = old_class
        self.notes = notes
        
    def __eq__(self, other):
        if type(self) == type(other):
            return (self.element_name == other.element_name and self.element_type == other.element_type and self.change_type == other.change_type and self.old_class == other.old_class)
        else:
            return False
            
    def __hash__(self):
        return (hash(self.element_name) + hash(self.element_type) + hash(self.change_type) + hash(self.old_class))
        
    def __str__(self):
        return str(self.element_name + " " + self.element_type + " " + self.change_type + " " + self.old_class + " " + self.notes).strip()
        
def test_changes():    
    try:
        c1 = Change('grow','member','insert','120.21','this is a new change')
        c2 = Change('grow','member','insert','120.21','this one is the same')
    
        c3 = Change('break','member','insert','120.21','this one is different')
        c4 = Change('grow','member','delete','120.21','this one is also different')
        print('test 1 success : init works')
        
        change_dict = {}
        change_dict[c1] = False
        change_dict[c2] = True
        change_dict[c3] = False
        change_dict[c4] = False
        
        if len(change_dict) == 3 and change_dict[c1]:
            print ('test 2 success : hashing works')
        else:
            print ('test 2 failed : hashing broken')
    except Exception as e:
        print (e)
        print ('test 1 failed : changes not created successfully')
        
    if (c1 != c2):
        print ('test 3 failed : c1 != c2')
    elif (c1 == c3):
        print ('test 4 failed : c1 == c3')
    elif (c1 == c4):
        print ('test 5 failed : c1 == c4')
    else:
        print ('test 3-5 success, equals works')

    if str(c1) == 'grow member insert 120.21 this is a new change':
        print ('test 6 success, str works')
    else:
        print ('test 6 failed, str broken', str(c1))

        
    try:
        Change('grow','member','member','120.21','this has an invalid change type')
        print ('test 7 failed : invalid change type accepted')
    except Exception as e:
        print ('test 7 success : invalid change type rejected')

    try:
        Change('grow','insert','insert','120.21','this has an invalid element type')
        print ('test 8 failed : invalid element type accepted')
    except Exception as e:
        print ('test 8 success : invalid element type rejected')

def test_member_comparisons():
    from compare_versions import compare_members

    from_vn = VerbNetParser(version="3.3")
    to_vn = VerbNetParser(version="3.4")

    from_vn.parse_files()
    to_vn.parse_files()

    from_vn_members = from_vn.get_all_members()
    to_vn_members = to_vn.get_all_members()

    x = compare_members(from_vn_members, to_vn_members)

    for k, v in x.items():
        if k:
            for change in v:
                if change.element_name in [m.name[0] for m in to_vn.get_verb_class(k).members]:
                    continue#print("Success: %s is now in %s" % (change.element_name, k))
                else:
                    print("Failed, %s is in %s: " % (change.element_name, ', '.join(search.find_members(to_vn_members, name=change.element_name))))
                    print({k: change.__dict__})
        else: # Deletions
            for change in v:
                potential_members = search.find_members(to_vn_members, name=change.element_name)
                if potential_members:
                    print("%s marked as Deleted could be in %s" % (change.element_name, ', '.join(potential_members)))

                                                                      
test_changes()
#test_member_comparisons()
