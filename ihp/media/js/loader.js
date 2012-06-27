// Notes:
// The *** is because the forum throws away the first space.
// My code used an assert method. Instead of adding more code, I documented preconditions.

/// Utility.
////////////

/** Clear the data display. */
function clearDataDisplay() {
    var display = d3.select("#DataDisplay");
    display.selectAll("svg").remove();
    display.selectAll("div").remove();
}


/// A "Loading" Indicator.
//////////////////////////

/** The current loading state. */
var loading = false;
/** The width for the data display element. */
var data_display_width = 400;
/** The height for the data display element. */
var data_display_height = 400;

/** Compute a partition of a domain with a "selected" item.
*** @param low The domain's lowest value. (pre: low < high)
*** @param high The domain's highest value. (pre: low < high)
*** @param div The number of partititions. (pre: div > 1)
*** @param index The index for the selection. If the index is negative,
***              than an equi-partition is performed. 
***              (pre: index < div)
*** @param inflation This factor magnifies the selection. (e.g. 20%
***                  increase in size implies inflation = 1.2)
***                  (pre: inflation > 0)
*** @return An array of pairs, where each pair is a region in the
***         partition, everything ordered from low to high. */
function computePartition(low, high, div, index, inflation) {
    // Setup.
    var delta = high - low;
    var reg_width = delta / div;
    var big_width = (index < 0) ? reg_width : inflation * reg_width;
    reg_width *= (delta - big_width) / (delta - reg_width);
    index = (index < 0) ? 0 : index;

    // Partition.
    var data = new Array(div);
    var anchor = reg_width * index + low;
    data[index] = [ anchor, anchor + big_width ];
    for (var i = index + 1; i < div; i++) {
        anchor = data[i - 1][1];
        data[i] = [ anchor, anchor + reg_width ];
    }
    for (var i = index - 1; i >= 0; i--) {
        anchor = data[i + 1][0];
        data[i] = [ anchor - reg_width, anchor ];
    }

    return data;
}

/** Create an arc-radial svg chunk.
*** @param index The index for the selected chunk. 
***              (assert 0 < index < 16) 
*** @param r1 The inner-radius for the chunk.
*** @param r2 The outer-radius for the chunk.
*** @return The created svg chunk. */
function createChunk(index, r1, r2) {
    // Setup with partition of [0, 2 * PI].
    var inflation = 1.1;
   var chunk_count = 16;
    var partition = 
        computePartition(0, 2 * Math.PI, chunk_count, index, inflation);

    // Create closures for anonymous functions.
    function startAngleClosure(list) {
        return function (d, i) { return list[i][0]; };
    }
    function endAngleClosure(list) {
        return function (d, i) { return list[i][1]; };
    }
    function outerRadiusClosure(index, inflation, r2) {
        return function (d, i) {
            if (i == index) return inflation * r2;
            else return r2; };
    }

    // Create the chunk.
    var chunk = d3.svg.arc()
        .startAngle(startAngleClosure(partition))
        .endAngle(endAngleClosure(partition))
        .innerRadius(r1)
        .outerRadius(outerRadiusClosure(index, inflation, r2));

    return chunk;
}

/** Continue the loading animation.
*** @param r1 The chunk's normal inner radius.
*** @param r2 The chunk's normal outer radius. */
function loadContinue(r1, r2) {
    var dead_time = 250; // ms

    function loadContinueRec() {
        // Remember which chunk is the big one.
        if (typeof loadContinueRec.index == "undefined")
            loadContinueRec.index = -1;
        if (++loadContinueRec.index > 15)
            loadContinueRec.index = 0;

        // Transform.
        if (loading) {
            var chunk = createChunk(loadContinueRec.index, r1, r2);
            var chunks = d3.select("#DataDisplay").selectAll(".chunk");
            chunks.transition()
                .duration(dead_time)
                .attr("d", chunk);
            setTimeout(loadContinueRec, dead_time);
        } 
    }
    loadContinueRec();
}

/** Start the loading widget. */
function loadStart() {
    // Setup.
    var size = Math.min(data_display_width, data_display_height);
    var center = "(" + size / 2 + ", " + size / 2 + ")";
    var r1 = 32;
    var r2 = 40;
    var r3 = 60;
    loading = true;
    clearDataDisplay();

    // Shape templates.
    var inner_circle = d3.svg.arc()
        .startAngle(0)
        .endAngle(2 * Math.PI)
        .innerRadius(0)
        .outerRadius(r1);
    var outer_chunk = createChunk(-1, r2, r3);

    // Construct the graphics for the loader.
    var loader = d3.select("#DataDisplay").append("svg")
        .attr("class", "loader")
        .attr("width", size)
        .attr("height", size)
        .append("g")
            .attr("transform", "translate" + center);
    var chunks = loader.selectAll("path")
        .data(d3.range(16))
        .enter().append("path")
            .attr("class", "chunk")
            .attr("d", outer_chunk);
    var circle = loader.append("path")
        .attr("d", inner_circle);

    // Start transition-callback loop.
    loadContinue(r2, r3);
}

/** Stop the loading widget. */
function loadStop() {
    loading = false;
    clearDataDisplay();
    // Fade away?
}
