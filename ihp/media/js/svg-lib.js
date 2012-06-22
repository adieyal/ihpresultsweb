function getParameterByName(name) {
      name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
      var regexS = "[\\?&]" + name + "=([^&#]*)";
      var regex = new RegExp(regexS);
      var results = regex.exec(window.location.search);
      if(results === null)
        return null;
      else
        return decodeURIComponent(results[1].replace(/\+/g, " "));
}



function load_svg(svg, json, element, callback){
    var rand = Math.floor((Math.random()*1000)+1);
    var page = getParameterByName('page');
    if (page === null || isNaN(page)){
        page = svg + '-page-1.svg';
    } else {
        page = parseInt(page, 10);
        page = svg + '-page-' + page + '.svg';
    }

    page = page + '?' + rand;
    json = json + '?' + rand;

    d3.json(json, function(e){
        d3.xml(page, 'image/svg+xml', function(xml){


            var ele = document.getElementById(element);
            if (ele === null){
                throw Error('Unable to find element "' + element + "'");
            }
            ele.appendChild(xml.documentElement);

            callback(e);
        });
    });
}



load_svg_image = function(url, node){
    if (d3.select(node).node() === null){
        throw Error('unable to find node "' + node + '" cannot load svg image');
    }
    var func = function(xml){
        var icon = document.importNode(d3.select(xml).select('g').node(), true);

        d3.select(node).append('g').node().appendChild(icon);
    };
    d3.xml(url, 'image/svg+xml', func);
};



/**
 * Use a foreignObject to insert html text into the svg element
 * at the location an size of the node element.
 */
var insert_text = function(node, text, classes, id){
    var n = node.node();
    if (n === null){
        throw Error('Unable to access the node to insert text');
    }
    var bb = n.getBBox();

    var parent = n.parentNode;
    if (parent === undefined || parent === null){
        throw Error('Unable to find parent node for element ' + node.node());
    }

    parent = d3.select(parent);

    var fo = parent.append("foreignObject")
        .attr('x', bb.x)
        .attr('y', bb.y)
        .attr("width", bb.width)
        .attr("height", bb.height)
        .append("xhtml:span")
            .html(text);

    if (id !== undefined){
        fo.attr('id', id);
    }

    if (classes !== undefined){
        fo.attr('class', classes);
    }
};