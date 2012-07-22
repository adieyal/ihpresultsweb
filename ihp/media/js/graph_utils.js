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
            },
            plotBands : [{
                from : options.target,
                to: options.target * 1.01,
                color : 'rgba(0, 0, 0, 1.0)',
                label : {text : options.target_text, y: -2},
            }]
        },
        chart : {
            renderTo : options.container,
            type : 'column'
        },
        var_name : options.graph_name,
        xAxis : {
            categories : options.categories
        },
        title : {
            text : options.title
        },
        legend : {
            enabled : true
        }
    });

}
