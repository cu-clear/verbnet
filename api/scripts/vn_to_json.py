import sys

local_verbnet_api_path = "../"

sys.path.append(local_verbnet_api_path)
import verbnet

def to_json(verbnet):
  res = {}
  for cl in verbnet.get_classes():
    for member in cl.members:
      print (cl, member)
      res[cl.classname+"-"+member.name] = {}
  return {}

verbnet = verbnet.VerbNet(directory="../../vn3.3.1-test")
print (verbnet)
to_json(verbnet)
