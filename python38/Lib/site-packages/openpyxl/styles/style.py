from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

from openpyxl.compat import safe_string

from openpyxl.descriptors.serialisable import Serialisable
from openpyxl.descriptors import (
    Alias,
    Typed,
    Bool,
    Integer,
    Set,
)

from openpyxl.xml.functions import Element


class StyleId(Serialisable):
    """
    Format aggregation class

    This is a virtual style composed of references to global format objects
    """
    tagname = "xf"

    numFmtId = Integer()
    number_format = Alias("numFmtId")
    fontId = Integer()
    font = Alias("fontId")
    fillId = Integer()
    fill = Alias("fillId")
    borderId = Integer()
    border = Alias("borderId")
    xfId = Integer()
    named_style = Alias("xfId")
    alignmentId = Integer()
    alignment = Alias("alignmentId")
    protectionId = Integer()
    protection = Alias("protectionId")
    quotePrefix = Bool(allow_none=True)
    pivotButton = Bool(allow_none=True)
    applyAlignment = Bool(allow_none=True)
    applyProtection = Bool(allow_none=True)


    def __init__(self,
                 numFmtId=0,
                 fontId=0,
                 fillId=0,
                 borderId=0,
                 alignmentId=0,
                 protectionId=0,
                 xfId=0,
                 quotePrefix=None,
                 pivotButton=None,
                 applyNumberFormat=None,
                 applyFont=None,
                 applyFill=None,
                 applyBorder=None,
                 applyAlignment=None,
                 applyProtection=None,
                 extLst=None,
                 ):
        self.numFmtId = numFmtId
        self.fontId = fontId
        self.fillId = fillId
        self.borderId = borderId
        self.xfId = xfId
        self.quotePrefix = quotePrefix
        self.pivotButton = pivotButton
        self.alignmentId = alignmentId
        self.protectionId = protectionId

    @property
    def applyAlignment(self):
        return self.alignmentId != 0 or None

    @property
    def applyProtection(self):
        return self.protectionId != 0 or None

    def to_tree(self):
        """
        Alignment and protection objects are implemented as child elements.
        This is a completely different API to other format objects. :-/
        """
        attrs = dict(self)
        if self.applyProtection:
            attrs['applyProtection'] = '1'
        if self.applyAlignment:
            attrs['applyAlignment'] = '1'
        for k in ('alignmentId', 'protectionId'):
            if k in attrs:
                del attrs[k]
        attrs = dict((k, safe_string(v)) for k,v in attrs.items())
        return Element(self.tagname, attrs)

    def __iter__(self):
        """
        Don't convert values to strings to allow use as **kw
        """
        attrs = set(self.__attrs__)
        for key in attrs:
            value = getattr(self, key)
            if value is not None:
                yield key, value

    def __eq__(self, other):
        return dict(self) == dict(other)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(tuple(self))

    def __repr__(self):
        return repr(dict(self))
