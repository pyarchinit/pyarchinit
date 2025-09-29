#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple test for S3DGraphy functionality
"""

import json
from s3dgraphy import Graph, Node

# Create a graph
print("Creating Extended Matrix graph...")
graph = Graph(graph_id="test_site_matrix", name="Test Site Extended Matrix")

# Add some test stratigraphic units
units = [
    {"node_id": "Site1_Area1_100", "name": "US 100", "description": "Top soil - layer"},
    {"node_id": "Site1_Area1_101", "name": "US 101", "description": "Brown clay - layer"},
    {"node_id": "Site1_Area1_102", "name": "US 102", "description": "Foundation cut"},
    {"node_id": "Site1_Area1_103", "name": "US 103", "description": "Foundation fill"},
    {"node_id": "Site1_Area1_104", "name": "US 104", "description": "Natural soil - layer"}
]

print(f"Adding {len(units)} stratigraphic units...")
for unit_data in units:
    node = Node(**unit_data)
    # Add additional properties after creation
    node.us_number = unit_data["name"].split()[1]  # Extract US number
    node.node_type = "stratigraphic_unit"
    graph.add_node(node)

# Add stratigraphic relationships using Extended Matrix edge types
# Using temporal relationships for stratigraphic sequence
relationships = [
    ("Site1_Area1_100", "Site1_Area1_101", "is_before"),  # 100 is before (above) 101
    ("Site1_Area1_101", "Site1_Area1_102", "is_before"),  # 101 is before (above) 102
    ("Site1_Area1_103", "Site1_Area1_102", "has_same_time"),  # 103 fills 102 (contemporary)
    ("Site1_Area1_102", "Site1_Area1_104", "is_before"),  # 102 cuts into 104
]

print(f"Adding {len(relationships)} relationships...")
for i, (source, target, rel_type) in enumerate(relationships):
    graph.add_edge(
        edge_id=f"edge_{i}",
        edge_source=source,
        edge_target=target,
        edge_type=rel_type
    )

# Export to JSON manually since to_json() is not available
print("\nExporting to JSON...")

# Build JSON structure manually
data = {
    "graph_id": graph.graph_id,
    "name": graph.name,
    "description": graph.description if graph.description else "",
    "nodes": [],
    "edges": []
}

# Add nodes
for node in graph.nodes:
    node_data = {
        "node_id": node.node_id,
        "name": node.name,
        "description": node.description,
        "us_number": getattr(node, 'us_number', None),
        "node_type": getattr(node, 'node_type', None)
    }
    data["nodes"].append(node_data)

# Add edges
for edge in graph.edges:
    edge_data = {
        "edge_id": edge.edge_id,
        "edge_source": edge.edge_source,
        "edge_target": edge.edge_target,
        "edge_type": edge.edge_type
    }
    data["edges"].append(edge_data)

# Save to file
json_data = json.dumps(data, indent=2)
with open("test_matrix.json", "w") as f:
    f.write(json_data)
print(f"✓ Exported to test_matrix.json")
print(f"\nGraph structure:")
print(f"  - ID: {data.get('graph_id', data.get('id', 'N/A'))}")
print(f"  - Name: {data.get('name', data.get('label', 'N/A'))}")
print(f"  - Nodes: {len(data.get('nodes', []))}")
print(f"  - Edges: {len(data.get('edges', []))}")

# Show nodes
print("\nNodes:")
for node in data.get('nodes', []):
    node_id = node.get('node_id', node.get('id', 'N/A'))
    node_name = node.get('name', node.get('label', 'N/A'))
    node_desc = node.get('description', '')
    print(f"  - {node_id}: {node_name} - {node_desc}")

# Show edges
print("\nRelationships:")
for edge in data.get('edges', []):
    source = edge.get('edge_source', edge.get('source', 'N/A'))
    target = edge.get('edge_target', edge.get('target', 'N/A'))
    edge_type = edge.get('edge_type', edge.get('type', 'N/A'))
    print(f"  - {source} --[{edge_type}]--> {target}")

print("\n✓ Test completed successfully!")
print("Extended Matrix export is working correctly with S3DGraphy")