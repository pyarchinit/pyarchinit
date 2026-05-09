# modules/utility/pyarchinit_theme_manager.py

## Overview

This file contains 21 documented elements.

## Classes

### ThemeManager

Manages PyArchInit UI themes.

#### Methods

##### __new__(cls)

Singleton pattern.

##### __init__(self)

Initialize theme manager.

##### get_saved_theme(cls)

Get the saved theme preference from settings.

##### save_theme(cls, theme)

Save theme preference to settings.

##### get_current_theme(cls)

Get the current theme.

##### get_stylesheet(cls, theme)

Get stylesheet for the specified theme.

##### apply_theme(cls, widget, theme)

Apply theme to a widget and all its children.

##### toggle_theme(cls)

Toggle between dark and light themes.

##### is_dark_theme(cls)

Check if current theme is dark.

##### create_toggle_button(cls, parent_widget, button_type)

Create a theme toggle button.

Args:
    parent_widget: The parent widget that owns this button
    button_type: 'tool' for QToolButton, 'push' for QPushButton

Returns:
    The created button with toggle functionality

##### add_toggle_button_to_toolbar(cls, toolbar, parent_widget)

Add a theme toggle button to an existing toolbar.

Args:
    toolbar: QToolBar to add the button to
    parent_widget: The parent widget to re-apply theme on toggle

Returns:
    The created toggle button

##### add_theme_toggle_to_form(cls, form)

Add a theme toggle button to a form, positioned in the bottom-right corner.

Args:
    form: The QDialog or QWidget to add the toggle button to

Returns:
    The created toggle button

## Functions

### apply_theme_to_widget(widget, theme)

Convenience function to apply theme to a widget.

**Parameters:**
- `widget`
- `theme: str`

### get_current_stylesheet()

Convenience function to get current theme stylesheet.

**Returns:** `str`

### toggle_theme()

Convenience function to toggle theme.

**Returns:** `str`

### is_dark_theme()

Convenience function to check if dark theme is active.

**Returns:** `bool`

### on_toggle()

Callback function invoked when the toggle button is clicked. It calls `cls.toggle_theme()` to switch the current theme, then updates the button's visual appearance via `cls._update_toggle_button_appearance(button)`, and finally re-applies the active theme to the parent widget by calling `cls.apply_theme(parent_widget)`.

### reposition_button(event)

*No description available.*
Calculates and applies the position of a toggle button in the bottom-right corner of its parent form, offset 12 pixels from both the right and bottom edges. After moving the button, it calls `raise_()` to ensure the button remains on top of other widgets. This function is called on initial render and is intended to be re-invoked whenever the parent form is resized.

**Parameters:**
- `event`

### new_resize_event(event)

*No description available.*
A replacement resize event handler assigned to the form that ensures the button is repositioned whenever the form is resized. It calls `reposition_button()` first, then delegates to the original `resizeEvent` handler if one existed, preserving any prior resize behavior. This function is bound directly to `form.resizeEvent`, overriding the default handler.

**Parameters:**
- `event`

