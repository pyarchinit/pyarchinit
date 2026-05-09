# gui/quantpanelmain_pottery.py

## Overview

This file contains 7 documented elements.

## Classes

### QuantPanelMain

*No description available.*
A `QDialog` subclass that loads its layout from `quantpanelmain_pottery.ui` and provides a panel for configuring quantification settings for pottery analysis. It manages two list widgets — `FieldsList` and `FieldListsort` — allowing the user to move fields between them via `on_pushButtonRight_pressed` and `on_pushButtonLeft_pressed` handlers. On confirmation via `on_pushButtonQuant_pressed`, it collects the ordered field selections into `ITEMS` and sets `TYPE_QUANT` to either `"QTY"` or `"Fragment"` based on the active radio button selection, closing the dialog or prompting a warning if no items have been configured.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, parent, db)

*No description available.*
Initializes a `QuantPanelMain` instance by invoking the `QDialog` base class constructor with the optional `parent` argument. Calls `setupUi(self)` to set up the user interface as defined by `MAIN_DIALOG_CLASS`. The `db` parameter is accepted but not used within this method.

##### on_pushButtonQuant_pressed(self)

Handles the press event of the `pushButtonQuant` button by collecting all items from the `FieldListsort` widget into the `ITEMS` list and setting the `TYPE_QUANT` attribute to either `"QTY"` or `"Fragment"` based on which radio button (`radioButtonFormeMin` or `radioButtonFrammenti`) is currently selected. If the `ITEMS` list is empty, a warning dialog is displayed prompting the user to confirm whether to exit; if the user confirms, the dialog is closed, otherwise no action is taken. If `ITEMS` is not empty, the dialog is closed immediately.

##### on_pushButtonRight_pressed(self)

*No description available.*
Handles the press event of the right button by moving the currently selected item from `FieldsList` to `FieldListsort`. It collects all items from `FieldsList`, removes the selected item (along with any empty string entry), and repopulates `FieldsList` with the remaining items. The selected item is then added to `FieldListsort`, effectively transferring it from one list widget to the other.

##### on_pushButtonLeft_pressed(self)

*No description available.*
Handles the left button press event by moving the currently selected item from `FieldListsort` back to `FieldsList`. It collects all items from `FieldListsort`, removes the selected item from that collection, adds it to `FieldsList`, and then repopulates `FieldListsort` with the remaining items. If no item is selected, the removal step is silently skipped via a bare `except` clause.

##### insertItems(self, lv)

*No description available.*
Inserts items into `FieldsList` starting at position `0` using the provided value `lv`. This method delegates directly to the `insertItems` method of the `FieldsList` widget, passing `0` as the index and `lv` as the collection of items to insert.

