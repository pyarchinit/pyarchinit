#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Extended Matrix export with real PyArchInit data
"""

import os
import sys
import json
from pathlib import Path

# Add the plugin path
plugin_path = Path(__file__).parent
sys.path.insert(0, str(plugin_path))

from modules.s3dgraphy.s3dgraphy_integration import S3DGraphyIntegration
from modules.s3dgraphy.graphviz_visualizer import GraphvizVisualizer

# Test with real data
print("=" * 60)
print("Testing Extended Matrix with real PyArchInit data")
print("=" * 60)

try:
    # Create integration instance
    integration = S3DGraphyIntegration()

    # Create test US data similar to what PyArchInit would have
    # This simulates what comes from the database
    us_data = [
        {'sito': 'Site1', 'area': 'A1', 'us': 100, 'unita_tipo': 'US', 'd_stratigrafica': 'Top layer soil'},
        {'sito': 'Site1', 'area': 'A1', 'us': 101, 'unita_tipo': 'US', 'd_stratigrafica': 'Fill layer'},
        {'sito': 'Site1', 'area': 'A1', 'us': 102, 'unita_tipo': 'USM', 'd_stratigrafica': 'Wall structure'},
        {'sito': 'Site1', 'area': 'A1', 'us': 103, 'unita_tipo': 'US', 'd_stratigrafica': 'Foundation cut'},
        {'sito': 'Site1', 'area': 'A1', 'us': 104, 'unita_tipo': 'USF', 'd_stratigrafica': 'Pit feature'},
        {'sito': 'Site1', 'area': 'A1', 'us': 105, 'unita_tipo': 'US', 'd_stratigrafica': 'Natural soil'},
    ]

    # Create relationships
    rapporti_data = [
        {'sito': 'Site1', 'area': 'A1', 'us': 100, 'rapporto': 'copre', 'us_r': 101},
        {'sito': 'Site1', 'area': 'A1', 'us': 100, 'rapporto': 'copre', 'us_r': 102},
        {'sito': 'Site1', 'area': 'A1', 'us': 101, 'rapporto': 'riempie', 'us_r': 104},
        {'sito': 'Site1', 'area': 'A1', 'us': 102, 'rapporto': 'si appoggia a', 'us_r': 103},
        {'sito': 'Site1', 'area': 'A1', 'us': 103, 'rapporto': 'taglia', 'us_r': 105},
        {'sito': 'Site1', 'area': 'A1', 'us': 104, 'rapporto': 'taglia', 'us_r': 105},
    ]

    print("\nProcessing US data:")
    print(f"  {len(us_data)} units")
    print(f"  {len(rapporti_data)} relationships")

    # Convert to Extended Matrix
    # The export method needs database access, so let's create the matrix directly
    matrix = integration.export_to_extended_matrix('Site1', 'A1', us_data=us_data, rapporti_data=rapporti_data)

    if matrix:
        # Save as JSON
        output_json = os.path.expanduser('~/Desktop/test_real_export.json')
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(matrix, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Extended Matrix saved to: {output_json}")

        # Print summary
        print("\nExtended Matrix summary:")
        print(f"  Nodes: {len(matrix.get('nodes', []))}")
        print(f"  Edges: {len(matrix.get('edges', []))}")

        # Show some edges
        edges = matrix.get('edges', [])[:5]
        print("\nFirst few edges:")
        for edge in edges:
            print(f"  {edge.get('edge_source')} -> {edge.get('edge_target')} ({edge.get('edge_type')})")

        # Create visualization
        print("\nCreating graph visualization...")
        visualizer = GraphvizVisualizer()
        output_png = os.path.expanduser('~/Desktop/test_real_export.png')
        success = visualizer.create_graph_image(matrix, output_png)

        if success:
            print(f"✅ Graph saved to: {output_png}")
        else:
            print("❌ Failed to create graph")
    else:
        print("\n❌ Failed to create Extended Matrix")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nTest complete")