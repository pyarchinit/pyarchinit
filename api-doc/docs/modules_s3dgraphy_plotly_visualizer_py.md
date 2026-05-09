# modules/s3dgraphy/plotly_visualizer.py

## Overview

This file contains 4 documented elements.

## Classes

### PlotlyMatrixVisualizer

Creates interactive stratigraphic matrix visualization using Plotly

#### Methods

##### __init__(self, qgis_integration)

Initializes an instance of the stratigraphic matrix visualization class, setting up the internal state required for graph rendering. Accepts a `qgis_integration` boolean parameter (defaulting to `True`) that enables QGIS integration only when the `QGIS_AVAILABLE` flag is also `True`. Initializes `positions`, `levels`, and `selected_nodes` as empty collections to hold node layout data during visualization.

##### create_interactive_graph(self, graph_data, output_path)

Create interactive graph visualization with Plotly

