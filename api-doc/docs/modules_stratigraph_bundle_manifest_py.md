# modules/stratigraph/bundle_manifest.py

## Overview

This file contains 7 documented elements.

## Classes

### BundleManifest

Generates and manages the StratiGraph bundle manifest.

The manifest contains the 6 mandatory BMD fields:
1. schema_version - Version of the bundle schema
2. tool_id - Identifier of the producing tool + version
3. provenance - Who created the data and when
4. integrity_hash - SHA-256 of the bundle content
5. export_timestamp - ISO 8601 UTC timestamp
6. ontology_references - URIs of ontologies used

Plus a list of all files in the bundle with their relative paths
and individual SHA-256 hashes.

#### Methods

##### __init__(self, tool_version, user, organization, ontology_references)

Initialize the manifest.

Args:
    tool_version: PyArchInit version string (e.g. "4.9.76").
        If None, reads from metadata.txt.
    user: Username of the exporter.
    organization: Organization name.
    ontology_references: List of ontology URIs. Uses defaults if None.

##### add_file(self, filepath, relative_path)

Register a file in the manifest.

Args:
    filepath: Absolute path to the file on disk.
    relative_path: Path relative to the bundle root.
        If None, uses the filename only.

Returns:
    dict: The file entry added to the manifest.

##### generate(self)

Generate the complete manifest dict.

Computes the export timestamp and integrity hash.

Returns:
    dict: The full manifest ready for JSON serialization.

##### to_json(self, indent)

Generate the manifest and return as JSON string.

Args:
    indent: JSON indentation level.

Returns:
    str: JSON string of the manifest.

##### write(self, filepath)

Generate the manifest and write to a file.

Args:
    filepath: Path to write the manifest JSON file.

Returns:
    str: The integrity hash of the bundle.

