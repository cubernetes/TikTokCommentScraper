from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

from openpyxl.utils.units import pixels_to_EMU

from .axis import CategoryAxis, ValueAxis
from .chart import Chart


class GraphChart(Chart):
    """Chart with axes"""

    x_axis = CategoryAxis
    y_axis = ValueAxis

    def __init__(self, auto_axis=False):
        super(GraphChart, self).__init__()
        self.auto_axis = auto_axis
        self.x_axis = getattr(self, "x_axis")(auto_axis)
        self.y_axis = getattr(self, "y_axis")(auto_axis)

    def compute_axes(self):
        """Calculate maximum value and units for axes"""
        mini, maxi = self._get_extremes()
        self.y_axis.min = mini
        self.y_axis.max = maxi
        self.y_axis._max_min()

        if not None in [s.xvalues for s in self]:
            mini, maxi = self._get_extremes('xvalues')
            self.x_axis.min = mini
            self.x_axis.max = maxi
            self.x_axis._max_min()

    def get_x_units(self):
        """ calculate one unit for x axis in EMU """
        return max([len(s.values) for s in self])

    def get_y_units(self):
        """ calculate one unit for y axis in EMU """

        dh = pixels_to_EMU(self.drawing.height)
        return (dh * self.height) / self.y_axis.max

    def _get_extremes(self, attr='values'):
        """Calculate the maximum and minimum values of all series for an axis
        'values' for columns
        'xvalues for rows
        """
        # calculate the maximum and minimum for all series
        series_max = [0]
        series_min = [0]
        for s in self:
            if s is not None:
                series_max.append(s.max(attr))
                series_min.append(s.min(attr))
        return min(series_min), max(series_max)
