from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


from .reference import Reference


class ErrorBar(object):

    PLUS = 1
    MINUS = 2
    PLUS_MINUS = 3

    def __init__(self, _type, values):

        self.type = _type
        self.values = values

    @property
    def values(self):
        """Return values from underlying reference"""
        return self._values

    @values.setter
    def values(self, reference):
        """Assign values from reference to serie"""
        if reference is not None:
            if not isinstance(reference, Reference):
                raise TypeError("Errorbar values must be a Reference instance")
            self._values = reference.values
        else:
            self._values = None
