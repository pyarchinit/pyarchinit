# modules/stratigraph/bundle_creator.py

## Overview

This file contains 7 documented elements.

## Classes

### BundleCreator

Creates StratiGraph-compliant export bundles.

Usage:
    creator = BundleCreator(
        output_dir="/path/to/output",
        site_name="MySite",
        user="archaeologist",
        organization="University"
    )
    creator.add_data_file("/path/to/export.jsonld", "data/cidoc_crm.jsonld")
    creator.add_data_file("/path/to/export.gpkg", "data/geopackage.gpkg")
    creator.add_media_file("/path/to/photo.jpg", "media/photo_001.jpg")
    result = creator.build()
    # result = {"success": True, "bundle_path": "/path/to/bundle.zip", ...}

#### Methods

##### __init__(self, output_dir, site_name, user, organization, tool_version, ontology_references)

Initialize the bundle creator.

Args:
    output_dir: Directory where the bundle ZIP will be created.
    site_name: Name of the archaeological site (used in filename).
    user: Username of the person creating the bundle.
    organization: Organization name for provenance.
    tool_version: PyArchInit version. Auto-detected if None.
    ontology_references: List of ontology URIs for BMD.

##### add_data_file(self, source_path, relative_path)

Add a data file to the bundle.

Args:
    source_path: Absolute path to the source file.
    relative_path: Path inside the bundle (e.g. "data/export.jsonld").
        If None, places file in data/ with original filename.

Returns:
    bool: True if file exists and was added.

##### add_media_file(self, source_path, relative_path)

Add a media file (image, drawing, etc.) to the bundle.

Args:
    source_path: Absolute path to the media file.
    relative_path: Path inside the bundle (e.g. "media/photo.jpg").
        If None, places file in media/ with original filename.

Returns:
    bool: True if file exists and was added.

##### add_directory(self, source_dir, bundle_subdir, extensions)

Add all files from a directory to the bundle.

Args:
    source_dir: Absolute path to the source directory.
    bundle_subdir: Subdirectory inside the bundle. Defaults to DIR_DATA.
    extensions: Optional list of file extensions to include
        (e.g. ['.jsonld', '.gpkg']). If None, includes all files.

Returns:
    int: Number of files added.

##### build(self)

Build the bundle ZIP file.

Creates a temporary directory, copies all registered files,
generates the manifest, and compresses everything into a ZIP.

Returns:
    dict: Result with keys:
        - success (bool)
        - bundle_path (str): Path to the generated ZIP file
        - manifest_hash (str): Integrity hash from the manifest
        - file_count (int): Number of files in the bundle
        - errors (list[str])
        - warnings (list[str])
        - timestamp (str): ISO 8601 export timestamp

