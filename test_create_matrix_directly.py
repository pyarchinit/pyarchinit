#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Extended Matrix creation directly without database
"""

import os
import sys
import json
from pathlib import Path

# Add the plugin path
plugin_path = Path(__file__).parent
sys.path.insert(0, str(plugin_path))

from modules.s3dgraphy.graphviz_visualizer import GraphvizVisualizer

# Create test Extended Matrix directly
print("=" * 60)
print("Creating Extended Matrix directly for testing")
print("=" * 60)

# Create a proper Extended Matrix structure
matrix = {
    "graph_id": "Site1_A1_matrix",
    "name": "Site1 Area A1 Extended Matrix",
    "graph_type": "Extended_Matrix",
    "nodes": [
        {
            "node_id": "Site1_A1_100",
            "name": "US 100",
            "us": 100,
            "node_type": "stratigraphic_unit",
            "unita_tipo": "US",
            "description": "Top layer soil",
            "sito": "Site1",
            "area": "A1"
        },
        {
            "node_id": "Site1_A1_101",
            "name": "US 101",
            "us": 101,
            "node_type": "stratigraphic_unit",
            "unita_tipo": "US",
            "description": "Fill layer",
            "sito": "Site1",
            "area": "A1"
        },
        {
            "node_id": "Site1_A1_102",
            "name": "US 102",
            "us": 102,
            "node_type": "stratigraphic_unit",
            "unita_tipo": "USM",
            "description": "Wall structure",
            "sito": "Site1",
            "area": "A1"
        },
        {
            "node_id": "Site1_A1_103",
            "name": "US 103",
            "us": 103,
            "node_type": "stratigraphic_unit",
            "unita_tipo": "US",
            "description": "Foundation cut",
            "sito": "Site1",
            "area": "A1"
        },
        {
            "node_id": "Site1_A1_104",
            "name": "US 104",
            "us": 104,
            "node_type": "stratigraphic_unit",
            "unita_tipo": "USF",
            "description": "Pit feature",
            "sito": "Site1",
            "area": "A1"
        },
        {
            "node_id": "Site1_A1_105",
            "name": "US 105",
            "us": 105,
            "node_type": "stratigraphic_unit",
            "unita_tipo": "US",
            "description": "Natural soil",
            "sito": "Site1",
            "area": "A1"
        }
    ],
    "edges": [
        {
            "edge_id": "e1",
            "edge_source": "Site1_A1_100",
            "edge_target": "Site1_A1_101",
            "edge_type": "is_before",
            "original_relationship": "copre"
        },
        {
            "edge_id": "e2",
            "edge_source": "Site1_A1_100",
            "edge_target": "Site1_A1_102",
            "edge_type": "is_before",
            "original_relationship": "copre"
        },
        {
            "edge_id": "e3",
            "edge_source": "Site1_A1_101",
            "edge_target": "Site1_A1_104",
            "edge_type": "has_same_time",
            "original_relationship": "riempie"
        },
        {
            "edge_id": "e4",
            "edge_source": "Site1_A1_102",
            "edge_target": "Site1_A1_103",
            "edge_type": "generic_connection",
            "original_relationship": "si appoggia a"
        },
        {
            "edge_id": "e5",
            "edge_source": "Site1_A1_103",
            "edge_target": "Site1_A1_105",
            "edge_type": "is_before",
            "original_relationship": "taglia"
        },
        {
            "edge_id": "e6",
            "edge_source": "Site1_A1_104",
            "edge_target": "Site1_A1_105",
            "edge_type": "is_before",
            "original_relationship": "taglia"
        }
    ]
}

# Save as JSON
output_json = os.path.expanduser('~/Desktop/test_matrix_direct.json')
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(matrix, f, indent=2, ensure_ascii=False)
print(f"\n✅ Extended Matrix saved to: {output_json}")

# Print summary
print("\nExtended Matrix summary:")
print(f"  Nodes: {len(matrix.get('nodes', []))}")
print(f"  Edges: {len(matrix.get('edges', []))}")

# Show edges
print("\nEdges:")
for edge in matrix.get('edges', []):
    print(f"  {edge.get('edge_source')} -> {edge.get('edge_target')} ({edge.get('edge_type')})")

# Create visualization
print("\nCreating graph visualization...")
visualizer = GraphvizVisualizer()
output_png = os.path.expanduser('~/Desktop/test_matrix_direct.png')
success = visualizer.create_graph_image(matrix, output_png)

if success:
    print(f"✅ Graph saved to: {output_png}")

    # Also save the DOT file to examine
    dot_path = output_png.replace('.png', '.dot')
    print(f"DOT file saved to: {dot_path}")

    # Show first 30 lines of DOT
    with open(dot_path, 'r') as f:
        lines = f.readlines()[:30]
        print("\nDOT file preview:")
        print("-" * 40)
        for line in lines:
            print(line.rstrip())
else:
    print("❌ Failed to create graph")

print("\nTest complete")