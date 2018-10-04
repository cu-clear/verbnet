import sys
import getopt
import json
import lxml
import os
from csv import writer

sys.path.append("../api/")
sys.path.append("../semlink/")

import verbnet
import vnfn

from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import WordNetError

import MineWiki

DEFAULT_VN_LOC = "C:/Users/Kevin/PycharmProjects/lexical_resources/verbnet3.3/"
DEFAULT_OUTPUT = "verb-semnet"
WN_LOCATION = "../../lexical_resources/Wordnet-3.0/dict/"
VN_OBJECTS_LOCATION = "../../lexical_resources/vn_objects/"
ON_LOCATION = "../../lexical_resources/sense-inventories/"

all_senses = None
verb_data = None

wiki_dict = MineWiki.tagged_wiki_dict()

def get_class_frequency_data(verb, sense):
    class_freq = "verb not in wiki data"
    class_count = "verb not in wiki data"
    verb_count = "verb not in wiki data"

    if verb in wiki_dict:
        data = wiki_dict[verb]
        verb_count = sum(data.values())
        if sense in data:
            class_count = data[sense]
            class_freq = float(class_count)/verb_count
        else:
            class_freq = "class not in verb data"
            class_count = "class not in verb data"

    return {"class frequency":class_freq, "class count":class_count, "verb count":verb_count}

def get_on_definition(verb, sense):
    if not sense:
        return []

    senses = [str(int(s.split(".")[1])) for s in sense]
    verb = verb.split("_")[0] + "-v.xml"

    res = []
    if verb in os.listdir(ON_LOCATION):
        with open(ON_LOCATION + verb) as f:
            on_tree = lxml.etree.parse(f)

            for s in senses:
                for roleset_element in on_tree.getroot().findall(".//sense"):
                    if roleset_element.get("n") and s in roleset_element.get("n").split():
                        res.append(roleset_element.get("name"))
    return res


def get_vn_objects(verb, vnc, how_many=10):
    try:
        class_objects = [item.split(",")[0] for item in open(VN_OBJECTS_LOCATION + verb.name + "_" + vnc.class_id(subclasses=False).split("-")[1] + ".txt").readlines()[:how_many]]
    except Exception as e:
        class_objects = []

    return class_objects


def get_wn_hypernyms(sense_keys, level=None):
    if type(sense_keys) != list:
        sense_keys = [sense_keys]

    hier_paths = []

    for sk in sense_keys:
        sk = sk.replace("?", "")
        try:
            lemm = wn.lemma_from_key(sk)
        except ValueError as e:
            try:
                lemm = wn.lemma_from_key(sk + "::")
            except WordNetError as e2:
                print (sk, e2)
                break

        hier_paths.extend(lemm.synset().hypernym_paths())
    if level:
        return list(set([p[level].name() for p in hier_paths]))
    else:
        return list(set([p[-2].name() for p in hier_paths if len(p) > 1]))


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
                return []
    
        byte_offset = all_senses[k][1]

        if byte_offset not in verb_data.keys():
            return []
        else:
            words_in_synset = int(verb_data[byte_offset][3], 16)
            synonyms.update([verb_data[byte_offset][w] for w in range(4, 4+(words_in_synset*2), 2)])
    return list(synonyms)


def extract_predicates(frames):
    res = set()

    for frame in frames:
        for pred in frame.predicates:
            if pred.value == ["path_rel"]:
                for a in pred.args:
                    if a["type"] == "Constant":
                        res.add(a["value"])
            else:
                res.add(pred.value[0])
    return list(res)


def process_restrictions(restr_list):
    res = []
    for item in restr_list:
        if not item:
            continue
        if item[0] in ["AND", "OR"]:
            res += process_restrictions(item[1:])
        elif item not in ["AND", "OR"]:
            res.append("".join(item))
    return set(res)


def build_semnet(vn):
    res = {}
    mappings = vnfn.load_mappings("../semlink/vn-fn.s", as_dict=True)
    c = 0
    for cl in vn.get_verb_classes():
        new_id = cl.ID
        full_themroles = cl.themroles
        restrictions = []

        while "-" in "-".join(new_id.split("-")[1:]):
            p_class = vn.verb_classes_dict["-".join(new_id.split("-")[:-1])]
            full_themroles.extend(p_class.themroles)
            new_id = "-".join(new_id.split("-")[:-1])

        for r in full_themroles:
            restrictions += process_restrictions([r.sel_restrictions])
        restrictions = list(set(restrictions))

        for member in cl.members:
            norm_id = "-".join(cl.ID.split("-")[1:])
            if member.name + ":" + norm_id not in mappings:
                mappings[member.name + ":" + norm_id] = ""

            member_data = {"wn": member.wn,
                           "themroles":list(set([r.role_type for r in full_themroles])),
                           "restrictions": restrictions,
                           "fn_frame":mappings[member.name + ":" + norm_id],
                           "predicates": extract_predicates(cl.frames),
                           "syn_frames":[f.pp_syntax() for f in cl.frames],
                           "vs_features":member.features,
                           "wn_synset":get_wn_synset(member.wn),
                           "wn_hypernyms":get_wn_hypernyms(member.wn, 0),
                           "common_objects":get_vn_objects(member, cl),
                           "on_definition":get_on_definition(member.name, member.grouping),
                           "class_frequency_data":get_class_frequency_data(member.name, cl.numerical_ID)
                           }
            if member.name in res:
                res[member.name][cl.ID] = member_data
            else:
                res[member.name] = {cl.ID:member_data}
    print (len(res))
    return res


def write_semnet(semnet, output_file, output_format):
    if output_format == "json":
        with open(output_file, 'w') as output:
            json.dump(semnet, output)
    elif output_format == "csv":
        for member in semnet.keys():
            for vn_class in semnet[member]:

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
                        except Exception as e:
                            pass
                
        with open(output_file, 'w') as output:
            output_writer = writer(output, delimiter=';')

            header=False
            for member in sorted(list(semnet.keys())):
                for vn_class in sorted(list(semnet[member].keys())):
                    if not header:
                        output_writer.writerow(["verb","class_name","class_id"] + sorted(list(semnet[member][vn_class].keys())))
                        header = True
                                                                                
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
        opts, args = getopt.getopt(argv[1:], "hi:o:", ["help", "input=", "output="])
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

    print('input dir    :  ' + input_dir)
    print('writing to   :  ' + output_file)

    sn = build_semnet(verbnet.VerbNetParser(directory=input_dir))
    write_semnet(sn, output_file+".json", "json")
#    write_semnet(sn, output_file+".csv", "csv")

    an = {"not in wiki":0, "class not in data":0, "single sense":0, "okay":0}
    for v in sn:
        for cl in sn[v]:
            data = sn[v][cl]["class_frequency_data"]
            if data["class frequency"] == 'verb not in wiki data':
                an["not in wiki"] += 1
            elif data["class frequency"] == 'class not in verb data':
                an['class not in data'] += 1
            elif data["class frequency"] == 1:
                an["single sense"] += 1
            else:
                an["okay"] += 1
    print (an)

if __name__ == "__main__":
    sys.exit(main())
