
import glob
import os
import xml.etree.ElementTree as ET


name_mismatch = []
class_numbers = {}

for file in glob.glob('./*.xml'):
    clsname = os.path.basename(file).replace('.xml','')
    clsnum = clsname.split('-')[1]

    if clsnum not in class_numbers:
        class_numbers[clsnum] = [clsname]
    else:
        class_numbers[clsnum].append(clsname) 

    try:
        vncls = ET.parse(file)
        root = vncls.getroot()
        clsid = root.get("ID")
        if clsname != clsid:
            name_mismatch.append((clsname,clsid))
    except:
        print 'Problem reading %s'%file 


### Multiple class names given class numbers:

print '\n'
for clsno in class_numbers:
    if len(class_numbers[clsno]) > 1:
        print 'Class number %s used in %s'%(clsno,', '.join(class_numbers[clsno]))


### Mismatch between filename and id in the xml

if len(name_mismatch) > 0:
    print '\nName Mismatches:'

    for filename,clsid in name_mismatch:
        print '\tFile %s has ID of %s'%(filename,clsid)
