# PlaceSelectionDialog.py

## Overview

This file contains 3 documented elements.

## Classes

### PlaceSelectionDialog

*No description available.*
A `QDialog` subclass used in the context of GeoCoding to present a place selection interface to the user. The dialog's layout and widgets are loaded at instantiation from the `Ui_PlaceSelection.ui` file located in the `gui/ui/` subdirectory relative to the module's file path.

**Inherits from**: QDialog

#### Methods

##### __init__(self)

Initializes a new instance of `PlaceSelectionDialog` by invoking the parent `QDialog` constructor via `super()`. Loads the associated Qt UI layout from `Ui_PlaceSelection.ui`, located in the `gui/ui` subdirectory relative to the current file, using `uic.loadUi`.

