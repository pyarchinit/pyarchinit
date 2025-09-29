#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test the graph visualizer independently
"""

import json
import os

# Test data
test_graph = {
    "graph_id": "test_matrix",
    "name": "Test Matrix",
    "nodes": [
        {"node_id": "Site1_A1_100", "name": "US 100", "node_type": "stratigraphic_unit", "unita_tipo": "US"},
        {"node_id": "Site1_A1_101", "name": "US 101", "node_type": "stratigraphic_unit", "unita_tipo": "US"},
        {"node_id": "Site1_A1_102", "name": "US 102", "node_type": "stratigraphic_unit", "unita_tipo": "USM"},
        {"node_id": "Site1_A1_103", "name": "US 103", "node_type": "stratigraphic_unit", "unita_tipo": "USF"},
    ],
    "edges": [
        {"edge_id": "e1", "edge_source": "Site1_A1_100", "edge_target": "Site1_A1_101", "edge_type": "is_before"},
        {"edge_id": "e2", "edge_source": "Site1_A1_101", "edge_target": "Site1_A1_102", "edge_type": "is_before"},
        {"edge_id": "e3", "edge_source": "Site1_A1_102", "edge_target": "Site1_A1_103", "edge_type": "has_same_time"},
    ]
}

# Save test data
with open('test_graph.json', 'w') as f:
    json.dump(test_graph, f)

print("Testing graph visualizer...")

try:
    from modules.s3dgraphy.matrix_graph_visualizer import MatrixGraphVisualizer, NETWORKX_AVAILABLE

    if not NETWORKX_AVAILABLE:
        print("NetworkX not available!")
    else:
        print("NetworkX is available, creating visualizer...")

        visualizer = MatrixGraphVisualizer()
        success = visualizer.create_interactive_graph(test_graph, "test_graph_output.png")

        if success:
            print("✅ Graph created successfully!")
            print("Check test_graph_output.png")
        else:
            print("❌ Failed to create graph")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Clean up
if os.path.exists('test_graph.json'):
    os.remove('test_graph.json')

print("Test complete")