# gui/sortpanelmain.py

## Overview

This file contains 8 documented elements.

## Classes

### SortPanelMain

*No description available.*
A `QDialog` subclass that provides a UI panel for configuring sort criteria on a list of fields. It allows the user to move fields between an available fields list (`FieldsList`) and a sort fields list (`FieldListsort`), and to select an ascending or descending sort order via radio buttons. On confirmation, the selected fields are collected into `ITEMS` and the sort direction is stored in `TYPE_ORDER` as either `"asc"` or `"desc"`; if no sort criteria are set, the user is prompted before the dialog closes.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, parent, db)

Initializes a `SortPanelMain` dialog instance by calling the parent `QDialog` constructor with the provided `parent` argument and invoking `setupUi` to set up the user interface. Accepts an optional `parent` widget and an optional `db` parameter, though `db` is not used within the method body. Initializes the instance attribute `ITEMS` as an empty list.

##### closeEvent(self, event)

*No description available.*
Handles the dialog's close event by ensuring the `ITEMS` list is populated before the dialog is destroyed. If `ITEMS` is empty at the time of closing, the text of the first item in `FieldsList` is appended to it. The method then schedules the dialog for deletion via `deleteLater()` and delegates to the base `QDialog.closeEvent()` to complete standard close processing.

##### on_pushButtonSort_pressed(self)

*No description available.*
Handles the sort button press event by collecting all items from the `FieldListsort` widget into the `ITEMS` list and setting `TYPE_ORDER` to `"asc"` or `"desc"` based on the state of `radioButtonAsc`. If no items have been collected, a warning dialog (in Italian) prompts the user to confirm whether they wish to exit without a sort criterion, closing the dialog only on confirmation. If items are present, the dialog closes immediately.

##### on_pushButtonRight_pressed(self)

*No description available.*
Handles the press event of the right button by moving the currently selected item from `FieldsList` to `FieldListsort`. The method collects all items from `FieldsList`, removes the selected item (and any empty string entry) from that collection, then adds the selected item to `FieldListsort`. Finally, `FieldsList` is cleared and repopulated with the remaining items.

##### on_pushButtonLeft_pressed(self)

*No description available.*
Handles the press event of the left push button by moving the currently selected item from `FieldListsort` back to `FieldsList`. It collects all items from `FieldListsort`, removes the selected item from that collection, adds it to `FieldsList`, and then repopulates `FieldListsort` with the remaining items. If no item is selected, the removal step is silently skipped via a bare `except` clause.

##### insertItems(self, lv)

*No description available.*
Inserts a list of items into `FieldsList` starting at position `0`. Accepts a single parameter `lv`, which is passed directly to the underlying `FieldsList.insertItems` call. No return value is produced by this method.

