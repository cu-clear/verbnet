# *** #
# This repository has been moved to https://github.com/cu-clear/verbnet, under our CLEAR account.
# I will still be active in maintaining VerbNet when I can, but I have accepted a new position and it doesn't make sense to keep the repository under my account.
# - Kevin


# Verbnet
University of Colorado VerbNet GitHub

This repository contains a variety of tools and resources for <a href="https://verbs.colorado.edu/verbnet/">VerbNet</a>. It is still being developed, but comments are greatly appreciated!

<h3>Contents</h3>
The repository contains three main components:
<ul>
<li><b>api</b> : A directory containing python tools for working with VerbNet data. We're primarily focused on making the verbnet.py API useful for using VerbNet XML. Additional tools that we've found useful can be found in the <b>scripts</b> folder.
</li>
<li><b>vn3.3</b> : Our most current publicly availabe version of VerbNet. For more official releases, see <a href="https://verbs.colorado.edu/verbnet/">our website</a>. Comments and suggestions on improving the XML here are appreciated!</li>
</ul>

Note that one method of pointing the API to the VerbNet XML is via a config.txt file, which you can create and into which you can enter text of the following format:

```
//Set the path to where your VerbNet files live

VERBNET_PATH_3.3 = path/to/verbnet_version3.3
VERBNET_PATH_3.2 = path/to/verbnet_version3.2

FRAMENET_MAPPING_PATH = path/to/framenet_mapping_file
```


