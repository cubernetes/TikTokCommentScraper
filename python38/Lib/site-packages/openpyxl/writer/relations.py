from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


from openpyxl.xml.functions import Element, SubElement
from openpyxl.xml.constants import (
    COMMENTS_NS,
    PKG_REL_NS,
    REL_NS,
    VML_NS,
)


def write_rels(worksheet, drawing_id, comments_id, vba_controls_id):
    """Write relationships for the worksheet to xml."""
    root = Element('{%s}Relationships' % PKG_REL_NS)
    for rel in worksheet.relationships:
        attrs = {'Id': rel.id, 'Type': rel.type, 'Target': rel.target}
        if rel.target_mode:
            attrs['TargetMode'] = rel.target_mode
        SubElement(root, '{%s}Relationship' % PKG_REL_NS, attrs)
    if worksheet._charts or worksheet._images:
        attrs = {'Id': 'rId1',
                 'Type': '%s/drawing' % REL_NS,
                 'Target': '../drawings/drawing%s.xml' % drawing_id}
        SubElement(root, '{%s}Relationship' % PKG_REL_NS, attrs)

    if worksheet.vba_controls is not None:
        attrs = {'Id': worksheet.vba_controls,
                 'Type': VML_NS,
                 'Target': '../drawings/vmlDrawing%s.vml' % vba_controls_id}
        SubElement(root, '{%s}Relationship' % PKG_REL_NS, attrs)
    if worksheet._comment_count > 0:
        # there's only one comments sheet per worksheet,
        # so there's no reason to call the Id rIdx
        attrs = {'Id': 'comments',
                 'Type': COMMENTS_NS,
                 'Target': '../comments%s.xml' % comments_id}
        SubElement(root, '{%s}Relationship' % PKG_REL_NS, attrs)
        if worksheet.vba_controls is None:
            attrs = {'Id': 'commentsvml',
                     'Type': VML_NS,
                     'Target': '../drawings/commentsDrawing%s.vml' % comments_id}
            SubElement(root, '{%s}Relationship' % PKG_REL_NS, attrs)
    return root
