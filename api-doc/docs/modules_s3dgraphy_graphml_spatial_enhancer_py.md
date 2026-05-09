# modules/s3dgraphy/graphml_spatial_enhancer.py

## Overview

This file contains 5 documented elements.

## Classes

### GraphMLSpatialEnhancer

Enhances GraphML files with spatial/functional grouping information
compatible with yEd's group nodes

#### Methods

##### __init__(self)

Initializes an instance of the class by setting up the `ns` attribute, a dictionary containing two XML namespace mappings used for parsing GraphML files. The `graphml` key maps to `'http://graphml.graphdrawing.org/xmlns'` and the `y` key maps to `'http://www.yworks.com/xml/graphml'`, corresponding to the standard GraphML namespace and the yWorks-specific namespace, respectively.

##### enhance_graphml_with_groups(self, graphml_file, groupings, output_file)

Enhance GraphML file with group nodes for spatial/functional groupings

Args:
    graphml_file: Path to input GraphML file
    groupings: Dictionary of group_name -> list of node IDs
    output_file: Optional output path (overwrites input if None)

##### create_hierarchical_groups(self, graphml_file, hierarchy, output_file)

Create hierarchical groups (e.g., Area -> Settore -> US)

Args:
    graphml_file: Input GraphML file
    hierarchy: Nested dictionary of groupings
    output_file: Output file path

