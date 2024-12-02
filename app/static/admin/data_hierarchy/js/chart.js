// chart.js
console.log('Starting chart.js');

import { showSidebar, closeSidebar } from './sidebar.js';

export function initChart(data) {
  // Get the container dimensions
  const container = document.getElementById('hierarchy-chart');
  const width = container.clientWidth;
  const height = container.clientHeight;

  // Clear existing content
  container.innerHTML = '';

  // Create new SVG
  const svg = d3.select("#hierarchy-chart")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  // Add zoom functionality
  const g = svg.append("g");
  svg.call(d3.zoom()
    .scaleExtent([0.1, 3])
    .on("zoom", (event) => {
      g.attr("transform", event.transform);
    }));

  // Create tree layout
  const tree = d3.tree()
    .size([width - 100, height - 100])
    .separation((a, b) => (a.parent == b.parent ? 1 : 1.2));

  // Create hierarchy
  const root = d3.hierarchy(data[0]);

  // Compute the tree layout
  tree(root);

  // Color scale
  const colorScale = d3.scaleOrdinal()
    .domain(["Group", "Company", "Team"])
    .range(["#1f77b4", "#ff7f0e", "#2ca02c"]);

  // Create links
  const links = g.append("g")
    .attr("fill", "none")
    .attr("stroke", "#555")
    .attr("stroke-opacity", 0.4)
    .attr("stroke-width", 1.5)
    .selectAll("path")
    .data(root.links())
    .join("path")
    .attr("d", d3.linkVertical()
      .x(d => d.x)
      .y(d => d.y));

  // Create nodes
  const node = g.append("g")
    .attr("stroke-linejoin", "round")
    .attr("stroke-width", 3)
    .selectAll("g")
    .data(root.descendants())
    .join("g")
    .attr("transform", d => `translate(${d.x},${d.y})`);

  // Add circles to nodes
  node.append("circle")
    .attr("fill", d => d.parent ? (d.data.details === "Company" ? colorScale("Company") : colorScale("Team")) : colorScale("Top-level"))
    .attr("r", 6);

  // Add labels to nodes
  node.append("text")
    .attr("dy", "0.31em")
    .attr("x", d => d.children ? -12 : 12)
    .attr("text-anchor", d => d.children ? "end" : "start")
    .text(d => d.data.name)
    .style("font-size", "20px")
    .style("font-weight", "500")
    .style("font-family", "Arial, sans-serif")
    .clone(true).lower()
    .attr("stroke", "white")
    .attr("stroke-width", 4);

  node.on("mouseover", function(event, d) {
    const usersList = d.data.users.map(user => `<li>${user.email}</li>`).join("");
    d3.select("#tooltip")
        .style("display", "block")
        .style("left", (event.pageX + 10) + "px")
        .style("top", (event.pageY - 10) + "px")
        .html(`
            <strong>Name:</strong> ${d.data.name}<br>
            <strong>Users:</strong> <ul>${usersList}</ul>
        `);
  })

  .on("mouseout", function() {
    d3.select("#tooltip").style("display", "none");
  });

    node.on("click", function(event, d) {
    event.stopPropagation(); // Prevent event from bubbling
    showSidebar(d);
  });

  // Click handler for closing active displays when clicking outside
  d3.select("body").on("click", function(event) {
    if (event.target.closest('#details-sidebar') || 
        event.target.closest('.node')) {
      return;
    }
    closeSidebar();
  });
  
  // Center the initial view
  const initialTransform = d3.zoomIdentity
    .translate(width/2 - root.x, 50);
  svg.call(d3.zoom().transform, initialTransform);

}

