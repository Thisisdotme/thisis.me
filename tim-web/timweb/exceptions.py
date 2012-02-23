
class GenericError(Exception):
  def __init__(self, msg):
    self.msg = msg
  
class UnexpectedAPIResponse(Exception):
  def __init__(self, msg):
    self.msg = msg