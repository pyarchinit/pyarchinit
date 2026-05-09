# modules/s3dgraphy/simple_graph_visualizer.py

## Overview

This file contains 4 documented elements.

## Classes

### SimpleGraphVisualizer

Creates a hierarchical graph visualization without NetworkX

#### Methods

##### __init__(self)

*No description available.*
Initializes a new instance of the hierarchical graph visualization class. Sets up two instance attributes: `positions`, an empty dictionary intended to store node position data, and `levels`, an empty dictionary intended to store node level data.

##### create_graph_image(self, graph_data, output_path)

Create a hierarchical graph visualization using only matplotlib

Args:
    graph_data: Extended Matrix data
    output_path: Path to save the image

Returns:
    True if successful

