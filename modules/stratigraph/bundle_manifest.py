# -*- coding: utf-8 -*-
"""
Bundle Manifest and BMD (Bundle Metadata) for StratiGraph integration.

Generates the manifest.json file required in every StratiGraph bundle.
Contains the 6 mandatory BMD fields plus the list of included files
with their individual integrity hashes.
"""

import hashlib
import json
import os
from datetime import datetime, timezone


# Current BMD schema version (placeholder until WP4 provides final spec)
BMD_SCHEMA_VERSION = "1.0-draft"

# CIDOC-CRM and related ontology URIs
DEFAULT_ONTOLOGY_REFERENCES = [
    "http://www.cidoc-crm.org/cidoc-crm/7.1.2",
    "http://www.cidoc-crm.org/extensions/crmdig/3.2.2",
    "http://pyarchinit.org/ontology/1.0",
]


def _sha256_file(filepath):
    """Compute SHA-256 hash of a file.

    Args:
        filepath: Path to the file.

    Returns:
        str: Hex-encoded SHA-256 hash.
    """
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def _sha256_bytes(data):
    """Compute SHA-256 hash of bytes data.

    Args:
        data: Bytes to hash.

    Returns:
        str: Hex-encoded SHA-256 hash.
    """
    return hashlib.sha256(data).hexdigest()


class BundleManifest:
    """Generates and manages the StratiGraph bundle manifest.

    The manifest contains the 6 mandatory BMD fields:
    1. schema_version - Version of the bundle schema
    2. tool_id - Identifier of the producing tool + version
    3. provenance - Who created the data and when
    4. integrity_hash - SHA-256 of the bundle content
    5. export_timestamp - ISO 8601 UTC timestamp
    6. ontology_references - URIs of ontologies used

    Plus a list of all files in the bundle with their relative paths
    and individual SHA-256 hashes.
    """

    def __init__(self, tool_version=None, user=None, organization=None,
                 ontology_references=None):
        """Initialize the manifest.

        Args:
            tool_version: PyArchInit version string (e.g. "4.9.76").
                If None, reads from metadata.txt.
            user: Username of the exporter.
            organization: Organization name.
            ontology_references: List of ontology URIs. Uses defaults if None.
        """
        self.tool_version = tool_version or self._detect_version()
        self.user = user or ""
        self.organization = organization or ""
        self.ontology_references = ontology_references or list(DEFAULT_ONTOLOGY_REFERENCES)
        self.files = []  # List of {path, hash, size_bytes}
        self.export_timestamp = None
        self.integrity_hash = None

    @staticmethod
    def _detect_version():
        """Try to read version from metadata.txt."""
        try:
            meta_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(
                    os.path.abspath(__file__)))),
                'metadata.txt'
            )
            with open(meta_path, 'r') as f:
                for line in f:
                    if line.startswith('version='):
                        return line.split('=', 1)[1].strip()
        except Exception:
            pass
        return "unknown"

    def add_file(self, filepath, relative_path=None):
        """Register a file in the manifest.

        Args:
            filepath: Absolute path to the file on disk.
            relative_path: Path relative to the bundle root.
                If None, uses the filename only.

        Returns:
            dict: The file entry added to the manifest.
        """
        if relative_path is None:
            relative_path = os.path.basename(filepath)

        file_hash = _sha256_file(filepath)
        size_bytes = os.path.getsize(filepath)

        entry = {
            "path": relative_path,
            "sha256": file_hash,
            "size_bytes": size_bytes,
        }
        self.files.append(entry)
        return entry

    def generate(self):
        """Generate the complete manifest dict.

        Computes the export timestamp and integrity hash.

        Returns:
            dict: The full manifest ready for JSON serialization.
        """
        self.export_timestamp = datetime.now(timezone.utc).isoformat()

        # Build manifest without integrity_hash first
        manifest = {
            "bmd": {
                "schema_version": BMD_SCHEMA_VERSION,
                "tool_id": f"pyarchinit/{self.tool_version}",
                "provenance": {
                    "user": self.user,
                    "organization": self.organization,
                    "created_at": self.export_timestamp,
                },
                "integrity_hash": "",  # placeholder
                "export_timestamp": self.export_timestamp,
                "ontology_references": self.ontology_references,
            },
            "files": self.files,
        }

        # Compute integrity hash over files section
        files_json = json.dumps(self.files, sort_keys=True).encode('utf-8')
        self.integrity_hash = _sha256_bytes(files_json)
        manifest["bmd"]["integrity_hash"] = self.integrity_hash

        return manifest

    def to_json(self, indent=2):
        """Generate the manifest and return as JSON string.

        Args:
            indent: JSON indentation level.

        Returns:
            str: JSON string of the manifest.
        """
        manifest = self.generate()
        return json.dumps(manifest, indent=indent, ensure_ascii=False)

    def write(self, filepath):
        """Generate the manifest and write to a file.

        Args:
            filepath: Path to write the manifest JSON file.

        Returns:
            str: The integrity hash of the bundle.
        """
        content = self.to_json()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return self.integrity_hash
