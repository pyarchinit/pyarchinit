#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test inverse relationship handling
"""

import json
from modules.s3dgraphy.plotly_visualizer import PlotlyMatrixVisualizer

# Create test data with inverse relationships
test_matrix = {
    "graph_id": "test_inverse",
    "name": "Test Inverse Relationships",
    "nodes": [
        {"node_id": "US1", "name": "US 1", "unita_tipo": "US"},
        {"node_id": "US2", "name": "US 2", "unita_tipo": "US"},
        {"node_id": "US3", "name": "US 3", "unita_tipo": "US"},
        {"node_id": "US4", "name": "US 4", "unita_tipo": "US"},
        {"node_id": "US5", "name": "US 5", "unita_tipo": "US"},
    ],
    "edges": [
        # US1 is covered by US2 (US2 is above US1)
        # This should be: US2 -> US1 with "is_before"
        {"edge_source": "US2", "edge_target": "US1", "edge_type": "is_before"},

        # US2 covers US3 (US2 is above US3)
        # This should be: US2 -> US3 with "is_before"
        {"edge_source": "US2", "edge_target": "US3", "edge_type": "is_before"},

        # US3 covers US5 (US3 is above US5) - This will make US5 level 2
        # This should be: US3 -> US5 with "is_before"
        {"edge_source": "US3", "edge_target": "US5", "edge_type": "is_before"},

        # US4 is contemporary with US2 (both at top level)
        # This should be: US4 and US2 at same level
        {"edge_source": "US4", "edge_target": "US2", "edge_type": "has_same_time"},
    ]
}

print("=" * 60)
print("Testing Inverse Relationship Handling")
print("=" * 60)

# Create visualizer
visualizer = PlotlyMatrixVisualizer(qgis_integration=False)

# Calculate levels internally (the method is private but we need to test it)
print("\nCalculating hierarchical levels...")
# The _calculate_levels is a private method but we need to test it
visualizer._calculate_levels(test_matrix)

print("\nExpected hierarchy:")
print("Level 0 (most recent): US2, US4 (contemporary)")
print("Level 1: US1, US3")
print("Level 2 (oldest): US5")

print("\nActual calculated levels (from self.levels):")
# Group by level
level_nodes = {}
for node_id, level in visualizer.levels.items():
    if level not in level_nodes:
        level_nodes[level] = []
    level_nodes[level].append(node_id)

for level in sorted(level_nodes.keys()):
    print(f"Level {level}: {', '.join(sorted(level_nodes[level]))}")

# Generate interactive graph
output_path = 'test_inverse_relationships.html'
print(f"\nGenerating interactive graph to: {output_path}")

success = visualizer.create_interactive_graph(test_matrix, output_path)

if success:
    print(f"\n✅ Graph created successfully!")
    print("Expected to see:")
    print("- US2 and US4 at the top (most recent)")
    print("- US1 and US3 in the middle")
    print("- US5 at the bottom (oldest)")
else:
    print("\n❌ Failed to create graph")

print("\nTest complete")