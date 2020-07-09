import sys
import getopt
local_verbnet_api_path = "../"

sys.path.append(local_verbnet_api_path)
import verbnet
import json

DEFAULT_VN_LOC = "../../vn3.4.1-test/"
DEFAULT_OUTPUT = "semnet.json"

def to_json_by_member(vn, output_file):
  res = {}
  for cl in vn.get_classes():
    for member in cl.members:
      res[cl.classname+"-"+member.name] = {"wn":member.wn, "themroles":[str(r) for r in cl.roles], "syntactic_frames":[str(f.syntax_string()) for f in cl.frames], "semantic_frames":[str(f.semantics_string()) for f in cl.frames]}

  with open(output_file, "w") as o:
    json.dump(res, o)
    
  return res

#Main method as suggested by van Rossum, simplified
def main(argv=None):
  if argv is None:
    argv = sys.argv
  try:
    opts, args = getopt.getopt(argv[1:], "hi:o:", ["help", "input=", "output="])
  except Exception as e:
    print (e)
    print ("Error in args : " + str(argv[1:]))
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
      
  
  print ('input dir    :  ' + input_dir)
  print ('writing to   :  ' + output_file)
  
  #to_json_by_member(verbnet.VerbNet(directory=input_dir), output_file)



if __name__ == "__main__":
  sys.exit(main())
