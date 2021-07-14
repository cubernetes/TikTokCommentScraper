from __future__ import absolute_import
from __future__ import division
# Copyright (c) 2010-2015 openpyxl


from openpyxl.drawing import Drawing, Shape

from .legend import Legend
from .series import Series


class Chart(object):
    """ raw chart class """

    GROUPING = 'standard'
    TYPE = None

    def mymax(self, values):
        return max([x for x in values if x is not None])

    def mymin(self, values):
        return min([x for x in values if x is not None])

    def __init__(self):

        self.series = []
        self._series = self.series # backwards compatible

        # public api
        self.legend = Legend()
        self.show_legend = True
        self.lang = 'en-GB'
        self.title = ''
        self.print_margins = dict(b=.75, l=.7, r=.7, t=.75, header=0.3, footer=.3)

        # the containing drawing
        self.drawing = Drawing()
        self.drawing.left = 10
        self.drawing.top = 400
        self.drawing.height = 400
        self.drawing.width = 800

        # the offset for the plot part in percentage of the drawing size
        self.width = .6
        self.height = .6
        self._margin_top = 1
        self._margin_top = self.margin_top
        self._margin_left = 0

        # the user defined shapes
        self.shapes = []
        self._shapes = self.shapes # backwards compatible

    def append(self, obj):
        """Add a series or a shape"""
        if isinstance(obj, Series):
            self.series.append(obj)
        elif isinstance(obj, Shape):
            self.shapes.append(obj)

    add_shape = add_serie = add_series = append

    def __iter__(self):
        return iter(self.series)

    def get_y_chars(self):
        """ estimate nb of chars for y axis """
        _max = max([s.max() for s in self])
        return len(str(int(_max)))

    @property
    def margin_top(self):
        """ get margin in percent """

        return min(self._margin_top, self._get_max_margin_top())

    @margin_top.setter
    def margin_top(self, value):
        """ set base top margin"""
        self._margin_top = value

    def _get_max_margin_top(self):

        mb = Shape.FONT_HEIGHT + Shape.MARGIN_BOTTOM
        plot_height = self.drawing.height * self.height
        return (self.drawing.height - plot_height - mb) / self.drawing.height

    @property
    def margin_left(self):

        return max(self._get_min_margin_left(), self._margin_left)

    @margin_left.setter
    def margin_left(self, value):
        self._margin_left = value

    def _get_min_margin_left(self):
        try:
            ychars = self.get_y_chars()
        except TypeError:
            ychars = 0

        ml = (ychars * Shape.FONT_WIDTH) + Shape.MARGIN_LEFT
        return ml / self.drawing.width
