#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for S3DGraphy Extended Matrix export
"""

import os
import sys
import json

# Add pyarchinit to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from modules.s3dgraphy.s3dgraphy_integration import S3DGraphyIntegration, S3DGRAPHY_AVAILABLE

def test_extended_matrix_export():
    """Test Extended Matrix export with real database data"""

    print("=" * 60)
    print("Testing S3DGraphy Extended Matrix Export")
    print("=" * 60)

    # Check if S3DGraphy is available
    if not S3DGRAPHY_AVAILABLE:
        print("ERROR: S3DGraphy is not installed")
        print("Install it with: pip install s3dgraphy")
        return False

    print("✓ S3DGraphy is installed")

    try:
        # Connect to database
        print("\nConnecting to database...")
        conn = Connection()
        conn_str = conn.conn_str()
        db_manager = Pyarchinit_db_management(conn_str)
        db_manager.connection()
        print("✓ Connected to database")

        # Get available sites
        print("\nQuerying available sites...")
        sites = db_manager.query_distinct('US', 'sito')

        if not sites:
            print("No sites found in database")
            return False

        print(f"Found {len(sites)} site(s):")
        for i, site in enumerate(sites[:5]):  # Show first 5 sites
            print(f"  {i+1}. {site}")

        # Use first site for testing
        test_site = sites[0]
        print(f"\nUsing site: {test_site}")

        # Get areas for this site
        search_dict = {'sito': test_site}
        us_records = db_manager.query_bool(search_dict, 'US')

        if not us_records:
            print(f"No US records found for site {test_site}")
            return False

        # Get unique areas
        areas = list(set([us.area for us in us_records]))
        print(f"Found {len(areas)} area(s): {', '.join(areas[:5])}")

        test_area = areas[0] if areas else None
        print(f"Using area: {test_area}")

        # Create S3DGraphy integration
        print("\nInitializing S3DGraphy integration...")
        integration = S3DGraphyIntegration(db_manager)

        # Import from PyArchInit
        print(f"Importing data from site '{test_site}', area '{test_area}'...")
        success = integration.import_from_pyarchinit(test_site, test_area)

        if not success:
            print("ERROR: Failed to import data")
            return False

        print("✓ Data imported successfully")

        # Validate stratigraphic sequence
        print("\nValidating stratigraphic sequence...")
        warnings = integration.validate_stratigraphic_sequence()

        if warnings:
            print(f"Found {len(warnings)} validation warning(s):")
            for warning in warnings[:5]:  # Show first 5 warnings
                print(f"  ⚠ {warning}")
        else:
            print("✓ No validation warnings")

        # Export to Extended Matrix formats
        output_dir = os.path.join(os.path.dirname(__file__), "pyarchinit_Extended_Matrix_exports")
        os.makedirs(output_dir, exist_ok=True)

        # Export to GraphML
        graphml_file = os.path.join(output_dir, f"{test_site}_{test_area}_extended_matrix.graphml")
        print(f"\nExporting to GraphML: {graphml_file}")
        success = integration.export_to_graphml(graphml_file)

        if success and os.path.exists(graphml_file):
            print(f"✓ GraphML exported ({os.path.getsize(graphml_file)} bytes)")
        else:
            print("ERROR: GraphML export failed")

        # Export to JSON
        json_file = os.path.join(output_dir, f"{test_site}_{test_area}_extended_matrix.json")
        print(f"Exporting to JSON: {json_file}")
        success = integration.export_to_json(json_file)

        if success and os.path.exists(json_file):
            print(f"✓ JSON exported ({os.path.getsize(json_file)} bytes)")

            # Show sample of JSON structure
            with open(json_file, 'r') as f:
                data = json.load(f)
                print("\nJSON structure sample:")
                if 'nodes' in data:
                    print(f"  - Nodes: {len(data.get('nodes', []))}")
                if 'edges' in data:
                    print(f"  - Edges: {len(data.get('edges', []))}")
                if 'metadata' in data:
                    print(f"  - Metadata: {data.get('metadata', {})}")
        else:
            print("ERROR: JSON export failed")

        # Generate Harris Matrix
        print("\nGenerating Harris Matrix...")
        matrix = integration.generate_harris_matrix()

        if matrix:
            harris_file = os.path.join(output_dir, f"{test_site}_{test_area}_harris_matrix.json")
            with open(harris_file, 'w') as f:
                json.dump(matrix, f, indent=2)
            print(f"✓ Harris Matrix generated: {harris_file}")
        else:
            print("⚠ Harris Matrix generation not available (may need additional configuration)")

        # Prepare 3D visualization data
        print("\nPreparing 3D visualization data...")
        viz_data = integration.prepare_for_3d_visualization()

        if viz_data:
            viz_file = os.path.join(output_dir, f"{test_site}_{test_area}_3d_viz.json")
            with open(viz_file, 'w') as f:
                json.dump(viz_data, f, indent=2)
            print(f"✓ 3D visualization data prepared: {viz_file}")
            print(f"  - Nodes: {len(viz_data.get('nodes', []))}")
            print(f"  - Edges: {len(viz_data.get('edges', []))}")
        else:
            print("⚠ 3D visualization data not available")

        print("\n" + "=" * 60)
        print("Test completed successfully!")
        print(f"Exports saved in: {output_dir}")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_extended_matrix_export()
    sys.exit(0 if success else 1)