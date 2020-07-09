# Verbnet
University of Colorado VerbNet GitHub

This repository contains a variety of tools and resources for <a href="https://verbs.colorado.edu/verbnet/">VerbNet</a>. It is still being developed, but comments are greatly appreciated!

<h3>Contents</h3>
The repository contains three main components:
<ul>
<li><b>api</b> : A directory containing python tools for working with VerbNet data. We're primarily focused on making the verbnet.py API useful for using VerbNet XML. Additional tools that we've found useful can be found in the <b>scripts</b> folder.
</li>
<li><b>vn3.4</b> : Our most current publicly availabe version of VerbNet. For more official releases, see <a href="https://verbs.colorado.edu/verbnet/">our website</a>. Comments and suggestions on improving the XML here are appreciated!</li>
<li><b>vn3.3</b> : Previous version of VerbNet. For code access, see <a href="https://github.com/cu-clear/verbnet/tree/vn-3.3">here</a>.</li>
</ul>

Note that one method of pointing the API to the VerbNet XML is via a config.txt file, which you can create and into which you can enter text of the following format:

```
//Set the path to where your VerbNet files live

VERBNET_PATH_3.4 = path/to/verbnet_version3.4
VERBNET_PATH_3.3 = path/to/verbnet_version3.3

FRAMENET_MAPPING_PATH = path/to/framenet_mapping_file
```


