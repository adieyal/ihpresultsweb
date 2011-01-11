from collections import defaultdict
from django.template import Library, Node, TemplateSyntaxError, Variable, VariableDoesNotExist
from django.template import resolve_variable
from submissions.indicators import calc_agency_country_indicators, NA_STR
import traceback
import random

register = Library()

def ffloat(x):
    if x == None: return "0"
    try:
        x = float(x)
        return "%.1f" % x
    except:
        return "0"

class AbsGraphNode(Node):
    def __init__(self, agency, indicator, data, element, title, yaxis, xaxis):
        self.agency = Variable(agency)
        self.indicator = indicator
        self.data = Variable(data)
        self.element = element
        self.title = Variable(title)
        self.yaxis = Variable(yaxis)
        self.xaxis = Variable(xaxis)

    def render(self, context):
        try:
            try:
                agency = self.agency.resolve(context)
            except VariableDoesNotExist:
                raise TemplateSyntaxError('"absgraph" tag got an unknown variable: %r' % self.agency)

            try:
                data = self.data.resolve(context)
            except VariableDoesNotExist:
                raise TemplateSyntaxError('"absgraph" tag got an unknown variable: %r' % self.data)

            try:
                title = self.title.resolve(context)
            except VariableDoesNotExist:
                raise TemplateSyntaxError('"absgraph" tag got an unknown variable: %r' % self.title)

            try:
                yaxis = self.yaxis.resolve(context)
            except VariableDoesNotExist:
                raise TemplateSyntaxError('"absgraph" tag got an unknown variable: %r' % self.yaxis)

            try:
                xaxis = self.xaxis.resolve(context)
            except VariableDoesNotExist:
                raise TemplateSyntaxError('"absgraph" tag got an unknown variable: %r' % self.xaxis)


            countries_list = ",".join('"%s"' % country for country, _ in data)
            baseline_vals = ",".join(ffloat(datum[self.indicator][0]) for country, datum in data)
            latest_vals = ",".join(ffloat(datum[self.indicator][1]) for country, datum in data)
            var_name = "chart_%s" % (random.randint(0, 10000000))
            target_element = self.element
            indicator = self.indicator

            s = """
                var %(var_name)s; // globally available
                $(document).ready(function() {
                    %(var_name)s = new Highcharts.Chart({
                        chart: {
                            renderTo: '%(target_element)s',
                            defaultSeriesType: 'column'
                        },
                        title: {
                           text: "%(title)s"
                        },
                        xAxis: {
                           categories: [%(countries_list)s],
                            title : {
                                text: "%(xaxis)s"
                            }
                        },
                        yAxis: {
                            title: {
                               text: "%(yaxis)s"
                            }
                        },
                        series: [{
                           name: 'baseline',
                           data: [%(baseline_vals)s]
                        }, {
                           name: 'latest',
                           data: [%(latest_vals)s]
                        }]
                    });
                });
            """ % locals()
            return s
        except:
            traceback.print_exc()

class RatioGraphNode(Node):
    def __init__(self, agency, indicator, data, element, title, yaxis, xaxis):
        self.agency = Variable(agency)
        self.indicator = indicator
        self.data = Variable(data)
        self.element = element
        self.title = Variable(title)
        self.yaxis = Variable(yaxis)
        self.xaxis = Variable(xaxis)

    def render(self, context):
        try:
            try:
                agency = self.agency.resolve(context)
            except VariableDoesNotExist:
                raise TemplateSyntaxError('"absgraph" tag got an unknown variable: %r' % self.agency)

            try:
                data = self.data.resolve(context)
            except VariableDoesNotExist:
                raise TemplateSyntaxError('"absgraph" tag got an unknown variable: %r' % self.data)

            try:
                title = self.title.resolve(context)
            except VariableDoesNotExist:
                raise TemplateSyntaxError('"absgraph" tag got an unknown variable: %r' % self.title)

            try:
                yaxis = self.yaxis.resolve(context)
            except VariableDoesNotExist:
                raise TemplateSyntaxError('"absgraph" tag got an unknown variable: %r' % self.yaxis)

            try:
                xaxis = self.xaxis.resolve(context)
            except VariableDoesNotExist:
                raise TemplateSyntaxError('"absgraph" tag got an unknown variable: %r' % self.xaxis)

            countries_list = ",".join('"%s"' % country for country, _ in data)
            data_vals = ",".join(ffloat(datum[self.indicator]) for country, datum in data)
            var_name = "chart_%s" % (random.randint(0, 10000000))
            target_element = self.element
            indicator = self.indicator

            s = """
                var %(var_name)s; // globally available
                $(document).ready(function() {
                    %(var_name)s = new Highcharts.Chart({
                        chart: {
                            renderTo: '%(target_element)s',
                            defaultSeriesType: 'column'
                        },
                        title: {
                           text: "%(title)s"
                        },
                        xAxis: {
                           categories: [%(countries_list)s],
                            title : {
                                text: "%(xaxis)s"
                            }
                        },
                        yAxis: {
                            title: {
                               text: "%(yaxis)s"
                            }
                        },
                        series: [{
                           name: 'data',
                           data: [%(data_vals)s]
                        }]
                    });
                });
            """ % locals() 
            return s
        except:
            traceback.print_exc()

def parse_absolute_graph(parser, token):
    """
    Output the javascript code for an absgraph

    e.g.
    {% absgraph agency indicator data element %}

    """
    tokens = token.contents.split()
    print tokens, len(tokens)
    if len(tokens) != 8:
        raise TemplateSyntaxError(u"'%r' tag requires 7 arguments." % tokens[0])
        
    return AbsGraphNode(tokens[1], tokens[2], tokens[3], tokens[4], tokens[5], tokens[6], tokens[7])

def parse_ratio_graph(parser, token):
    """
    Output the javascript code for a ratiograph

    e.g.
    {% ratiograph agency indicator data element %}

    """
    tokens = token.contents.split()
    if len(tokens) != 8:
        raise TemplateSyntaxError(u"'%r' tag requires 7 arguments." % tokens[0])
        
    return RatioGraphNode(tokens[1], tokens[2], tokens[3], tokens[4], tokens[5], tokens[6], tokens[7])

def resolve_variable(variable, context):
    try:
        return variable.resolve(context)
    except VariableDoesNotExist:
        raise TemplateSyntaxError('tag got an unknown variable: %r' % variable)
    
class OverallGraphNode(Node):
    def __init__(self, element, baseline_value, latest_value, target_value, title, yaxis, xaxis):
        self.element = element
        self.baseline_value = Variable(baseline_value)
        self.latest_value = Variable(latest_value)
        self.target_value = Variable(target_value)
        self.title = Variable(title)
        self.yaxis = Variable(yaxis)
        self.xaxis = Variable(xaxis)

    def render(self, context):
        try:
            target_element = self.element
            baseline_value = ffloat(resolve_variable(self.baseline_value, context))
            latest_value = ffloat(resolve_variable(self.latest_value, context))
            target_value = resolve_variable(self.target_value, context)
            title = resolve_variable(self.title, context)
            yaxis = resolve_variable(self.yaxis, context)
            xaxis = resolve_variable(self.xaxis, context)

            var_name = "chart_%s" % (random.randint(0, 10000000))
            s = """
                var %(var_name)s; // globally available
                $(document).ready(function() {
                    %(var_name)s = new Highcharts.Chart({
                        chart: {
                            renderTo: '%(target_element)s',
                            defaultSeriesType: 'column'
                        },
                        title: {
                           text: "%(title)s"
                        },
                        xAxis: [{
                           categories: ["Baseline", "2009"],
                           title : {
                                text: "%(xaxis)s"
                           },
                           showFirstLabel: false,
                           showLastLabel: false,
                        }, {
                           opposite: true,
                           labels: {
                                style: {
                                    display: 'None'
                                } 
                           },
                        }],
                        yAxis: {
                            title: {
                               text: "%(yaxis)s"
                            }
                        },
                        series: [{
                           name: 'baseline',
                           data: [%(baseline_value)s, %(latest_value)s],
                           xAxis: 0
                        }, {
                           type: 'line',
                           xAxis: 1,
                           name: 'Target',
                           data: [%(target_value)s, %(target_value)s],
                           dashStyle: 'shortDash',
                           marker: {
                               enabled: false
                           },
                           pointStart: -1,
                           pointInterval:3,
                        }],
                        tooltip : {
                            formatter: function() {
                                if (this.point.category == -1 || this.point.category == 2)
                                    return "Target: " + this.point.y + "%%";
                                return this.point.category + ": " + this.point.y + "%%";
                            }
                        }
                    });
                });
            """ % locals() 
            return s
        except:
            traceback.print_exc()

def parse_overall_graph(parser, token):
    """
    Output the javascript code for an overall graph

    e.g.
    {% overallgraph element baseline_value latest_value target_value title yaxis xaxis %}

    """
    tokens = token.contents.split()
    if len(tokens) != 8:
        raise TemplateSyntaxError(u"'%r' tag requires 7 arguments." % tokens[0])
        
    return OverallGraphNode(tokens[1], tokens[2], tokens[3], tokens[4], tokens[5], tokens[6], tokens[7])

class ProjectionGraphNode(Node):
    def __init__(self, element, baseline_value, baseline_year, latest_value, latest_year, target_value, title, yaxis, xaxis):
        self.element = element
        self.baseline_value = Variable(baseline_value)
        self.baseline_year = int(baseline_year)
        self.latest_value = Variable(latest_value)
        self.latest_year = int(latest_year)
        self.target_value = Variable(target_value)
        self.title = Variable(title)
        self.yaxis = Variable(yaxis)
        self.xaxis = Variable(xaxis)

    def render(self, context):
        try:
            target_element = self.element
            baseline_value = (resolve_variable(self.baseline_value, context))
            baseline_year = self.baseline_year
            latest_value = (resolve_variable(self.latest_value, context))
            latest_year = self.latest_year
            target_value = resolve_variable(self.target_value, context)
            title = resolve_variable(self.title, context)
            yaxis = resolve_variable(self.yaxis, context)
            xaxis = resolve_variable(self.xaxis, context)

            # Find the intersection point between the horizontal target line and the trend line
            # i.e. x = (y - c)/m 
            m = (latest_value - baseline_value) / (latest_year - baseline_year)
            c = baseline_value
            intersection = (target_value - c) / m  + baseline_year
            y = lambda x : ffloat(m * (x - baseline_year) + c)

            end_year = int(round(intersection, 0) + 1)
            x_categories = ",".join([('"%d"' % year) for year in range(baseline_year, end_year + 1)])
            target_data = ",".join(['%s' % target_value for i in range(baseline_year, end_year + 1)])
            actual_data = ",".join(['%s' % y(year) for year in range(baseline_year, latest_year + 1)])
            projected_data = ",".join(['[%s, %s]' % (year - baseline_year, y(year)) for year in range(latest_year, end_year + 1)])

            var_name = "chart_%s" % (random.randint(0, 10000000))
            s = """
                var %(var_name)s; // globally available
                $(document).ready(function() {
                    %(var_name)s = new Highcharts.Chart({
                        chart: {
                            renderTo: '%(target_element)s',
                            marginTop: 50,
                        },
                        title: {
                           text: "%(title)s"
                        },
                        xAxis: {
                           title : {
                                text: "%(xaxis)s"
                           },
                           categories: [%(x_categories)s]
                        },
                        yAxis: {
                            title: {
                               text: "%(yaxis)s"
                            }
                        },
                        series: [{
                           type: 'line',
                           name: 'Actual',
                           data: [%(actual_data)s],
                        }, {
                           type: 'line',
                           name: 'Target',
                           data: [%(target_data)s],
                           marker: {
                               enabled: false
                           },
                        }, {
                           type: 'line',
                           name: 'Projected',
                           data: [%(projected_data)s],
                           dashStyle: 'shortDash',
                        }],
                    });
                });
            """ % locals() 
            return s
        except:
            traceback.print_exc()

def parse_projection_graph(parser, token):
    """
    Output the javascript code for an overall graph

    e.g.
    {% overallgraph element baseline_value baseline_year latest_value latest_year target_value title yaxis xaxis %}

    """
    tokens = token.contents.split()
    if len(tokens) != 10:
        raise TemplateSyntaxError(u"'%r' tag requires 9 arguments." % tokens[0])
        
    return ProjectionGraphNode(tokens[1], tokens[2], tokens[3], tokens[4], tokens[5], tokens[6], tokens[7], tokens[8], tokens[9])

class CountryBarGraphNode(Node):
    def __init__(self, element, data):
        self.element = element
        self.data = Variable(data)

    def render(self, context):
        try:
            target_element = self.element
            data = resolve_variable(self.data, context)

            title = data["title"]
            y_axis = data.get("y-axis", "%")
            
            values = data["data"]
            countries = ",".join('"%s"' % el for el in values.keys())
            baseline_data = ",".join(ffloat(el["baseline"]) for el in values.values())
            latest_data = ",".join(ffloat(el["latest"]) for el in values.values())

            if "target" in data:
                target_name = data["target"].get("name", "Target")
                target_value = data["target"]["value"]
                target_data = ",".join(ffloat(target_value) for el in values.keys())
                target_series = """ {
                           type: 'line',
                           color: '#ff0000',
                           name: '%(target_name)s',
                           data: [%(target_data)s],
                           marker: {
                               enabled: false
                           },
                        }""" % locals()
            else:
                target_series = ""


            var_name = "chart_%s" % (random.randint(0, 10000000))
            s = """
                var %(var_name)s; // globally available
                $(document).ready(function() {
                    %(var_name)s = new Highcharts.Chart({
                        chart: {
                            renderTo: '%(target_element)s',
                            defaultSeriesType: 'column',
                            marginTop: 50,
                        },
                        title: {
                           text: "%(title)s"
                        },
                        xAxis: {
                           categories: [%(countries)s]
                        },
                        yAxis: {
                            title: {
                               text: "%(y_axis)s"
                            }
                        },
                        series: [{
                           name: 'Baseline',
                           data: [%(baseline_data)s],
                        }, {
                           name: '2009',
                           data: [%(latest_data)s],
                        }, %(target_series)s ],
                    });
                });
            """ % locals() 
            return s
        except:
            traceback.print_exc()

class Series(object):
    def __init__(self, data):
        self.data = data

    def _format(self, v):
        if type(v) == str:
            if v == "false" or v == "true":
                return v
            return "'%s'" % v
        elif type(v) == list or type(v) == tuple:
            return "[" + ",".join(self._format(i) for i in v) + "]"
        elif type(v) == int:
            return str(v)
        elif type(v) == float:
            return ffloat(v)
        elif type(v) == dict:
            return str(Series(v))

    def __str__(self):
        return "{" + ",".join(["%s : %s" % (k, self._format(v)) for (k, v) in self.data.items()]) + "}"

class StackedBarGraph(Node):
    def __init__(self, element, data):
        self.element = element
        self.data = Variable(data)

    def render(self, context):
        try:
            target_element = self.element
            data = resolve_variable(self.data, context)

            title = data["title"]
            y_axis = data.get("y-axis", "%")
            
            values = data["data"]
            keys = [key for key, _ in values]
            categories = ",".join('"%s"' % el for el in keys)

            data_series = zip(*[k for _, k in values])
            series_labels = data["series"]
            data_series = zip(series_labels, data_series)

            series = []
            for series_name, series_data in data_series:
                series.append(Series({
                    "data" : series_data,
                    "name" : series_name,
                }))

            if "target" in data:
                target_value = data["target"]["value"]
                series.append(Series({
                    "name" : data["target"].get("name", "Target"),
                    "color": '#ff0000',
                    "data" : [target_value] * len(values),
                    "marker" : { "enabled" : "false" },
                    "type" : "line",
                }))

            series_text = ",\n".join(str(s) for s in series)


            var_name = "chart_%s" % (random.randint(0, 10000000))
            s = """
                var %(var_name)s; // globally available
                $(document).ready(function() {
                    %(var_name)s = new Highcharts.Chart({
                        chart: {
                            renderTo: '%(target_element)s',
                            defaultSeriesType: 'column',
                            marginTop: 50,
                        },
                        title: {
                           text: "%(title)s"
                        },
                        xAxis: {
                           categories: [%(categories)s]
                        },
                        yAxis: {
                            title: {
                               text: "%(y_axis)s"
                            }
                        },
                        plotOptions : {
                            column: {
                                stacking: 'percent'
                            }
                        },
                        series: [%(series_text)s]
                    });
                });
            """ % locals() 
            return s
        except:
            traceback.print_exc()

def parse_countrybar_graph(parser, token):
    """
    Output the javascript code for a country bar graph

    e.g.
    {% countrybargraph element data %}

    """
    tokens = token.contents.split()
    if len(tokens) != 3:
        raise TemplateSyntaxError(u"'%r' tag requires 2 arguments." % tokens[0])
        
    return CountryBarGraphNode(tokens[1], tokens[2])

def parse_stacked_graph(parser, token):
    """
    Output the javascript code for a stacked bar graph

    e.g.
    {% stackedbargraph element data %}

    """
    tokens = token.contents.split()
    if len(tokens) != 3:
        raise TemplateSyntaxError(u"'%r' tag requires 2 arguments." % tokens[0])
        
    return StackedBarGraph(tokens[1], tokens[2])

register.tag('absgraph', parse_absolute_graph)
register.tag('ratiograph', parse_ratio_graph)
register.tag('overallgraph', parse_overall_graph)
register.tag('projectiongraph', parse_projection_graph)
register.tag('countrybargraph', parse_countrybar_graph)
register.tag('stackedbargraph', parse_stacked_graph)
