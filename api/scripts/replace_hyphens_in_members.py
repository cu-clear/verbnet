from api.verbnet import *
import argparse


HYPHEN_VERBS = ["flip-flop", "co-occur", "sweet-talk", "mass-produce", "arm-twist", "e-mail", "hee-haw", "ki-yi",
                "cross-examine", "pre-empt", "re-emerge", "charcoal-broil", "deep-fry", "french-fry", "oven-fry",
                "oven-poach", "pan-broil", "pan-fry", "pot-roast", "steam-bake", "stir-fry", "force-feed", "de-escalate", "short-circuit"]

if __name__ == '__main__':
  # DEFINE ARGS
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--input_dir', help='Where to find the xml files', required=True)
  parser.add_argument('-o', '--output_dir', help='Where to dump the updated xml files',
                      required=True)
  args = vars(parser.parse_args())

  # GET VARIABLES FROM ARGS
  input_dir = args.get("input_dir")
  output_dir = args.get("output_dir")

  vn = VerbNetParser(directory=input_dir)
  updated_members = []

  for m in vn.get_members():
    if "-" in m.name and m.name not in HYPHEN_VERBS:
      updated_members.append(m)
      new_name = m.name.replace("-", "_")
      m.update_name(new_name)

  for vnc in vn.get_verb_classes_by_members(updated_members):
    # We do not want to output a file for a subclass; it will be in the parent class XML
    if not vnc.is_subclass():
      # Produce the name of the output file
      outfile = output_dir + vnc.ID + ".xml"
      with open(outfile, "w") as f:
        print("saving %s" % outfile)
        # Hard code DOCTYPE declaration
        f.write("<!DOCTYPE VNCLASS SYSTEM \"vn_class-3.dtd\">\n")
        # Pretty print the class XML
        f.write(vnc.pp())