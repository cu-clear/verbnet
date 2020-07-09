import sys, os

local_verbnet_api_path = "../"

sys.path.append(local_verbnet_api_path)
from verbnet import *

DOCTYPE = '<!DOCTYPE VNCLASS SYSTEM "vn_class-3.dtd">\n'

def gen_sense_keys(members, count_dict):
    member_names = [member['name'] for member in members]

    #Dictionary of duplicate members in different subclasses within the same class (e.g. "learn" and "read" in 14-1 and 14-2-1)
    duplicate_members = {name: member_names.count(name) for name in member_names if member_names.count(name)>1}

    #Print duplicates to terminal for reference
    if len(duplicate_members) > 0:
        for member in duplicate_members.keys(): print(member)

    for member in members:
        member_name = member['name']
        if member_name not in count_dict:
            count_dict[member_name] = 1

        #For duplicate members within the same class:
        if member_name in duplicate_members.keys():
            #Save current count as verbnet_key identifier
            member['verbnet_key'] = member_name+'#'+str(count_dict[member_name])

            #Increment the count in the global count dictionary if this is the last instance of this member in the class
            if duplicate_members[member_name] == 1:
                count_dict[member_name] += 1

            #Decrememnt duplicate count (to meet above IF-condition on encountering last member)
            duplicate_members[member_name] -= 1
            
        else:
            member['verbnet_key'] = member_name+'#'+str(count_dict[member_name])
            count_dict[member_name] += 1

    return count_dict

def run_script():
    # CHANGE DIRECTORY to desired verbnet version;
    vn_directory = "../../vn3.4.1-test/"

    vnp = VerbNetParser(directory=vn_directory)

    count_dict = {}

    # Save output to a separate directory instead of writing changes in-place
    if not os.path.exists('sense_key_output'):
        os.mkdir('sense_key_output')

    # parse_files() returns a list of soup objects
    for v in vnp.parse_files():
        class_soup = v.VNCLASS
        members = class_soup.find_all('MEMBER')
        gen_sense_keys(members, count_dict)

        with open("sense_key_output/" + class_soup['ID'] + '.xml', 'w') as outfile:
            outfile.write(DOCTYPE)
            outfile.write(class_soup.prettify())


if __name__ == '__main__':
    run_script()