# gui/ui/pyarchinit_splash.py

## Overview

This file contains 17 documented elements.

## Classes

### AnimatedGearWidget

Widget that displays animated rotating gears around a central logo.

**Inherits from**: QWidget

#### Methods

##### __init__(self, parent)

Initializes an `AnimatedGearWidget` instance by configuring the widget's minimum size, time-based animation state variables (including speed, target speed, and inertia time constant), and two meshing external gears with their respective tooth counts and angles. Attempts to load the PyArchInit Archeoimagineers logo from a primary path, falling back to `IconPAI.png` if the primary is not found, or setting `self.logo` to `None` if neither exists. Sets up a `QTimer` with a precise timer type connected to `update_animation`, and defines three colors derived from the Archeoimagineers logo palette.

##### start_animation(self)

Start the gear animation.

##### stop_animation(self)

Stop the gear animation.

##### update_animation(self)

Update rotation angles (continuous, meshed gears).

##### paintEvent(self, event)

Paint the gears and logo.

### PyArchInitSplash

Splash screen dialog for PyArchInit.

Displays the PyArchInit logo with animated rotating gears
and a status message.

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent, message)

*No description available.*
Initializes the PyArchInit splash screen dialog with the specified parent widget and status message. Sets the window flags to frameless, always-on-top, and dialog mode, enables a translucent background attribute, and marks the dialog as modal. Delegates UI component construction to `init_ui`, passing the provided message string.

##### init_ui(self, message)

Initialize the UI components.

##### center_on_screen(self)

Center the splash screen on the screen.

##### set_message(self, message)

Update the status message.

##### showEvent(self, event)

Start animation when shown.

##### hideEvent(self, event)

Stop animation when hidden.

##### closeEvent(self, event)

Stop animation when closed.

## Functions

### show_splash_during_operation(operation_func, message, parent)

Show the splash screen while executing an operation.

Args:
    operation_func: Function to execute while showing splash
    message: Initial message to display
    parent: Parent widget

Returns:
    The result of operation_func

**Parameters:**
- `operation_func`
- `message`
- `parent`

### update_message()

*No description available.*
Schedules a sequential series of status messages to be displayed on the splash screen using `QTimer.singleShot`, with each message delayed by 1500 milliseconds from the previous one. The messages cycle through installation progress updates for `numpy`, `pandas`, `sqlalchemy`, `reportlab`, and a final "Finalizing installation..." notice, each applied via `splash.set_message`. After all messages have been displayed, a final timer fires to close the splash screen.

