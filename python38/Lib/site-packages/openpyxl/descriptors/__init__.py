from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

from .base import *


class MetaStrict(type):

    def __new__(cls, clsname, bases, methods):
        for k, v in methods.items():
            if isinstance(v, Descriptor):
                v.name = k
        return type.__new__(cls, clsname, bases, methods)


class MetaSerialisable(type):

    def __new__(cls, clsname, bases, methods):
        attrs = []
        nested = []
        elements = []
        for k, v in methods.items():
            if isinstance(v, Descriptor):
                if getattr(v, 'nested', False):
                    nested.append(k)
                elif isinstance(v, Sequence):
                    elements.append(k)
                elif isinstance(v, Typed):
                    if hasattr(v.expected_type, 'to_tree'):
                        elements.append(k)
                    else:
                        attrs.append(k)
                else:
                    if not isinstance(v, Alias):
                        attrs.append(k)
        methods['__attrs__'] = tuple(attrs)
        if methods.get('__nested__') is None:
            methods['__nested__'] = tuple(sorted(nested))
        if methods.get('__elements__') is None:
            methods['__elements__'] = tuple(sorted(elements))
        return MetaStrict.__new__(cls, clsname, bases, methods)


Strict = MetaStrict('Strict', (object,), {})

_Serialiasable = MetaSerialisable('_Serialisable', (object,), {})

#del MetaStrict
#del MetaSerialisable
