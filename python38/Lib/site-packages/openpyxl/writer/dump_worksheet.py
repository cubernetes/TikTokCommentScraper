from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


"""Write worksheets to xml representations in an optimized way"""

from fileinput import FileInput
from inspect import isgenerator
import os
from tempfile import NamedTemporaryFile
import atexit

from openpyxl.compat import OrderedDict
from openpyxl.cell import get_column_letter, Cell
from openpyxl.worksheet import Worksheet
from openpyxl.worksheet.properties import write_sheetPr

from openpyxl.utils.exceptions import WorkbookAlreadySaved
from openpyxl.writer.excel import ExcelWriter
from openpyxl.writer.comments import CommentWriter
from .relations import write_rels
from .worksheet import (
    write_autofilter,
    write_datavalidation,
    write_cell,
    write_cols,
    write_format,
)
from openpyxl.xml.constants import (
    PACKAGE_WORKSHEETS,
    SHEET_MAIN_NS,
    REL_NS,
    MAX_COLUMN,
    MAX_ROW,
    PACKAGE_XL
)
from openpyxl.xml.functions import (
    xmlfile,
    Element,
    SubElement,
    tostring,
)

DESCRIPTORS_CACHE_SIZE = 50
ALL_TEMP_FILES = []


@atexit.register
def _openpyxl_shutdown():
    global ALL_TEMP_FILES
    for path in ALL_TEMP_FILES:
        if os.path.exists(path):
            os.remove(path)


class CommentParentCell(object):
    __slots__ = ('coordinate', 'row', 'column')

    def __init__(self, cell):
        self.coordinate = cell.coordinate
        self.row = cell.row
        self.column = cell.column


def create_temporary_file(suffix=''):
    fobj = NamedTemporaryFile(mode='w+', suffix=suffix,
                              prefix='openpyxl.', delete=False)
    filename = fobj.name
    ALL_TEMP_FILES.append(filename)
    return filename


def WriteOnlyCell(ws=None, value=None):
    return Cell(worksheet=ws, column='A', row=1, value=value)


class DumpWorksheet(Worksheet):
    """
    Streaming worksheet using lxml
    Optimised to reduce memory by writing rows just in time
    Cells can be styled and have comments
    Styles for rows and columns must be applied before writing cells
    """

    __saved = False
    writer = None

    def __init__(self, parent_workbook, title):
        Worksheet.__init__(self, parent_workbook, title)

        self._max_col = 0
        self._max_row = 0
        self._parent = parent_workbook

        self._fileobj_name = create_temporary_file()

        self._comments = []


    @property
    def filename(self):
        return self._fileobj_name


    def _write_header(self):
        """
        Generator that creates the XML file and the sheet header
        """

        with xmlfile(self.filename) as xf:
            with xf.element("worksheet", xmlns=SHEET_MAIN_NS):

                if self.sheet_properties:
                    pr = write_sheetPr(self.sheet_properties)

                xf.write(pr)
                views = Element('sheetViews')
                views.append(self.sheet_view.to_tree())
                xf.write(views)
                xf.write(write_format(self))

                cols = write_cols(self)
                if cols is not None:
                    xf.write(cols)

                with xf.element("sheetData"):
                    try:
                        while True:
                            r = (yield)
                            xf.write(r)
                    except GeneratorExit:
                        pass
                if self.protection.sheet:
                    prot = Element('sheetProtection', dict(self.protection))
                    xf.write(prot)
                af = write_autofilter(self)
                if af is not None:
                    xf.write(af)
                dv = write_datavalidation(self)
                if dv is not None:
                    xf.write(dv)
                if self._comments:
                    comments = Element('legacyDrawing', {'{%s}id' % REL_NS: 'commentsvml'})
                    xf.write(comments)

    def close(self):
        if self.__saved:
            self._already_saved()
        if self.writer is None:
            self.writer = self._write_header()
            next(self.writer)
        self.writer.close()
        self.__saved = True

    def _cleanup(self):
        os.remove(self.filename)

    def append(self, row):
        """
        :param row: iterable containing values to append
        :type row: iterable
        """
        if (not isgenerator(row) and
            not isinstance(row, (list, tuple, range))
            ):
            self._invalid_row(row)
        cell = WriteOnlyCell(self)  # singleton

        self._max_row += 1
        row_idx = self._max_row
        if self.writer is None:
            self.writer = self._write_header()
            next(self.writer)

        el = Element("row", r='%d' % self._max_row)

        col_idx = None
        for col_idx, value in enumerate(row, 1):
            if value is None:
                continue
            column = get_column_letter(col_idx)

            if isinstance(value, Cell):
                cell = value
            else:
                cell.value = value

            cell.coordinate = '%s%d' % (column, row_idx)
            if cell.comment is not None:
                comment = cell.comment
                comment._parent = CommentParentCell(cell)
                self._comments.append(comment)

            tree = write_cell(self, cell)
            el.append(tree)
            if cell.has_style: # styled cell or datetime
                cell = WriteOnlyCell(self)

        if col_idx:
            self._max_col = max(self._max_col, col_idx)
            el.set('spans', '1:%d' % col_idx)
        try:
            self.writer.send(el)
        except StopIteration:
            self._already_saved()


    def _already_saved(self):
        raise WorkbookAlreadySaved('Workbook has already been saved and cannot be modified or saved anymore.')


    def _invalid_row(self, iterable):
        raise TypeError('Value must be a list, tuple, range or a generator Supplied value is {0}'.format(
            type(iterable))
                        )

def removed_method(*args, **kw):
    raise NotImplementedError

setattr(DumpWorksheet, '__getitem__', removed_method)
setattr(DumpWorksheet, '__setitem__', removed_method)
setattr(DumpWorksheet, 'cell', removed_method)
setattr(DumpWorksheet, 'range', removed_method)
setattr(DumpWorksheet, 'merge_cells', removed_method)


def save_dump(workbook, filename):
    if workbook.worksheets == []:
        workbook.create_sheet()
    writer = ExcelDumpWriter(workbook)
    writer.save(filename)
    return True


class DumpCommentWriter(CommentWriter):
    def extract_comments(self):
        for comment in self.sheet._comments:
            if comment is not None:
                self.authors.add(comment.author)
                self.comments.append(comment)


class ExcelDumpWriter(ExcelWriter):

    def _write_worksheets(self, archive):
        drawing_id = 1
        comments_id = 1

        for i, sheet in enumerate(self.workbook.worksheets, 1):
            sheet.close()
            archive.write(sheet.filename, PACKAGE_WORKSHEETS + '/sheet%d.xml' % i)
            sheet._cleanup()

            # write comments
            if sheet._comments:
                rels = write_rels(sheet, drawing_id, comments_id, False)
                archive.writestr( PACKAGE_WORKSHEETS +
                                  '/_rels/sheet%d.xml.rels' % i, tostring(rels) )

                cw = DumpCommentWriter(sheet)
                archive.writestr(PACKAGE_XL + '/comments%d.xml' % comments_id,
                    cw.write_comments())
                archive.writestr(PACKAGE_XL + '/drawings/commentsDrawing%d.vml' % comments_id,
                    cw.write_comments_vml())
                comments_id += 1
