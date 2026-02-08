# -*- coding: utf-8 -*-
"""
Bundle Validator for StratiGraph integration.

Validates a StratiGraph bundle before export or sync, checking:
- BMD metadata completeness and correctness
- File integrity (all files in manifest exist, hashes match)
- UUID consistency (no missing or duplicate UUIDs)
- Ontology reference validity

Produces a validation report with ERROR and WARNING levels.
"""

import hashlib
import json
import os
import zipfile

from modules.stratigraph.uuid_manager import validate_uuid


class ValidationLevel:
    """Validation result severity levels."""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class ValidationResult:
    """Single validation check result.

    Attributes:
        level: ValidationLevel (ERROR, WARNING, INFO)
        code: Machine-readable code (e.g. "BMD_MISSING_FIELD")
        message: Human-readable description
        context: Optional dict with additional details
    """

    def __init__(self, level, code, message, context=None):
        self.level = level
        self.code = code
        self.message = message
        self.context = context or {}

    def __repr__(self):
        return f"[{self.level}] {self.code}: {self.message}"

    def to_dict(self):
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "context": self.context,
        }


# Required BMD fields
BMD_REQUIRED_FIELDS = [
    "schema_version",
    "tool_id",
    "provenance",
    "integrity_hash",
    "export_timestamp",
    "ontology_references",
]

# Required provenance sub-fields
PROVENANCE_REQUIRED_FIELDS = ["user", "created_at"]


def _sha256_file(filepath):
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


class BundleValidator:
    """Validates StratiGraph bundle contents and metadata.

    Usage:
        validator = BundleValidator()

        # Validate a bundle directory (before zipping)
        results = validator.validate_directory("/path/to/bundle_dir")

        # Or validate a ZIP file
        results = validator.validate_zip("/path/to/bundle.zip")

        # Check results
        errors = [r for r in results if r.level == ValidationLevel.ERROR]
        if errors:
            print("Bundle has errors, cannot sync")
    """

    def validate_directory(self, bundle_dir):
        """Validate a bundle directory.

        Args:
            bundle_dir: Path to the unzipped bundle directory.

        Returns:
            list[ValidationResult]: All validation results.
        """
        results = []

        # Check directory exists
        if not os.path.isdir(bundle_dir):
            results.append(ValidationResult(
                ValidationLevel.ERROR, "BUNDLE_DIR_NOT_FOUND",
                f"Bundle directory not found: {bundle_dir}"
            ))
            return results

        # Check manifest exists
        manifest_path = os.path.join(bundle_dir, "metadata", "manifest.json")
        if not os.path.isfile(manifest_path):
            results.append(ValidationResult(
                ValidationLevel.ERROR, "MANIFEST_NOT_FOUND",
                "manifest.json not found in metadata/"
            ))
            return results

        # Load manifest
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            results.append(ValidationResult(
                ValidationLevel.ERROR, "MANIFEST_PARSE_ERROR",
                f"Cannot parse manifest.json: {e}"
            ))
            return results

        # Validate BMD
        results.extend(self._validate_bmd(manifest))

        # Validate files
        results.extend(self._validate_files(manifest, bundle_dir))

        # Validate UUIDs in data files
        results.extend(self._validate_uuids(bundle_dir))

        return results

    def validate_zip(self, zip_path):
        """Validate a bundle ZIP file.

        Extracts to a temp directory and validates.

        Args:
            zip_path: Path to the bundle ZIP file.

        Returns:
            list[ValidationResult]: All validation results.
        """
        import tempfile
        import shutil

        results = []

        if not os.path.isfile(zip_path):
            results.append(ValidationResult(
                ValidationLevel.ERROR, "ZIP_NOT_FOUND",
                f"Bundle ZIP not found: {zip_path}"
            ))
            return results

        if not zipfile.is_zipfile(zip_path):
            results.append(ValidationResult(
                ValidationLevel.ERROR, "ZIP_INVALID",
                f"File is not a valid ZIP: {zip_path}"
            ))
            return results

        tmp_dir = tempfile.mkdtemp(prefix="bundle_validate_")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(tmp_dir)
            results = self.validate_directory(tmp_dir)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        return results

    def _validate_bmd(self, manifest):
        """Validate the 6 mandatory BMD fields.

        Args:
            manifest: Parsed manifest dict.

        Returns:
            list[ValidationResult]: BMD validation results.
        """
        results = []

        bmd = manifest.get("bmd")
        if not bmd:
            results.append(ValidationResult(
                ValidationLevel.ERROR, "BMD_MISSING",
                "Manifest has no 'bmd' section"
            ))
            return results

        # Check required fields
        for field in BMD_REQUIRED_FIELDS:
            if field not in bmd or bmd[field] is None:
                results.append(ValidationResult(
                    ValidationLevel.ERROR, "BMD_MISSING_FIELD",
                    f"Required BMD field missing: {field}",
                    {"field": field}
                ))
            elif isinstance(bmd[field], str) and not bmd[field].strip():
                results.append(ValidationResult(
                    ValidationLevel.ERROR, "BMD_EMPTY_FIELD",
                    f"Required BMD field is empty: {field}",
                    {"field": field}
                ))

        # Validate schema_version format
        sv = bmd.get("schema_version", "")
        if sv and not any(c.isdigit() for c in sv):
            results.append(ValidationResult(
                ValidationLevel.WARNING, "BMD_SCHEMA_VERSION_FORMAT",
                f"schema_version has unexpected format: {sv}"
            ))

        # Validate tool_id
        tool_id = bmd.get("tool_id", "")
        if tool_id and not tool_id.startswith("pyarchinit"):
            results.append(ValidationResult(
                ValidationLevel.WARNING, "BMD_TOOL_ID_UNEXPECTED",
                f"tool_id does not start with 'pyarchinit': {tool_id}"
            ))

        # Validate provenance
        provenance = bmd.get("provenance")
        if isinstance(provenance, dict):
            for field in PROVENANCE_REQUIRED_FIELDS:
                if field not in provenance or not provenance[field]:
                    results.append(ValidationResult(
                        ValidationLevel.WARNING, "BMD_PROVENANCE_INCOMPLETE",
                        f"Provenance field missing or empty: {field}",
                        {"field": field}
                    ))
        elif provenance is not None:
            results.append(ValidationResult(
                ValidationLevel.ERROR, "BMD_PROVENANCE_TYPE",
                "Provenance must be a dict"
            ))

        # Validate integrity_hash format (SHA-256 = 64 hex chars)
        ih = bmd.get("integrity_hash", "")
        if ih and (len(ih) != 64 or not all(c in '0123456789abcdef' for c in ih.lower())):
            results.append(ValidationResult(
                ValidationLevel.ERROR, "BMD_HASH_FORMAT",
                f"integrity_hash is not a valid SHA-256: {ih[:20]}..."
            ))

        # Validate ontology_references
        onto_refs = bmd.get("ontology_references")
        if isinstance(onto_refs, list):
            if not onto_refs:
                results.append(ValidationResult(
                    ValidationLevel.WARNING, "BMD_NO_ONTOLOGIES",
                    "ontology_references list is empty"
                ))
            for ref in onto_refs:
                if not isinstance(ref, str) or not ref.startswith("http"):
                    results.append(ValidationResult(
                        ValidationLevel.WARNING, "BMD_ONTOLOGY_FORMAT",
                        f"Ontology reference is not a valid URI: {ref}",
                        {"uri": ref}
                    ))
        elif onto_refs is not None:
            results.append(ValidationResult(
                ValidationLevel.ERROR, "BMD_ONTOLOGIES_TYPE",
                "ontology_references must be a list"
            ))

        return results

    def _validate_files(self, manifest, bundle_dir):
        """Validate that all files in the manifest exist and have correct hashes.

        Args:
            manifest: Parsed manifest dict.
            bundle_dir: Path to the bundle directory.

        Returns:
            list[ValidationResult]: File validation results.
        """
        results = []

        files = manifest.get("files", [])
        if not files:
            results.append(ValidationResult(
                ValidationLevel.WARNING, "NO_FILES",
                "Manifest contains no file entries"
            ))
            return results

        for entry in files:
            rel_path = entry.get("path", "")
            expected_hash = entry.get("sha256", "")

            if not rel_path:
                results.append(ValidationResult(
                    ValidationLevel.ERROR, "FILE_NO_PATH",
                    "File entry has no path"
                ))
                continue

            full_path = os.path.join(bundle_dir, rel_path)

            # Check file exists
            if not os.path.isfile(full_path):
                results.append(ValidationResult(
                    ValidationLevel.ERROR, "FILE_MISSING",
                    f"File listed in manifest not found: {rel_path}",
                    {"path": rel_path}
                ))
                continue

            # Check hash if provided
            if expected_hash:
                actual_hash = _sha256_file(full_path)
                if actual_hash != expected_hash:
                    results.append(ValidationResult(
                        ValidationLevel.ERROR, "FILE_HASH_MISMATCH",
                        f"Hash mismatch for {rel_path}",
                        {"path": rel_path,
                         "expected": expected_hash,
                         "actual": actual_hash}
                    ))

        return results

    def _validate_uuids(self, bundle_dir):
        """Validate UUID consistency in JSON-LD data files.

        Checks that entity_uuid fields are present, valid, and unique.

        Args:
            bundle_dir: Path to the bundle directory.

        Returns:
            list[ValidationResult]: UUID validation results.
        """
        results = []
        seen_uuids = set()

        data_dir = os.path.join(bundle_dir, "data")
        if not os.path.isdir(data_dir):
            return results

        for filename in os.listdir(data_dir):
            if not filename.endswith('.jsonld') and not filename.endswith('.json'):
                continue

            filepath = os.path.join(data_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

            # Walk the JSON structure looking for entity_uuid fields
            uuids_in_file = self._extract_uuids(data)

            for uid, context in uuids_in_file:
                if not validate_uuid(uid):
                    results.append(ValidationResult(
                        ValidationLevel.ERROR, "UUID_INVALID_FORMAT",
                        f"Invalid UUID format in {filename}: {uid}",
                        {"file": filename, "uuid": uid, "context": context}
                    ))
                elif uid in seen_uuids:
                    results.append(ValidationResult(
                        ValidationLevel.ERROR, "UUID_DUPLICATE",
                        f"Duplicate UUID in {filename}: {uid}",
                        {"file": filename, "uuid": uid}
                    ))
                else:
                    seen_uuids.add(uid)

        return results

    def _extract_uuids(self, data, path=""):
        """Recursively extract entity_uuid values from a JSON structure.

        Args:
            data: JSON-parsed data (dict, list, or primitive).
            path: Current JSON path for context.

        Returns:
            list[tuple]: List of (uuid_string, json_path) pairs.
        """
        uuids = []

        if isinstance(data, dict):
            if "entity_uuid" in data:
                val = data["entity_uuid"]
                if isinstance(val, str) and val:
                    uuids.append((val, path))
            for key, value in data.items():
                uuids.extend(self._extract_uuids(value, f"{path}.{key}"))

        elif isinstance(data, list):
            for i, item in enumerate(data):
                uuids.extend(self._extract_uuids(item, f"{path}[{i}]"))

        return uuids


def validate_bundle(bundle_path):
    """Convenience function to validate a bundle.

    Args:
        bundle_path: Path to a bundle ZIP file or directory.

    Returns:
        dict: Validation summary with keys:
            - valid (bool): True if no errors
            - errors (list[dict]): Error results
            - warnings (list[dict]): Warning results
            - info (list[dict]): Info results
            - total_checks (int): Total number of checks performed
    """
    validator = BundleValidator()

    if os.path.isdir(bundle_path):
        results = validator.validate_directory(bundle_path)
    else:
        results = validator.validate_zip(bundle_path)

    errors = [r.to_dict() for r in results if r.level == ValidationLevel.ERROR]
    warnings = [r.to_dict() for r in results if r.level == ValidationLevel.WARNING]
    info = [r.to_dict() for r in results if r.level == ValidationLevel.INFO]

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "total_checks": len(results),
    }
