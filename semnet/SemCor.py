import os
import re
SEMCOR_LOCATION = "C:/Users/Kevin/PycharmProjects/lexical_resources/semcor3.0/semcor3.0/"

def load_semcor_freq_dict(location=SEMCOR_LOCATION):
    sc_dict = {}

    for d in os.listdir(SEMCOR_LOCATION):
        if os.path.isdir(SEMCOR_LOCATION + d):
            for f in os.listdir(SEMCOR_LOCATION + d + "/tagfiles"):
                for line in open(SEMCOR_LOCATION + d + "/tagfiles/" + f).readlines():
                    if "lexsn" in line:
                        tag = re.split(r"[>| ]", line.split("lexsn=")[1])[0]
                        lemma = line.split("lemma=")[1].split()[0].replace("_", " ")
                        if lemma not in sc_dict:
                            sc_dict[lemma] = {}
                        if tag not in sc_dict[lemma]:
                            sc_dict[lemma][tag] = 0
                        sc_dict[lemma][tag] += 1
    return sc_dict