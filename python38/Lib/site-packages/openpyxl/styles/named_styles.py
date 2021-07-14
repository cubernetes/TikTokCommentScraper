from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


from openpyxl.descriptors import (
    Strict,
    Typed,
)
from .fills import PatternFill, GradientFill, Fill
from . fonts import Font
from . borders import Border
from . alignment import Alignment
from . numbers import NumberFormatDescriptor
from . protection import Protection

from openpyxl.xml.constants import SHEET_MAIN_NS


class NamedStyle(Strict):

    tag = '{%s}cellStyleXfs' % SHEET_MAIN_NS

    """
    Named and editable styles
    """

    font = Typed(expected_type=Font)
    fill = Typed(expected_type=Fill)
    border = Typed(expected_type=Border)
    alignment = Typed(expected_type=Alignment)
    number_format = NumberFormatDescriptor()
    protection = Typed(expected_type=Protection)

    __fields__ = ("name", "font", "fill", "border", "number_format", "alignment", "protection")

    def __init__(self,
                 name,
                 font=Font(),
                 fill=PatternFill(),
                 border=Border(),
                 alignment=Alignment(),
                 number_format=None,
                 protection=Protection()
                 ):
        self.name = name
        self.font = font
        self.fill = fill
        self.border = border
        self.alignment = alignment
        self.number_format = number_format
        self.protection = protection


    def _make_key(self):
        """Use a tuple of fields as the basis for a key"""
        self._key = hash(tuple(getattr(self, x) for x in self.__fields__))

    def __hash__(self):
        if not hasattr(self, '_key'):
            self._make_key()
        return self._key


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if not hasattr(self, '_key'):
                self._make_key()
            if not hasattr(other, '_key'):
                other._make_key()
            return self._key == other._key
        return self._key == other

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        pieces = []
        for k in self.__fields__:
            value = getattr(self, k)
            pieces.append('%s=%s' % (k, repr(value)))
        return '%s(%s)' % (self.__class__.__name__, ', '.join(pieces))
