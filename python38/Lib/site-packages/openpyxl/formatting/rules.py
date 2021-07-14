from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


from collections import Mapping

from openpyxl.compat import iteritems
from openpyxl.styles import Font, PatternFill, Border


class FormatRule(Mapping):
    """Utility dictionary for formatting rules with specified keys only"""

    __slots__ = ('aboveAverage', 'bottom', 'dxfId', 'equalAverage',
                 'operator', 'percent', 'priority', 'rank', 'stdDev', 'stopIfTrue',
                 'text', 'type', 'formula', 'colorScale', 'iconSet')

    def update(self, dictionary):
        for k, v in iteritems(dictionary):
            self[k] = v

    def __contains__(self, key):
        return hasattr(self, key)

    def __getitem__(self, key):
        if key not in self.__slots__:
            raise KeyError("{0} is not a valid key for a formatting rule".format(key))
        return getattr(self, key, None)

    def __setitem__(self, key, value):
        if key not in self.__slots__:
            raise KeyError("{0} is not a valid key for a formatting rule".format(key))
        setattr(self, key, value)

    def __iter__(self):
        return iter(self.__slots__)

    def iterkeys(self):
        for key in self.__slots__:
            if getattr(self, key, None) is not None:
                yield key
            continue

    def keys(self):
        return list(self.iterkeys())

    def itervalues(self):
        for key in self.iterkeys():
            yield self[key]

    def values(self):
        return list(self.itervalues())

    def iteritems(self):
        for key in self.iterkeys():
            yield key, getattr(self, key)

    def items(self):
        return [(key, value) for key, value in self.iteritems()]

    def __len__(self):
        return len(self.keys())


class ColorScaleRule(object):
    """Conditional formatting rule based on a color scale rule."""
    valid_types = ('min', 'max', 'num', 'percent', 'percentile', 'formula')
    type = 'colorScale'
    attrs = ('type', 'colorScale')

    def __init__(self,
                 start_type=None,
                 start_value=None,
                 start_color=None,
                 mid_type=None,
                 mid_value=None,
                 mid_color=None,
                 end_type=None,
                 end_value=None,
                 end_color=None
                 ):
        self.start_type = start_type
        self.start_value = start_value
        self.start_color = start_color
        self.mid_type = mid_type
        self.mid_value = mid_value
        self.mid_color = mid_color
        self.end_type = end_type
        self.end_value = end_value
        self.end_color = end_color

    @property
    def start_value(self):
        return self._start_value

    @start_value.setter
    def start_value(self, value):
        if value is not None and self.start_type in ('min', 'max'):
            raise ValueError("ColorScaleRule with min or max cannot have values")
        self._start_value = value

    @property
    def end_value(self):
        return self._end_value

    @end_value.setter
    def end_value(self, value):
        if value is not None and self.end_type in ('min', 'max'):
            raise ValueError("ColorScaleRule with min or max cannot have values")
        self._end_value = value

    @property
    def mid_value(self):
        return self._mid_value

    @mid_value.setter
    def mid_value(self, value):
        if value is not None and self.mid_type in ('min', 'max'):
            raise ValueError("ColorScaleRule with min or max cannot have values")
        self._mid_value = value

    @property
    def cfvo(self):
        """Return a dictionary representation"""
        vals = []
        for attr in 'start', 'mid', 'end':
            typ = getattr(self, attr + '_type')
            if typ is None:
                continue
            d = {'type': typ}
            v = getattr(self, attr + '_value')
            if v is not None:
                d['val'] = str(v)
            vals.append(d)
        return vals

    @property
    def colorScale(self):
        colors = [v for v in (self.start_color, self.mid_color, self.end_color) if v is not None]
        return {'color':colors, 'cfvo':self.cfvo}

    def __iter__(self):
        for attr in self.attrs:
            yield attr, getattr(self, attr)

    @property
    def rule(self):
        return dict(self)


class FormulaRule(object):
    """Conditional formatting rule based on a formula."""
    def __init__(self, formula=None, stopIfTrue=None, font=None, border=None, fill=None):
        self.formula = formula
        self.stopIfTrue = stopIfTrue
        self.font = font
        self.border = border
        self.fill = fill

    @property
    def rule(self):
        r = {'type': 'expression', 'formula': self.formula,
             'dxf': {'font': self.font, 'border': self.border, 'fill': self.fill}}
        if self.stopIfTrue:
            r['stopIfTrue'] = '1'
        return r


class CellIsRule(object):
    """Conditional formatting rule based on cell contents."""
    # Excel doesn't use >, >=, etc, but allow for ease of python development
    expand = {">": "greaterThan", ">=": "greaterThanOrEqual", "<": "lessThan", "<=": "lessThanOrEqual",
              "=": "equal", "==": "equal", "!=": "notEqual"}

    def __init__(self, operator=None, formula=None, stopIfTrue=None, font=None, border=None, fill=None):
        self.operator = operator
        self.formula = formula
        self.stopIfTrue = stopIfTrue
        self.font = font
        self.border = border
        self.fill = fill

    @property
    def operator(self):
        return self._operator

    @operator.setter
    def operator(self, value):
        expanded = self.expand.get(value)
        if expanded:
            self._operator = expanded
        else:
            self._operator = value

    @property
    def rule(self):
        r = {'type': 'cellIs', 'operator': self.operator, 'formula': self.formula,
             'dxf': {'font': self.font, 'border': self.border, 'fill': self.fill}}
        if self.stopIfTrue:
            r['stopIfTrue'] = '1'
        return r
