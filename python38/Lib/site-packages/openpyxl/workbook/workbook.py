from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


"""Workbook is the top-level container for all document information."""

__docformat__ = "restructuredtext en"

# Python stdlib imports
import threading

# package imports
from openpyxl.utils.indexed_list import IndexedList
from openpyxl.utils.datetime  import CALENDAR_WINDOWS_1900
from openpyxl.worksheet import Worksheet
from openpyxl.writer.dump_worksheet import DumpWorksheet, save_dump
from . names.named_range import NamedRange
from openpyxl.styles import Style
from openpyxl.styles.styleable import StyleId
from openpyxl.styles.numbers import BUILTIN_FORMATS
from openpyxl.writer.excel import save_workbook
from openpyxl.utils.exceptions import ReadOnlyWorkbookException
from openpyxl.xml import LXML
from openpyxl.xml.functions import fromstring
from openpyxl.xml.constants import SHEET_MAIN_NS
from openpyxl.compat import deprecated
from . properties import DocumentProperties, DocumentSecurity


class Workbook(object):
    """Workbook is the container for all other parts of the document."""

    _optimized_worksheet_class = DumpWorksheet

    def __init__(self,
                 optimized_write=False,
                 encoding='utf-8',
                 worksheet_class=Worksheet,
                 guess_types=False,
                 data_only=False,
                 read_only=False,
                 write_only=False):
        self.worksheets = []
        self._active_sheet_index = 0
        self._named_ranges = []
        self._external_links = []
        self.properties = DocumentProperties()
        self.style = Style()
        self.security = DocumentSecurity()
        self.__write_only = write_only or optimized_write
        self.__read_only = read_only
        self.__thread_local_data = threading.local()
        self.shared_strings = IndexedList()

        self._setup_styles()
        self.loaded_theme = None
        self._worksheet_class = worksheet_class
        self.vba_archive = None
        self.is_template = False
        self._differential_styles = []
        self._guess_types = guess_types
        self.data_only = data_only
        self.relationships = []
        self.drawings = []
        self.code_name = None
        self.excel_base_date = CALENDAR_WINDOWS_1900
        self.encoding = encoding

        if not self.write_only:
            self.worksheets.append(self._worksheet_class(parent_workbook=self))


    def _setup_styles(self):
        """Bootstrap styles"""
        from openpyxl.styles.alignment import Alignment
        from openpyxl.styles.borders import DEFAULT_BORDER
        from openpyxl.styles.fills import DEFAULT_EMPTY_FILL, DEFAULT_GRAY_FILL
        from openpyxl.styles.fonts import DEFAULT_FONT
        from openpyxl.styles.protection import Protection
        from openpyxl.styles.colors import COLOR_INDEX

        self._fonts = IndexedList()
        self._fonts.add(DEFAULT_FONT)

        self._alignments = IndexedList([Alignment()])

        self._borders = IndexedList()
        self._borders.add(DEFAULT_BORDER)

        self._fills = IndexedList()
        self._fills.add(DEFAULT_EMPTY_FILL)
        self._fills.add(DEFAULT_GRAY_FILL)

        self._number_formats = IndexedList()

        self._protections = IndexedList([Protection()])

        self._colors = COLOR_INDEX
        self._cell_styles = IndexedList([StyleId()])


    @deprecated('this method is private and should not be called directly')
    def read_workbook_settings(self, xml_source):
        self._read_workbook_settings(xml_source)

    def _read_workbook_settings(self, xml_source):
        root = fromstring(xml_source)
        view = root.find('*/' '{%s}workbookView' % SHEET_MAIN_NS)
        if view is not None:
            if 'activeTab' in view.attrib:
                self.active = int(view.attrib['activeTab'])

    @property
    def shared_styles(self):
        """
        Legacy
        On the fly conversion of style references to style objects
        """
        styles = []
        for sid in self._cell_styles:
            font = self._fonts[sid.font]
            fill = self._fills[sid.fill]
            border = self._borders[sid.border]
            alignment = self._alignments[sid.alignment]
            protection = self._protections[sid.protection]
            nf_id = sid.number_format
            if nf_id < 164:
                number_format = BUILTIN_FORMATS.get(nf_id, "General")
            else:
                number_format = self._number_formats[sid.number_format - 164]
            styles.append(Style(font, fill, border, alignment,
                                number_format, protection))
        return styles


    @property
    def _local_data(self):
        return self.__thread_local_data

    @property
    def read_only(self):
        return self.__read_only

    @property
    def write_only(self):
        return self.__write_only

    def get_active_sheet(self):
        """Returns the current active sheet."""
        return self.active

    @property
    def active(self):
        """Get the currently active sheet"""
        return self.worksheets[self._active_sheet_index]

    @active.setter
    def active(self, value):
        """Set the active sheet"""
        self._active_sheet_index = value

    def create_sheet(self, index=None, title=None):
        """Create a worksheet (at an optional index).

        :param index: optional position at which the sheet will be inserted
        :type index: int

        """

        if self.read_only:
            raise ReadOnlyWorkbookException('Cannot create new sheet in a read-only workbook')

        if self.write_only :
            new_ws = self._optimized_worksheet_class(parent_workbook=self,
                                                      title=title)
            self._worksheet_class = self._optimized_worksheet_class
        else:
            if title is not None:
                new_ws = self._worksheet_class(
                    parent_workbook=self, title=title)
            else:
                new_ws = self._worksheet_class(parent_workbook=self)

        self._add_sheet(worksheet=new_ws, index=index)
        return new_ws

    @deprecated("you probably want to use Workbook.create_sheet('sheet name') instead")
    def add_sheet(self, worksheet, index=None):
        self._add_sheet(worksheet, index)

    def _add_sheet(self, worksheet, index=None):
        """Add an existing worksheet (at an optional index)."""
        if not isinstance(worksheet, self._worksheet_class):
            raise TypeError("The parameter you have given is not of the type '%s'" % self._worksheet_class.__name__)
        if worksheet.parent != self:
            raise ValueError("You cannot add worksheets from another workbook.")

        if index is None:
            self.worksheets.append(worksheet)
        else:
            self.worksheets.insert(index, worksheet)

    def remove_sheet(self, worksheet):
        """Remove a worksheet from this workbook."""
        self.worksheets.remove(worksheet)

    def get_sheet_by_name(self, name):
        """Returns a worksheet by its name.

        :param name: the name of the worksheet to look for
        :type name: string

        """
        return self[name]

    def __contains__(self, key):
        return key in set(self.sheetnames)

    def get_index(self, worksheet):
        """Return the index of the worksheet."""
        return self.worksheets.index(worksheet)

    def __getitem__(self, key):
        """Returns a worksheet by its name.

        :param name: the name of the worksheet to look for
        :type name: string

        """
        for sheet in self.worksheets:
            if sheet.title == key:
                return sheet
        raise KeyError("Worksheet {0} does not exist.".format(key))

    def __delitem__(self, key):
        sheet = self[key]
        self.remove_sheet(sheet)

    def __iter__(self):
        return iter(self.worksheets)

    def get_sheet_names(self):
        return self.sheetnames

    @property
    def sheetnames(self):
        """Returns the list of the names of worksheets in the workbook.

        Names are returned in the worksheets order.

        :rtype: list of strings

        """
        return [s.title for s in self.worksheets]

    def create_named_range(self, name, worksheet, range, scope=None):
        """Create a new named_range on a worksheet"""
        if not isinstance(worksheet, self._worksheet_class):
            raise TypeError("Worksheet is not of the right type")
        named_range = NamedRange(name, [(worksheet, range)], scope)
        self.add_named_range(named_range)

    def get_named_ranges(self):
        """Return all named ranges"""
        return self._named_ranges

    def add_named_range(self, named_range):
        """Add an existing named_range to the list of named_ranges."""
        self._named_ranges.append(named_range)

    def get_named_range(self, name):
        """Return the range specified by name."""
        requested_range = None
        for named_range in self._named_ranges:
            if named_range.name == name:
                requested_range = named_range
                break
        return requested_range

    def remove_named_range(self, named_range):
        """Remove a named_range from this workbook."""
        self._named_ranges.remove(named_range)

    def save(self, filename):
        """Save the current workbook under the given `filename`.
        Use this function instead of using an `ExcelWriter`.

        .. warning::
            When creating your workbook using `write_only` set to True,
            you will only be able to call this function once. Subsequents attempts to
            modify or save the file will raise an :class:`openpyxl.shared.exc.WorkbookAlreadySaved` exception.
        """
        if self.read_only:
            raise TypeError("""Workbook is read-only""")
        if self.write_only:
            save_dump(self, filename)
        else:
            save_workbook(self, filename)
