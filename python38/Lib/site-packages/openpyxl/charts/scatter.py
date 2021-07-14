from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

from .graph import GraphChart


class ScatterChart(GraphChart):

    TYPE = "scatterChart"

    def __init__(self, auto_axis=False):
        super(ScatterChart, self).__init__(auto_axis)
        self.x_axis.type = "valAx"
        self.x_axis.cross_between = "midCat"
        self.y_axis.cross_between = "midCat"
