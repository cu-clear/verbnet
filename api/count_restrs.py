import verbnet

vn = verbnet.VerbNet(directory="/home/kevin/Lexical_Resources/verbnet/")

role_restrs = {}

for cl in vn.get_classes():
    for r in cl.roles:
        n = r.name
        if not r.restrictions:
            if n in role_restrs:
                if "none" in role_restrs[n]:
                    role_restrs[n]["none"] += 1
                else:
                    role_restrs[n]["none"] = 1
            else:
                role_restrs[n] = {"none":1}
                
        for restr in r.restrictions:
            if n in role_restrs:
                if restr in role_restrs[n]:
                    role_restrs[n][restr] += 1
                else:
                    role_restrs[n][restr] = 1
            else:
                role_restrs[n] = {restr:1}

res =[]
for role in role_restrs:
#    print (role)
    if "none" in role_restrs[role]:
        res.append([sum([role_restrs[role][k] for k in role_restrs[role]]), str(role_restrs[role]["none"]), role])
#    else:
#        print ("!!" + role)
#    for restr in role_restrs[role]:
#        print (restr, role_restrs[role][restr])

res = sorted(res)
for r in res:
    print (str(r[0]) + " " + r[1] + " " + r[2])
