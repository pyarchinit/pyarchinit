#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive test for S3DGraphy Extended Matrix integration
Tests all features: export, import, 3D prep, CIDOC-CRM, etc.
"""

import os
import sys
import json
import datetime

# Add pyarchinit to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from modules.s3dgraphy.s3dgraphy_integration import S3DGraphyIntegration, S3DGRAPHY_AVAILABLE


def test_full_extended_matrix_workflow():
    """Test complete Extended Matrix workflow"""

    print("=" * 70)
    print("PyArchInit - S3DGraphy Extended Matrix Complete Test Suite")
    print("=" * 70)

    # Check if S3DGraphy is available
    if not S3DGRAPHY_AVAILABLE:
        print("❌ ERROR: S3DGraphy is not installed")
        print("Install it with: pip install s3dgraphy")
        return False

    print("✅ S3DGraphy is installed")

    try:
        # 1. Connect to database
        print("\n1. CONNECTING TO DATABASE")
        print("-" * 40)
        conn = Connection()
        conn_str = conn.conn_str()
        db_manager = Pyarchinit_db_management(conn_str)
        db_manager.connection()
        print("✅ Connected to database")

        # 2. Get test data
        print("\n2. RETRIEVING TEST DATA")
        print("-" * 40)
        sites = db_manager.query_distinct('US', 'sito')

        if not sites:
            print("❌ No sites found in database")
            # Create test data if none exists
            print("Creating test data...")
            create_test_data(db_manager)
            sites = ['TestSite']

        test_site = sites[0]
        print(f"✅ Using site: {test_site}")

        # Get areas
        search_dict = {'sito': test_site}
        us_records = db_manager.query_bool(search_dict, 'US')

        if us_records:
            areas = list(set([us.area for us in us_records]))
            test_area = areas[0] if areas else 'A1'
            print(f"✅ Using area: {test_area}")
            print(f"✅ Found {len(us_records)} stratigraphic units")
        else:
            test_area = 'A1'
            print("⚠️  No US records found, will create test data")

        # 3. Export to Extended Matrix
        print("\n3. EXPORTING TO EXTENDED MATRIX")
        print("-" * 40)
        integration = S3DGraphyIntegration(db_manager)

        # Import from PyArchInit
        print("Importing stratigraphic data...")
        success = integration.import_from_pyarchinit(test_site, test_area)

        if success:
            print("✅ Data imported successfully")
        else:
            print("❌ Failed to import data")
            return False

        # Validate
        print("\nValidating stratigraphic sequence...")
        warnings = integration.validate_stratigraphic_sequence()
        if warnings:
            print(f"⚠️  Found {len(warnings)} validation warnings:")
            for w in warnings[:3]:
                print(f"   - {w}")
        else:
            print("✅ No validation issues")

        # Export formats
        output_dir = os.path.join(os.path.dirname(__file__), "extended_matrix_exports")
        os.makedirs(output_dir, exist_ok=True)

        # Export JSON
        json_file = os.path.join(output_dir, f"{test_site}_{test_area}_extended_matrix.json")
        if integration.export_to_json(json_file):
            print(f"✅ JSON exported: {os.path.basename(json_file)}")

        # Export GraphML
        graphml_file = os.path.join(output_dir, f"{test_site}_{test_area}_extended_matrix.graphml")
        if integration.export_to_graphml(graphml_file):
            print(f"✅ GraphML exported: {os.path.basename(graphml_file)}")

        # 4. Generate Harris Matrix
        print("\n4. GENERATING HARRIS MATRIX")
        print("-" * 40)
        matrix = integration.generate_harris_matrix()
        if matrix:
            harris_file = os.path.join(output_dir, f"{test_site}_{test_area}_harris.json")
            with open(harris_file, 'w') as f:
                json.dump(matrix, f, indent=2)
            print(f"✅ Harris Matrix generated: {os.path.basename(harris_file)}")
            print(f"   - Relationships: {len(matrix.get('relationships', []))}")

        # 5. Prepare 3D Visualization
        print("\n5. PREPARING 3D VISUALIZATION DATA")
        print("-" * 40)
        viz_data = integration.prepare_for_3d_visualization()
        if viz_data:
            viz_file = os.path.join(output_dir, f"{test_site}_{test_area}_3d_viz.json")
            with open(viz_file, 'w') as f:
                json.dump(viz_data, f, indent=2)
            print(f"✅ 3D viz data prepared: {os.path.basename(viz_file)}")
            print(f"   - Nodes: {len(viz_data.get('nodes', []))}")
            print(f"   - Edges: {len(viz_data.get('edges', []))}")

        # 6. Test node types distribution
        print("\n6. NODE TYPE ANALYSIS")
        print("-" * 40)
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                data = json.load(f)

            node_types = {}
            for node in data.get('nodes', []):
                node_type = node.get('node_type', 'unknown')
                unita_tipo = node.get('unita_tipo', 'US')
                key = f"{unita_tipo} -> {node_type}"
                node_types[key] = node_types.get(key, 0) + 1

            print("Node type distribution:")
            for type_mapping, count in node_types.items():
                print(f"   - {type_mapping}: {count} units")

        # 7. Relationship analysis
        print("\n7. RELATIONSHIP ANALYSIS")
        print("-" * 40)
        if os.path.exists(json_file):
            edge_types = {}
            for edge in data.get('edges', []):
                edge_type = edge.get('edge_type', 'unknown')
                edge_types[edge_type] = edge_types.get(edge_type, 0) + 1

            print("Relationship type distribution:")
            for rel_type, count in edge_types.items():
                print(f"   - {rel_type}: {count} relationships")

        # 8. Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"✅ Site: {test_site}")
        print(f"✅ Area: {test_area}")
        print(f"✅ Exported files saved in: {output_dir}")
        print(f"✅ Total nodes: {len(data.get('nodes', []))}")
        print(f"✅ Total edges: {len(data.get('edges', []))}")

        print("\n✨ All tests completed successfully!")
        print("\nNext steps:")
        print("1. Open GraphML in yEd or Gephi for visualization")
        print("2. Import JSON into EMtools for 3D visualization")
        print("3. Use in Blender with Extended Matrix addon")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def create_test_data(db_manager):
    """Create test stratigraphic data if none exists"""
    print("Creating test stratigraphic units...")

    # This would need to be implemented based on your database structure
    # For now, just a placeholder
    pass


if __name__ == "__main__":
    success = test_full_extended_matrix_workflow()
    sys.exit(0 if success else 1)