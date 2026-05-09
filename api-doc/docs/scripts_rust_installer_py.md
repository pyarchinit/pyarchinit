# scripts/rust_installer.py

## Overview

This file contains 3 documented elements.

## Functions

### check_rust_available()

Check if the Rust acceleration module is available.

Returns:
    tuple: (available: bool, version: str or None)

### install_rust_acceleration(version)

Download and install the Rust acceleration module.

Args:
    version: Version to install. Defaults to DEFAULT_VERSION.

Returns:
    tuple: (success: bool, message: str)

**Parameters:**
- `version`

