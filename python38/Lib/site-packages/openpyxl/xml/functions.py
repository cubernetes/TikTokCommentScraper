from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

"""Shared xml tools.

Shortcut functions taken from:
    http://lethain.com/entry/2009/jan/22/handling-very-large-csv-and-xml-files-in-python/

"""

# Python stdlib imports
import re
from functools import partial
from xml.sax.saxutils import XMLGenerator

XMLGenerator = partial(XMLGenerator, encoding="utf-8")

# compatibility

# package imports
from openpyxl import LXML

if LXML is True:
    from lxml.etree import (
    Element,
    ElementTree,
    SubElement,
    fromstring,
    tostring,
    register_namespace,
    iterparse,
    QName,
    xmlfile
    )
    from xml.etree.cElementTree import iterparse
else:
    try:
        from xml.etree.cElementTree import (
        ElementTree,
        Element,
        SubElement,
        fromstring,
        tostring,
        iterparse,
        QName
        )
    except ImportError:
        from xml.etree.ElementTree import (
        ElementTree,
        Element,
        SubElement,
        fromstring,
        tostring,
        iterparse,
        QName
        )
    from .namespace import register_namespace
    from .xmlfile import xmlfile


from openpyxl.xml.constants import (
    CHART_NS,
    DRAWING_NS,
    SHEET_DRAWING_NS,
    CHART_DRAWING_NS,
    SHEET_MAIN_NS,
    REL_NS,
    VTYPES_NS,
    COREPROPS_NS,
    DCTERMS_NS,
    DCTERMS_PREFIX
)

# allow LXML interface
_iterparse = iterparse
def safe_iterparse(source, *args, **kw):
    return _iterparse(source)

iterparse = safe_iterparse


register_namespace(DCTERMS_PREFIX, DCTERMS_NS)
register_namespace('dcmitype', 'http://purl.org/dc/dcmitype/')
register_namespace('cp', COREPROPS_NS)
register_namespace('c', CHART_NS)
register_namespace('a', DRAWING_NS)
register_namespace('s', SHEET_MAIN_NS)
register_namespace('r', REL_NS)
register_namespace('vt', VTYPES_NS)
register_namespace('xdr', SHEET_DRAWING_NS)
register_namespace('cdr', CHART_DRAWING_NS)


tostring = partial(tostring, encoding="utf-8")


def get_document_content(xml_node):
    """Print nicely formatted xml to a string."""
    pretty_indent(xml_node)
    return tostring(xml_node)


def pretty_indent(elem, level=0):
    """Format xml with nice indents and line breaks."""
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            pretty_indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def safe_iterator(node, tag=None):
    """Return an iterator that is compatible with Python 2.6"""
    if node is None:
        return []
    if hasattr(node, "iter"):
        return node.iter(tag)
    else:
        return node.getiterator(tag)


def ConditionalElement(node, tag, condition, attr=None):
    """
    Utility function for adding nodes if certain criteria are fulfilled
    An optional attribute can be passed in which will always be serialised as '1'
    """
    sub = partial(SubElement, node, tag)
    if bool(condition):
        if isinstance(attr, str):
            elem = sub({attr:'1'})
        elif isinstance(attr, dict):
            elem = sub(attr)
        else:
            elem = sub()
        return elem


NS_REGEX = re.compile("{(?P<namespace>.*)}(?P<localname>.*)")

def localname(node):
    m = NS_REGEX.match(node.tag)
    return m.group('localname')
