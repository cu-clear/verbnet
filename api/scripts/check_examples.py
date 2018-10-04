import sys
import re
import string

local_verbnet_api_path = "../"

sys.path.append(local_verbnet_api_path)
from verbnet import *
from nltk.stem import WordNetLemmatizer

def check_examples(vn):
  bad = 0
  all_verb_classes = vn.get_verb_classes()
  wordnet_lemmatizer = WordNetLemmatizer()

  for c in all_verb_classes:
    for fr in c.frames:
      found = False
      for ex in fr.examples:
        example_words = [wordnet_lemmatizer.lemmatize(w.strip(string.punctuation), pos="v") for w in ex.strip("[.,]").split()]
        members = [re.split("-|_", mem.name) for mem in c.members]
        for sc in c.get_all_subclasses():
          members += [re.split("-|_", mem.name) for mem in sc.members]

        for member in members:
          if len(list(set(example_words) & set(member))) == len(member):
            found = True
          else:
            pass
      if not found:
        bad += 1
        print(c.ID, fr.examples)
  print(bad)

vn = VerbNetParser()
check_examples(vn)