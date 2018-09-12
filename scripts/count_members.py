from api.verbnet import *
from sys import argv, stderr
from bs4 import BeautifulSoup as soup

if __name__ == '__main__':
  if len(argv) == 2:
    vn_dir = argv[1]
    vn = VerbNetParser(directory=vn_dir)
  else:
    print("using default vn directory...")
    vn = VerbNetParser()

  print("%i members in %s classes" % (len(vn.get_members()), len([c for c in vn.get_verb_classes() if not c.is_subclass()])))
