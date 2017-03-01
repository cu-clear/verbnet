"""writer.py

Utilities to write HTML files.

"""


import os


class HtmlWriter(object):

    """Class that knows how to create html files for set of GLVerbClass
    instances. This class is responsible for writing the index file and for
    invoking HtmlClassWriter on individual classes."""
    
    def __init__(self, directory='html'):
        self.directory = directory
        self.index = open(os.path.join(self.directory, 'index.html'), 'w')
        self._write_begin()

    def _write_begin(self):
        self.index.write("<html>\n")
        self.index.write("<head>\n")
        self.index.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
        self.index.write("</head>\n")
        self.index.write("<body>\n")
        self.index.write("<table class=noborder >\n")
        self.index.write("<tr valign=top>\n")

    def write(self, gl_verb_classes, header, group=''):
        self.index.write("<td>\n")
        self.index.write("<table cellpadding=8 cellspacing=0>\n")
        self.index.write("<tr class=header><td>%s</a>\n" % header)
        for verbclass in gl_verb_classes:
            infix = group + '-' if group else ''
            class_file = "vnclass-%s%s.html" % (infix, verbclass.ID)
            self.index.write("<tr class=vnlink><td><a href=\"%s\">%s</a>\n" % (class_file, verbclass.ID))
            fh =  open(os.path.join(self.directory, class_file), 'w')
            HtmlClassWriter(fh, verbclass).write()
        self.index.write("</table>\n")
        self.index.write("</td>\n")

    def finish(self):
        self.index.write("</tr>\n")
        self.index.write("</table>\n")
        self.index.write("</body>\n")
        self.index.write("</html>\n")


class HtmlClassWriter(object):

    """Class that knows how to write the HTML representation for a GLVerbClass to a
    file handle."""

    def __init__(self, fh, glverbclass):
        self.fh = fh
        self.glverbclass = glverbclass

    def write(self, frames=None):
        self.fh.write("<html>\n")
        self.fh.write("<head>\n")
        self.fh.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
        self.fh.write("</head>\n")
        self.fh.write("<body>\n")
        self.fh.write("\n<h1>%s</h1>\n" % str(self.glverbclass.ID))
        frames_to_print = range(len(self.glverbclass.frames))
        if frames is not None:
            frames_to_print = frames
        for i in frames_to_print:
            vn_frame = self.glverbclass.verbclass.frames[i]
            gl_frame = self.glverbclass.frames[i]
            self.fh.write("\n<table class=frame cellpadding=8 cellspacing=0 border=0 width=1000>\n")
            self.pp_html_description(gl_frame, i)
            self.pp_html_example(gl_frame)
            self.pp_html_predicate(vn_frame)
            self.pp_html_subcat(gl_frame)
            self.pp_html_qualia(gl_frame)
            self.pp_html_event(gl_frame)
            self.fh.write("</table>\n\n")

    def pp_html_description(self, gl_frame, frame_number=None):
        self.fh.write("<tr class=description>\n")
        frame_number = '' if frame_number is None else "Frame %s: " % frame_number
        self.fh.write("  <td colspan=2>%s%s\n" % (frame_number,
                                                  ' '.join(gl_frame.pri_description)))

    def pp_html_example(self, gl_frame):
        self.fh.write("<tr class=vn valign=top>\n")
        self.fh.write("  <td width=180>Example\n")
        self.fh.write("  <td>\"%s\"" % gl_frame.example[0])

    def pp_html_predicate(self, vn_frame):
        def predicate_str(pred):
            args = ', '.join([argtype[1] for argtype in pred.argtypes])
            return "<span class=pred>%s</span>(%s)" % (pred.value[0], args)
        self.fh.write("<tr class=vn valign=top>\n")
        self.fh.write("  <td width=180>VerbNet&nbsp;predicates\n")
        self.fh.write("  <td>")
        self.fh.write(', '.join([predicate_str(pred) for pred in vn_frame.predicates]))

    def pp_html_subcat(self, gl_frame):
        self.fh.write("<tr class=qualia valign=top>\n")
        self.fh.write("  <td>GL&nbsp;subcategorisation\n")
        self.fh.write("  <td>\n")
        for element in gl_frame.subcat:
            #self.fh.write("      { %s } <br>\n" % element)
            self.fh.write("      {")
            if element.var is not None:
                self.fh.write(" var=%s" % element.var)
            self.fh.write(" cat=%s" % element.cat)
            if element.role:
                self.fh.write(" role=%s" % element.role[0])
            self.fh.write(" } / [")
            self.pp_html_restriction(element.sel_res)
            self.fh.write("]<br>\n")

    def pp_html_restriction(self, restriction):
        # print '>>', restriction
        if not restriction:
            pass
        elif restriction[0] in ['+', '-']:
            self.fh.write("%s%s" % (restriction[0], restriction[1]))
        elif restriction[0] in ['OR', 'AND'] and len(restriction) == 3:
            self.fh.write("(")
            self.pp_html_restriction(restriction[1])
            self.fh.write(" %s " % restriction[0])
            self.pp_html_restriction(restriction[2])
            self.fh.write(")")
        else:
            self.fh.write("%s" % restriction)

    def pp_html_qualia(self, gl_frame):
        self.fh.write("<tr class=qualia valign=top>\n")
        self.fh.write("  <td>GL&nbsp;qualia&nbsp;structure\n")
        self.fh.write("  <td>%s\n" % gl_frame.qualia)

    def pp_html_event(self, gl_frame):
        self.fh.write("<tr class=event valign=top>\n")
        self.fh.write("  <td>GL event structure")
        self.fh.write("  <td>var = %s<br>\n" % gl_frame.events.var)
        self.fh.write("      initial_state = %s<br>\n" % gl_frame.events.initial_state)
        self.fh.write("      final_state = %s\n" % gl_frame.events.final_state)
