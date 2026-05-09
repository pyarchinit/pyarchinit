# modules/utility/testtable_checkbox.py

## Overview

This file contains 4 documented elements.

## Classes

### Window

*No description available.*
A `QWidget` subclass that displays a table populated with labeled text items arranged in a specified number of rows and columns. Odd-numbered rows are rendered as user-checkable items initialized to an unchecked state, while even-numbered rows are non-checkable. When a table item is clicked, the `handleItemClicked` handler prints the item's checked or clicked state to the console and, for checked items, appends the row index to an internal list (`_list`).

**Inherits from**: QWidget

#### Methods

##### __init__(self, rows, columns)

Initializes a `Window` instance by calling the parent `QWidget` constructor and creating a `QTableWidget` with the specified number of `rows` and `columns`. Each cell is populated with a `QTableWidgetItem` labelled `'Text{row}'`; items at odd row indices are additionally configured with user-checkable flags and set to an unchecked state. A `QVBoxLayout` is applied to contain the table, the `itemClicked` signal is connected to `handleItemClicked`, and an empty list `_list` is initialized for tracking checked row indices.

##### handleItemClicked(self, item)

*No description available.*
Handles a click event on a table item by inspecting its check state. If the item is checked (`Qt.Checked`), the item's text is printed with a "Checked" label and its row index is appended to the internal `_list` collection. If the item is not checked, its text is printed with a "Clicked" label and no further action is taken.

