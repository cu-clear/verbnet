import os
import random

bolt_input = "C:\\Users\\Kevin\\PycharmProjects\\verbnet\\api\\scripts\\bolt_fixedFAILED\\"
google_input = "C:\\Users\\Kevin\\PycharmProjects\\verbnet\\api\\scripts\\google_fixedFAILED\\"
ewt_input = "C:\\Users\\Kevin\\PycharmProjects\\verbnet\\api\\scripts\\ewt_fixedFAILED\\"
ipsoft_input = "C:\\Users\\Kevin\\PycharmProjects\\verbnet\\api\\scripts\\ipsoft_fixedFAILED\\"


def clean_ann(line):
    if not line.startswith("word/"):
        line = "word/" + line
    if len(line.split()) > 4:
        line = " ".join(line.split()[:-1]) + "-v\n"
    else:
        line = line[:-1] + "-v\n"
    return line

def combine_and_fix():
    inputs = [bolt_input, google_input, ewt_input, ipsoft_input]
    all_anns = []
    for input in inputs:
        for f in [f for f in os.listdir(input)]:
            with open(input + f) as in_file:
                all_anns.extend(open(input + f).readlines())

    results = {}

    for a in all_anns:
        a = clean_ann(a)
        verb = a.split()[-1][:-2]
        if verb not in results:
            results[verb] = set()
        results[verb].add(a)

    for key in sorted(results):
        with open("to_redo/" + key + ".ann", "w") as outfile:
            random.shuffle(list(results[key]))
            outfile.writelines(results[key])

def generate_tasks(input_dir, name):
    for f in [f for f in os.listdir(input_dir)]:

        with open(input_dir+f) as in_file:
            lines = open(input_dir + f).readlines()

        if lines:
            with open("to_redo\\" + f + "-" + name, "w") as outfile:
                for l in lines:
                    outfile.write(" ".join(l.split()[:-1]) + "-v\n")


combine_and_fix()