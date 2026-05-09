# modules/utility/delegateComboBox_simple.py

## Overview

This file contains 8 documented elements.

## Classes

### ComboBoxDelegate

Simple ComboBox delegate with built-in tooltip support

**Inherits from**: QItemDelegate

#### Methods

##### __init__(self, values, parent)

Initializes a `ComboBoxDelegate` instance by calling the parent `QItemDelegate` constructor with the provided `parent` argument. Sets the `values` attribute to the supplied `values` list, defaulting to an empty list if `None` or a falsy value is provided. Sets the `editable` attribute to the string `"False"`.

##### def_values(self, values)

Sets the `values` attribute of the delegate to the provided `values` parameter. This method replaces any previously assigned values with the new input.

##### def_editable(self, editable)

*No description available.*
Sets the `editable` attribute of the instance to the provided value. This method assigns the given `editable` argument directly to `self.editable`, controlling whether the associated component permits editing.

**Signature:** `def_editable(self, editable)`

| Parameter | Description |
|-----------|-------------|
| `editable` | The value assigned to `self.editable`. |

##### createEditor(self, parent, option, index)

*No description available.*
Creates and returns a `QComboBox` widget to be used as a cell editor. The combo box is populated with all items from `self.values`, configured with a maximum of 10 visible items, and its size is adjusted to fit its contents. A tooltip displaying the current selection is set and updated on each selection change; the editability of the combo box is determined by the `editable` attribute if present and non-empty, otherwise it defaults to non-editable.

##### setEditorData(self, editor, index)

*No description available.*
Populates the delegate's editor widget with data retrieved from the model at the given index. It fetches the display text via `Qt.DisplayRole`, locates the corresponding entry in the editor using `findText`, and falls back to index `0` if no match is found. The editor's current selection is then set to the resolved index, and its tooltip is updated to display `"Valore corrente: "` followed by the currently selected text.

##### setModelData(self, editor, model, index)

*No description available.*
Transfers data from the editor widget back to the model. Retrieves the current text from the `editor` and writes it to the model at the specified `index` using `model.setData`. This method follows the standard delegate interface for committing user-edited values to the underlying data model.

