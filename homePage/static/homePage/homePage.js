var graph
var svg
const dims = { height: 1400, width: 800 };
var users = []
d3 = window.d3
var data = []
$( window ).on( "load", function() {
  var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
  var socket = new WebSocket(ws_scheme + '://' + window.location.host + "/treeChannel" + window.location.pathname);

  //let socket = new WebSocket("wss://limitless-wildwood-61701.herokuapp.com/treeChannel");
  socket.onmessage = function(event) {
    data = event.data
    alert(`[message] Data received from server: ${event.data}`);
    update()
    };

    

    //console.log(data.find(node=>node.id = 64), " it has a fucking parent")
    
        //this.alert(this.JSON.stringify(data.find()))
      //define dimensions
      
      //create the svg element
      svg = d3.select('.canvas')
        .append('svg')
        .attr('width', dims.width + 100)
        .attr('height', dims.height + 100);
      //add the group element that will contain all the drawings of the graph
      graph = svg.append('g')
      .attr('transform', 'translate(50, 50)');

//add the group element that will contain all the drawings of the graph
  


 

function update() {
   
      var scale = d3.scaleOrdinal(d3["schemeSet3"])
        .domain(users.map((element) => element.name))


      this.graph.selectAll('.node').remove();
      this.graph.selectAll('.link').remove();
      data.sort((a,b)=>a.number - b.number)
      data.sort((a,b)=>a.number % 2 == 1 ? a.number - b.number : b.number - a.number)

        // stratify the data
        this.rootNode = d3.stratify()
          .id(function (d) {
            return d.number
          })
          .parentId(function (d) {
            return d.parent;
          })
          (data)
      //stratified data -> tree form data
      var treeData = d3.tree().size([1400, 800])(this.rootNode)
      //create the selection of nodes from the tree data descendants
      this.nodes = this.graph.selectAll('.node')
        .data(treeData.descendants())

      // save the links data from the stratified data
      var links = this.graph.selectAll('.link').data(this.rootNode.links())

      // draw the links as path elements
      links.enter().append('path')
        .attr('stroke', 'blue')
        .attr('d', d3.linkHorizontal()
          .x(function (d) { return d.y; })
          .y(function (d) { return d.x; }))
        .attr('class', 'link')
        .attr('fill', 'none')
        .attr('stroke', d => d.target.data.hasOwnProperty('userName') ? scale(d.source.data.userName) : 'gray')////#aaa
        .attr('stroke-width', 2)

      // add a group for each node with the specified coordinates
      var enterNodes = this.nodes.enter().append('g')
        .attr('transform', (d, i, n) => {
          //rotates the tree
          let x = d.y
          let y = d.x
          return `translate(${x},${y})`
        })
        .attr('class', "node")

      // draw rectangles in each node group
      var rectangles = enterNodes.append('rect')
        .attr('fill', d => d.data.userName != null ? scale(d.data.userName) : 'gray')
        .attr('stroke', 'black')
        .attr('width', 30)//30
        .attr('height', 30)
        .attr('transform', d => `translate(${-5}, ${-10})`).raise();


      // add a click event on each rectangle

      


      enterNodes.on("click", (d) => {
        console.log(d)

      })
      enterNodes.on("mouseenter", (d) => {
        console.log(d)

      })





      // add text to each of the node groups
      enterNodes.append('text')
        .text((d) => { return d.data.number })
        .attr('fill', d => d.data.childrenMissing>0 ? 'black' : "red")
        .attr('transform', d => `translate(${2}, ${10})`);

      var colorLegend = d3.legendColor()
        .shape("path", d3.symbol().type(d3.symbolTriangle).size(150)())
        .shapePadding(10)
        //use cellFilter to hide the "e" cell
        .cellFilter(function (d) { return d.label !== "e" })
        .scale(scale)

       this.graph.append("g")
        .attr("class", "userLegend")
      this.graph.select(".userLegend").call(colorLegend) 




      

    }
    var local = "http://127.0.0.1:5000/"
    var production = "https://limitless-wildwood-61701.herokuapp.com/"
    $.ajax({
        url: production + "users/", success: function(result){
      users = result
     }});
    $.ajax({
        url: production + "nodes/", success: function(result){
      data = result
      console.log(data, "this is the damn data")
      update()
    }});
    //fix the sorting of positive numbers

    //

    
      






      let mario = this


   
    //update()
      
 
    });


  

