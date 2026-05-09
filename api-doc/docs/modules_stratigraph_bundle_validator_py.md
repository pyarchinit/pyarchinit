# modules/stratigraph/bundle_validator.py

## Overview

This file contains 10 documented elements.

## Classes

### ValidationLevel

Validation result severity levels.

### ValidationResult

Single validation check result.

Attributes:
    level: ValidationLevel (ERROR, WARNING, INFO)
    code: Machine-readable code (e.g. "BMD_MISSING_FIELD")
    message: Human-readable description
    context: Optional dict with additional details

#### Methods

##### __init__(self, level, code, message, context)

*No description available.*
Initializes a new instance with the provided `level`, `code`, `message`, and optional `context` values. Assigns each argument directly to the corresponding instance attribute, defaulting `context` to an empty dictionary if no value is supplied.

**Parameters:**
- `level` — severity or classification level of the entry.
- `code` — identifier code associated with the entry.
- `message` — human-readable description.
- `context` *(optional)* — dict with additional details; defaults to `{}`.

##### __repr__(self)

*No description available.*
Returns a string representation of the object in the format `[{level}] {code}: {message}`. This method provides a human-readable identifier combining the instance's `level`, `code`, and `message` attributes into a single formatted string.

##### to_dict(self)

Converts the object's core attributes into a dictionary representation. The returned dictionary contains four keys — `"level"`, `"code"`, `"message"`, and `"context"` — mapped to their corresponding instance attribute values.

### BundleValidator

Validates StratiGraph bundle contents and metadata.

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

#### Methods

##### validate_directory(self, bundle_dir)

Validate a bundle directory.

Args:
    bundle_dir: Path to the unzipped bundle directory.

Returns:
    list[ValidationResult]: All validation results.

##### validate_zip(self, zip_path)

Validate a bundle ZIP file.

Extracts to a temp directory and validates.

Args:
    zip_path: Path to the bundle ZIP file.

Returns:
    list[ValidationResult]: All validation results.

## Functions

### validate_bundle(bundle_path)

Convenience function to validate a bundle.

Args:
    bundle_path: Path to a bundle ZIP file or directory.

Returns:
    dict: Validation summary with keys:
        - valid (bool): True if no errors
        - errors (list[dict]): Error results
        - warnings (list[dict]): Warning results
        - info (list[dict]): Info results
        - total_checks (int): Total number of checks performed

**Parameters:**
- `bundle_path`

