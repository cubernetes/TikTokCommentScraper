from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

from openpyxl.compat import iterkeys, itervalues, safe_string

from openpyxl.utils import COORD_RE, column_index_from_string
from openpyxl.xml.functions import xmlfile, Element, SubElement


def row_sort(cell):
    """Translate column names for sorting."""
    return column_index_from_string(cell.column)


def get_rows_to_write(worksheet):
    """Return all rows, and any cells that they contain"""
    # Ensure a blank cell exists if it has a style
    for styleCoord in iterkeys(worksheet._styles):
        if isinstance(styleCoord, str) and COORD_RE.search(styleCoord):
            worksheet.cell(styleCoord)

    # create rows of cells
    cells_by_row = {}
    for cell in itervalues(worksheet._cells):
        cells_by_row.setdefault(cell.row, []).append(cell)

    # make sure rows that only have a height set are returned
    for row_idx in worksheet.row_dimensions:
        if row_idx not in cells_by_row:
            cells_by_row[row_idx] = []

    return cells_by_row


def write_rows(xf, worksheet):
    """Write worksheet data to xml."""

    cells_by_row = get_rows_to_write(worksheet)

    with xf.element("sheetData"):
        for row_idx in sorted(cells_by_row):
            # row meta data
            row_dimension = worksheet.row_dimensions[row_idx]
            attrs = {'r': '%d' % row_idx,
                     'spans': '1:%d' % worksheet.max_column}
            attrs.update(dict(row_dimension))

            with xf.element("row", attrs):

                row_cells = cells_by_row[row_idx]
                for cell in sorted(row_cells, key=row_sort):
                    el = write_cell(worksheet, cell)
                    xf.write(el)


def write_cell(worksheet, cell):
    string_table = worksheet.parent.shared_strings
    coordinate = cell.coordinate
    attributes = {'r': coordinate}
    if cell.has_style:
        attributes['s'] = '%d' % cell.style_id

    if cell.data_type != 'f':
        attributes['t'] = cell.data_type

    value = cell.internal_value

    el = Element("c", attributes)
    if value in ('', None):
        return el

    if cell.data_type == 'f':
        shared_formula = worksheet.formula_attributes.get(coordinate, {})
        if (shared_formula.get('t') == 'shared'
            and 'ref' not in shared_formula):
            value = None
        formula = SubElement(el, 'f', shared_formula)
        if value is not None:
            formula.text = value[1:]
            value = None

    if cell.data_type == 's':
        value = string_table.add(value)
    cell_content = SubElement(el, 'v')
    if value is not None:
        cell_content.text = safe_string(value)
    return el
