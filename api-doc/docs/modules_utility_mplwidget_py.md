# modules/utility/mplwidget.py

## Overview

This file contains 5 documented elements.

## Classes

### MplCanvas

*No description available.*
A `FigureCanvas` subclass that initializes a Matplotlib figure with a single subplot (`add_subplot(111)`). The canvas is configured with an expanding size policy in both horizontal and vertical directions, and geometry is updated upon initialization to reflect the size policy.

**Inherits from**: FigureCanvas

#### Methods

##### __init__(self)

*No description available.*
Initializes a `Mplwidget` instance by delegating to the `QWidget` base class constructor with the provided `parent` argument. Accepts an optional `parent` parameter (defaulting to `None`) that specifies the parent widget in the Qt widget hierarchy.

### Mplwidget

*No description available.*
A `QWidget` subclass that embeds a Matplotlib canvas (`MplCanvas`) together with a `NavigationToolbar` into a single, self-contained widget. On initialization, both the canvas and the navigation toolbar are arranged vertically using a `QVBoxLayout`, with the canvas positioned above the toolbar. This class serves as a reusable Qt widget component for displaying and interacting with Matplotlib figures within a PyQt interface.

**Inherits from**: QWidget

#### Methods

##### __init__(self, parent)

Initializes a `Mplwidget` instance by calling the parent `QWidget` constructor with the optional `parent` argument. Creates an `MplCanvas` instance assigned to `self.canvas` and a `NavigationToolbar` instance assigned to `self.navBar`, using the canvas and the widget itself as arguments. Arranges both widgets vertically using a `QVBoxLayout`, which is set as the layout of the widget.

