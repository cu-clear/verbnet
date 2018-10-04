import sys
from lxml import etree

local_verbnet_api_path = "../api/"

sys.path.append(local_verbnet_api_path)
from verbnet import *
import search

def generate_groupings():
    # CHANGE DIRECTORY to desired verbnet version;
    vn_directory = "../../lexical_resources/verbnet3.3/"

    vnp = VerbNetParser(directory=vn_directory)

    member_names = set([m.name for m in vnp.get_members()])

    for member_name in member_names:
        root = etree.Element("root")

        inv = etree.Element("inventory", lemma=member_name+"-v")
        members = search.find_members(members = vnp.get_members(), name=member_name)

        for i in range(len(members)):
            member = members[i]
            sense = etree.Element("sense", group="1", n=str(i), name=member.vnc + ".xml", type="")
            examples = etree.Element("examples")
            examples.text = "\n".join([f.examples[0] for f in vnp.verb_classes_dict[member.vnc].frames])
            sense.append(examples)

            mappings = etree.Element("mappings")
            wn_map = etree.Element("wn", version="", lemma=" ".join(member.wn))
            mappings.append(wn_map)

            mappings.append(etree.Element("pb"))
            mappings.append(etree.Element("vn"))
            mappings.append(etree.Element("fn"))

            sense.append(mappings)

            inv.append(sense)
        root.append(inv)
        doctype_string = '<!DOCTYPE inventory SYSTEM "inventory.dtd">'

        with open("groupings/" + member_name + "-v.xml", "wb") as output:
            output.write(etree.tostring(root, xml_declaration=True, encoding="UTF-8", doctype=doctype_string, pretty_print=True))

if __name__ == '__main__':
    generate_groupings()