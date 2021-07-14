from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

"""Worksheet is the 2nd-level container in Excel."""


# Python stdlib imports
from itertools import islice, chain
import re
from inspect import isgenerator

# compatibility imports
from openpyxl.compat import (
    unicode,
    range,
    basestring,
    iteritems,
    deprecated,
    safe_string
)

# package imports
from openpyxl.utils import (
    coordinate_from_string,
    COORD_RE,
    ABSOLUTE_RE,
    column_index_from_string,
    get_column_letter,
    range_boundaries,
    cells_from_range,
)
from openpyxl.cell import Cell
from openpyxl.utils.exceptions import (
    SheetTitleException,
    InsufficientCoordinatesException,
    CellCoordinatesException,
    NamedRangeException
)
from openpyxl.utils.units import (
    points_to_pixels,
    DEFAULT_COLUMN_WIDTH,
    DEFAULT_ROW_HEIGHT
)
from openpyxl.styles import DEFAULTS as DEFAULTS_STYLE
from openpyxl.formatting import ConditionalFormatting
from openpyxl.workbook.names.named_range import NamedRange

from .header_footer import HeaderFooter
from .relationship import Relationship
from .page import PageSetup, PageMargins, PrintOptions
from .dimensions import ColumnDimension, RowDimension, DimensionHolder
from .protection import SheetProtection
from .filters import AutoFilter
from .views import SheetView, Pane, Selection
from .properties import WorksheetProperties, Outline, PageSetupProperties


def flatten(results):
    """Return cell values row-by-row"""

    for row in results:
        yield(c.value for c in row)


class Worksheet(object):
    """Represents a worksheet.

    Do not create worksheets yourself,
    use :func:`openpyxl.workbook.Workbook.create_sheet` instead

    """
    repr_format = unicode('<Worksheet "%s">')
    bad_title_char_re = re.compile(r'[\\*?:/\[\]]')

    BREAK_NONE = 0
    BREAK_ROW = 1
    BREAK_COLUMN = 2

    SHEETSTATE_VISIBLE = 'visible'
    SHEETSTATE_HIDDEN = 'hidden'
    SHEETSTATE_VERYHIDDEN = 'veryHidden'

    # Paper size
    PAPERSIZE_LETTER = '1'
    PAPERSIZE_LETTER_SMALL = '2'
    PAPERSIZE_TABLOID = '3'
    PAPERSIZE_LEDGER = '4'
    PAPERSIZE_LEGAL = '5'
    PAPERSIZE_STATEMENT = '6'
    PAPERSIZE_EXECUTIVE = '7'
    PAPERSIZE_A3 = '8'
    PAPERSIZE_A4 = '9'
    PAPERSIZE_A4_SMALL = '10'
    PAPERSIZE_A5 = '11'

    # Page orientation
    ORIENTATION_PORTRAIT = 'portrait'
    ORIENTATION_LANDSCAPE = 'landscape'

    def __init__(self, parent_workbook, title='Sheet'):
        self._parent = parent_workbook
        self._title = ''
        if not title:
            self.title = 'Sheet%d' % (1 + len(self._parent.worksheets))
        else:
            self.title = title
        self.row_dimensions = {}
        self.column_dimensions = DimensionHolder(worksheet=self,
                                                 direction=[])
        self.page_breaks = []
        self._cells = {}
        self._styles = {}
        self._charts = []
        self._images = []
        self._comment_count = 0
        self._merged_cells = []
        self.relationships = []
        self._data_validations = []
        self.sheet_state = self.SHEETSTATE_VISIBLE
        self.page_setup = PageSetup(self)
        self.print_options = PrintOptions()
        self.page_margins = PageMargins()
        self.header_footer = HeaderFooter()
        self.sheet_view = SheetView()
        self.protection = SheetProtection()
        self.default_row_dimension = RowDimension(worksheet=self)
        self.default_column_dimension = ColumnDimension(worksheet=self)
        self._auto_filter = AutoFilter()
        self._freeze_panes = None
        self.paper_size = None
        self.formula_attributes = {}
        self.orientation = None
        self.conditional_formatting = ConditionalFormatting()
        self.vba_controls = None
        self.sheet_properties = WorksheetProperties()
        self.sheet_properties.outlinePr = Outline(summaryBelow=True, summaryRight=True)


    @property
    def selected_cell(self):
        return self.sheet_view.selection.sqref

    @property
    def active_cell(self):
        return self.sheet_view.selection.activeCell

    @property
    def show_gridlines(self):
        return self.sheet_view.showGridLines

    def __repr__(self):
        return self.repr_format % self.title

    """ To keep compatibility with previous versions"""
    @property
    def show_summary_below(self):
        return self.sheet_properties.outlinePr.summaryBelow

    @property
    def show_summary_right(self):
        return self.sheet_properties.outlinePr.summaryRight

    @property
    def vba_code(self):
        for attr in ("codeName", "enableFormatConditionsCalculation",
                     "filterMode", "published", "syncHorizontal", "syncRef",
                     "syncVertical", "transitionEvaluation", "transitionEntry"):
            value = getattr(self.sheet_properties, attr)
            if value is not None:
                yield attr, safe_string(value)

    @vba_code.setter
    def vba_code(self, value):
        for k, v in value.items():
            if k in ("codeName", "enableFormatConditionsCalculation",
                     "filterMode", "published", "syncHorizontal", "syncRef",
                     "syncVertical", "transitionEvaluation", "transitionEntry"):
                setattr(self.sheet_properties, k, v)

    """ End To keep compatibility with previous versions"""

    @property
    def parent(self):
        return self._parent

    @property
    def encoding(self):
        return self._parent.encoding

    @deprecated('this method is private and should not be called directly')
    def garbage_collect(self):
        self._garbage_collect()

    def _garbage_collect(self):
        """Delete cells that are not storing a value."""
        delete_list = []
        for coordinate, cell in iteritems(self._cells):
            if (cell.value in ('', None)
            and cell.comment is None
            and (coordinate not in self._styles or cell.style == DEFAULTS_STYLE)):
                delete_list.append(coordinate)
        for coordinate in delete_list:
            del self._cells[coordinate]

    def get_cell_collection(self):
        """Return an unordered list of the cells in this worksheet."""
        return self._cells.values()

    @property
    def title(self):
        """Return the title for this sheet."""
        return self._title

    @title.setter
    def title(self, value):
        """Set a sheet title, ensuring it is valid.
           Limited to 31 characters, no special characters."""
        if self.bad_title_char_re.search(value):
            msg = 'Invalid character found in sheet title'
            raise SheetTitleException(msg)
        value = self._unique_sheet_name(value)
        if len(value) > 31:
            msg = 'Maximum 31 characters allowed in sheet title'
            raise SheetTitleException(msg)
        self._title = value

    @deprecated('this method is private and should not be called directly')
    def unique_sheet_name(self, value):
        return self._unique_sheet_name(value)

    def _unique_sheet_name(self, value):
        # check if sheet_name already exists
        # do this *before* length check
        sheets = self._parent.get_sheet_names()
        if value in sheets:
            sheets = ",".join(sheets)
            sheet_title_regex = re.compile("(?P<title>%s)(?P<count>\d?),?" % re.escape(value))
            matches = sheet_title_regex.findall(sheets)
            if matches:
                # use name, but append with the next highest integer
                counts = [int(idx) for (t, idx) in matches if idx.isdigit()]
                if counts:
                    highest = max(counts)
                else:
                    highest = 0
                value = "%s%d" % (value, highest + 1)
        return value

    @property
    def auto_filter(self):
        """Return :class:`~openpyxl.worksheet.AutoFilter` object.

        `auto_filter` attribute stores/returns string until 1.8. You should change your code like ``ws.auto_filter.ref = "A1:A3"``.

        .. versionchanged:: 1.9
        """
        return self._auto_filter

    @property
    def freeze_panes(self):
        if self.sheet_view.pane is not None:
            return self.sheet_view.pane.topLeftCell

    @freeze_panes.setter
    def freeze_panes(self, topLeftCell):
        if not topLeftCell:
            topLeftCell = None
        elif isinstance(topLeftCell, str):
            topLeftCell = topLeftCell.upper()
        else:  # Assume a cell
            topLeftCell = topLeftCell.coordinate
        if topLeftCell == 'A1':
            topLeftCell = None

        if not topLeftCell:
            self.sheet_view.pane = None
            return

        if topLeftCell is not None:
            colName, row = coordinate_from_string(topLeftCell)
            column = column_index_from_string(colName)

        view = self.sheet_view
        view.pane = Pane(topLeftCell=topLeftCell,
                        activePane="topRight",
                        state="frozen")
        view.selection[0].pane = "topRight"

        if column > 1:
            view.pane.xSplit = column - 1
        if row > 1:
            view.pane.ySplit = row - 1
            view.pane.activePane = 'bottomLeft'
            view.selection[0].pane = "bottomLeft"
            if column > 1:
                view.selection[0].pane = "bottomRight"
                view.pane.activePane = 'bottomRight'

        if row > 1 and column > 1:
            sel = list(view.selection)
            sel.insert(0, Selection(pane="topRight", activeCell=None, sqref=None))
            sel.insert(1, Selection(pane="bottomLeft", activeCell=None, sqref=None))
            view.selection = sel

    def add_print_title(self, n, rows_or_cols='rows'):
        """ Print Titles are rows or columns that are repeated on each printed sheet.
        This adds n rows or columns at the top or left of the sheet
        """

        scope = self.parent.get_index(self)

        if rows_or_cols == 'cols':
            r = '$A:$%s' % get_column_letter(n)
        else:
            r = '$1:$%d' % n

        self.parent.create_named_range('_xlnm.Print_Titles', self, r, scope)

    def cell(self, coordinate=None, row=None, column=None, value=None):
        """Returns a cell object based on the given coordinates.

        Usage: cell(coodinate='A15') **or** cell(row=15, column=1)

        If `coordinates` are not given, then row *and* column must be given.

        Cells are kept in a dictionary which is empty at the worksheet
        creation.  Calling `cell` creates the cell in memory when they
        are first accessed, to reduce memory usage.

        :param coordinate: coordinates of the cell (e.g. 'B12')
        :type coordinate: string

        :param row: row index of the cell (e.g. 4)
        :type row: int

        :param column: column index of the cell (e.g. 3)
        :type column: int

        :raise: InsufficientCoordinatesException when coordinate or (row and column) are not given

        :rtype: :class:openpyxl.cell.Cell

        """
        if coordinate is None:
            if (row is None or column is None):
                msg = "You have to provide a value either for " \
                    "'coordinate' or for 'row' *and* 'column'"
                raise InsufficientCoordinatesException(msg)
            else:
                column = get_column_letter(column)
                coordinate = '%s%s' % (column, row)
        else:
            coordinate = coordinate.upper().replace('$', '')

        cell = self._get_cell(coordinate)
        if value is not None:
            cell.value = value
        return cell


    def _get_cell(self, coordinate):
        """
        Internal method for getting a cell from a worksheet.
        Will create a new cell if one doesn't already exist.
        """
        coordinate = coordinate.upper()
        if not coordinate in self._cells:
            column, row = coordinate_from_string(coordinate)
            self._new_cell(column, row)
        return self._cells[coordinate]


    def _new_cell(self, column, row, value=None):
        cell = Cell(self, column, row, value)
        self._add_cell(cell)


    def _add_cell(self, cell):
        """
        Internal method for adding cell objects.
        """
        column = cell.column
        row = cell.row
        self._cells[cell.coordinate] = cell
        if column not in self.column_dimensions:
            self.column_dimensions[column] = ColumnDimension(index=column, worksheet=self)
        if row not in self.row_dimensions:
            self.row_dimensions[row] = RowDimension(index=row, worksheet=self)
        self._cells[cell.coordinate] = cell


    def __getitem__(self, key):
        """Convenience access by Excel style address"""
        if isinstance(key, slice):
            return self.iter_rows("{0}:{1}".format(key.start, key.stop))
        if ":" in key:
            return self.iter_rows(key)
        return self._get_cell(key)

    def __setitem__(self, key, value):
        self[key].value = value

    def get_highest_row(self):
        """Returns the maximum row index containing data

        :rtype: int
        """
        if self.row_dimensions:
            return max(self.row_dimensions)
        else:
            return 0

    @property
    def min_row(self):
        if self.row_dimensions:
            return min(self.row_dimensions)
        else:
            return 1

    @property
    def max_row(self):
        return self.get_highest_row()

    def get_highest_column(self):
        """Get the largest value for column currently stored.

        :rtype: int
        """
        if self.column_dimensions:
            return max([column_index_from_string(column_index)
                        for column_index in self.column_dimensions])
        else:
            return 1

    @property
    def min_col(self):
        if self.column_dimensions:
            return max([column_index_from_string(column_index)
                        for column_index in self.column_dimensions])
        else:
            return 1

    @property
    def max_column(self):
        return self.get_highest_column()

    def calculate_dimension(self):
        """Return the minimum bounding range for all cells containing data."""
        return '%s%d:%s%d' % (
            get_column_letter(1),
            self.min_row,
            get_column_letter(self.max_column or 1),
            self.max_row or 1)


    @property
    def dimensions(self):
        return self.calculate_dimension()


    def iter_rows(self, range_string=None, row_offset=0, column_offset=0):
        """
        Returns a squared range based on the `range_string` parameter,
        using generators.
        If no range is passed, will iterate over all cells in the worksheet

        :param range_string: range of cells (e.g. 'A1:C4')
        :type range_string: string

        :param row_offset: additional rows (e.g. 4)
        :type row: int

        :param column_offset: additonal columns (e.g. 3)
        :type column: int

        :rtype: generator
        """
        if range_string is not None:
            min_col, min_row, max_col, max_row = range_boundaries(range_string.upper())
        else:
            min_col, min_row, max_col, max_row = (1, 1, self.max_column, self.max_row)
        if max_col is not None:
            max_col += column_offset
        if max_row is not None:
            max_row += row_offset
        return self.get_squared_range(min_col + column_offset,
                                      min_row + row_offset,
                                      max_col,
                                      max_row)


    def get_squared_range(self, min_col, min_row, max_col, max_row):
        """Returns a 2D array of cells

        :param min_col: smallest column index (1-based index)
        :type min_col: int

        :param min_row: smallest row index (1-based index)
        :type min_row: int

        :param max_col: largest column index (1-based index)
        :type max_col: int

        :param max_row: smallest row index (1-based index)
        :type max_row: int

        :rtype: generator
        """
        # Column name cache is very important in large files.
        cache = dict((col, get_column_letter(col)) for col in range(min_col, max_col + 1))
        for row in range(min_row, max_row + 1):
            yield tuple(self._get_cell('%s%d' % (cache[col], row))
                        for col in range(min_col, max_col + 1))


    def get_named_range(self, range_string):
        """
        Returns a 2D array of cells, with optional row and column offsets.

        :param range_string: `named range` name
        :type range_string: string

        :rtype: tuples of tuples of :class:`openpyxl.cell.Cell`
        """
        named_range = self._parent.get_named_range(range_string)
        if named_range is None:
            msg = '%s is not a valid range name' % range_string
            raise NamedRangeException(msg)
        if not isinstance(named_range, NamedRange):
            msg = '%s refers to a value, not a range' % range_string
            raise NamedRangeException(msg)

        result = []
        for destination in named_range.destinations:
            worksheet, cells_range = destination

            if worksheet is not self:
                msg = 'Range %s is not defined on worksheet %s' % \
                    (cells_range, self.title)
                raise NamedRangeException(msg)

            for row in self.iter_rows(cells_range):
                result.extend(row)

        return tuple(result)


    @deprecated("""
    Use .iter_rows() working with coordinates 'A1:D4',
    and .get_squared_range() when working with indices (1, 1, 4, 4)
    and .get_named_range() for named ranges""")
    def range(self, range_string, row=0, column=0):
        """Returns a 2D array of cells, with optional row and column offsets.

        :param range_string: cell range string or `named range` name
        :type range_string: string

        :param row: number of rows to offset
        :type row: int

        :param column: number of columns to offset
        :type column: int

        :rtype: tuples of tuples of :class:`openpyxl.cell.Cell`

        """
        _rs = range_string.upper()
        m = ABSOLUTE_RE.match(_rs)
         # R1C1 range
        if m is not None:
            rows = self.iter_rows(_rs, row_offset=row, column_offset=column)
            return tuple(row for row in rows)
        else:
            return self.get_named_range(range_string)


    @deprecated("Access styles directly from cells, columns or rows")
    def get_style(self, coordinate):
        """Return a copy of the style object for the specified cell."""
        try:
            obj = self[coordinate]
        except ValueError:
            if isinstance(coordinate, int):
                obj = self.row_dimensions[obj]
            else:
                obj = self.column_dimensions[obj]
        return obj.style

    @deprecated("Set styles directly on cells, columns or rows")
    def set_style(self, coordinate, style):
        try:
            obj = self[coordinate]
        except ValueError:
            if isinstance(coordinate, int):
                obj = self.row_dimensions[obj]
            else:
                obj = self.column_dimensions[obj]
        obj.style = style

    def set_printer_settings(self, paper_size, orientation):
        """Set printer settings """

        self.page_setup.paperSize = paper_size
        if orientation not in (self.ORIENTATION_PORTRAIT, self.ORIENTATION_LANDSCAPE):
            raise ValueError("Values should be %s or %s" % (self.ORIENTATION_PORTRAIT, self.ORIENTATION_LANDSCAPE))
        self.page_setup.orientation = orientation

    @deprecated('this method is private and should not be called directly')
    def create_relationship(self, rel_type):
        return self._create_relationship(rel_type)

    def _create_relationship(self, rel_type):
        """Add a relationship for this sheet."""
        rel = Relationship(rel_type)
        self.relationships.append(rel)
        rel_id = self.relationships.index(rel)
        rel.id = 'rId' + str(rel_id + 1)
        return self.relationships[rel_id]

    def add_data_validation(self, data_validation):
        """ Add a data-validation object to the sheet.  The data-validation
            object defines the type of data-validation to be applied and the
            cell or range of cells it should apply to.
        """
        data_validation._sheet = self
        self._data_validations.append(data_validation)

    def add_chart(self, chart):
        """ Add a chart to the sheet """
        chart._sheet = self
        self._charts.append(chart)
        self.add_drawing(chart)

    def add_image(self, img):
        """ Add an image to the sheet """
        img._sheet = self
        self._images.append(img)
        self.add_drawing(img)

    def add_drawing(self, obj):
        """Images and charts both create drawings"""
        self._parent.drawings.append(obj)

    def add_rel(self, obj):
        """Drawings and hyperlinks create relationships"""
        self._parent.relationships.append(obj)

    def merge_cells(self, range_string=None, start_row=None, start_column=None, end_row=None, end_column=None):
        """ Set merge on a cell range.  Range is a cell range (e.g. A1:E1) """
        if not range_string:
            if (start_row is None
                or start_column is None
                or end_row is None
                or end_column is None):
                msg = "You have to provide a value either for "\
                    "'coordinate' or for 'start_row', 'start_column', 'end_row' *and* 'end_column'"
                raise InsufficientCoordinatesException(msg)
            else:
                range_string = '%s%s:%s%s' % (get_column_letter(start_column),
                                              start_row,
                                              get_column_letter(end_column),
                                              end_row)
        elif ":" not in range_string:
            if COORD_RE.match(range_string):
                return  # Single cell
            msg = "Range must be a cell range (e.g. A1:E1)"
            raise InsufficientCoordinatesException(msg)
        else:
            range_string = range_string.replace('$', '')

        if range_string not in self._merged_cells:
            self._merged_cells.append(range_string)

        cells = cells_from_range(range_string)
        # only the top-left cell is preserved
        for c in islice(chain.from_iterable(cells), 1, None):
            if c in self._cells:
                del self._cells[c]


    @property
    def merged_cells(self):
        """Utility for checking whether a cell has been merged or not"""
        cells = set()
        for _range in self._merged_cells:
            for row in cells_from_range(_range):
                cells = cells.union(set(row))
        return cells


    @property
    def merged_cell_ranges(self):
        """Public attribute for which cells have been merged"""
        return self._merged_cells


    def unmerge_cells(self, range_string=None, start_row=None, start_column=None, end_row=None, end_column=None):
        """ Remove merge on a cell range.  Range is a cell range (e.g. A1:E1) """
        if not range_string:
            if start_row is None or start_column is None or end_row is None or end_column is None:
                msg = "You have to provide a value either for "\
                    "'coordinate' or for 'start_row', 'start_column', 'end_row' *and* 'end_column'"
                raise InsufficientCoordinatesException(msg)
            else:
                range_string = '%s%s:%s%s' % (get_column_letter(start_column), start_row, get_column_letter(end_column), end_row)
        elif len(range_string.split(':')) != 2:
            msg = "Range must be a cell range (e.g. A1:E1)"
            raise InsufficientCoordinatesException(msg)
        else:
            range_string = range_string.replace('$', '')

        if range_string in self._merged_cells:
            self._merged_cells.remove(range_string)

        else:
            msg = 'Cell range %s not known as merged.' % range_string
            raise InsufficientCoordinatesException(msg)

    def append(self, iterable):
        """Appends a group of values at the bottom of the current sheet.

        * If it's a list: all values are added in order, starting from the first column
        * If it's a dict: values are assigned to the columns indicated by the keys (numbers or letters)

        :param iterable: list, range or generator, or dict containing values to append
        :type iterable: list/tuple/range/generator or dict

        Usage:

        * append(['This is A1', 'This is B1', 'This is C1'])
        * **or** append({'A' : 'This is A1', 'C' : 'This is C1'})
        * **or** append({1 : 'This is A1', 3 : 'This is C1'})

        :raise: TypeError when iterable is neither a list/tuple nor a dict

        """
        row_idx = self.max_row + 1

        if (isinstance(iterable, (list, tuple, range))
            or isgenerator(iterable)):
            for col_idx, content in enumerate(iterable, 1):
                col = get_column_letter(col_idx)
                if isinstance(content, Cell):
                    # compatible with write-only mode
                    cell = content
                    cell.parent = self
                    cell.column = col
                    cell.row = row_idx
                    cell.coordinate = "%s%s" % (col, row_idx)
                    self._add_cell(cell)
                else:
                    cell = self._new_cell(col, row_idx, content)

        elif isinstance(iterable, dict):
            for col_idx, content in iteritems(iterable):
                if isinstance(col_idx, basestring):
                    col_idx = column_index_from_string(col_idx)
                self.cell(row=row_idx, column=col_idx, value=content)

        else:
            self._invalid_row(iterable)
        self.row_dimensions[row_idx] = RowDimension(worksheet=self, index=row_idx)

    def _invalid_row(self, iterable):
        raise TypeError('Value must be a list, tuple, range or generator, or a dict. Supplied value is {0}'.format(
            type(iterable))
                        )

    @property
    def rows(self):
        """Iterate over all rows in the worksheet"""
        return tuple(self.iter_rows())

    @property
    def columns(self):
        """Iterate over all columns in the worksheet"""
        max_row = self.max_row
        min_row = 1
        cols = []
        for col_idx in range(self.max_column):
            cells = self.get_squared_range(col_idx + 1, min_row, col_idx + 1, max_row)
            col = chain.from_iterable(cells)
            cols.append(tuple(col))
        return tuple(cols)

    def point_pos(self, left=0, top=0):
        """ tells which cell is under the given coordinates (in pixels)
        counting from the top-left corner of the sheet.
        Can be used to locate images and charts on the worksheet """
        current_col = 1
        current_row = 1
        column_dimensions = self.column_dimensions
        row_dimensions = self.row_dimensions
        default_width = points_to_pixels(DEFAULT_COLUMN_WIDTH)
        default_height = points_to_pixels(DEFAULT_ROW_HEIGHT)
        left_pos = 0
        top_pos = 0

        while left_pos <= left:
            letter = get_column_letter(current_col)
            current_col += 1
            if letter in column_dimensions:
                cdw = column_dimensions[letter].width
                if cdw is not None:
                    left_pos += points_to_pixels(cdw)
                    continue
            left_pos += default_width

        while top_pos <= top:
            row = current_row
            current_row += 1
            if row in row_dimensions:
                rdh = row_dimensions[row].height
                if rdh is not None:
                    top_pos += points_to_pixels(rdh)
                    continue
            top_pos += default_height

        return (letter, row)
