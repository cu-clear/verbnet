import vnfn

old_semlink = vnfn.load_mappings()
good_mappings = []
for m in old_semlink:
    if not m.verify():
        good_mappings.append(m)
    else:
        print (m, "!!" + str(m.verify()))

vnfn.write_mappings(good_mappings, "good_mappings")
