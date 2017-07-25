from lxml import etree
from nltk.corpus import framenet
import datetime
import verbnet

VNFN_LOC = "vn-fn.s"
VN_LOC = "../vn3.3.1-test"


class Mapping():
    def __init__(self, member, vn_class, fn_frame):
        self.member = member
        self.vn_class = vn_class
        self.fn_frame = fn_frame

    def __str__(self):
        return self.member + " " + self.vn_class + " " + self.fn_frame

    def __eq__(self, other):
        return self.member == other.member and self.vn_class == other.vn_class and self.fn_frame == other.fn_frame

    def __lt__(self, other):
        return self.vn_class < other.vn_class

    def __gt__(self, other):
        return self.vn_class > other.vn_class

    def __hash__(self):
        return hash(self.member) * hash(self.vn_class) * hash(self.fn_frame)

    def as_xml(self):
        out_node = etree.Element("vncls", attrib={"class":self.vn_class, "fnframe":self.fn_frame, "vnmember":self.member, "versionID":"vn3.3"})
        return out_node

    def verify(self, vn):
        possible_classes = {"-".join(c.classname.split("-")[1:]):[m.name for m in c.members] for c in vn.get_classes()}

        possible_frames = {}
        for lu in framenet.lus():
            if lu.frame.name not in possible_frames:
                possible_frames[lu.frame.name] = [lu.lexemes[0].name]
            else:
                possible_frames[lu.frame.name].append(lu.lexemes[0].name)

        if self.vn_class.split("-")[0] not in possible_classes.keys() or self.member not in possible_classes[self.vn_class.split("-")[0]]:
            return False
        if self.fn_frame not in possible_frames.keys() or self.member not in possible_frames[self.fn_frame]:
            return False
        return True


def load_mappings(mapping_file=VNFN_LOC):
    mappings = []
    tree = etree.parse(open(mapping_file))
    root = tree.getroot()

    for e in root:
        mappings.append(Mapping(e.attrib["vnmember"], e.attrib["class"], e.attrib["fnframe"]))

    return mappings


#Removes any mapping that isn't accurate : bad vn, bad fn, duplicates
def verify_mappings(mappings):
    mappings = set(mappings)
    res = []
    vn = verbnet.VerbNet(directory=VN_LOC)
    for m in mappings:
        if m.verify(vn):
            res.append(m)

    return res


def write_mappings(mappings):
    root = etree.Element('verbnet-framenet_MappingData', attrib={"date": str(datetime.datetime)})

    for m in mappings:
        root.append(m.as_xml())
    out_str = etree.tostring(root, pretty_print=True)
    with open('vn-fn-updated.s', 'wb') as output:
        output.write(out_str)