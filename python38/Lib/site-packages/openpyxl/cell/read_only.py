from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


from openpyxl.compat import unicode

from openpyxl.cell import Cell
from openpyxl.utils.datetime  import from_excel
from openpyxl.styles import is_date_format, Style
from openpyxl.styles.numbers import BUILTIN_FORMATS
from openpyxl.styles.styleable import StyleableObject


class ReadOnlyCell(object):

    __slots__ =  ('parent', 'row', 'column', '_value', 'data_type', '_style_id')

    def __init__(self, sheet, row, column, value, data_type='n', style_id=None):
        self.parent = sheet
        self._value = None
        self.row = row
        self.column = column
        self.data_type = data_type
        self.value = value
        self._style_id = style_id

    def __eq__(self, other):
        for a in self.__slots__:
            if getattr(self, a) != getattr(other, a):
                return
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def shared_strings(self):
        return self.parent.shared_strings

    @property
    def base_date(self):
        return self.parent.base_date

    @property
    def coordinate(self):
        if self.row is None or self.column is None:
            raise AttributeError("Empty cells have no coordinates")
        return "{1}{0}".format(self.row, self.column)

    @property
    def style_id(self):
        if not self._style_id:
            return
        return self.parent.parent._cell_styles[self._style_id]

    @property
    def number_format(self):
        if not self.style_id:
            return
        _id = self.style_id.number_format
        if _id < 164:
            return BUILTIN_FORMATS.get(_id, "General")
        else:
            return self.parent.parent._number_formats[_id - 164]

    @property
    def font(self):
        _id = self.style_id.font
        return self.parent.parent._fonts[_id]

    @property
    def fill(self):
        _id = self.style_id.fill
        return self.parent.parent._fills[_id]

    @property
    def border(self):
        _id = self.style_id.border
        return self.parent.parent._borders[_id]

    @property
    def alignment(self):
        _id = self.style_id.alignment
        return self.parent.parent._alignments[_id]

    @property
    def protection(self):
        _id = self.style_id.protection
        return self.parent.parent._protections[_id]

    @property
    def is_date(self):
        return self.data_type == 'n' and is_date_format(self.number_format)

    @property
    def internal_value(self):
        return self._value

    @property
    def value(self):
        if self._value is None:
            return
        if self.data_type == 'n':
            if is_date_format(self.number_format):
                return from_excel(self._value, self.base_date)
            return self._value
        if self.data_type == 'b':
            return self._value == '1'
        elif self.data_type in(Cell.TYPE_INLINE, Cell.TYPE_FORMULA_CACHE_STRING):
            return unicode(self._value)
        elif self.data_type == 's':
            return unicode(self.shared_strings[int(self._value)])
        return self._value

    @value.setter
    def value(self, value):
        if self._value is not None:
            raise AttributeError("Cell is read only")
        if value is None:
            self.data_type = 'n'
        elif self.data_type == 'n':
            try:
                value = int(value)
            except ValueError:
                value = float(value)
        self._value = value

    @property
    def style(self):
        return Style(font=self.font, alignment=self.alignment,
                     fill=self.fill, number_format=self.number_format, border=self.border,
                     protection=self.protection)


EMPTY_CELL = ReadOnlyCell(None, None, None, None)
