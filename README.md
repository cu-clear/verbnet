# Verbnet
University of Colorado VerbNet GitHub

This repository contains a variety of tools and resources for <a href="https://verbs.colorado.edu/verbnet/">VerbNet</a>. It is still being developed, but comments are greatly appreciated!

<h3>Contents</h3>
The repository contains three main components:
<ul>
<li><b>api</b> : A directory containing python tools for working with VerbNet data. We're primarily focused on making the verbnet.py API useful for using VerbNet XML. Additional tools that we've found useful can be found in the <b>scripts</b> folder.
</li>
<li><b>vn3.3.1-test</b> : Our most current TEST version of the VerbNet XML. This is the version we are implementing live updates into. It is not stable, and should not be used in applications. For the official releases, see <a href="https://verbs.colorado.edu/verbnet/">our website</a>. Comments and suggestions on improving the XML here are appreciated!</li>
<li><b>semnet</b> : SemNet is a resource under development. The goal is to map the key components of VN verbs with other resources such as PropBank and FrameNet. We are experimenting with generating semnet in different formats, and comments are appreciated! It currently resides here in JSON.</li>
</ul>

Note that one method of pointing the API to the VerbNet XML is via a config.txt file, which you can create and into which you can enter text of the following format:

```
//Set the path to where your VerbNet files live

VERBNET_PATH_3.3 = path/to/verbnet_version3.3
VERBNET_PATH_3.2 = path/to/verbnet_version3.2

FRAMENET_MAPPING_PATH = path/to/framenet_mapping_file
```


