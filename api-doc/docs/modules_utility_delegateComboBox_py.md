# modules/utility/delegateComboBox.py

## Overview

This file contains 15 documented elements.

## Classes

### TooltipListView

Custom ListView that properly shows tooltips

**Inherits from**: QListView

#### Methods

##### __init__(self, parent)

Initializes a `TooltipListView` instance by calling the parent `QListView` constructor with the optional `parent` argument. Enables mouse tracking on the view and sets the `Qt.WA_AlwaysShowToolTips` attribute on the viewport to ensure tooltip events are consistently generated.

##### viewportEvent(self, event)

Handle viewport events including tooltips

### TooltipComboBox

Custom ComboBox that shows tooltips for items in the dropdown

**Inherits from**: QComboBox

#### Methods

##### __init__(self, parent)

Initializes a `TooltipComboBox` instance by calling the parent `QComboBox` constructor with the optional `parent` argument. A `TooltipListView` instance is created and assigned as the combo box's view via `setView`. A default tooltip of `"Click per aprire la lista"` is set on the combo box itself.

##### addItem(self, text, userData)

Override to ensure we can add tooltips

##### showPopup(self)

Override to ensure view is properly configured when shown

### ComboBoxDelegate

*No description available.*
A `QItemDelegate` subclass that renders and manages a `TooltipComboBox` editor within item views. It maintains a list of selectable values and an editability flag, using these to configure the combo box editor created for each cell. The delegate handles synchronisation between the editor and the underlying model via `setEditorData` and `setModelData`, mapping display text to combo box index on read and writing the current text back to the model on commit.

**Inherits from**: QItemDelegate

#### Methods

##### __init__(self, values, parent)

Initializes a `ComboBoxDelegate` instance by calling the parent `QItemDelegate` constructor with the given `parent` argument. If a `values` argument is provided and evaluates to a truthy value, it assigns that value to the instance's `values` attribute, overriding the class-level default. Both `values` and `parent` parameters are optional and default to `None`.

##### def_values(self, values)

*No description available.*
Sets the `values` attribute of the delegate to the provided `values` argument. This method directly assigns the given parameter to `self.values`, replacing any previously stored value.

**Parameters:**
- `values` — The value or collection of values to assign to the delegate's `values` attribute.

##### def_editable(self, editable)

Sets the `editable` attribute of the instance to the provided `editable` value. This method stores the given argument directly on the object, controlling whether the associated editor component is editable.

##### createEditor(self, parent, option, index)

Creates and configures a `TooltipComboBox` widget to serve as the cell editor for a delegate. Populates the combo box with items from `self.values` and sets its size adjust policy to `QComboBox.AdjustToContents`. The editability of the combo box is determined by evaluating `self.editable` if the attribute exists and is non-empty; otherwise, the editor defaults to non-editable.

##### setEditorData(self, editor, index)

*No description available.*
Populates the editor widget with data from the model at the given index. Retrieves the display text from the model using `Qt.DisplayRole` and locates the corresponding entry in the editor via `findText`. If no matching entry is found, the editor's current index defaults to `0`.

##### setModelData(self, editor, model, index)

*No description available.*
Writes data from the editor widget back to the model at the specified index. Retrieves the current text from the `editor` (a combo box) using `currentText()` and stores it in the `model` via `model.setData(index, ...)`. This method overrides the default delegate behavior to ensure the selected text value is persisted to the underlying data model.

