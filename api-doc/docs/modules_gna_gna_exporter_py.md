# modules/gna/gna_exporter.py

## Overview

This file contains 5 documented elements.

## Classes

### GNAExporter

Exports PyArchInit UT data to GNA-compliant GeoPackage.

Usage:
    exporter = GNAExporter(db_manager, 'ProjectName', '/path/output.gpkg')
    result = exporter.export(project_polygon, ut_records, options)

#### Methods

##### __init__(self, db_manager, project_name, output_path, crs, language)

Initialize GNA exporter.

Args:
    db_manager: PyArchInit database manager
    project_name: Name of the project (used for CPR code)
    output_path: Path for output GeoPackage file
    crs: QgsCoordinateReferenceSystem (default WGS84)
    language: Language code for translations

##### export(self, project_polygon, ut_records, options)

Export UT data to GNA GeoPackage.

Args:
    project_polygon: QgsGeometry of project area (MOPR)
    ut_records: List of UT database records to export
    options: Dict with export options:
        - generate_mosi: bool (default True)
        - generate_vrp: bool (default True)
        - generate_vrd: bool (default True)
        - heatmap_method: 'kde', 'idw', or 'grid' (default 'kde')
        - cell_size: int (default 50)
        - project_info: dict with title, responsible, dates, etc.
        - geometries: dict mapping record IDs to QgsGeometry

Returns:
    Dict with:
        - success: bool
        - gpkg_path: output file path
        - layers: list of created layer names
        - record_count: number of records exported
        - errors: list of error messages
        - warnings: list of warning messages

##### validate_geopackage(gpkg_path)

Validate a GNA GeoPackage for completeness.

Args:
    gpkg_path: Path to GeoPackage file

Returns:
    Dict with validation results

