import sys
import getopt
import json

from csv import writer

sys.path.append("../api/")
sys.path.append("../semlink/")

import verbnet
import vnfn

DEFAULT_VN_LOC = "../vn3.3.1-test/"
DEFAULT_OUTPUT = "semnet3"
WN_LOCATION = "/home/kevin/Lexical_Resources/Wordnet/WordNet-3.0/dict/"
VN_OBJECTS_LOCATION = "../../vn_versions/vn_objects/"

all_senses = None
verb_data= None

def get_vn_objects(verb, vnc, how_many=10):
    try:
        class_objects = [item.split(",")[0] for item in open(VN_OBJECTS_LOCATION + verb.name + "_" + vnc.class_id(subclasses=False).split("-")[1] + ".txt").readlines()[:how_many]]
        print(verb.name, vnc.ID, class_objects)

    except:
        print (VN_OBJECTS_LOCATION + verb.name + "_" + vnc.class_id(subclasses=False).split("-")[1] + ".txt")
        class_objects = []

    return class_objects

def get_wn_synset(sense_key):
    global all_senses, verb_data
    if not all_senses:
        all_senses = {sense.split()[0]:sense.split() for sense in open(WN_LOCATION + 'index.sense').readlines()}
    if not verb_data:
        verb_data = {verb.split()[0]:verb.split() for verb in open(WN_LOCATION + 'data.verb').readlines()}

    if type(sense_key) == str:
        sense_key = [sense_key]

    synonyms = set()
    for k in sense_key:
        if k not in all_senses:
            if k + "::" in all_senses:
                k = k + "::"
            else:
                return None
    
        byte_offset = all_senses[k][1]

        if byte_offset not in verb_data.keys():
            return None
        else:
            words_in_synset = int(verb_data[byte_offset][3], 16)
            synonyms.update([verb_data[byte_offset][w] for w in range(4, 4+(words_in_synset*2), 2)])
    return synonyms

                                                
def build_semnet(vn):
    res = {}
    mappings = vnfn.load_mappings("../semlink/vn-fn.s", as_dict=True)

    for cl in vn.get_verb_classes():
        new_id = cl.ID
        full_themroles = cl.themroles
        restrictions = []
        while "-" in "-".join(new_id.split("-")[1:]):
            p_class = vn.verb_classes_dict["-".join(new_id.split("-")[:-1])]
            full_themroles.extend(p_class.themroles)
            for r in full_themroles:
                for thing in r.sel_restrictions:
                    if type(thing) == list and len(thing) == 2 and "".join(thing) not in restrictions:
                        restrictions.append("".join(thing))
                        
            new_id = "-".join(new_id.split("-")[:-1])

        for member in cl.members:
            norm_id = "-".join(cl.ID.split("-")[1:])
            if member.name + ":" + norm_id not in mappings:
                mappings[member.name + ":" + norm_id] = ""

            member_data = {"wn": member.wn,
                           "themroles": [r.role_type for r in full_themroles],
                           "restrictions": restrictions,
                           "frames": cl.frames,
                           "fn_frame":mappings[member.name + ":" + norm_id],
                           #"wn_synset":get_wn_synset(member.wn),
                           "common_objects":get_vn_objects(member, cl)}
            
            if member.name in res:
                res[member.name][cl.ID] = member_data
            else:
                res[member.name] = {cl.ID:member_data}
    return res

def write_semnet(semnet, output_file, output_format):
    for member in semnet.keys():
        for vn_class in semnet[member]:
            semnet[member][vn_class]["predicates"] = set([p.value[0] for f in semnet[member][vn_class]["frames"] for p in f.predicates])
            semnet[member][vn_class].pop("frames", None) 
            semnet[member][vn_class]["themroles"] = semnet[member][vn_class]["themroles"]
            
            for component in semnet[member][vn_class].keys():
                if component == "restrictions":
                    res = []
                    for r in semnet[member][vn_class]["restrictions"]:
                        res.append([r[0], r[1:]])
                    semnet[member][vn_class]["restrictions"] = str(res).translate({ord("'"):None, ord('['):ord('{'), ord("]"):ord("}")})
                    
                elif component == "fn_frame":
                    pass
                else:
                    try:
                        semnet[member][vn_class][component] = " ".join(semnet[member][vn_class][component])
                    except:
                        pass
                
    if output_format == "json":
        with open(output_file, 'w') as output:
            json.dump(semnet, output)
    elif output_format == "csv":
        with open(output_file, 'w') as output:
            output_writer = writer(output, delimiter=';')

            for member in sorted(list(semnet.keys())):
                for vn_class in sorted(list(semnet[member].keys())):
                    data = [member, vn_class.split("-")[0], "-".join(vn_class.split("-")[1:])] + [semnet[member][vn_class][item] for item in sorted(list(semnet[member][vn_class].keys()))]
                    output_writer.writerow(data)
    return None


def print_help():
    print ("SemNet Generator")


# Main method as suggested by van Rossum, simplified
def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        opts, args = getopt.getopt(argv[1:], "hi:o:j", ["help", "input=", "output=", "json"])
    except Exception as e:
        print(e)
        print("Error in args : " + str(argv[1:]))
        return 2

    input_dir = DEFAULT_VN_LOC
    output_file = DEFAULT_OUTPUT

    for o in opts:
        if o[0] in ["-i", "--input"]:
            input_dir = o[1]
        if o[0] in ["-o", "--output"]:
            output_file = o[1]
        if o[0] in ["-h", "--help"]:
            print_help()
        if o[0] in ["-j", "--json"]:
            generate_json = True
            
    print('input dir    :  ' + input_dir)
    print('writing to   :  ' + output_file)

    sn = build_semnet(verbnet.VerbNetParser(directory=input_dir))
#    write_semnet(sn, output_file+".json", "json")
    write_semnet(sn, output_file+".csv", "csv")

if __name__ == "__main__":
    sys.exit(main())
