from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

"""Write the shared style table."""

# package imports

from openpyxl.compat import safe_string
from openpyxl.utils.indexed_list import IndexedList
from openpyxl.xml.functions import (
    Element,
    SubElement,
    ConditionalElement,
    tostring,
    )
from openpyxl.xml.constants import SHEET_MAIN_NS

from openpyxl.styles.colors import COLOR_INDEX
from openpyxl.styles import DEFAULTS
from openpyxl.styles import numbers
from openpyxl.styles.fills import GradientFill, PatternFill


class StyleWriter(object):

    def __init__(self, workbook):
        self.wb = workbook
        self._root = Element('styleSheet', {'xmlns': SHEET_MAIN_NS})

    @property
    def styles(self):
        return self.wb._cell_styles

    @property
    def fonts(self):
        return self.wb._fonts

    @property
    def fills(self):
        return self.wb._fills

    @property
    def borders(self):
        return self.wb._borders

    @property
    def number_formats(self):
        return self.wb._number_formats

    @property
    def alignments(self):
        return self.wb._alignments

    @property
    def protections(self):
        return self.wb._protections

    def write_table(self):
        self._write_number_formats()
        self._write_fonts()
        self._write_fills()
        self._write_borders()

        self._write_named_styles()
        self._write_cell_styles()
        self._write_style_names()
        self._write_differential_styles()
        self._write_table_styles()
        self._write_colors()

        return tostring(self._root)


    def _write_number_formats(self):
        node = SubElement(self._root, 'numFmts', count= "%d" % len(self.number_formats))
        for idx, nf in enumerate(self.number_formats, 164):
            SubElement(node, 'numFmt', {'numFmtId':'%d' % idx,
                                        'formatCode':'%s' % nf}
                       )

    def _write_fonts(self):
        fonts_node = SubElement(self._root, 'fonts', count="%d" % len(self.fonts))
        for font in self.fonts:
            fonts_node.append(font.to_tree())


    def _write_fills(self):
        fills_node = SubElement(self._root, 'fills', count="%d" % len(self.fills))
        for fill in self.fills:
            fills_node.append(fill.to_tree())

    def _write_borders(self):
        """Write the child elements for an individual border section"""
        borders_node = SubElement(self._root, 'borders', count="%d" % len(self.borders))
        for border in self.borders:
            borders_node.append(border.to_tree())

    def _write_named_styles(self):
        cell_style_xfs = SubElement(self._root, 'cellStyleXfs', {'count':'1'})
        SubElement(cell_style_xfs, 'xf',
            {'numFmtId':"0", 'fontId':"0", 'fillId':"0", 'borderId':"0"})

    def _write_cell_styles(self):
        """ write styles combinations based on ids found in tables """
        # writing the cellXfs
        cell_xfs = SubElement(self._root, 'cellXfs',
                              count='%d' % len(self.styles))

        for style in self.styles:

            node = style.to_tree()
            cell_xfs.append(node)

            if style.applyAlignment:
                node.set('applyAlignment', '1')
                al = self.alignments[style.alignmentId]
                el = al.to_tree()
                node.append(el)

            if style.applyProtection:
                node.set('applyProtection', '1')
                prot = self.protections[style.protectionId]
                el = prot.to_tree()
                node.append(el)


    def _write_style_names(self):
        cell_styles = SubElement(self._root, 'cellStyles', {'count':'1'})
        SubElement(cell_styles, 'cellStyle',
            {'name':"Normal", 'xfId':"0", 'builtinId':"0"})


    def _write_differential_styles(self):
        dxfs = SubElement(self._root, "dxfs", count=str(len(self.wb._differential_styles)))
        for fmt in self.wb._differential_styles:
            dxfs.append(fmt.to_tree())
        return dxfs


    def _write_table_styles(self):

        SubElement(self._root, 'tableStyles',
            {'count':'0', 'defaultTableStyle':'TableStyleMedium9',
            'defaultPivotStyle':'PivotStyleLight16'})

    def _write_colors(self):
        """
        Workbook contains a different colour index.
        """

        colors = self.wb._colors
        if colors == COLOR_INDEX:
            return

        cols = SubElement(self._root, "colors")
        rgb = SubElement(cols, "indexedColors")
        for color in colors:
            SubElement(rgb, "rgbColor", rgb=color)
