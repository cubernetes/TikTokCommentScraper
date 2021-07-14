from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

import math
from openpyxl.styles.colors import Color, BLACK, WHITE
from openpyxl.utils.units import pixels_to_EMU, EMU_to_pixels, short_color
from openpyxl.cell import column_index_from_string

class Shadow(object):

    SHADOW_BOTTOM = 'b'
    SHADOW_BOTTOM_LEFT = 'bl'
    SHADOW_BOTTOM_RIGHT = 'br'
    SHADOW_CENTER = 'ctr'
    SHADOW_LEFT = 'l'
    SHADOW_TOP = 't'
    SHADOW_TOP_LEFT = 'tl'
    SHADOW_TOP_RIGHT = 'tr'

    def __init__(self):
        self.visible = False
        self.blurRadius = 6
        self.distance = 2
        self.direction = 0
        self.alignment = self.SHADOW_BOTTOM_RIGHT
        self.color = Color()
        self.alpha = 50


class Drawing(object):
    """ a drawing object - eg container for shapes or charts
        we assume user specifies dimensions in pixels; units are
        converted to EMU in the drawing part
    """

    count = 0

    def __init__(self):

        self.name = ''
        self.description = ''
        self.coordinates = ((1, 2), (16, 8))
        self.left = 0
        self.top = 0
        self._width = EMU_to_pixels(200000)
        self._height = EMU_to_pixels(1828800)
        self.resize_proportional = False
        self.rotation = 0
#        self.shadow = Shadow()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, w):
        if self.resize_proportional and w:
            ratio = self._height / self._width
            self._height = round(ratio * w)
        self._width = w

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, h):
        if self.resize_proportional and h:
            ratio = self._width / self._height
            self._width = round(ratio * h)
        self._height = h

    def set_dimension(self, w=0, h=0):

        xratio = w / self._width
        yratio = h / self._height

        if self.resize_proportional and w and h:
            if (xratio * self._height) < h:
                self._height = math.ceil(xratio * self._height)
                self._width = w
            else:
                self._width = math.ceil(yratio * self._width)
                self._height = h

    def get_emu_dimensions(self):
        """ return (x, y, w, h) in EMU """

        return (pixels_to_EMU(self.left), pixels_to_EMU(self.top),
            pixels_to_EMU(self._width), pixels_to_EMU(self._height))


class Shape(object):
    """ a drawing inside a chart
        coordiantes are specified by the user in the axis units
    """

    MARGIN_LEFT = 6 + 13 + 1
    MARGIN_BOTTOM = 17 + 11

    FONT_WIDTH = 7
    FONT_HEIGHT = 8

    ROUND_RECT = 'roundRect'
    RECT = 'rect'

    # other shapes to define :
    '''
    "line"
    "lineInv"
    "triangle"
    "rtTriangle"
    "diamond"
    "parallelogram"
    "trapezoid"
    "nonIsoscelesTrapezoid"
    "pentagon"
    "hexagon"
    "heptagon"
    "octagon"
    "decagon"
    "dodecagon"
    "star4"
    "star5"
    "star6"
    "star7"
    "star8"
    "star10"
    "star12"
    "star16"
    "star24"
    "star32"
    "roundRect"
    "round1Rect"
    "round2SameRect"
    "round2DiagRect"
    "snipRoundRect"
    "snip1Rect"
    "snip2SameRect"
    "snip2DiagRect"
    "plaque"
    "ellipse"
    "teardrop"
    "homePlate"
    "chevron"
    "pieWedge"
    "pie"
    "blockArc"
    "donut"
    "noSmoking"
    "rightArrow"
    "leftArrow"
    "upArrow"
    "downArrow"
    "stripedRightArrow"
    "notchedRightArrow"
    "bentUpArrow"
    "leftRightArrow"
    "upDownArrow"
    "leftUpArrow"
    "leftRightUpArrow"
    "quadArrow"
    "leftArrowCallout"
    "rightArrowCallout"
    "upArrowCallout"
    "downArrowCallout"
    "leftRightArrowCallout"
    "upDownArrowCallout"
    "quadArrowCallout"
    "bentArrow"
    "uturnArrow"
    "circularArrow"
    "leftCircularArrow"
    "leftRightCircularArrow"
    "curvedRightArrow"
    "curvedLeftArrow"
    "curvedUpArrow"
    "curvedDownArrow"
    "swooshArrow"
    "cube"
    "can"
    "lightningBolt"
    "heart"
    "sun"
    "moon"
    "smileyFace"
    "irregularSeal1"
    "irregularSeal2"
    "foldedCorner"
    "bevel"
    "frame"
    "halfFrame"
    "corner"
    "diagStripe"
    "chord"
    "arc"
    "leftBracket"
    "rightBracket"
    "leftBrace"
    "rightBrace"
    "bracketPair"
    "bracePair"
    "straightConnector1"
    "bentConnector2"
    "bentConnector3"
    "bentConnector4"
    "bentConnector5"
    "curvedConnector2"
    "curvedConnector3"
    "curvedConnector4"
    "curvedConnector5"
    "callout1"
    "callout2"
    "callout3"
    "accentCallout1"
    "accentCallout2"
    "accentCallout3"
    "borderCallout1"
    "borderCallout2"
    "borderCallout3"
    "accentBorderCallout1"
    "accentBorderCallout2"
    "accentBorderCallout3"
    "wedgeRectCallout"
    "wedgeRoundRectCallout"
    "wedgeEllipseCallout"
    "cloudCallout"
    "cloud"
    "ribbon"
    "ribbon2"
    "ellipseRibbon"
    "ellipseRibbon2"
    "leftRightRibbon"
    "verticalScroll"
    "horizontalScroll"
    "wave"
    "doubleWave"
    "plus"
    "flowChartProcess"
    "flowChartDecision"
    "flowChartInputOutput"
    "flowChartPredefinedProcess"
    "flowChartInternalStorage"
    "flowChartDocument"
    "flowChartMultidocument"
    "flowChartTerminator"
    "flowChartPreparation"
    "flowChartManualInput"
    "flowChartManualOperation"
    "flowChartConnector"
    "flowChartPunchedCard"
    "flowChartPunchedTape"
    "flowChartSummingJunction"
    "flowChartOr"
    "flowChartCollate"
    "flowChartSort"
    "flowChartExtract"
    "flowChartMerge"
    "flowChartOfflineStorage"
    "flowChartOnlineStorage"
    "flowChartMagneticTape"
    "flowChartMagneticDisk"
    "flowChartMagneticDrum"
    "flowChartDisplay"
    "flowChartDelay"
    "flowChartAlternateProcess"
    "flowChartOffpageConnector"
    "actionButtonBlank"
    "actionButtonHome"
    "actionButtonHelp"
    "actionButtonInformation"
    "actionButtonForwardNext"
    "actionButtonBackPrevious"
    "actionButtonEnd"
    "actionButtonBeginning"
    "actionButtonReturn"
    "actionButtonDocument"
    "actionButtonSound"
    "actionButtonMovie"
    "gear6"
    "gear9"
    "funnel"
    "mathPlus"
    "mathMinus"
    "mathMultiply"
    "mathDivide"
    "mathEqual"
    "mathNotEqual"
    "cornerTabs"
    "squareTabs"
    "plaqueTabs"
    "chartX"
    "chartStar"
    "chartPlus"
    '''

    def __init__(self,
                 chart,
                 coordinates=((0, 0), (1, 1)),
                 text=None,
                 scheme="accent1"):
        self.chart = chart
        self.coordinates = coordinates  # in axis units
        self.text = text
        self.scheme = scheme
        self.style = Shape.RECT
        self.border_width = 0
        self.border_color = BLACK  # "F3B3C5"
        self.color = WHITE
        self.text_color = BLACK

    @property
    def border_color(self):
        return self._border_color

    @border_color.setter
    def border_color(self, color):
        self._border_color = short_color(color)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = short_color(color)

    @property
    def text_color(self):
        return self._text_color

    @text_color.setter
    def text_color(self, color):
        self._text_color = short_color(color)

    @property
    def border_width(self):
        return self._border_width

    @border_width.setter
    def border_width(self, w):
        self._border_width = w

    @property
    def coordinates(self):
        """Return coordindates in axis units"""
        return self._coordinates

    @coordinates.setter
    def coordinates(self, coords):
        """ set shape coordinates in percentages (left, top, right, bottom)
        """
        # this needs refactoring to reflect changes in charts
        self.axis_coordinates = coords
        (x1, y1), (x2, y2) = coords # bottom left, top right
        drawing_width = pixels_to_EMU(self.chart.drawing.width)
        drawing_height = pixels_to_EMU(self.chart.drawing.height)
        plot_width = drawing_width * self.chart.width
        plot_height = drawing_height * self.chart.height

        margin_left = self.chart._get_margin_left() * drawing_width
        xunit = plot_width / self.chart.get_x_units()

        margin_top = self.chart._get_margin_top() * drawing_height
        yunit = self.chart.get_y_units()

        x_start = (margin_left + (float(x1) * xunit)) / drawing_width
        y_start = ((margin_top
                    + plot_height
                    - (float(y1) * yunit))
                    / drawing_height)

        x_end = (margin_left + (float(x2) * xunit)) / drawing_width
        y_end = ((margin_top
                  + plot_height
                  - (float(y2) * yunit))
                  / drawing_height)

        # allow user to specify y's in whatever order
        # excel expect y_end to be lower
        if y_end < y_start:
            y_end, y_start = y_start, y_end

        self._coordinates = (
            self._norm_pct(x_start), self._norm_pct(y_start),
            self._norm_pct(x_end), self._norm_pct(y_end)
        )

    @staticmethod
    def _norm_pct(pct):
        """ force shapes to appear by truncating too large sizes """
        if pct > 1:
            return 1
        elif pct < 0:
            return 0
        return pct


def bounding_box(bw, bh, w, h):
    """
    Returns a tuple (new_width, new_height) which has the property
    that it fits within box_width and box_height and has (close to)
    the same aspect ratio as the original size
    """
    new_width, new_height = w, h
    if bw and new_width > bw:
        new_width = bw
        new_height = new_width / (float(w) / h)
    if bh and new_height > bh:
        new_height = bh
        new_width = new_height * (float(w) / h)
    return (new_width, new_height)


class Image(object):
    """ Raw Image class """

    @staticmethod
    def _import_image(img):
        try:
            try:
                import Image as PILImage
            except ImportError:
                from PIL import Image as PILImage
        except ImportError:
            raise ImportError('You must install PIL to fetch image objects')

        if not isinstance(img, PILImage.Image):
            img = PILImage.open(img)

        return img

    def __init__(self, img, coordinates=((0, 0), (1, 1)), size=(None, None),
                 nochangeaspect=True, nochangearrowheads=True):

        self.image = self._import_image(img)
        self.nochangeaspect = nochangeaspect
        self.nochangearrowheads = nochangearrowheads

        # the containing drawing
        self.drawing = Drawing()
        self.drawing.coordinates = coordinates

        newsize = bounding_box(size[0], size[1],
                               self.image.size[0], self.image.size[1])
        size = newsize
        self.drawing.width = size[0]
        self.drawing.height = size[1]

        self.drawing.anchortype = None

    def anchor(self, cell, anchortype="absolute"):
        """ anchors the image to the given cell
            optional parameter anchortype supports 'absolute' or 'oneCell'"""
        self.drawing.anchortype = anchortype
        if anchortype == "absolute":
            self.drawing.left, self.drawing.top = cell.anchor
            return ((cell.column, cell.row),
                    cell.parent.point_pos(self.drawing.top + self.drawing.height,
                                          self.drawing.left + self.drawing.width))
        elif anchortype == "oneCell":
            self.drawing.anchorcol = column_index_from_string(cell.column) - 1
            self.drawing.anchorrow = cell.row - 1
            return ((self.drawing.anchorcol, self.drawing.anchorrow), None)
        else:
            raise ValueError("unknown anchortype %s" % anchortype)

