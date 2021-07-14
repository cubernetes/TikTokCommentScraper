from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


from openpyxl.xml.constants import REL_NS, PKG_REL_NS
from openpyxl.xml.functions import Element, SubElement, tostring

class Relationship(object):
    """Represents many kinds of relationships."""
    # TODO: Use this object for workbook relationships as well as
    # worksheet relationships

    TYPES = ("hyperlink", "drawing", "image")

    def __init__(self, rel_type, target=None, target_mode=None, id=None):
        if rel_type not in self.TYPES:
            raise ValueError("Invalid relationship type %s" % rel_type)
        self.type = "%s/%s" % (REL_NS, rel_type)
        self.target = target
        self.target_mode = target_mode
        self.id = id

    def __repr__(self):
        root = Element("{%s}Relationships" % PKG_REL_NS)
        SubElement(root, "{%s}Relationship" % PKG_REL_NS, self.__dict__)
        return tostring(root)

