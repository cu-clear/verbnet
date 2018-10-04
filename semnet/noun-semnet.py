import sys
import getopt
import json
import math
from re import finditer

from nltk.corpus import wordnet as wn

import MineWiki
import SemCor


def cc_split(identifier):
        matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
        return " ".join([m.group(0) for m in matches])


def get_wn_hypernyms(lemma, level=None):
    lemma = "_".join(lemma.split())
    hier_paths = []
    for synset in wn.synsets(lemma, pos=wn.NOUN):
        hier_paths.extend(synset.hypernym_paths())
    if level:
        return list(set([p[level].name() for p in hier_paths if len(p)>level]))
    else:
        return list(set([p[-2].name() for p in hier_paths if len(p) > 1]))


def get_wn_synsets(lemma):
    lemma = "_".join(lemma.split())
    res = []
    for item in wn.synsets(lemma):
        res.extend([l.name() for l in item.lemmas()])
    return res


def get_semcor_wn_freq(lemma, semcor_dict):
    if lemma in semcor_dict:
        return {key:semcor_dict[lemma][key]/float(sum(semcor_dict[lemma].values())) for key in semcor_dict[lemma]}
    else:
        return None


def get_semcor_lemma_freq(lemma, semcor_dict, semcor_sum):
    if lemma in semcor_dict:
        return math.log(float(sum(semcor_dict[lemma].values())/semcor_sum))
    else:
        return None

def load_sumo_hierarchy(loc="ISArelations.json"):
    sumo_hierarchy = json.load(open(loc))
    return {cc_split(key).lower():sumo_hierarchy[key] for key in sumo_hierarchy}

def load_wiktionary_defs(loc="wiktionary_nouns.json"):
    wiktionary_defs = json.load(open(loc))
    return {key.lower():wiktionary_defs[key] for key  in wiktionary_defs}

def build_noun_semnet():
    sumo_hierarchy = load_sumo_hierarchy()
    wiktionary_defs = load_wiktionary_defs()
    wiki_dict = MineWiki.wiki_noun_dict()
    semcor_dict = SemCor.load_semcor_freq_dict()

    n_semnet = {key:[] for key in sumo_hierarchy}
    n_semnet.update({key:[] for key in wiktionary_defs})
    n_semnet.update({key:[] for key in wiki_dict})
    n_semnet.update({key:[] for key in semcor_dict})

    semcor_sum = 0
    for key in semcor_dict:
        semcor_sum += sum(semcor_dict[key].values())

    for key in n_semnet.keys():
        n_semnet[key] = {"sumo_parent":None, "wiktionary_def":None, "wn_hypernyms":None, "wn_synsets":None, "wn_frequencies":None, "lemma_frequency":None}
        if key in sumo_hierarchy:
            n_semnet[key]["sumo_parent"] = sumo_hierarchy[key]
        if key in wiktionary_defs:
            n_semnet[key]["wiktionary_def"] = wiktionary_defs[key]["noun_def_text"]
        n_semnet[key]["wn_hypernyms"] = get_wn_hypernyms(key)
        n_semnet[key]["wn_synsets"] = get_wn_synsets(key)
        n_semnet[key]["wn_frequencies"] = get_semcor_wn_freq(key, semcor_dict)
        n_semnet[key]["lemma_frequency"] = get_semcor_lemma_freq(key, semcor_dict, semcor_sum)

    return n_semnet


def write_semnet(n_semnet, output_file="noun-semnet3.json"):
    with open(output_file, 'w') as output:
        json.dump(n_semnet, output)


def print_help():
    print ("SemNet, the noun version")


# Main method as suggested by van Rossum, simplified
def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        opts, args = getopt.getopt(argv[1:], "hi:o:", ["help", "output="])
    except Exception as e:
        print(e)
        print("Error in args : " + str(argv[1:]))
        return 2

    output_file = "noun-semnet.json"

    for o in opts:
        if o[0] in ["-o", "--output"]:
            output_file = o[1]
        if o[0] in ["-h", "--help"]:
            print_help()

    sn = build_noun_semnet()
    write_semnet(sn, output_file)

if __name__ == "__main__":
    sys.exit(main())
