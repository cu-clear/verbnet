import sys, os

local_verbnet_api_path = "../"

sys.path.append(local_verbnet_api_path)
from verbnet import *

DOCTYPE = '<!DOCTYPE VNCLASS SYSTEM "vn_class-3.dtd">\n'

def gen_sense_keys(members, count_dict):
    counts_dict = {}

    for member in members:
        member_name = member['name']
        if member_name not in count_dict:
            count_dict[member_name] = 1
        member['verbnet_key'] = member_name+'#'+str(count_dict[member_name])
        count_dict[member_name] += 1

    return count_dict

def run_script():
    # CHANGE DIRECTORY to desired verbnet version;
    vn_directory = "../../vn3.3.1-test/"

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