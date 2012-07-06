if (typeof Number.prototype.formatThousands != 'function') {
    Number.prototype.formatThousands = function(c, d, t) {
        var n = this,
            c = isNaN(c = Math.abs(c)) ? 2 : c,
            d = d == undefined ? "." : d,
            t = t == undefined ? "," : t,
            s = n < 0 ? "-" : "",
            i = parseInt(n = Math.abs(+n || 0).toFixed(c)) + "",
            j = (j = i.length) > 3 ? j % 3 : 0;
       return s
              + (j ? i.substr(0, j) + t : "")
              + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t)
              + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
    }
}

var fill_svg = function(json){
    var n, i;
    d3.selectAll(".remove").remove();

    n = d3.select("#country_flag");
    if (n.node() !== null){
        n.attr("xlink:href", json.info.flag);
    }

    n = d3.selectAll(".country_name");
    if (n.node() !== null){
        n.text(json.info.country);
    }

    n = d3.selectAll("#_x5F_total");
    if (n.node() !== null){
      build_total_health(json.health_finance.total.series);
    }
    for (i in json.managing_results){
        n = d3.select('#' + i);
        if (n.node() !== null){
            n.selectAll('g').remove();
            n.selectAll('polygon').remove();

            load_svg_image(json.managing_results[i], '#' + i);
        }
    }

    for (i in json.systems){
        id = '#' + i;
        n = d3.select(id);

        if (n.node() !== null){
            data = json.systems[i];


            load_svg_image(data.logo, id + ' .icon');
            insert_text(n.select('.header'), data.header ,"header-text");
            insert_text(n.select('.description'), data.description, "description-text");
        }
    }

    var rounding = {
        phcclinincs : 0,
        healthworkers : 1,
        healthsystems : 0,
    }

    for (i in json.health_systems){
        var height = 75;
        var max_height = 90;

        id = '#' + i;
        n = d3.select(id);

        if (n.node() !== null){
            data = json.health_systems[i];
            
            var r = rounding[i];
            
            if (data.value != null) {
                if (i == "healthsystems") {
                    d3.select(id+'-text')
                        .select('.value')
                        .text("US$" + data.value.formatThousands(r));
                } else {
                    d3.select(id+'-text')
                        .select('.value')
                        .text(data.value.formatThousands(r));
                }
            } else {
               d3.select(id + '-text div').text(data.missing_data_text); 
            }
            

            var g = n.select('.graph');
            g.select('.point');
            if (data.percent == null) {
                g.remove();
            } else {
                pixels = data.percent / 100 * height * -1;

                if (pixels < 0){
                    pixels = d3.max([pixels, -max_height])
                    g.select('rect')
                        .attr('y', pixels)
                        .attr('class', 'health_green')
                        .attr('height', pixels * -1);

                    g.select('.point')
                        .attr('class', 'health_green')
                        .attr('transform', 'translate(0, ' + (pixels - 7)  +')');

                    if (data.percent != 0) {
                        g.select('text')
                            .attr("y", pixels)
                            .attr('dy', -10)
                            .attr('class', 'health-value')
                            .text(d3.round(data.percent, 1) + '%');
                    }
                }else {
                    pixels = d3.min([pixels, max_height])
                    g.select('rect')
                        .attr('y', 0)
                        .attr('class', 'health_red')
                        .attr('height', pixels);

                    g.select('.point')
                        .attr('transform', 'rotate(180)translate(-84)translate(0, ' + ( -1 *pixels - 7)  +')');
                    g.select('polygon')
                        .attr('class', 'health_red');

                    if (data.percent != 0) {
                        g.select('text')
                            .attr("y", pixels)
                            .attr('dy', 20)
                            .attr('class', 'health-value')
                            .text(d3.round(data.percent, 1) + '%');
                    }

                }
                if (Math.abs(data.percent) < 0.1)
                    g.select('polygon').remove()
            }
        }
    }

    n = d3.select("#pooled_funding");

    if (n.node() !== null){
        rects = n.selectAll('rect');
        count = rects[0].length;

        for (i =0 ; i < count; i++){
            if (i < json.health_finance.pooled){
                d3.select(rects[0][i])
                    .attr('fill', '#FAA627');
                }else {
                d3.select(rects[0][i])
                    .attr('fill', '#D1DDD9');
            }

        }
    }

    n = d3.select("#budget");

    if (n.node() !== null){

        total = json.health_finance.budget.allocated + json.health_finance.budget.increase;


        var segpie = {
            width: 75,
            height:75,
            node :'#budget_chart',

            arc: {
                margin: 0,
                width: 10
            },
            data : [
                {'value': json.health_finance.budget.allocated},
                {'value': json.health_finance.budget.increase},
                {'value': 100 - total}
            ],
            colors: ['#B1C529', '#FAA627', '#0D3E3E']
        };

        d3.select('#budget_allocated')
            .text( json.health_finance.budget.allocated + '%');
        d3.select('#budget_increase')
            .text( json.health_finance.budget.increase + '%');
        var segpiegraph = new SegmentPieGraph(segpie);
    }

    for (i in json.country_ownership){
        id = '#' + i;
        n = d3.select(id);

        if (n.node() !== null){
            data = json.country_ownership[i];

            for (j =0; j < data.length; j++){
                build_text_element(n.select('.data'), i, data, j);
            }
        }
    }

    for (i in json.commitments){
        data = json.commitments[i];

        id = '#' + i;
        n = d3.select(id);

        d3.select(id + '-text')
            .text(data.description);

        if (n.node() !== null){
            //var text= n.selectAll('.text');
            //if (text.node() !== null){
            //    insert_text(n.selectAll('.text'), data.description, 'commitment-text');
            //}
            var icon = n.selectAll('.icon');
            if (icon.node() !== null){
                load_svg_image(data.rating, id + ' .icon');
            }

            var graph = n.selectAll('.graph');
            if (graph.node() !== null && data.type != 'dot') {

                var series = [];
                for (var k = 0; k < data.progress.length; k ++) {
                    var d = data.progress[k];
                    series.push({'key': d.year, 'value': d.value <= data.max ? d.value : data.max});
                }
                var hb = {
                    width:165,
                    height: 45,
                    node: id + ' .graph',

                    bar :{
                        'height': 15,
                        'margin': 2,
                        'max': data.max === undefined ? 100 : data.max,
                        'text': false,
                        'background': '#dfe7e5'
                    },
                    line : data.line,

                    data : series
                };
                hb = new HorizontalBarGraph(hb);
            } else if (data.type == 'dot') {
                build_dot_graph(data);

            }

        }
    }

    for (i in json.progress){
        id = '#' + i;
        n = d3.select(id);
        data = json.progress[i];
        if (n.node() !== null){
	    console.log('doing '+i);
            value_mode = data.type == "percent" ? '%' : '';
            change_mode = data.change_type == "percent" ? '%' : '';

            n.select('.year')
                .text(data.year);

            n.select('.value')
                .attr('class', data.color)
                .text(data.value + value_mode);

            n.select('.change_year')
                .text(data.change_year);

            n.select('.change_value')
                .attr('class', data.color)
                .text(data.change_value + change_mode);

            var src = '/media/icons/arrow_' + data.arrow + '_'
		+ data.color + '.svg';
	    n.select('img.arrow')
		.attr('src', '/media/icons/arrow_' + data.arrow + '_' + data.color + '.svg')
            //load_svg_image('/media/icons/arrow_' + data.arrow + '_' + data.color + '.svg',
            //id + ' .arrow');
            //load_svg_image('/media/icons/arrow_' + data.arrow + '_' + data.color + '.svg',
            //    id + ' .arrow');
        }
    }

    n = d3.select('#countryflags');
    if (n.node() !== null){
        var y = d3.scale.linear()
            .domain([0, 5])
            .rangeRound([0, 230]);
        var x = d3.scale.linear()
            .domain([0, 4])
            .rangeRound([0, 260]);
        n.selectAll('image').data(json.countries)
            .enter()
            .append('image')
                .attr('x', function(d, i){
                    return x(i % 4);
                })
                .attr('y', function(d, i){
                    return y (parseInt(i / 4, 10));
                })
                .attr('xlink:href', function(d){ return d; })
                .attr('width', '70')
                .attr('height', '50');


    }
};

var build_dot_graph = function(data){

    options =['no', 'a', 'b', 'c', 'd'];
    for (var i =0; i < data.progress.length; i++){
        var n = d3.select('#line_' + (i + 1));

        var p = data.progress[i];

        n.select('text').text(p.year);

        var grads = n.selectAll('.gradient');
        n.selectAll('.stop').remove();
        for (var j =0; j < options.length; j++){
            var o = options[j];
            var g = d3.select(grads[0][j]);
	    
            build_gradient(g, (p.value || 'no').toLowerCase() == o);
        }
    }
};

var build_gradient = function(node, on){
    if (on){
        add_stop(node, '#D1DDD9', '0.0061');
        add_stop(node, '#0D3E3E', '1');
    }else {
        add_stop(node, "#E5E1DF" , "0");
        add_stop(node, "#F0EFF0" , "0");
        add_stop(node, "#F2F2F2" , "0");
        add_stop(node, "#E3E8E7" , "0");
        add_stop(node, "#D1DDD9" , "0");
        add_stop(node, "#86A49A" , "1");
    }
};


var add_stop = function(node, color, offset){
        node.append('stop')
            .attr('stop-color', color)
            .attr('offset', offset);
};

build_text_element = function(n, id, data, index){
    var h = 40;
    var w = 140;
    var d = data[index];

    var g = n.append('g')
        .attr('transform', 'translate(0, ' + (j * h) +')')
        .attr('id',  id + '-' + index);

    if (index < data.length - 1){
        g.append('line')
            .style('stroke-width', '0.59')
            .style('stroke-dasharray', '0.9899,0.9899')
            .style('stroke', '#0E3D3D')
            .attr('y1', h-1)
            .attr('y2', h-1)
            .attr('x1', 0)
            .attr('x2', w + 30);
    }

    var rect = g.append('rect')
            .attr('width', w)
        .attr('height', '100px')
            .attr('x', 3)
            .style('opacity', 0)
            .attr('y', 3);

    var text =  d.description;
    if (d.bullet === undefined || d.bullet){
        text = '&bull; ' + text;
    }
    insert_text(rect, text, "text-list");

    if (d.logo !== undefined){
        g.append('g')
            .attr('class', 'logo')
            .attr('transform', 'translate(143, 4)scale(0.7)');


        load_svg_image(d.logo, '#' + id + '-' + index + ' .logo');
    }

    if (d.text !== undefined){
        g.append('g')
            .attr('class', 'logo')
            .attr('transform', 'translate(146, 20)')
            .append('text')
            .style('font-size', '20px')
            .style('text-align', 'center')
            .text(d.text);



    }


};

in_millions = function(v) {
    return v / 1000000;
}

build_total_health = function(data){
    var t, i;
    var h = 100;
    var w = 17;
    var n = d3.select('#total_health_chart');
    var years = d3.selectAll('#_x5F_years text');

    var max = 0;
    for (i =0; i < data.length; i++){
        data[i].domestic = in_millions(data[i].domestic)
        data[i].external = in_millions(data[i].external)
        t = data[i].domestic + data[i].external;
        if (t > max){
            max = t;
        }
    }
    max = sigFigs(max * 1.2, 1);

    if (isNaN(max))
        max = 100;
    var y = d3.scale.linear()
        .domain([0, max])
        .rangeRound([0, -100]);

    var values = d3.selectAll('#_x5F_values text');

    var ticks = y.ticks(values[0].length);
    for (i = 0; i < values[0].length - 1; i++){
        d3.select(values[0][i]).text( 'US $' + ticks[i] + 'm');
    }

    offset= [0, 55, 107];
    for (i = 0; i < data.length; i++){
        var x = offset[i];
        var d = data[i];

        t = d3.round(d.domestic + d.external, 2);
        var height = y(t);
        var ext_height = y(d.external);


        d3.select(years[0][i]).text(d.name);

        n.append('rect')
            .attr('x', x)
            .attr('y', height)
            .attr('height', -1 * height - 2)
            .attr('width', 17)
            .attr('rx', 3)
            .attr('class', 'background');

        n.append('rect')
            .attr('x', x)
            .attr('y', height)
            .attr('height', -1 * ext_height)
            .attr('width', 17)
            .attr('rx', 3)
            .attr('class', 'external');

        n.append('rect')
            .attr('x', x)
            .attr('y', height - ext_height + 1 )
            .attr('height', d.domestic / max * 100 - 2)
            .attr('width', 17)
            .attr('rx', 3)
            .attr('class', 'domestic');

        if (t > 0) {
                n.append('text')
            .attr('x', x + 8)
            .attr('y', height)
            .attr('dy', -5)
            .style('text-anchor', 'middle')
            .text('$' + t + 'm');
        }
    }


};

function sigFigs(n, sig) {
    var mult = Math.pow(10, sig - Math.floor(Math.log(n) / Math.LN10) - 1);
    return Math.ceil(n * mult) / mult;
}

load_svg(SVG, json, 'figure', fill_svg);
