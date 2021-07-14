from __future__ import absolute_import
#copyright openpyxl 2010-2015

"""
Excel specific descriptors
"""

from openpyxl.compat import basestring
from . import MatchPattern, MinMax, Integer


class HexBinary(MatchPattern):

    pattern = "[0-9a-fA-F]+$"


class UniversalMeasure(MatchPattern):

    pattern = "[0-9]+(\.[0-9]+)?(mm|cm|in|pt|pc|pi)"


class TextPoint(MinMax):
    """
    Size in hundredths of points.
    In theory other units of measurement can be used but these are unbounded
    """
    expected_type = int

    min = -400000
    max = 400000


Coordinate = Integer


class Percentage(MatchPattern):

    pattern = "((100)|([0-9][0-9]?))(\.[0-9][0-9]?)?%"
