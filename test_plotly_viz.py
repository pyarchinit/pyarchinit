#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Plotly interactive visualizer
"""

import os
import json
from modules.s3dgraphy.plotly_visualizer import PlotlyMatrixVisualizer

# Create test data with proper US types and relationships
test_matrix = {
    "graph_id": "Site1_A1_matrix",
    "name": "Site1 Area A1 Matrix",
    "nodes": [
        {"node_id": "US100", "name": "US 100", "us": 100, "unita_tipo": "US", "description": "Humus layer", "sito": "Site1", "area": "A1"},
        {"node_id": "US101", "name": "US 101", "us": 101, "unita_tipo": "US", "description": "Fill deposit", "sito": "Site1", "area": "A1"},
        {"node_id": "US102", "name": "USM 102", "us": 102, "unita_tipo": "USM", "description": "Wall foundation", "sito": "Site1", "area": "A1"},
        {"node_id": "US103", "name": "USM 103", "us": 103, "unita_tipo": "USM", "description": "Wall elevation", "sito": "Site1", "area": "A1"},
        {"node_id": "US104", "name": "USF 104", "us": 104, "unita_tipo": "USF", "description": "Post hole", "sito": "Site1", "area": "A1"},
        {"node_id": "US105", "name": "US 105", "us": 105, "unita_tipo": "US", "description": "Floor layer", "sito": "Site1", "area": "A1"},
        {"node_id": "US106", "name": "USD 106", "us": 106, "unita_tipo": "USD", "description": "Destruction layer", "sito": "Site1", "area": "A1"},
        {"node_id": "US107", "name": "USR 107", "us": 107, "unita_tipo": "USR", "description": "Fill of cut", "sito": "Site1", "area": "A1"},
        {"node_id": "US108", "name": "US 108", "us": 108, "unita_tipo": "US", "description": "Natural soil", "sito": "Site1", "area": "A1"},
    ],
    "edges": [
        {"edge_source": "US100", "edge_target": "US101", "edge_type": "is_before"},
        {"edge_source": "US100", "edge_target": "US106", "edge_type": "is_before"},
        {"edge_source": "US101", "edge_target": "US105", "edge_type": "is_before"},
        {"edge_source": "US106", "edge_target": "US103", "edge_type": "is_before"},
        {"edge_source": "US103", "edge_target": "US102", "edge_type": "has_same_time"},
        {"edge_source": "US102", "edge_target": "US105", "edge_type": "is_before"},
        {"edge_source": "US105", "edge_target": "US104", "edge_type": "is_before"},
        {"edge_source": "US104", "edge_target": "US107", "edge_type": "has_same_time"},
        {"edge_source": "US107", "edge_target": "US108", "edge_type": "is_before"},
        {"edge_source": "US104", "edge_target": "US108", "edge_type": "is_before"},
    ]
}

print("=" * 60)
print("Testing Plotly Interactive Visualizer")
print("=" * 60)

# Check if Plotly is available
try:
    import plotly
    print(f"✅ Plotly version: {plotly.__version__}")
except ImportError:
    print("❌ Plotly not installed. Install with: pip install plotly")
    exit(1)

# Create visualizer
visualizer = PlotlyMatrixVisualizer(qgis_integration=False)

# Generate interactive graph
output_path = os.path.expanduser('~/Desktop/test_plotly_interactive.html')
print(f"\nGenerating interactive graph to: {output_path}")

success = visualizer.create_interactive_graph(test_matrix, output_path)

if success:
    print(f"\n✅ Interactive graph created successfully!")
    print(f"Open in browser: {output_path}")
    print("\nFeatures:")
    print("- Hover over nodes to see details")
    print("- Click and drag to rotate")
    print("- Scroll to zoom")
    print("- Different colors for US, USM, USF, USD, USR types")
    print("- Different edge styles for relationships")
else:
    print("\n❌ Failed to create interactive graph")

print("\nTest complete")