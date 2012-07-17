build_graph = function(options) {
    chart_559136 = new Highcharts.Chart({
        series : [
            {
                data : options.base_data,
                name : '2007 data'
            },
            {
                data : options.y2009_data,
                name : '2009 data'
            },
            {
                data : options.cur_data,
                name : '2011 data'
            }
        ],
        yAxis : {
            title : {
                text : options.yaxis
            }
        },
        chart : {
            renderTo : options.container,
            type : 'column'
        },
        var_name : options.graph_name,
        xAxis : {
            categories : countries
        },
        title : {
            text : options.title
        },
        legend : {
            enabled : true
        }
    });
}
