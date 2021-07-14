from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

"""Write a .xlsx file."""

# Python stdlib imports
from io import BytesIO
from re import match
from zipfile import ZipFile, ZIP_DEFLATED

# package imports
from openpyxl.xml.constants import (
    ARC_SHARED_STRINGS,
    ARC_CONTENT_TYPES,
    ARC_ROOT_RELS,
    ARC_WORKBOOK_RELS,
    ARC_APP, ARC_CORE,
    ARC_THEME,
    ARC_STYLE,
    ARC_WORKBOOK,
    PACKAGE_WORKSHEETS,
    PACKAGE_DRAWINGS,
    PACKAGE_CHARTS,
    PACKAGE_IMAGES,
    PACKAGE_XL
    )
from openpyxl.xml.functions import tostring
from openpyxl.writer.strings import write_string_table
from openpyxl.writer.workbook import (
    write_content_types,
    write_root_rels,
    write_workbook_rels,
    write_properties_app,
    write_workbook
    )
from openpyxl.workbook.properties import write_properties
from openpyxl.writer.theme import write_theme
from openpyxl.writer.styles import StyleWriter
from openpyxl.writer.drawings import DrawingWriter, ShapeWriter
from openpyxl.charts.writer import ChartWriter
from .relations import write_rels
from openpyxl.writer.worksheet import write_worksheet
from openpyxl.workbook.names.external import (
    write_external_link,
    write_external_book_rel
)

from openpyxl.writer.comments import CommentWriter

ARC_VBA = ('xl/vba', r'xl/drawings/.*\.vml', 'xl/ctrlProps', 'customUI',
           'xl/activeX', r'xl/media/.*\.emf')

class ExcelWriter(object):
    """Write a workbook object to an Excel file."""

    def __init__(self, workbook):
        self.workbook = workbook
        self.style_writer = StyleWriter(workbook)

    def write_data(self, archive, as_template=False):
        """Write the various xml files into the zip archive."""
        # cleanup all worksheets

        archive.writestr(ARC_CONTENT_TYPES, write_content_types(self.workbook,
                                                                as_template=as_template))
        archive.writestr(ARC_ROOT_RELS, write_root_rels(self.workbook))
        archive.writestr(ARC_WORKBOOK_RELS, write_workbook_rels(self.workbook))
        archive.writestr(ARC_APP, write_properties_app(self.workbook))
        archive.writestr(ARC_CORE, write_properties(self.workbook.properties))
        if self.workbook.loaded_theme:
            archive.writestr(ARC_THEME, self.workbook.loaded_theme)
        else:
            archive.writestr(ARC_THEME, write_theme())
        archive.writestr(ARC_WORKBOOK, write_workbook(self.workbook))

        if self.workbook.vba_archive:
            vba_archive = self.workbook.vba_archive
            for name in vba_archive.namelist():
                for s in ARC_VBA:
                    if match(s, name):
                        archive.writestr(name, vba_archive.read(name))
                        break

        for sheet in self.workbook.worksheets:
            sheet.conditional_formatting._save_styles(self.workbook)

        self._write_worksheets(archive)
        self._write_string_table(archive)
        self._write_external_links(archive)
        archive.writestr(ARC_STYLE, self.style_writer.write_table())

    def _write_string_table(self, archive):
        archive.writestr(ARC_SHARED_STRINGS,
                write_string_table(self.workbook.shared_strings))

    def _write_images(self, images, archive, image_id):
        for img in images:
            buf = BytesIO()
            img.image.save(buf, format= 'PNG')
            archive.writestr(PACKAGE_IMAGES + '/image%d.png' % image_id, buf.getvalue())
            image_id += 1
        return image_id

    def _write_worksheets(self, archive):
        drawing_id = 1
        chart_id = 1
        image_id = 1
        shape_id = 1
        comments_id = 1
        vba_controls_id = 1

        for i, sheet in enumerate(self.workbook.worksheets):
            archive.writestr(PACKAGE_WORKSHEETS + '/sheet%d.xml' % (i + 1),
                             write_worksheet(sheet, self.workbook.shared_strings,
                                             ))
            if (sheet._charts or sheet._images
                or sheet.relationships
                or sheet._comment_count > 0
                or sheet.vba_controls is not None):
                rels = write_rels(sheet, drawing_id, comments_id, vba_controls_id)
                archive.writestr(
                    PACKAGE_WORKSHEETS + '/_rels/sheet%d.xml.rels' % (i + 1),
                    tostring(rels)
                )
            if sheet._charts or sheet._images:
                dw = DrawingWriter(sheet)
                archive.writestr(PACKAGE_DRAWINGS + '/drawing%d.xml' % drawing_id,
                    dw.write())
                archive.writestr(PACKAGE_DRAWINGS + '/_rels/drawing%d.xml.rels' % drawing_id,
                    dw.write_rels(chart_id, image_id)) # TODO remove this dependency
                drawing_id += 1

                for chart in sheet._charts:
                    cw = ChartWriter(chart)
                    archive.writestr(PACKAGE_CHARTS + '/chart%d.xml' % chart_id,
                        cw.write())

                    if chart._shapes:
                        archive.writestr(PACKAGE_CHARTS + '/_rels/chart%d.xml.rels' % chart_id,
                            cw.write_rels(drawing_id)) # TODO remove this dependency
                        sw = ShapeWriter(chart._shapes)
                        archive.writestr(PACKAGE_DRAWINGS + '/drawing%d.xml' % drawing_id,
                            sw.write(shape_id)) # TODO remove this dependency
                        shape_id += len(chart._shapes)
                        drawing_id += 1

                    chart_id += 1

                image_id = self._write_images(sheet._images, archive, image_id)

            if sheet._comment_count > 0:
                cw = CommentWriter(sheet)
                archive.writestr(PACKAGE_XL + '/comments%d.xml' % comments_id,
                    cw.write_comments())
                archive.writestr(PACKAGE_XL + '/drawings/commentsDrawing%d.vml' % comments_id,
                    cw.write_comments_vml())
                comments_id += 1

            if sheet.vba_controls is not None:
                vba_controls_id += 1

    def _write_external_links(self, archive):
        """Write links to external workbooks"""
        wb = self.workbook
        for idx, book in enumerate(wb._external_links, 1):
            el = write_external_link(book.links)
            rel = write_external_book_rel(book)
            archive.writestr(
                "{0}/externalLinks/externalLink{1}.xml".format(PACKAGE_XL, idx),
                 tostring(el)
            )
            archive.writestr(
                "{0}/externalLinks/_rels/externalLink{1}.xml.rels".format(PACKAGE_XL, idx),
                tostring(rel)
            )


    def save(self, filename, as_template=False):
        """Write data into the archive."""
        archive = ZipFile(filename, 'w', ZIP_DEFLATED, allowZip64=True)
        self.write_data(archive, as_template=as_template)
        archive.close()


def save_workbook(workbook, filename, as_template=False):
    """Save the given workbook on the filesystem under the name filename.

    :param workbook: the workbook to save
    :type workbook: :class:`openpyxl.workbook.Workbook`

    :param filename: the path to which save the workbook
    :type filename: string

    :rtype: bool

    """
    writer = ExcelWriter(workbook)
    writer.save(filename, as_template=as_template)
    return True


def save_virtual_workbook(workbook, as_template=False):
    """Return an in-memory workbook, suitable for a Django response."""
    writer = ExcelWriter(workbook)
    temp_buffer = BytesIO()
    try:
        archive = ZipFile(temp_buffer, 'w', ZIP_DEFLATED, allowZip64=True)
        writer.write_data(archive, as_template=as_template)
    finally:
        archive.close()
    virtual_workbook = temp_buffer.getvalue()
    temp_buffer.close()
    return virtual_workbook
