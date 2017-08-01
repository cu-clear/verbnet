possible_frames = {}

class Annotation(object):
  def __hash__(self):
    return hash(self.__str__())

  #Verify that this instance has a vn class, and the class/member pair is valid for a certain VN version
  #Verify that this instance has a vn class, and the class/member pair is valid for a certain VN version
  def check_vn(self, vn):
    try:
      self.vn_class
    except:
      return False

    if self.vn_class and vn.get_verb_class(self.vn_class):
      return self.verb.split() in [member.name for member in vn.get_verb_class(self.vn_class).members]
    else:
      return False

  #Verify that instance hsa fn frame, the frame is valid, and the member is in the frame
  def check_fn(self, fn):
    try:
      self.fn_frame
    except:
      return False

    #only build possible_frames once if we can
    global possible_frames
    if not possible_frames:
      for lu in fn.lus():
        if lu.frame.name not in possible_frames:
          possible_frames[lu.frame.name] = [lu.lexemes[0].name]
        else:
          possible_frames[lu.frame.name].append(lu.lexemes[0].name)

    if self.fn_frame not in possible_frames.keys() or self.verb not in possible_frames[self.fn_frame]:
        return False
    return True

  #PB and ON checking will probably require PB/ON apis that we can work with.
  def check_pb(self, pb):

    return False

  def check_on(self, on):

    return False

  # Update the line with info from a VN member
  def update_vn_info(self, vn_member):
    try:
      self.vn_class
    except:
      raise Exception ("this instace of Annotation object doesn't have a verbnet clsas")

    # AbstractXML method get_category() will return a list
    # But because it can only have one name, we can take index 0
    self.verb = vn_member.name[0]
    self.vn_class = vn_member.vn_class()

  # Check if the ref in the annotation exists in the given version of VN
  def exists_in(self, vn):
    if self.vn_class and vn.verb_classes_dict.get(self.vn_class):
      return self.verb in [member.name for member in vn.get_verb_class(self.vn_class).members]
    elif self.vn_class and vn.verb_classes_numerical_dict.get(self.vn_class):
      return self.verb in [member.name for member in vn.verb_classes_numerical_dict.get(self.vn_class).members]
    else:
      return False

class VnAnnotation(Annotation):
  def __init__(self, line, dep=[]):
    self.input_line = line.strip()
    attr_list = line.split()

    self.dep = dep
    self.source_file = attr_list[0]
    self.sentence_no = attr_list[1]
    self.token_no = attr_list[2]
    self.verb = attr_list[3]
    self.vn_class = attr_list[4]

  def __eq__(self, other):
    if self.sentence_no == other.sentence_no and self.token_no == other.token_no and self.verb == other.verb and self.vn_class == other.vn_class:
      return True
    else:
      return False

  def __str__(self):
    return self.source_file + " " + self.sentence_no + " " + self.token_no + " " + self.verb + " " + self.vn_class + " " + " ".join(
      self.dep)

class SemLinkAnnotation(Annotation):
  def __init__(self, line):
    self.input_line = line.strip()
    attr_list = line.split()

    self.source_file = attr_list[0] if len(attr_list) > 1 else None
    self.sentence_no = attr_list[1] if len(attr_list) > 2 else None
    self.token_no = attr_list[2] if len(attr_list) > 3 else None
    self.verb = attr_list[4][:-2] if len(attr_list) > 5 else None
    self.vn_class = attr_list[5] if len(attr_list) > 6 else None
    self.fn_frame = attr_list[6] if len(attr_list) > 7 else None
    self.pb_frame = attr_list[7] if len(attr_list) > 8 else None
    self.on_group = attr_list[8] if len(attr_list) > 9 else None
    self.dependencies = attr_list[10:] if len(attr_list) > 11 else None

  def __eq__(self, other):
    if self.source_file == other.source_file and self.sentence_no == other.sentence_no and self.token_no == other.token_no and self.verb == other.verb:
      return True
    else:
      return False

  def __str__(self):
    return self.source_file + " " + self.sentence_no + " " + self.token_no + " " + self.verb + " " + self.vn_class + " " + self.fn_frame + " " + self.pb_frame + " " + self.on_group + " " +  " ".join(self.dependencies)