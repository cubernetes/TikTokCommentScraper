from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


from openpyxl.xml.functions import (
    Element,
    SubElement,
    ConditionalElement,
    tostring,
    )
from openpyxl.xml.constants import (
    CHART_NS,
    DRAWING_NS,
    REL_NS,
    PKG_REL_NS
    )
from openpyxl.compat import (
    iteritems,
    safe_string
    )
from .import (
    ErrorBar,
    BarChart,
    LineChart,
    PieChart,
    ScatterChart,
    GraphChart
    )


class BaseChartWriter(object):

    series_type = '{%s}val' % CHART_NS

    def __init__(self, chart):
        self.chart = chart
        self.root = Element("{%s}chartSpace" % CHART_NS)

    def write(self):
        """ write a chart """
        SubElement(self.root, '{%s}lang' % CHART_NS, {'val':self.chart.lang})
        self._write_chart()
        self._write_print_settings()
        self._write_shapes()

        return tostring(self.root)

    def _write_chart(self):
        ch = SubElement(self.root, '{%s}chart' % CHART_NS)
        self._write_title(ch)
        self._write_layout(ch)
        self._write_legend(ch)
        SubElement(ch, '{%s}plotVisOnly' % CHART_NS, {'val':'1'})

    def _write_layout(self, element):
        chart = self.chart
        plot_area = SubElement(element, '{%s}plotArea' % CHART_NS)
        layout = SubElement(plot_area, '{%s}layout' % CHART_NS)
        mlayout = SubElement(layout, '{%s}manualLayout' % CHART_NS)
        SubElement(mlayout, '{%s}layoutTarget' % CHART_NS, {'val':'inner'})
        SubElement(mlayout, '{%s}xMode' % CHART_NS, {'val':'edge'})
        SubElement(mlayout, '{%s}yMode' % CHART_NS, {'val':'edge'})
        SubElement(mlayout, '{%s}x' % CHART_NS, {'val':safe_string(chart.margin_left)})
        SubElement(mlayout, '{%s}y' % CHART_NS, {'val':safe_string(chart.margin_top)})
        SubElement(mlayout, '{%s}w' % CHART_NS, {'val':safe_string(chart.width)})
        SubElement(mlayout, '{%s}h' % CHART_NS, {'val':safe_string(chart.height)})

        chart_type = self.chart.TYPE
        subchart = SubElement(plot_area, '{%s}%s' % (CHART_NS, chart_type))
        self._write_options(subchart)
        self._write_series(subchart)
        if isinstance(chart, GraphChart):
            SubElement(subchart, '{%s}axId' % CHART_NS, {'val':safe_string(chart.x_axis.id)})
            SubElement(subchart, '{%s}axId' % CHART_NS, {'val':safe_string(chart.y_axis.id)})
            self._write_axis(plot_area, chart.x_axis, '{%s}%s' % (CHART_NS, chart.x_axis.type))
            self._write_axis(plot_area, chart.y_axis, '{%s}%s' % (CHART_NS, chart.y_axis.type))

    def _write_options(self, subchart):
        pass

    def _write_title(self, chart):
        if self.chart.title != '':
            title = SubElement(chart, '{%s}title' % CHART_NS)
            tx = SubElement(title, '{%s}tx' % CHART_NS)
            rich = SubElement(tx, '{%s}rich' % CHART_NS)
            SubElement(rich, '{%s}bodyPr' % DRAWING_NS)
            SubElement(rich, '{%s}lstStyle' % DRAWING_NS)
            p = SubElement(rich, '{%s}p' % DRAWING_NS)
            pPr = SubElement(p, '{%s}pPr' % DRAWING_NS)
            SubElement(pPr, '{%s}defRPr' % DRAWING_NS)
            r = SubElement(p, '{%s}r' % DRAWING_NS)
            SubElement(r, '{%s}rPr' % DRAWING_NS, {'lang':self.chart.lang})
            SubElement(r, '{%s}t' % DRAWING_NS).text = self.chart.title
            SubElement(title, '{%s}layout' % CHART_NS)

    def _write_axis_title(self, axis, ax):

        if axis.title != '':
            title = SubElement(ax, '{%s}title' % CHART_NS)
            tx = SubElement(title, '{%s}tx' % CHART_NS)
            rich = SubElement(tx, '{%s}rich' % CHART_NS)
            SubElement(rich, '{%s}bodyPr' % DRAWING_NS)
            SubElement(rich, '{%s}lstStyle' % DRAWING_NS)
            p = SubElement(rich, '{%s}p' % DRAWING_NS)
            pPr = SubElement(p, '{%s}pPr' % DRAWING_NS)
            SubElement(pPr, '{%s}defRPr' % DRAWING_NS)
            r = SubElement(p, '{%s}r' % DRAWING_NS)
            SubElement(r, '{%s}rPr' % DRAWING_NS, {'lang':self.chart.lang})
            SubElement(r, '{%s}t' % DRAWING_NS).text = axis.title
            SubElement(title, '{%s}layout' % CHART_NS)

    def _write_axis(self, plot_area, axis, label):

        if self.chart.auto_axis:
            self.chart.compute_axes()

        ax = SubElement(plot_area, label)
        SubElement(ax, '{%s}axId' % CHART_NS, {'val':safe_string(axis.id)})

        scaling = SubElement(ax, '{%s}scaling' % CHART_NS)
        SubElement(scaling, '{%s}orientation' % CHART_NS, {'val':axis.orientation})
        if axis.delete_axis:
            SubElement(scaling, '{%s}' % CHART_NS, {'val':'1'})
        if axis.type == "valAx" and axis.auto_axis:
            SubElement(scaling, '{%s}max' % CHART_NS, {'val':safe_string(axis.max)})
            SubElement(scaling, '{%s}min' % CHART_NS, {'val':safe_string(axis.min)})

        SubElement(ax, '{%s}axPos' % CHART_NS, {'val':axis.position})
        if axis.type == "valAx":
            SubElement(ax, '{%s}majorGridlines' % CHART_NS)
        SubElement(ax, '{%s}numFmt' % CHART_NS,
                   {'formatCode':axis.number_format,
                    'sourceLinked':safe_string(axis.sourceLinked)
                    }
                   )
        self._write_axis_title(axis, ax)
        SubElement(ax, '{%s}tickLblPos' % CHART_NS, {'val':axis.tick_label_position})
        SubElement(ax, '{%s}crossAx' % CHART_NS, {'val':str(axis.cross)})
        SubElement(ax, '{%s}crosses' % CHART_NS, {'val':axis.crosses})
        if axis.auto:
            SubElement(ax, '{%s}auto' % CHART_NS, {'val':safe_string(axis.auto)})
        if axis.label_align:
            SubElement(ax, '{%s}lblAlgn' % CHART_NS, {'val':axis.label_align})
        if axis.label_offset:
            SubElement(ax, '{%s}lblOffset' % CHART_NS, {'val':str(axis.label_offset)})

        if axis.type == 'valAx':
            SubElement(ax, '{%s}crossBetween' % CHART_NS, val=axis.cross_between)
        if axis.unit:
            SubElement(ax, '{%s}majorUnit' % CHART_NS, val=safe_string(axis.unit))

    def _write_series(self, subchart):

        for i, series in enumerate(self.chart):
            ser = SubElement(subchart, '{%s}ser' % CHART_NS)
            SubElement(ser, '{%s}idx' % CHART_NS, {'val':safe_string(i)})
            SubElement(ser, '{%s}order' % CHART_NS, {'val':safe_string(i)})

            if series.title:
                tx = SubElement(ser, '{%s}tx' % CHART_NS)
                SubElement(tx, '{%s}v' % CHART_NS).text = series.title

            if isinstance(self, LineChart):
                marker = SubElement(ser, "{%s}marker" % CHART_NS)
                SubElement(marker, "{%s}symbol" % CHART_NS, val=safe_string(series.marker))

            if series.color:
                sppr = SubElement(ser, '{%s}spPr' % CHART_NS)
                self._write_series_color(sppr, series)

            if series.error_bar:
                self._write_error_bar(ser, series)

            if series.labels:
                self._write_series_labels(ser, series)

            if series.xvalues:
                self._write_series_xvalues(ser, series)

            val = SubElement(ser, self.series_type)
            self._write_serial(val, series.reference)

    def _write_series_color(self, node, series):
        # edge color
        ln = SubElement(node, '{%s}ln' % DRAWING_NS)
        fill = SubElement(ln, '{%s}solidFill' % DRAWING_NS)
        SubElement(fill, '{%s}srgbClr' % DRAWING_NS, {'val':series.color})

    def _write_series_labels(self, node, series):
        cat = SubElement(node, '{%s}cat' % CHART_NS)
        self._write_serial(cat, series.labels)

    def _write_series_xvalues(self, node, series):
        raise NotImplemented("""x values not possible for this chart type""")

    def _write_serial(self, node, reference, literal=False):
        is_ref = hasattr(reference, 'pos1')
        data_type = reference.data_type
        number_format = getattr(reference, 'number_format')

        mapping = {'n':{'ref':'numRef', 'cache':'numCache'},
                   's':{'ref':'strRef', 'cache':'strCache'},
                   'f':{'ref':'numRef', 'cache':'numCache'},
                   }
        data = None

        if is_ref:
            ref = SubElement(node, '{%s}%s' %(CHART_NS, mapping[data_type]['ref']))
            SubElement(ref, '{%s}f' % CHART_NS).text = str(reference)
        else:
            data = SubElement(node, '{%s}numLit' % CHART_NS)
            values = (1,)

        if data is not None:
            if data_type == 'n':
                SubElement(data, '{%s}formatCode' % CHART_NS).text = number_format or 'General'
            SubElement(data, '{%s}ptCount' % CHART_NS, {'val':str(len(values))})
            for j, val in enumerate(values):
                if val is not None:
                    val = safe_string(val)
                else:
                    val = ''
                point = SubElement(data, '{%s}pt' % CHART_NS, idx='%d' %j)
                SubElement(point, '{%s}v' % CHART_NS).text = val

    def _write_error_bar(self, node, serie):

        flag = {ErrorBar.PLUS_MINUS:'both',
                ErrorBar.PLUS:'plus',
                ErrorBar.MINUS:'minus'}

        eb = SubElement(node, '{%s}errBars' % CHART_NS)
        SubElement(eb, '{%s}errBarType' % CHART_NS, {'val':flag[serie.error_bar.type]})
        SubElement(eb, '{%s}errValType' % CHART_NS, {'val':'cust'})

        plus = SubElement(eb, '{%s}plus' % CHART_NS)
        # apart from setting the type of data series the following has
        # no effect on the writer
        self._write_serial(plus, serie.error_bar.reference,
            literal=(serie.error_bar.type == ErrorBar.MINUS))

        minus = SubElement(eb, '{%s}minus' % CHART_NS)
        self._write_serial(minus, serie.error_bar.reference,
            literal=(serie.error_bar.type == ErrorBar.PLUS))

    def _write_legend(self, chart):

        if self.chart.show_legend:
            legend = SubElement(chart, '{%s}legend' % CHART_NS)
            SubElement(legend, '{%s}legendPos' % CHART_NS, {'val':self.chart.legend.position})
            SubElement(legend, '{%s}layout' % CHART_NS)

    def _write_print_settings(self):

        settings = SubElement(self.root, '{%s}printSettings' % CHART_NS)
        SubElement(settings, '{%s}headerFooter' % CHART_NS)
        margins = dict([(k, safe_string(v)) for (k, v) in iteritems(self.chart.print_margins)])
        SubElement(settings, '{%s}pageMargins' % CHART_NS, margins)
        SubElement(settings, '{%s}pageSetup' % CHART_NS)

    def _write_shapes(self):

        if self.chart.shapes:
            SubElement(self.root, '{%s}userShapes' % CHART_NS, {'{%s}id' % REL_NS:'rId1'})

    def write_rels(self, drawing_id):
        root = Element("{%s}Relationships" % PKG_REL_NS)

        attrs = {'Id' : 'rId1',
            'Type' : '%s/chartUserShapes' % REL_NS,
            'Target' : '../drawings/drawing%s.xml' % drawing_id }
        SubElement(root, '{%s}Relationship' % PKG_REL_NS, attrs)
        return tostring(root)


class PieChartWriter(BaseChartWriter):

    def _write_options(self, subchart):
        SubElement(subchart, '{%s}varyColors' % CHART_NS, {'val':'1'})

    def _write_axis(self, plot_area, axis, label):
        """Pie Charts have no axes, do nothing"""
        pass


class LineChartWriter(BaseChartWriter):

    def _write_options(self, subchart):
        SubElement(subchart, '{%s}grouping' % CHART_NS, {'val':self.chart.GROUPING})


class BarChartWriter(LineChartWriter):

    def _write_options(self, subchart):
        SubElement(subchart, '{%s}barDir' % CHART_NS, {'val':'col'})
        SubElement(subchart, '{%s}grouping' % CHART_NS, {'val':self.chart.GROUPING})

    def _write_series_color(self, node, serie):
        # fill color
        fillc = SubElement(node, '{%s}solidFill' % DRAWING_NS)
        SubElement(fillc, '{%s}srgbClr' % DRAWING_NS, {'val':serie.color})
        super(BarChartWriter, self)._write_series_color(node, serie)


class ScatterChartWriter(LineChartWriter):

    series_type = '{%s}yVal' % CHART_NS

    def _write_options(self, subchart):
        SubElement(subchart, '{%s}scatterStyle' % CHART_NS,
                   {'val':'lineMarker'})

    def _write_series_xvalues(self, node, serie):
        if serie.xvalues:
            xval = SubElement(node, '{%s}xVal' % CHART_NS)
            self._write_serial(xval, serie.xreference)


class ChartWriter(object):
    """
    Preserve interface for chart writer
    """

    def __init__(self, chart):
        if isinstance(chart, PieChart):
            self.cw = PieChartWriter(chart)
        elif isinstance(chart, LineChart):
            self.cw = LineChartWriter(chart)
        elif isinstance(chart, BarChart):
            self.cw = BarChartWriter(chart)
        elif isinstance(chart, ScatterChart):
            self.cw = ScatterChartWriter(chart)
        else:
            raise ValueError("Don't know how to handle %s", chart.__class__.__name__)

    def write(self):
        return self.cw.write()
