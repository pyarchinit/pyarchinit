# modules/s3dgraphy/matrix_visualizer_qgis.py

## Overview

This file contains 4 documented elements.

## Classes

### MatrixVisualizerQGIS

Creates a visual representation of the Extended Matrix in QGIS

#### Methods

##### __init__(self, iface)

Initializes an instance of the Extended Matrix QGIS visualization class. Accepts an optional `iface` parameter representing the QGIS interface, and sets it as an instance attribute alongside two empty dictionaries, `node_positions` and `layers`, which are used to store node position data and layer references respectively.

##### visualize_extended_matrix(self, graph_data, chronological_sequence)

Create QGIS layers to visualize the Extended Matrix

Args:
    graph_data: Extended Matrix data
    chronological_sequence: Optional chronological ordering

Returns:
    Dictionary of created layers

