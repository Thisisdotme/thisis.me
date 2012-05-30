'''
Created on May 26, 2012

@author: howard
'''


def to_boolean(val):
  """
  Get the boolean value of the provided input.

      If the value is a boolean return the value.
      Otherwise check to see if the value is in
      ["false", "f", "no", "n", "none", "0", "[]", "{}", "" ]
      and returns True if value is not in the list
  """

  if val is True or val is False:
      return val

  falseItems = ["false", "f", "no", "n", "none", "0", "[]", "{}", ""]

  return not str(val).strip().lower() in falseItems
