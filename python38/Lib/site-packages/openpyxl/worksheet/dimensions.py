from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

from openpyxl.compat import safe_string
from openpyxl.cell import get_column_interval, column_index_from_string
from openpyxl.descriptors import Integer, Float, Bool, Strict, String, Alias
from openpyxl.compat import OrderedDict
from openpyxl.styles.styleable import StyleableObject


class Dimension(Strict, StyleableObject):
    """Information about the display properties of a row or column."""
    __fields__ = ('index',
                 'hidden',
                 'outlineLevel',
                 'collapsed',)

    index = Integer()
    hidden = Bool()
    outlineLevel = Integer(allow_none=True)
    outline_level = Alias('outlineLevel')
    collapsed = Bool()
    _style_id = None

    def __init__(self, index, hidden, outlineLevel,
                 collapsed, worksheet, visible=True, style=None):
        super(Dimension, self).__init__(sheet=worksheet)
        self.index = index
        self.hidden = hidden
        self.outlineLevel = outlineLevel
        self.collapsed = collapsed
        if style is not None:
            style_id = int(style)
            style = self.parent.parent._cell_styles[style_id]
            self._font_id = style.fontId
            self._fill_id = style.fillId
            self._border_id = style.borderId
            self._alignment_id = style.alignmentId
            self._protection_id = style.protectionId
            self._number_format_id = style.numFmtId


    def __iter__(self):
        for key in self.__fields__[1:]:
            value = getattr(self, key)
            if value:
                yield key, safe_string(value)

    @property
    def visible(self):
        return not self.hidden


class RowDimension(Dimension):
    """Information about the display properties of a row."""

    __fields__ = Dimension.__fields__ + ('ht', 'customFormat', 'customHeight', 's')
    r = Alias('index')
    ht = Float(allow_none=True)
    height = Alias('ht')
    thickBot = Bool()
    thickTop = Bool()

    def __init__(self,
                 worksheet,
                 index=0,
                 ht=None,
                 customHeight=None, # do not write
                 s=None,
                 customFormat=None, # do not write
                 hidden=False,
                 outlineLevel=0,
                 outline_level=None,
                 collapsed=False,
                 visible=None,
                 height=None,
                 r=None,
                 spans=None,
                 thickBot=None,
                 thickTop=None,
                 **kw
                 ):
        if r is not None:
            index = r
        if height is not None:
            ht = height
        self.ht = ht
        if visible is not None:
            hidden = not visible
        if outline_level is not None:
            outlineLevel = outlineLevel
        super(RowDimension, self).__init__(index, hidden, outlineLevel,
                                           collapsed, worksheet, style=s)

    @property
    def customFormat(self):
        """Always true if there is a style for the row"""
        return self.has_style

    @property
    def customHeight(self):
        """Always true if there is a height for the row"""
        return self.ht is not None

    #@property
    #def s(self):
        #return self.styleid

    #@s.setter
    #def s(self, style):
        #self._style = style

    def __iter__(self):
        for key in self.__fields__[1:]:
            if key == 's':
                value = getattr(self, 'style_id')
            else:
                value = getattr(self, key)
            if value:
                yield key, safe_string(value)


class ColumnDimension(Dimension):
    """Information about the display properties of a column."""

    width = Float(allow_none=True)
    bestFit = Bool()
    auto_size = Alias('bestFit')
    index = String()
    min = Integer(allow_none=True)
    max = Integer(allow_none=True)
    collapsed = Bool()

    __fields__ = Dimension.__fields__ + ('width', 'bestFit', 'customWidth', 'style',
                                         'min', 'max')

    def __init__(self,
                 worksheet,
                 index='A',
                 width=None,
                 bestFit=False,
                 hidden=False,
                 outlineLevel=0,
                 outline_level=None,
                 collapsed=False,
                 style=None,
                 min=None,
                 max=None,
                 customWidth=False, # do not write
                 visible=None,
                 auto_size=None,):
        self.width = width
        self.min = min
        self.max = max
        if visible is not None:
            hidden = not visible
        if auto_size is not None:
            bestFit = auto_size
        self.bestFit = bestFit
        if outline_level is not None:
            outlineLevel = outline_level
        self.collapsed = collapsed
        super(ColumnDimension, self).__init__(index, hidden, outlineLevel,
                                              collapsed, worksheet, style=style)

    @property
    def customWidth(self):
        """Always true if there is a width for the column"""
        return self.width is not None

    def __iter__(self):
        for key in self.__fields__[1:]:
            if key == 'style':
                value = self.style_id
            else:
                value = getattr(self, key)
            if value:
                yield key, safe_string(value)

   #@property
    # def col_label(self):
        # return get_column_letter(self.index)


class DimensionHolder(OrderedDict):
    "hold (row|column)dimensions and allow operations over them"
    def __init__(self, worksheet, direction, *args, **kwargs):
        self.worksheet = worksheet
        self.direction = direction
        super(DimensionHolder, self).__init__(*args, **kwargs)

    def group(self, start, end=None, outline_level=1, hidden=False):
        """allow grouping a range of consecutive columns together

        :param start: first column to be grouped (mandatory)
        :param end: last column to be grouped (optional, default to start)
        :param outline_level: outline level
        :param hidden: should the group be hidden on workbook open or not
        """
        if end is None:
            end = start
        if start in self:
            new_dim = self.pop(start)
        else:
            new_dim = ColumnDimension(worksheet=self.worksheet, index=start)

        work_sequence = get_column_interval(start, end)
        for column_letter in work_sequence:
            if column_letter in self:
                del self[column_letter]
        new_dim.min, new_dim.max = map(column_index_from_string, (start, end))
        new_dim.outline_level = outline_level
        new_dim.hidden = hidden
        self[start] = new_dim
