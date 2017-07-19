VNFN_LOC = "vn-fn.s"
VN_LOC = "../vn3.3.1-test"

from lxml import etree
import verbnet

class Mapping():
    #def from_node(element_node):
     #   return Mapping(element_node.attributes["member"])

    def __init__(self, member, vn_class, fn_frame):
        self.member = member
        self.vn_class = vn_class
        self.fn_frame = fn_frame

    def __str__(self):
        return self.member + " " + self.vn_class + " " + self.fn_frame

    def __eq__(self, other):
        return self.member == other.member and self.vn_class == other.vn_class and self.fn_frame == other.fn_frame

    def verify(self, vn, fn=None):


        return True

def load_mappings(mapping_file = VNFN_LOC):
    mappings = []
    tree = etree.parse(open(mapping_file))
    root = tree.getroot()

    for e in root:
        mappings.append(Mapping(e.attrib["vnmember"], e.attrib["class"], e.attrib["fnframe"]))

    return mappings

#Removes any mapping that isn't accurate : bad vn, bad fn, duplicates
def verify_mappings(mappings):
    res = []
    vn = verbnet.VerbNet(VN_LOC)
    fn = None
    for m in mappings:
        if m.verify(vn, fn):
            res.append(m)

    return res
mappings = verify_mappings(load_mappings())