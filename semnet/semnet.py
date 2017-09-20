import sys
import getopt
import json

sys.path.append("../api/")

import verbnet
import vnfn

DEFAULT_VN_LOC = "../vn3.3.1-test/"
DEFAULT_OUTPUT = "semnet-test.json"


def to_json_by_member(vn, output_file):
    res = {}
    mappings = vnfn.load_mappings("../api/vn-fn.s", as_dict=True)

    for cl in vn.get_verb_classes():
        new_id = cl.ID
        full_themroles = cl.themroles
        while "-" in "-".join(new_id.split("-")[1:]):
            p_class = vn.verb_classes_dict["-".join(new_id.split("-")[:-1])]
            full_themroles.extend(p_class.themroles)
            new_id = "-".join(new_id.split("-")[:-1])

        for member in cl.members:
            if cl.frames:
                norm_id = "-".join(cl.ID.split("-")[1:])
                if member.name + ":" + norm_id not in mappings:
                    mappings[member.name + ":" + norm_id] = ""
                res[cl.ID + "-" + member.name] = {"wn": member.wn, "themroles": [str(r) for r in full_themroles],
                                                  "syntactic_frames": [f.pp_syntax() for f in cl.frames],
                                                  "semantic_frames": [f.pp_semantics() for f in cl.frames],
                                                  "fn_frame":mappings[member.name + ":" + norm_id]}

    with open(output_file, "w") as o:
        json.dump(res, o)

    return res


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

    to_json_by_member(verbnet.VerbNetParser(directory=input_dir), output_file)


if __name__ == "__main__":
    sys.exit(main())
