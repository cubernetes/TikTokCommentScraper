from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


"""
Handling Shared and Array Formulae
"""

class SharedFormula(object):

    #__slots__ = ('range', 'key', 'expression')

    def __init__(self, range, key, expression):
        self.range = range
        self.key = key
        self.expression = expression

    def range(self):
        """Range of cells to which the formula applies"""

    def key(self):
        """Key"""

    def expression(self):
        """Expression"""


# Unpack expression?
# Value
# Return expression or information about shared formula?

# Creating - first incidence


if __name__ == "__main__":

    if 'key' not in ws.formula_attributes:
        shared = SharedFormula(range, key, expression)
        ws.formula_attributes[key] = shared
    else:
        # expression already stored
        pass
    cell.value = ws.formula_attributes[key].expression
