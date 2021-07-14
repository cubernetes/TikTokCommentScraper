from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


"""Constants for fixed paths in a file and xml namespace urls."""

MIN_ROW = 0
MIN_COLUMN = 0
MAX_COLUMN = 16384
MAX_ROW = 1048576

# constants
PACKAGE_PROPS = 'docProps'
PACKAGE_XL = 'xl'
PACKAGE_RELS = '_rels'
PACKAGE_THEME = PACKAGE_XL + '/' + 'theme'
PACKAGE_WORKSHEETS = PACKAGE_XL + '/' + 'worksheets'
PACKAGE_DRAWINGS = PACKAGE_XL + '/' + 'drawings'
PACKAGE_CHARTS = PACKAGE_XL + '/' + 'charts'
PACKAGE_IMAGES = PACKAGE_XL + '/' + 'media'
PACKAGE_WORKSHEET_RELS = PACKAGE_WORKSHEETS + '/' + '_rels'

ARC_CONTENT_TYPES = '[Content_Types].xml'
ARC_ROOT_RELS = PACKAGE_RELS + '/.rels'
ARC_WORKBOOK_RELS = PACKAGE_XL + '/' + PACKAGE_RELS + '/workbook.xml.rels'
ARC_CORE = PACKAGE_PROPS + '/core.xml'
ARC_APP = PACKAGE_PROPS + '/app.xml'
ARC_WORKBOOK = PACKAGE_XL + '/workbook.xml'
ARC_STYLE = PACKAGE_XL + '/styles.xml'
ARC_THEME = PACKAGE_THEME + '/theme1.xml'
ARC_SHARED_STRINGS = PACKAGE_XL + '/sharedStrings.xml'
ARC_CUSTOM_UI = 'customUI/customUI.xml'

## namespaces
# Dublin Core
DCORE_NS = 'http://purl.org/dc/elements/1.1/'
DCTERMS_NS = 'http://purl.org/dc/terms/'
DCTERMS_PREFIX = 'dcterms'

# Document
DOC_NS = "http://schemas.openxmlformats.org/officeDocument/2006/"
REL_NS = DOC_NS + "relationships"
COMMENTS_NS = REL_NS + "/comments"
VML_NS =  REL_NS + "/vmlDrawing"
VTYPES_NS = DOC_NS + 'docPropsVTypes'
XPROPS_NS = DOC_NS + 'extended-properties'
EXTERNAL_LINK_NS = REL_NS + "/externalLink"

# Package
PKG_NS = "http://schemas.openxmlformats.org/package/2006/"
PKG_REL_NS = PKG_NS + "relationships"
COREPROPS_NS = PKG_NS + 'metadata/core-properties'
CONTYPES_NS = PKG_NS + 'content-types'

XSI_NS = 'http://www.w3.org/2001/XMLSchema-instance'
XML_NS = 'http://www.w3.org/XML/1998/namespace'
SHEET_MAIN_NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'

# Drawing
CHART_NS = "http://schemas.openxmlformats.org/drawingml/2006/chart"
DRAWING_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
SHEET_DRAWING_NS = "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing"
CHART_DRAWING_NS = "http://schemas.openxmlformats.org/drawingml/2006/chartDrawing"

CUSTOMUI_NS = 'http://schemas.microsoft.com/office/2006/relationships/ui/extensibility'


NAMESPACES = {
    'cp': COREPROPS_NS,
    'dc': DCORE_NS,
    DCTERMS_PREFIX: DCTERMS_NS,
    'dcmitype': 'http://purl.org/dc/dcmitype/',
    'xsi': XSI_NS,
    'vt': VTYPES_NS,
    'xml': XML_NS,
    'main': SHEET_MAIN_NS
}

## Mime types
WORKBOOK_MACRO = "application/vnd.ms-excel.%s.macroEnabled.main+xml"
WORKBOOK = "application/vnd.openxmlformats-officedocument.spreadsheetml.%s.main+xml"
SPREADSHEET = "application/vnd.openxmlformats-officedocument.spreadsheetml.%s+xml"
SHARED_STRINGS = SPREADSHEET % "sharedStrings"
EXTERNAL_LINK = SPREADSHEET % "externalLink"
WORKSHEET_TYPE = SPREADSHEET % "worksheet"
COMMENTS_TYPE = SPREADSHEET % "comments"
STYLES_TYPE = SPREADSHEET % "styles"
DRAWING_TYPE = "application/vnd.openxmlformats-officedocument.drawing+xml"
CHART_TYPE = "application/vnd.openxmlformats-officedocument.drawingml.chart+xml"
CHARTSHAPE_TYPE = "application/vnd.openxmlformats-officedocument.drawingml.chartshapes+xml"
THEME_TYPE = "application/vnd.openxmlformats-officedocument.theme+xml"
XLTM = WORKBOOK_MACRO % 'template'
XLSM = WORKBOOK_MACRO % 'sheet'
XLTX = WORKBOOK % 'template'
XLSX = WORKBOOK % 'sheet'
