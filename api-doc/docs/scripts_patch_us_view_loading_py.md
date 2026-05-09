# scripts/patch_us_view_loading.py

## Overview

This file contains 5 documented elements.

## Functions

### patch_pyqgis_file(file_path)

Patch the pyarchinit_pyqgis.py file to fix view loading issues

**Parameters:**
- `file_path`

### main()

*No description available.*
Entry point of the patching script that locates the `pyarchinit_pyqgis.py` file relative to the current file's directory, resolving the expected path as `<plugin_root>/modules/gis/pyarchinit_pyqgis.py`. If the file does not exist at that path, the function prints an error message and exits with code `1`; otherwise, it invokes `patch_pyqgis_file()` to apply the patch. Upon completion, it prints instructions advising the user to restart QGIS and, if necessary, run `fix_spatialite_view_registration.py`.

### replace_layer_creation(match)

Serves as a regex substitution callback used with `re.sub` to inject a `fix_spatialite_view_columns` call immediately after each matched `QgsVectorLayer` creation statement targeting `pyarchinit_us_view`. It extracts the original layer creation line, the surrounding indentation, and the following line from the match groups, then inserts a comment and a `self.fix_spatialite_view_columns(layerUS, 'pyarchinit_us_view')` call between them. The reconstructed string preserves the original indentation and the subsequent line (`###` or `if layerUS.isValid`), ensuring the patched source remains syntactically consistent.

**Parameters:**
- `match`

### add_fix_after_layer(match)

*No description available.*
A regex match callback function used as a replacement handler in a `re.sub` call targeting the `pyarchinit_us_view` layer initialization block. Given a match object, it extracts the original matched text, determines the indentation level of the `layerUS = ` assignment line, and appends a call to `self.fix_spatialite_view_columns(layerUS, 'pyarchinit_us_view')` at the same indentation level immediately after the matched block. The modified string, consisting of the original match followed by the injected fix line, is returned as the substitution result.

**Parameters:**
- `match`

