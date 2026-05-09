# tabs/PlaceSelectionDialog.py

## Overview

This file contains 3 documented elements.

## Classes

### PlaceSelectionDialog

*No description available.*
A Qt dialog class used for geocoding place selection, built on top of `QDialog` (PyQt4). It loads its user interface layout at instantiation time from the external Qt Designer file `Ui_PlaceSelection.ui`, located in the `gui/ui` subdirectory relative to the module's parent directory. The UI is applied dynamically using `uic.loadUi`, meaning all widgets and layout are defined in the accompanying `.ui` file rather than in code.

**Inherits from**: QDialog

#### Methods

##### __init__(self)

Initializes a new instance of the `PlaceSelectionDialog` class, which serves as a dialog for GeoCoding place selection. Calls the parent `QDialog` constructor via `super()` and then loads the associated UI layout from the `Ui_PlaceSelection.ui` file located in the `gui/ui` subdirectory relative to the current file's parent directory.

