# modules/utility/rust_helpers.py

## Overview

This file contains 4 documented elements.

## Functions

### parse_rapporti(rapporti_str)

Parse rapporti field - uses Rust if available, else ast.literal_eval.

**Parameters:**
- `rapporti_str`

### compute_style_categories(d_stratigrafica_list)

Compute style categories - uses Rust if available.

**Parameters:**
- `d_stratigrafica_list`

### is_rust_available()

Check if the Rust acceleration module is available.

