# modules/s3dgraphy/graphviz_visualizer.py

## Overview

This file contains 4 documented elements.

## Classes

### GraphvizVisualizer

Creates a hierarchical graph visualization using Graphviz

#### Methods

##### __init__(self)

*No description available.*
Initializes a new instance of the hierarchical graph visualization class. Sets up two instance attributes: `dot_content`, initialized as an empty list, and `levels`, initialized as an empty dictionary.

##### create_graph_image(self, graph_data, output_path)

Create a hierarchical graph visualization using Graphviz

Args:
    graph_data: Extended Matrix data
    output_path: Path to save the image

Returns:
    True if successful

