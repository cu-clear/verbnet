"""writer.py

Utilities to write HTML files.

"""


import os


class HtmlGLWriter(object):

    """Class that knows how to create html files for set of GLVerbClass
    instances. This class is responsible for writing the index file and for
    invoking HtmlClassWriter on individual classes."""

    def __init__(self, directory='html'):
        import errno
        try:
            os.makedirs(directory)
        except OSError:
            if not os.path.isdir(directory):
                raise

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


class HtmlFNWriter(object):
    """Class that knows how to create html files for set of FrameNet Frame
    instances."""

    def __init__(self, directory='fn-html'):
        import errno
        try:
            os.makedirs(directory)
        except OSError:
            if not os.path.isdir(directory):
                raise

        self.directory = directory
        self.index = open(os.path.join(self.directory, 'index.html'), 'w')
        self.pure_frame_index = open(os.path.join(self.directory, 'pure-frame-index.html'), 'w')
        self._write_begin()

    def _write_begin(self):
        self.index.write("<html>\n")
        self.index.write("<head>\n")
        self.index.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
        self.index.write(bootstrap_header())
        self.index.write("</head>\n")
        self.index.write("<body>\n")

    def write(self, fn):
        self.write_pure_frames(fn)
        fn_frames = fn.frames
        self.index.write("<div class=framenet-header>")
        self.index.write("\n<h1 class=container>Framenet Frames</h1>\n")
        self.index.write("\n</div>")
        self.index.write("<div class='container frames'>\n")
        self.index.write("<a href=pure-frame-index.html class='btn btn-success pure-frames-btn'>View Pure Frames</a>")
        # order frames by name
        fn_frames.sort(key=lambda x: x.name)
        # store size of 1/3 frames for splitting into 3 cols
        frames_col_size = int(len(fn_frames)/3)
        self.index.write("<div class=row>")
        self.index.write("<div class=col-sm-4>")
        for i, fn_frame in enumerate(fn_frames):
            if fn_frame.has_classes():
                fn_frame_file = "%s.html" % fn_frame.name
                self.index.write("<div class='vnlink frame-name'><a href=\"%s\">%s</a></div>\n" % (fn_frame_file, fn_frame.name))
                fh = open(os.path.join(self.directory, fn_frame_file), 'w')
                HtmlFNFrameWriter(fh, fn_frame).write()
                # this is where to split into cols
                if i in [frames_col_size, frames_col_size * 2]:
                    self.index.write("</div>")
                    self.index.write("<div class=col-sm-4>")
        self.index.write("</div></div>\n")

    def write_pure_frames(self, fn):
        self.pure_frame_index.write("<html>\n")
        self.pure_frame_index.write("<head>\n")
        self.pure_frame_index.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
        self.pure_frame_index.write(bootstrap_header())
        self.pure_frame_index.write("</head>\n")
        self.pure_frame_index.write("<body>\n")
        pure_frames = fn.get_pure_frames()
        self.pure_frame_index.write("<div class=framenet-header>")
        self.pure_frame_index.write("\n<h1 class=container>Pure Framenet Frames</h1>\n")
        self.pure_frame_index.write("\n</div>")
        self.pure_frame_index.write("<div class='container frames'>\n")
        self.pure_frame_index.write("<div class=back-button><a href=index.html><< back</a></div>")
        # order frames by purity
        pure_frames.sort(key=lambda x: x.purity(), reverse=True)
        # store size of 1/3 frames for splitting into 3 cols
        pure_frames_col_size = int(len(pure_frames) / 3)
        self.pure_frame_index.write("<div class=row>")
        self.pure_frame_index.write("<div class=col-sm-4>")
        for i, pure_frame in enumerate(pure_frames):
            if pure_frame.has_classes():
                pure_frame_file = "%s.html" % pure_frame.name
                self.pure_frame_index.write(
                    "<div class='vnlink frame-name'><a href=\"%s\">%s</a></div>\n" % (pure_frame_file, pure_frame.name))
                # this is where to split into cols
                if i in [pure_frames_col_size, pure_frames_col_size * 2]:
                    self.pure_frame_index.write("</div>")
                    self.pure_frame_index.write("<div class=col-sm-4>")
        self.pure_frame_index.write("</div></div>\n")

    def finish(self):
        self.index.write("</body>\n")
        self.index.write("</html>\n")

class HtmlFNFrameWriter(object):

    """Class that knows how to write the HTML representation for a GLVerbClass to a
    file handle."""

    def __init__(self, fh, fn_frame):
        self.fh = fh
        self.fn_frame = fn_frame

    def write(self):
        self.fh.write("<html>\n")
        self.fh.write("<head>\n")
        self.fh.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\">\n")
        self.fh.write(bootstrap_header())
        self.fh.write("</head>\n")
        self.fh.write("<body>\n")
        self.fh.write("\n<div class=framenet-header>")
        self.fh.write("<h1 class=container>%s</h1>\n" % str(self.fn_frame.name))
        self.fh.write("\n</div>")
        self.fh.write("<div class=container>")
        self.fh.write("\n<h3>VN Classes</h3>\n")
        for vn_class in self.fn_frame.get_vn_classes():
            if vn_class.has_vn_counterpart():
                self.fh.write("<div class=vn-class>")
                self.fh.write("<a class=vn-class-name data-toggle=collapse href=#vn-class-%s aria-expanded=true aria-controls=vn-class-%s>" % (vn_class.ID.replace('.', '-'), vn_class.ID.replace('.', '-')))
                self.fh.write(vn_class.full_name())
                self.fh.write("<span class=vn-class-plus>+</span>")
                self.fh.write("</a>")
                self.fh.write("<div id=vn-class-%s class='collapse in' role=tabpanel>" % vn_class.ID.replace('.', '-'))
                self.fh.write("<ul>")
                for member in vn_class.members:
                    self.pp_member(member)
                self.fh.write("</ul></div></div>")

        self.fh.write("</div></div>")

    def pp_member(self, vn_member):
        self.fh.write("<li class='vn-member'>")
        self.fh.write(vn_member.name)
        self.fh.write("</li>")

def bootstrap_header():
    # Add jquery
    jquery_ref = "<script src=\"https://ajax.googleapis.com/ajax/libs/jquery/3.2.0/jquery.min.js\"></script>"
    # Add bootstrap css
    css_ref = "<link rel=\"stylesheet\" href=\"https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css\">"
    # Add bootstrap JS
    js_ref = "<script src=\"https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js\"></script>"

    return jquery_ref + css_ref + js_ref
