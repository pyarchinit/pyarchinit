# modules/s3dgraphy/matrix_graph_visualizer.py

## Overview

This file contains 6 documented elements.

## Classes

### MatrixGraphVisualizer

Creates a hierarchical graph visualization of the stratigraphic matrix

#### Methods

##### __init__(self)

Initializes a new instance of the stratigraphic matrix hierarchical graph visualization class. Sets `graph`, `pos`, `node_colors`, and `node_shapes` instance attributes to their default values (`None`, `None`, an empty dictionary, and an empty dictionary, respectively).

##### create_interactive_graph(self, graph_data, output_path)

Create an interactive hierarchical graph visualization

Args:
    graph_data: Extended Matrix data
    output_path: Optional path to save the image

Returns:
    True if successful

##### export_to_dot(self, graph_data, output_path)

Export to DOT format for Graphviz

## Functions

### calculate_level(node_id, visited_in_path)

*No description available.*
Recursively determines the hierarchical level of a given node within a directed graph using topological sort. The level of a node is computed as one greater than the maximum level among all nodes directly above it in the `above` mapping; nodes with no parents are assigned level 0. Cycle detection is handled by tracking nodes in the current recursion path via `visited_in_path`, returning 0 immediately if a cycle is encountered, and previously computed levels are cached in `levels` to avoid redundant recalculation.

**Parameters:**
- `node_id`
- `visited_in_path`

