"""

This module contains the VerbNet class which interfaces to the contents of
VerbNet. In addition it has a couple of classes that are wrappers around a
couple of VerbNet elements, these classes include VerbClass, Frame, Predicate
and Role. Finally, PredicateStatistics is a class that generates statistics for
predicates.

You can open a VerbNet instance using a list of XML files with verb classes:

>>> fnames = ('data/slide-11.2.xml', 'data/tell-37.2.xml')
>>> vn = VerbNet(fnames=fnames)
>>> print vn
<VerbNet on 2 classes>

Alternatively you can open an instance on all XML files in a directory:

>>> vn = VerbNet(directory='data')
>>> print vn
<VerbNet on 2 classes>

You can get all classes:

>>> for cl in sorted(vn.get_classes()):
...      print cl
<VerbClass slide-11.2>
<VerbClass tell-37.2>

Or just look up one class using its full name including the class version:

>>> print vn.get_class('slide-11.2')
<VerbClass slide-11.2>

Frames can be accessed easily:

>>> for frame in  vn.get_class('slide-11.2').frames[:3]:
...     print frame
<Frame slide-11.2 'NP V'>
<Frame slide-11.2 'NP V PP.initial_location'>
<Frame slide-11.2 'NP V PP.destination'>

The PredicateStatistics class produces some html files with statistics:

>>> stats = PredicateStatistics(vn, pred='motion')
>>> stats.print_missing_links('out-missing-roles.html')
>>> stats.print_predicates('out-predicates.txt')

In the case above, the results are written to two files and the statistics are
limited to classes that contain a motion predicate.

"""


import os, sys, glob, collections, doctest
from xml.dom.minidom import parse, Node


# This is a hard-wired link to the online version at colorado of 3.2.4
VERBNET_URL = 'http://verbs.colorado.edu/vn3.2.4-test-uvi/vn/'


TEXT_HEAD = """
<head>
<style>
dt { margin-top: 12pt; margin-bottom: 5pt; }
dd { margin-bottom: 8pt; }
.classname { font-size: 120% }
.pred { color: darkred; font-weight: bold; font-variant: small-caps; font-size: 125%; }
.role { color: darkblue; font-weight: bold; }
.example { font-style: italic; }
.synsem { display: block; margin-left: 20pt; margin-top: 3pt; }
.boxed { border: thin dotted grey; padding: 3pt; }
</style>
</head>
"""

TEXT_MISSING_LINKS = """
<p>This lists all occurrences where the thematic roles expressed in the syntax
of a frame are not the same as those in the semantics. The links lead to pages
at <a href="http://verbs.colorado.edu/vn3.2.4-test-uvi/vn/"
>http://verbs.colorado.edu/vn3.2.4-test-uvi/vn/</a>. Those pages are not always
based on the same XML files as used by these diagnostics. This is for example
the case for the admit verb class. The XML files for these diagnostics have
admit-65.xml for this class, but online we have admit-64.3.php, a slightly
earlier version. As a result, clicking the admit-65 link will give a
page-not-found error.</p>
"""


# A few abbreviations of dom methods

def get_attr(node, attr):
    return node.getAttribute(attr)


def get_type(node):
    return node.getAttribute('type')


def get_value(node):
    return node.getAttribute('value')


def get_elements(node, tagname):
    return node.getElementsByTagName(tagname)


def is_role(role):
    return role and (role[0].isupper() or role[0] == '?')


def remove_role_suffix(role):
    """Map things like Theme_i and Theme_j to Theme, which makes role mapping a
    bit more tolerant."""
    return role[:-2] if role[-2:] in ('_i', '_j') else role


def spanned(text, css_class):
    """Wrap text in a span tag using css_class for the class."""
    return "<span class=%s>%s</span>" % (css_class, text)


class VerbNet(object):

    """Object that contains all VerbNet classes or a subset of those classes,
    taken from a directory with xml files or a list of filenames. Contains a
    dictionary of VerbClasses indexed on class name."""

    def __init__(self, fnames=None, directory=None, url=VERBNET_URL):
        self.directory = directory
        self.fnames = fnames
        self.url = url
        if directory is None and fnames is None:
            exit('ERROR: VebNet instance needs fnames or directory argument')
        if self.fnames is None:
            self.fnames = glob.glob("%s/*.xml" % self.directory)
        self.classes = {}
        for fname in self.fnames:
            vc = VerbClass(fname)
            self.classes[vc.classname] = vc

    def get_class(self, classname):
        """Return a VerbClass instance where self.classname is classname, return
        None if there is no such class."""
        return self.classes.get(classname)

    def get_classes(self):
        """Return a list of all classes."""
        return self.classes.values()

    def __str__(self):
        return "<VerbNet on %d classes>" % len(self.fnames)


class VerbNetObject(object):

    """VerbNetObject instances are wrappers around DOM elements. Subclasses all have
    a node instance variable that contains the DOM Element."""

    def get_elements(self, tagname):
        """Return all elements from the DOM node that match tagname."""
        return get_elements(self.node, tagname)


class VerbClass(VerbNetObject):

    """A VerbClass object is generated from an xml file, the class name is taken
    from the file name and the node object is the DOM object for the file. in
    addition, there is a list of roles and a list of frames, implemented as ROle
    objects and Frame objects respectively."""

    def __init__(self, fname):
        self.fname = fname
        self.classname = os.path.basename(fname)[:-4]
        self.node = parse(open(fname))
        self.roles = [Role(role) for role in self.get_elements('THEMROLE')]
        self.frames = [Frame(self, frame) for frame in self.get_elements('FRAME')]

    def __str__(self):
        return "<VerbClass %s>" % self.classname

    def __cmp__(self, other):
        return cmp(self.classname, other.classname)

    def predicates(self):
        """Return DOM nodes of predicates in all the frames of the verb class."""
        return get_elements(self.node, 'PRED')

    def contains_predicate(self, predname):
        """Return True if one of the predicates used in frames of the verb class
        is equal to predname."""
        for p in self.predicates():
            if get_value(p) == predname:
                return True
        return False

    def pp(self):
        print self.classname

    def print_html(self, fh=None):
        if fh is None:
            fh = sys.stdout
        fh.write("<html>\n")
        fh.write(TEXT_HEAD)
        fh.write("<body>\n\n")
        fh.write("<h2>%s</h2>\n\n" % self.classname)
        for frame in self.frames:
            frame.print_html()
            fh.write("\n")
        fh.write("</body>\n")
        fh.write("</html>\n")


class Role(VerbNetObject):

    def __init__(self, role_node):
        self.node = role_node


class Frame(VerbNetObject):

    def __init__(self, verb_class, frame_node):
        self.vc = verb_class
        self.node = frame_node
        description_nodes = self.get_elements('DESCRIPTION')
        example_nodes = self.get_elements('EXAMPLE')
        self.description = description_nodes[0].getAttribute('primary')
        self.example = example_nodes[0].firstChild.data
        self.syntax = self.get_elements('SYNTAX')[0]
        self.semantics = self.get_elements('SEMANTICS')[0]

    def __str__(self):
        return "<Frame %s '%s'>" % (self.vc.classname, self.description)

    def predicates(self):
        return [Predicate(pred, self.vc) for pred in get_elements(self.semantics, 'PRED')]

    def syntax_roles(self):
        """Return a set with all roles expressed in the syntax, these are in the value
        attribute of elements like NP."""
        roles = set()
        for child in self.syntax.childNodes:
            if child.nodeType == Node.ELEMENT_NODE:
                role = get_value(child)
                if is_role(role):
                    roles.add(get_value(child))
        return roles

    def semantics_roles(self):
        """Return a set with all roles expressed in the semantics, these are in the value
        attribute of ARG elemengts with type=ThemRole."""
        roles = set()
        for pred in self.predicates():
            for arg in pred.args:
                t = get_type(arg)
                v = get_value(arg)
                if t == 'ThemRole' and is_role(v):
                    role = remove_role_suffix(get_value(arg))
                    roles.add(role)
        return roles

    def syntax_string(self):
        elements = []
        for child in self.syntax.childNodes:
            if child.nodeType == Node.ELEMENT_NODE:
                tag = child.tagName
                role = get_value(child)
                elements.append("%s-%s" % (tag, spanned(role, 'role')) if role else tag)
        return ' '.join(elements)

    def semantics_string(self):
        return ' &amp; '.join([pred.as_html_string() for pred in self.predicates()])

    def print_html(self, description=True, fh=None):
        if fh is None:
            fh = sys.stdout
        if description:
            fh.write("<p>%s</p>\n\n" % self.description)
        fh.write("<table class=synsem>\n")
        fh.write("  <tr><td class=example>%s</td></tr>\n" % self.example)
        fh.write("  <tr><td>SYN: %s</td></tr>\n" % self.syntax_string())
        fh.write("  <tr><td>SEM: %s</td></tr>\n" % self.semantics_string())
        fh.write("</table>\n")


class Predicate(VerbNetObject):

    def __init__(self, pred_node, verbnetclass):
        self.vc = verbnetclass
        self.node = pred_node
        self.value = get_value(pred_node)
        self.boolean = None
        self.args = get_elements(pred_node, 'ARG')
        self.argtypes = [(get_type(arg), get_value(arg)) for arg in self.args]
        self._init_bool()

    def _init_bool(self):
        # bool="!" is rather common and indicates not(self.value)
        boolean = get_attr(self.node, 'bool')
        if boolean:
            self.boolean = boolean

    def __str__(self):
        return "<Predicate %s>" % self.value

    def as_html_string(self):
        args = ["%s" % spanned(at[1], 'role') for at in self.argtypes]
        pred = "<span class=pred>%s</span>(%s)" % (self.value, ', '.join(args))
        if self.boolean == '!':
            pred = "<span class=pred>not</span>(%s)" % pred
        return pred


class PredicateStatistics(object):

    """Contains statistics on predicates in a set of VerbNet classes."""

    def __init__(self, vn, pred=None):
        self.vnclasses = vn.get_classes()
        if pred is not None:
            self.vnclasses = [c for c in self.vnclasses if c.contains_predicate(pred)]
        self.predicates = {}
        self.statistics = {}
        self.missing_links = {}
        self._collect_predicates()
        self._collect_statistics()
        self._collect_missing_links()

    def _collect_predicates(self):
        for vc in self.vnclasses:
            for pred in vc.predicates():
                predicate = Predicate(pred, vc)
                self.predicates.setdefault(predicate.value, []).append(predicate)

    def _collect_statistics(self):
        for pvalue, predicates in self.predicates.items():
            self.statistics[pvalue] = {'classes': {},
                                       'arguments': collections.Counter()}
            for pred in predicates:
                self.statistics[pvalue]['classes'][pred.vc.classname] = True
                self.statistics[pvalue]['arguments'].update(pred.argtypes)

    def _collect_missing_links(self):
        for vnclass in self.vnclasses:
            classname = vnclass.classname
            for frame in vnclass.frames:
                syn_roles = frame.syntax_roles()
                sem_roles = frame.semantics_roles()
                for role in sem_roles.difference(syn_roles):
                    # the ? indicates that the role does not need to be expressed in
                    # the syntax
                    if not role.startswith('?'):
                        self.missing_links.setdefault(classname, []).append(['syntax', role, frame])
                for role in syn_roles.difference(sem_roles):
                    self.missing_links.setdefault(classname, []).append(['semantics', role, frame])

    def print_missing_links(self, fname=None):
        fh = sys.stdout if fname is None else open(fname, 'w')
        fh.write("<html>\n")
        fh.write(TEXT_HEAD)
        fh.write("<body>\n\n")
        fh.write("<h2>Role mismatches</h2>\n\n")
        fh.write(TEXT_MISSING_LINKS)
        fh.write("\n<div class=boxed>Verb classes with missing roles\n" +
                 "<blockquote>\n")
        for classname in sorted(self.missing_links.keys()):
            fh.write("  <a href=\"#%s\">%s</a>\n" % (classname, classname.split('-')[0]))
        fh.write("</blockquote>\n</div>\n\n")
        fh.write("<dl>\n")
        for classname in sorted(self.missing_links.keys()):
            href = "%s%s.php" % (VERBNET_URL, classname)
            link = "<a href=\"%s\" class=classname>%s</a>" % (href, classname)
            fh.write("\n<a name=\"%s\"></a>\n<dt>\n  %s\n</dt>\n" % (classname, link))
            for (level, role, frame) in self.missing_links[classname]:
                fh.write("<dd>\n<span class=role>%s</span> is not expressed in %s of frame [%s]"
                         % (role, level, frame.description))
                fh.write("\n")
                frame.print_html(description=False, fh=fh)
                fh.write("</dd>\n")
        fh.write("\n</dl>\n\n")
        fh.write("</body>\n")
        fh.write("</html>\n")

    def print_predicates(self, fname=None):
        fh = sys.stdout if fname is None else open(fname, 'w')
        fh.write("\nFound %d predicates in %d verb classes\n\n"
                 % (len(self.predicates), len(self.vnclasses)))
        for pvalue in sorted(self.predicates):
            fh.write("\nPRED: %s\n" % pvalue)
            stats = self.statistics[pvalue]
            fh.write("\n   VN-CLASSES: %s\n" % ' '.join(sorted(stats['classes'])))
            fh.write("\n   ARGS:\n")
            for pair, count in sorted(stats['arguments'].items()):
                fh.write("   %3d  %s - %s\n" % (count, pair[0], pair[1]))


if __name__ == '__main__':

    import doctest
    doctest.testmod()
