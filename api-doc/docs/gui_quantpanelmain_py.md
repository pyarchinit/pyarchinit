# gui/quantpanelmain.py

## Overview

This file contains 7 documented elements.

## Classes

### QuantPanelMain

*No description available.*
A `QDialog` subclass that loads its layout from `quantpanelmain.ui` and provides a panel for configuring quantification criteria. It manages two list widgets — `FieldsList` and `FieldListsort` — allowing the user to move items between them via directional buttons, and captures the selected quantification type (`"Forme minime"` or `"Frammenti"`) via radio buttons. On confirmation, it validates that at least one criterion has been selected before closing; if none are present, it prompts the user with a warning dialog.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, parent, db)

*No description available.*
Initializes a `QuantPanelMain` instance by invoking the `QDialog` constructor with the optional `parent` argument. Calls `setupUi(self)` to set up the user interface as defined by `MAIN_DIALOG_CLASS`. The `db` parameter is accepted but not used within this method.

##### on_pushButtonQuant_pressed(self)

Handles the press event of the `pushButtonQuant` button by collecting all items from the `FieldListsort` widget into the `ITEMS` list and determining the quantification type (`TYPE_QUANT`) based on which radio button (`radioButtonFormeMin` or `radioButtonFrammenti`) is currently selected. If the `ITEMS` list is empty, a warning dialog is displayed prompting the user to confirm whether to exit; if confirmed, the dialog is closed. If `ITEMS` is not empty, the dialog closes immediately without further prompting.

##### on_pushButtonRight_pressed(self)

*No description available.*
Handles the press event of the right button by moving the currently selected item from `FieldsList` to `FieldListsort`. It collects all items from `FieldsList`, removes the selected item (and any empty string entry) from that collection, then adds the selected item to `FieldListsort` and repopulates `FieldsList` with the remaining items.

##### on_pushButtonLeft_pressed(self)

*No description available.*
Handles the press event of the left push button by moving the currently selected item from `FieldListsort` back to `FieldsList`. It collects all items from `FieldListsort`, removes the selected item from that collection, adds it to `FieldsList`, and then repopulates `FieldListsort` with the remaining items. If no item is selected, the removal step is silently skipped via a bare `except` clause.

##### insertItems(self, lv)

*No description available.*
Inserts items into `FieldsList` starting at position `0` using the provided list `lv`. This method delegates directly to the `insertItems` method of the `FieldsList` widget, passing `0` as the index and `lv` as the collection of items to insert.

