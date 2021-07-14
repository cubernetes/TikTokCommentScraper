from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

"""Write worksheets to xml representations."""

# Python stdlib imports
from io import BytesIO

# compatibility imports

from openpyxl.compat import safe_string, itervalues, iteritems

from openpyxl import LXML

# package imports
from openpyxl.utils import (
    coordinate_from_string,
    column_index_from_string,
)
from openpyxl.xml.functions import (
    Element,
    SubElement,
    xmlfile,
)
from openpyxl.xml.constants import (
    SHEET_MAIN_NS,
    REL_NS,
)
from openpyxl.formatting import ConditionalFormatting
from openpyxl.worksheet.datavalidation import writer
from openpyxl.worksheet.properties import WorksheetProperties, write_sheetPr

from .etree_worksheet import write_cell


def write_properties(worksheet):
    wsp = worksheet.sheet_properties
    pr = write_sheetPr(wsp)
    return pr


def write_format(worksheet):
    attrs = {'defaultRowHeight': '15', 'baseColWidth': '10'}
    dimensions_outline = [dim.outline_level
                          for dim in itervalues(worksheet.column_dimensions)]
    if dimensions_outline:
        outline_level = max(dimensions_outline)
        if outline_level:
            attrs['outlineLevelCol'] = str(outline_level)
    return Element('sheetFormatPr', attrs)


def write_cols(worksheet):
    """Write worksheet columns to xml.

    <cols> may never be empty -
    spec says must contain at least one child
    """
    cols = []
    for label, dimension in iteritems(worksheet.column_dimensions):
        col_def = dict(dimension)
        if col_def == {}:
            continue
        idx = column_index_from_string(label)
        cols.append((idx, col_def))

    if not cols:
        return

    el = Element('cols')

    for idx, col_def in sorted(cols):
        v = "%d" % idx
        cmin = col_def.get('min') or v
        cmax = col_def.get('max') or v
        col_def.update({'min': cmin, 'max': cmax})
        el.append(Element('col', col_def))
    return el


def write_autofilter(worksheet):
    auto_filter = worksheet.auto_filter
    if auto_filter.ref is None:
        return

    el = Element('autoFilter', ref=auto_filter.ref)
    if (auto_filter.filter_columns
        or auto_filter.sort_conditions):
        for col_id, filter_column in sorted(auto_filter.filter_columns.items()):
            fc = SubElement(el, 'filterColumn', colId=str(col_id))
            attrs = {}
            if filter_column.blank:
                attrs = {'blank': '1'}
            flt = SubElement(fc, 'filters', attrs)
            for val in filter_column.vals:
                flt.append(Element('filter', val=val))
        if auto_filter.sort_conditions:
            srt = SubElement(el, 'sortState', ref=auto_filter.ref)
            for sort_condition in auto_filter.sort_conditions:
                sort_attr = {'ref': sort_condition.ref}
                if sort_condition.descending:
                    sort_attr['descending'] = '1'
                srt.append(Element('sortCondtion', sort_attr))
    return el


def write_mergecells(worksheet):
    """Write merged cells to xml."""
    cells = worksheet._merged_cells
    if not cells:
        return

    merge = Element('mergeCells', count='%d' % len(cells))
    for range_string in cells:
        merge.append(Element('mergeCell', ref=range_string))
    return merge


def write_conditional_formatting(worksheet):
    """Write conditional formatting to xml."""
    for range_string, rules in iteritems(worksheet.conditional_formatting.cf_rules):
        if not len(rules):
            # Skip if there are no rules.  This is possible if a dataBar rule was read in and ignored.
            continue
        cf = Element('conditionalFormatting', {'sqref': range_string})
        for rule in rules:
            if rule['type'] == 'dataBar':
                # Ignore - uses extLst tag which is currently unsupported.
                continue
            attr = {'type': rule['type']}
            for rule_attr in ConditionalFormatting.rule_attributes:
                if rule_attr in rule:
                    attr[rule_attr] = str(rule[rule_attr])
            cfr = SubElement(cf, 'cfRule', attr)
            if 'formula' in rule:
                for f in rule['formula']:
                    SubElement(cfr, 'formula').text = f
            if 'colorScale' in rule:
                cs = SubElement(cfr, 'colorScale')
                for cfvo in rule['colorScale']['cfvo']:
                    SubElement(cs, 'cfvo', cfvo)
                for color in rule['colorScale']['color']:
                    SubElement(cs, 'color', dict(color))
            if 'iconSet' in rule:
                iconAttr = {}
                for icon_attr in ConditionalFormatting.icon_attributes:
                    if icon_attr in rule['iconSet']:
                        iconAttr[icon_attr] = rule['iconSet'][icon_attr]
                iconSet = SubElement(cfr, 'iconSet', iconAttr)
                for cfvo in rule['iconSet']['cfvo']:
                    SubElement(iconSet, 'cfvo', cfvo)
        yield cf


def write_datavalidation(worksheet):
    """ Write data validation(s) to xml."""
    # Filter out "empty" data-validation objects (i.e. with 0 cells)
    required_dvs = [x for x in worksheet._data_validations
                    if len(x.cells) or len(x.ranges)]
    if not required_dvs:
        return

    dvs = Element("{%s}dataValidations" % SHEET_MAIN_NS,
                  count=str(len(required_dvs)))
    for dv in required_dvs:
        dvs.append(writer(dv))

    return dvs


def write_header_footer(worksheet):
    header = worksheet.header_footer.getHeader()
    footer = worksheet.header_footer.getFooter()
    if header or footer:
        tag = Element('headerFooter')
        if header:
            SubElement(tag, 'oddHeader').text = header
        if footer:
            SubElement(tag, 'oddFooter').text = footer
        return tag


def write_hyperlinks(worksheet):
    """Write worksheet hyperlinks to xml."""
    tag = Element('hyperlinks')
    for cell in worksheet.get_cell_collection():
        if cell.hyperlink_rel_id is not None:
            attrs = {'display': cell.hyperlink,
                     'ref': cell.coordinate,
                     '{%s}id' % REL_NS: cell.hyperlink_rel_id}
            tag.append(Element('hyperlink', attrs))
    if tag.getchildren():
        return tag


def write_pagebreaks(worksheet):
    breaks = worksheet.page_breaks
    if breaks:
        tag = Element('rowBreaks', {'count': str(len(breaks)),
                                     'manualBreakCount': str(len(breaks))})
        for b in breaks:
            tag.append(Element('brk', id=str(b), man="true", max='16383',
                               min='0'))
        return tag


def write_worksheet(worksheet, shared_strings):
    """Write a worksheet to an xml file."""
    if LXML is True:
        from .lxml_worksheet import write_cell, write_rows
    else:
        from .etree_worksheet import write_cell, write_rows

    out = BytesIO()

    with xmlfile(out) as xf:
        with xf.element('worksheet', xmlns=SHEET_MAIN_NS):

            props = write_properties(worksheet)
            xf.write(props)

            dim = Element('dimension', {'ref': '%s' % worksheet.calculate_dimension()})
            xf.write(dim)

            views = Element('sheetViews')
            views.append(worksheet.sheet_view.to_tree())
            xf.write(views)

            xf.write(write_format(worksheet))
            cols = write_cols(worksheet)
            if cols is not None:
                xf.write(cols)
            write_rows(xf, worksheet)

            if worksheet.protection.sheet:
                prot = Element('sheetProtection', dict(worksheet.protection))
                xf.write(prot)

            af = write_autofilter(worksheet)
            if af is not None:
                xf.write(af)

            merge = write_mergecells(worksheet)
            if merge is not None:
                xf.write(merge)

            cfs = write_conditional_formatting(worksheet)
            for cf in cfs:
                xf.write(cf)

            dv = write_datavalidation(worksheet)
            if dv is not None:
                xf.write(dv)

            hyper = write_hyperlinks(worksheet)
            if hyper is not None:
                xf.write(hyper)


            options = worksheet.print_options
            if len(dict(options)) > 0:
                new_element = options.write_xml_element()
                xf.write(new_element)
                del new_element

            margins = Element('pageMargins', dict(worksheet.page_margins))
            xf.write(margins)
            del margins

            setup = worksheet.page_setup
            if len(dict(setup)) > 0:
                new_element = setup.write_xml_element()
                xf.write(new_element)
                del new_element

            hf = write_header_footer(worksheet)
            if hf is not None:
                xf.write(hf)

            if worksheet._charts or worksheet._images:
                drawing = Element('drawing', {'{%s}id' % REL_NS: 'rId1'})
                xf.write(drawing)
                del drawing

            pb = write_pagebreaks(worksheet)
            if pb is not None:
                xf.write(pb)

            # If vba is being preserved then add a legacyDrawing element so
            # that any controls can be drawn.
            if worksheet.vba_controls is not None:
                xml = Element("{%s}legacyDrawing" % SHEET_MAIN_NS,
                              {"{%s}id" % REL_NS : worksheet.vba_controls})
                xf.write(xml)
            elif worksheet._comment_count > 0:
                # add a legacyDrawing so that excel can draw comments
                # If a legacyDrawing element has already been added then
                # we have to hope it already contains the vml for
                # comments because we cannot add another.
                comments = Element('{%s}legacyDrawing' % SHEET_MAIN_NS,
                                {'{%s}id' % REL_NS: 'commentsvml'})
                xf.write(comments)

    xml = out.getvalue()
    out.close()
    return xml
