import csv
import string
import re
import nltk
import json

def mine_wiki():
    wiki_data = csv.reader(open("C:/Users/Kevin/PycharmProjects/lexical_resources/documents_utf8_filtered_20pageviews.csv", encoding="utf-8"), quoting=csv.QUOTE_NONE)
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    out = {}

    with open("wiki_sents.txt", "w", encoding="utf-8") as outfile:
        count = 0
        for line in wiki_data:
            count += 1
            if count % 100 == 0:
                print (count)
            for p_l in line[1].split("  "):
                for l in tokenizer.tokenize(p_l):
                    if l.startswith("\" "):
                        l = l[2:]
                    words = l.split()
                    if len(words) > 4 and words[0] == words[2] and words[1] == words[3]:
                        l = " ".join(words[2:])
                    if not l.endswith("."):
                        l += "."
                    l = l.replace("\"\"", "\"")
                    outfile.write(l + "\n")

def tagged_wiki_dict(input_file = "tagged_wiki.vn"):
    vn_reg_ex = r"([0-9]+.*)|(NONE)"
    verbs = {}
    lemmatizer = nltk.WordNetLemmatizer()

    for line in open(input_file, encoding="utf-8").readlines():
        tokens = line.split()
        for t in tokens:
            if "_" in t:
                verb_data = t.split("_")
                tag = verb_data[-1]
                if re.match(vn_reg_ex, tag):
                    verb = lemmatizer.lemmatize("_".join(verb_data[:-1]).lower(), "v")
                    if verb not in verbs:
                        verbs[verb] = {}
                    if tag not in verbs[verb]:
                        verbs[verb][tag] = 0
                    verbs[verb][tag] += 1
    return verbs

def wiki_noun_dict(input_file = "wiki_sents.txt", save=False):
    if not save:
        return json.load(open("pos_wiki.dict"))

    res = {}
    lemmatizer = nltk.WordNetLemmatizer()
    count = 0
    data = open(input_file, encoding="utf-8").readlines()
    for line in data:
        count += 1
        if count % 5000 == 0:
            print (count, len(data))
            json.dump(res, open("pos_wiki.dict", "w"))
        tokens = [t.lower() for t in line.split()]
        for t in nltk.pos_tag(tokens):
            if t[1][0] == "N":
                word = lemmatizer.lemmatize(t[0], pos="n")
            else:
                continue
            if word not in res:
                res[word] = 0
            res[word] += 1
    return res