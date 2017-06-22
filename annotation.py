class Annotation(object):
  def __init__(self, line, dep=[]):
    self.input_line = line.strip()

    attr_list = self.input_line.split()

    self.dep = dep
    self.source_file = attr_list[0]
    self.sentence_no = attr_list[1]
    self.token_no = attr_list[2]
    self.verb = attr_list[3]
    self.class_ID = attr_list[4]

  def __eq__(self, other):
    if self.sentence_no == other.sentence_no and self.token_no == other.token_no and self.verb == other.verb and self.class_ID == other.class_ID:
      return True
    else:
      return False

  def __hash__(self):
    return hash(self.__str__())

  def __str__(self):
    return self.source_file + " " + self.sentence_no + " " + self.token_no + " " + self.verb + " " + self.class_ID + " " + " ".join(
      self.dep)

  # Check if the ref in the annotation exists in the given version of VN
  def exists_in(self, vn):
    if self.class_ID and vn.get_verb_class(self.class_ID):
        return self.verb.split() in [member.name for member in vn.get_verb_class(self.class_ID).members]
    else:
        return False

  # Update the line with info from a VN member
  def update_vn_info(self, vn_member):
    # AbstractXML method get_category() will return a list
    # But because it can only have one name, we can take index 0
    self.verb = vn_member.name[0]
    self.class_ID = vn_member.class_id()