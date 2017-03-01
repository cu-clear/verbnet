# Class to write to the verbnet XML structure

import os
import xml.etree.ElementTree as ET


class XmlWriter(object):
  def __init__(self, directory='xml'):
    self.directory = directory
    self._write_begin()
  def write(self, gl_verb_classes):
    self.index = open(os.path.join(self.directory, 'index.html'), 'w')
    self.index.write("<td>\n")
    self.index.write("<table cellpadding=8 cellspacing=0>\n")
    self.index.write("<tr class=header><td>%s</a>\n" % header)
    for verbclass in gl_verb_classes:
      infix = group + '-' if group else ''
      class_file = "vnclass-%s%s.html" % (infix, verbclass.ID)
      self.index.write("<tr class=vnlink><td><a href=\"%s\">%s</a>\n" % (class_file, verbclass.ID))
      fh = open(os.path.join(self.directory, class_file), 'w')
      HtmlClassWriter(fh, verbclass).write()
    self.index.write("</table>\n")
    self.index.write("</td>\n")

  def finish(self):
    self.index.write("</tr>\n")
    self.index.write("</table>\n")
    self.index.write("</body>\n")
    self.index.write("</html>\n")


class XmlClassWriter(object):
  """Class that knows how to write the VN XML representation for a VerbClass to a
  file handle."""

  def __init__(self, filehandle, verbclass):
    self.filehandle = filehandle
    self.verbclass = verbclass
    self.root = ET.Element("VNCLASS", {"ID": verbclass.classname})

  def write(self, frames=None):
    self._add_members()
    self._add_themroles()
    self._add_frames()

  def _add_members(self):
    members_node = ET.SubElement(self.root, "MEMBERS")
    for member in vnclass.members:
      member_attributes = {"name": member.name[0], "wn": ' '.join(member.wn), "grouping": ' '.join(member.grouping)}
      ET.SubElement(members_node, "MEMBER", member_attributes)

  def _add_themroles(self):
    themroles_node = ET.SubElement(self.root, "THEMROLES")
    for themrole in vnclass.themroles:
      them_role_attributes = {"type": themrole.role_type}
      themrole_node = ET.SubElement(themroles_node, them_role_attributes)
      for selectional_restriction in themrole.sel_restrictions:
        selectional_restriction_attributes = {"value": , "type": }
        ET.SubElement(themrole_node, selectional_restriction, selectional_restriction_attributes)

  def _add_frames(self):

    all_frames = range(len(self.verbclass.frames))
    if frames is not None:
      all_frames = frames
    for i in all_frames:
      #
      vn_frame = self.verbclass.verbclass.frames[i]
      gl_frame = self.verbclass.frames[i]
      self.fh.write("\n<table class=frame cellpadding=8 cellspacing=0 border=0 width=1000>\n")
      self.pp_html_description(gl_frame, i)
      self.pp_html_example(gl_frame)
      self.pp_html_predicate(vn_frame)
      self.pp_html_subcat(gl_frame)
      self.pp_html_qualia(gl_frame)
      self.pp_html_event(gl_frame)
      self.fh.write("</table>\n\n")

  def subcats(self):

  def gl_subcat(self, gl_frame):
    self.fh.write("<tr class=qualia valign=top>\n")
    self.fh.write("  <td>GL&nbsp;subcategorisation\n")
    self.fh.write("  <td>\n")
    for element in gl_frame.subcat:
      # self.fh.write("      { %s } <br>\n" % element)
      self.fh.write("      {")
      if element.var is not None:
        self.fh.write(" var=%s" % element.var)
      self.fh.write(" cat=%s" % element.cat)
      if element.role:
        self.fh.write(" role=%s" % element.role[0])
      self.fh.write(" } / [")
      self.pp_html_restriction(element.sel_res)
      self.fh.write("]<br>\n")

  def gl_qualia(self, gl_frame):
    self.fh.write("<tr class=qualia valign=top>\n")
    self.fh.write("  <td>GL&nbsp;qualia&nbsp;structure\n")
    self.fh.write("  <td>%s\n" % gl_frame.qualia)

  def gl_event(self, gl_frame):
    self.fh.write("<tr class=event valign=top>\n")
    self.fh.write("  <td>GL event structure")
    self.fh.write("  <td>var = %s<br>\n" % gl_frame.events.var)
    self.fh.write("      initial_state = %s<br>\n" % gl_frame.events.initial_state)
    self.fh.write("      final_state = %s\n" % gl_frame.events.final_state)