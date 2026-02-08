# -*- coding: utf-8 -*-
"""
Bundle Creator for StratiGraph integration.

Creates standardized StratiGraph bundle ZIP files containing:
- Archaeological data exports (JSON-LD, GeoPackage, CSV)
- Media files (images, drawings)
- Bundle manifest with BMD metadata
- Integrity hashes for all included files

A bundle is a self-contained, validated package ready for
synchronization with the StratiGraph Knowledge Graph.
"""

import os
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone

from modules.stratigraph.bundle_manifest import BundleManifest


class BundleCreator:
    """Creates StratiGraph-compliant export bundles.

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
    """

    # Standard directory structure inside the bundle
    DIR_DATA = "data"
    DIR_METADATA = "metadata"
    DIR_MEDIA = "media"

    def __init__(self, output_dir, site_name=None, user=None,
                 organization=None, tool_version=None,
                 ontology_references=None):
        """Initialize the bundle creator.

        Args:
            output_dir: Directory where the bundle ZIP will be created.
            site_name: Name of the archaeological site (used in filename).
            user: Username of the person creating the bundle.
            organization: Organization name for provenance.
            tool_version: PyArchInit version. Auto-detected if None.
            ontology_references: List of ontology URIs for BMD.
        """
        self.output_dir = output_dir
        self.site_name = site_name or "unknown_site"
        self.user = user or ""
        self.organization = organization or ""
        self.tool_version = tool_version
        self.ontology_references = ontology_references

        # Files to include: list of (source_path, bundle_relative_path)
        self._files = []
        self._errors = []
        self._warnings = []

    def add_data_file(self, source_path, relative_path=None):
        """Add a data file to the bundle.

        Args:
            source_path: Absolute path to the source file.
            relative_path: Path inside the bundle (e.g. "data/export.jsonld").
                If None, places file in data/ with original filename.

        Returns:
            bool: True if file exists and was added.
        """
        if not os.path.isfile(source_path):
            self._errors.append(f"Data file not found: {source_path}")
            return False

        if relative_path is None:
            relative_path = f"{self.DIR_DATA}/{os.path.basename(source_path)}"

        self._files.append((source_path, relative_path))
        return True

    def add_media_file(self, source_path, relative_path=None):
        """Add a media file (image, drawing, etc.) to the bundle.

        Args:
            source_path: Absolute path to the media file.
            relative_path: Path inside the bundle (e.g. "media/photo.jpg").
                If None, places file in media/ with original filename.

        Returns:
            bool: True if file exists and was added.
        """
        if not os.path.isfile(source_path):
            self._warnings.append(f"Media file not found: {source_path}")
            return False

        if relative_path is None:
            relative_path = f"{self.DIR_MEDIA}/{os.path.basename(source_path)}"

        self._files.append((source_path, relative_path))
        return True

    def add_directory(self, source_dir, bundle_subdir=None, extensions=None):
        """Add all files from a directory to the bundle.

        Args:
            source_dir: Absolute path to the source directory.
            bundle_subdir: Subdirectory inside the bundle. Defaults to DIR_DATA.
            extensions: Optional list of file extensions to include
                (e.g. ['.jsonld', '.gpkg']). If None, includes all files.

        Returns:
            int: Number of files added.
        """
        if not os.path.isdir(source_dir):
            self._errors.append(f"Directory not found: {source_dir}")
            return 0

        if bundle_subdir is None:
            bundle_subdir = self.DIR_DATA

        count = 0
        for root, _dirs, files in os.walk(source_dir):
            for filename in files:
                if extensions and not any(filename.endswith(ext) for ext in extensions):
                    continue
                source_path = os.path.join(root, filename)
                rel_from_source = os.path.relpath(source_path, source_dir)
                bundle_path = f"{bundle_subdir}/{rel_from_source}"
                self._files.append((source_path, bundle_path))
                count += 1

        return count

    def build(self):
        """Build the bundle ZIP file.

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
        """
        result = {
            "success": False,
            "bundle_path": None,
            "manifest_hash": None,
            "file_count": 0,
            "errors": list(self._errors),
            "warnings": list(self._warnings),
            "timestamp": None,
        }

        if not self._files:
            result["errors"].append("No files added to the bundle")
            return result

        # Check for pre-existing errors
        if result["errors"]:
            return result

        # Create output directory if needed
        os.makedirs(self.output_dir, exist_ok=True)

        # Generate bundle filename
        timestamp = datetime.now(timezone.utc)
        ts_str = timestamp.strftime("%Y%m%dT%H%M%SZ")
        safe_site = self.site_name.replace(" ", "_").replace("/", "_")
        bundle_filename = f"stratigraph_bundle_{safe_site}_{ts_str}.zip"
        bundle_path = os.path.join(self.output_dir, bundle_filename)

        # Work in a temp directory
        tmp_dir = tempfile.mkdtemp(prefix="stratigraph_bundle_")
        try:
            # Create bundle directory structure
            for subdir in [self.DIR_DATA, self.DIR_METADATA, self.DIR_MEDIA]:
                os.makedirs(os.path.join(tmp_dir, subdir), exist_ok=True)

            # Initialize manifest
            manifest = BundleManifest(
                tool_version=self.tool_version,
                user=self.user,
                organization=self.organization,
                ontology_references=self.ontology_references,
            )

            # Copy files and register in manifest
            for source_path, rel_path in self._files:
                dest_path = os.path.join(tmp_dir, rel_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(source_path, dest_path)
                manifest.add_file(dest_path, rel_path)

            # Write manifest
            manifest_path = os.path.join(tmp_dir, self.DIR_METADATA, "manifest.json")
            integrity_hash = manifest.write(manifest_path)

            # Create ZIP
            with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, _dirs, files in os.walk(tmp_dir):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        arcname = os.path.relpath(file_path, tmp_dir)
                        zf.write(file_path, arcname)

            result["success"] = True
            result["bundle_path"] = bundle_path
            result["manifest_hash"] = integrity_hash
            result["file_count"] = len(self._files) + 1  # +1 for manifest
            result["timestamp"] = manifest.export_timestamp

        except Exception as e:
            result["errors"].append(f"Bundle creation failed: {e}")
        finally:
            # Clean up temp directory
            shutil.rmtree(tmp_dir, ignore_errors=True)

        return result
