import sys
from lxml import etree

local_verbnet_api_path = "../api/"

sys.path.append(local_verbnet_api_path)
import annotation

def generate_tasks(input_file, format="semlink"):
    with open(input_file) as input_data:
        verbs = {}
        for line in input_data.readlines():
            if format=="semlink":
                ann = annotation.SemLinkAnnotation(line)
                if ann.verb not in verbs:
                    verbs[ann.verb] = [ann]
                else:
                    verbs[ann.verb].append(ann)

        for v in verbs:
            with open("tasks/" + v + ".task", "w") as output:
                for a in verbs[v]:
                    output.write(" ".join(["word/"+a.source_file.split("/")[-1], a.sentence_no, a.token_no, a.verb + "-v"]) + "\n")

generate_tasks("test")