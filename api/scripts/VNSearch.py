import sys
import getopt
import os
import re
import _pickle as cPickle

ALL_DATASETS = ["mms", "bolt", "ipsoft", "ewt", "google"]
FILE_LOCATION = "all_anns.p"

HIGHLIGHT = '\033[92m'
END = '\033[0m'


class Annotation():
  def __init__(self, source_file="", sentence_no="", token_no="", verb="", vnc="", dep=[], sentence="", source_dir=""):
    self.source_file = source_file
    self.sentence_no = sentence_no
    self.token_no = token_no
    self.verb = verb
    self.vnc = vnc.strip()
    self.dep = dep
    self.sentence = sentence
    self.source_dir = source_dir

  def __eq__(self, other):
    if self.sentence_no == other.sentence_no and self.token_no == other.token_no and self.verb == other.verb and self.vnc == other.vnc:
      return True
    else:
      return False

  def __hash__(self):
    return hash(self.__str__())

  def __str__(self):
    return self.source_file + " " + self.sentence_no + " " + self.token_no + " " + self.verb + " " + self.vnc + " " + " ".join(
      self.dep)


def loadAnns(datasets, params, from_file=False):
  if from_file:
    return cPickle.load(open(FILE_LOCATION))
  else:
    anns = set()
    for d in [d for d in datasets if (os.path.isdir(d) and params[d]["fields"] > 0)]:
      for f in [f for f in os.listdir(d) if f.endswith(".ann")]:
        for l in open(d + "/" + f):
          data = l.split()
          new_ann = Annotation(source_file=data[0], sentence_no=data[1], token_no=data[2], verb=data[3], vnc=data[4],
                               source_dir=d)
          if "-v" in new_ann.verb:
            new_ann.verb = new_ann.verb[:-2]
          if re.search('[a-zA-Z]', new_ann.vnc) and "-" in new_ann.vnc:
            new_ann.vnc = new_ann.vnc[new_ann.vnc.index("-") + 1:]

          if params[d]["fields"] == "6":
            new_ann.dep = data[5:]
          anns.add(new_ann)
    cPickle.dump(anns, open(FILE_LOCATION, "w"))
    return anns


def loadParams(datasets=ALL_DATASETS):
  params = {d: {} for d in datasets}
  for d in datasets:
    notes = open(d + "/NOTES")
    params[d] = {line.split("=")[0].strip(): line.split("=")[1].strip() for line in notes.readlines()}

  return params


def findVerb(verb, data, vnc="", soft=True):
  anns = []
  for a in data:
    if a.verb == verb and (vnc == "" or vnc == a.vnc or (soft and vnc in a.vnc)):
      anns.append(a)

  return anns


def findSentences(data, params):
  sents = []
  for d in data:
    source_lines = [l for l in open(params[d.source_dir]["corpora_path"] + d.source_file)]
    res = source_lines[int(d.sentence_no)].split()
    res.insert(int(d.token_no) + 1, END)
    res.insert(int(d.token_no), HIGHLIGHT)
    sents.append(" ".join(res) + "\n")

  return sents


# Main method as suggested by van Rossum, simplified
def main(argv=None):
  if argv is None:
    argv = sys.argv
  try:
    opts, args = getopt.getopt(argv[1:], "hs", ["help", "sentences"])
  except:
    print("Error in args : " + str(argv[1:]))
    return 2

  sentences = False
  for o in opts:
    if o[0] == "-s" or o[1] == "--sentences":
      sentences = True

  params = loadParams(ALL_DATASETS)
  anns = loadAnns(ALL_DATASETS, params, True)
  res = []
  print(len(anns))

  if len(args) == 1:
    res = findVerb(args[0], anns)
  elif len(args) == 2:
    res = findVerb(args[0], anns, args[1])

  if sentences:
    res = findSentences(res, params)

  for r in res:
    print(r)
  print(str(len(res)) + " results found for " + str(args))
