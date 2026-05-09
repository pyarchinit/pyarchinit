# gui/ui/mplwidget.py

## Overview

This file contains 5 documented elements.

## Classes

### MplCanvas

*No description available.*
A `FigureCanvas` subclass that initializes a Matplotlib figure with a single subplot for embedding in a Qt5 application. On construction, it creates a `Figure` instance, adds a single `111`-layout subplot accessible via `self.ax`, and configures the canvas with an expanding size policy in both horizontal and vertical directions. The geometry is updated immediately after initialization to reflect the applied size policy.

**Inherits from**: FigureCanvas

#### Methods

##### __init__(self)

*No description available.*
Initializes a `Mplwidget` instance by invoking the parent `QWidget` constructor with the optional `parent` argument. The `parent` parameter accepts a `QWidget` instance to designate the widget's parent in the Qt object hierarchy, defaulting to `None` if no parent is specified.

### Mplwidget

*No description available.*
A `QWidget` subclass that embeds a Matplotlib canvas (`MplCanvas`) together with a `NavigationToolbar` into a single, self-contained widget. On initialization, both the canvas and the navigation toolbar are arranged vertically using a `QVBoxLayout`, with the canvas positioned above the toolbar. This class serves as a reusable Qt widget for displaying Matplotlib figures with built-in navigation controls.

**Inherits from**: QWidget

#### Methods

##### __init__(self, parent)

Initializes an `Mplwidget` instance by calling the parent `QWidget` constructor with the optional `parent` argument. Creates an `MplCanvas` instance assigned to `self.canvas` and a `NavigationToolbar` instance assigned to `self.navBar`, using the canvas and the widget itself as arguments. Arranges both widgets vertically using a `QVBoxLayout`, which is set as the layout of the widget.

