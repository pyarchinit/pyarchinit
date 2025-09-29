#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug script for Graphviz visualizer
"""

import json
import os
from modules.s3dgraphy.graphviz_visualizer import GraphvizVisualizer

# Create test data with clear hierarchical relationships
test_data = {
    "graph_id": "test_matrix",
    "name": "Test Stratigraphic Matrix",
    "nodes": [
        {"node_id": "US1", "name": "US 1", "node_type": "stratigraphic_unit", "unita_tipo": "US", "description": "Top layer"},
        {"node_id": "US2", "name": "US 2", "node_type": "stratigraphic_unit", "unita_tipo": "US", "description": "Middle layer 1"},
        {"node_id": "US3", "name": "US 3", "node_type": "stratigraphic_unit", "unita_tipo": "USM", "description": "Wall"},
        {"node_id": "US4", "name": "US 4", "node_type": "stratigraphic_unit", "unita_tipo": "US", "description": "Middle layer 2"},
        {"node_id": "US5", "name": "US 5", "node_type": "stratigraphic_unit", "unita_tipo": "USF", "description": "Feature"},
        {"node_id": "US6", "name": "US 6", "node_type": "stratigraphic_unit", "unita_tipo": "US", "description": "Bottom layer"},
    ],
    "edges": [
        {"edge_id": "e1", "edge_source": "US1", "edge_target": "US2", "edge_type": "is_before"},
        {"edge_id": "e2", "edge_source": "US1", "edge_target": "US3", "edge_type": "is_before"},
        {"edge_id": "e3", "edge_source": "US2", "edge_target": "US4", "edge_type": "is_before"},
        {"edge_id": "e4", "edge_source": "US3", "edge_target": "US4", "edge_type": "has_same_time"},
        {"edge_id": "e5", "edge_source": "US4", "edge_target": "US5", "edge_type": "is_before"},
        {"edge_id": "e6", "edge_source": "US4", "edge_target": "US6", "edge_type": "is_before"},
        {"edge_id": "e7", "edge_source": "US5", "edge_target": "US6", "edge_type": "has_same_time"},
    ]
}

print("=" * 60)
print("Testing Graphviz Visualizer with sample data")
print("=" * 60)

# Save test data
with open('test_matrix.json', 'w') as f:
    json.dump(test_data, f, indent=2)
print("\nTest data saved to test_matrix.json")

# Create visualizer
visualizer = GraphvizVisualizer()

# Generate graph
output_path = os.path.expanduser('~/Desktop/test_graphviz.png')
print(f"\nGenerating graph to: {output_path}")
success = visualizer.create_graph_image(test_data, output_path)

if success:
    print(f"\n✅ Graph created successfully!")
    print(f"Check: {output_path}")

    # Also check the DOT file
    dot_path = output_path.replace('.png', '.dot')
    if os.path.exists(dot_path):
        print(f"\nDOT file content (first 50 lines):")
        print("-" * 40)
        with open(dot_path, 'r') as f:
            lines = f.readlines()[:50]
            for line in lines:
                print(line.rstrip())
else:
    print("\n❌ Failed to create graph")

print("\nTest complete")