# gui/ui/mplwidgetmatrix.py

## Overview

This file contains 5 documented elements.

## Classes

### MplCanvas

*No description available.*
A `FigureCanvas` subclass that initializes a Matplotlib figure with a single subplot (`111`) and embeds it in a Qt5 widget context. The canvas is configured with an expanding size policy on both horizontal and vertical axes, and geometry is updated upon initialization to reflect the size constraints.

**Inherits from**: FigureCanvas

#### Methods

##### __init__(self)

Initializes an `MplwidgetMatrix` instance by invoking the parent `QWidget` constructor with the optional `parent` argument. Accepts an optional `parent` parameter (defaulting to `None`) that specifies the parent widget in the Qt widget hierarchy.

### MplwidgetMatrix

*No description available.*
A `QWidget` subclass that embeds a Matplotlib canvas (`MplCanvas`) together with a `NavigationToolbar` within a vertical box layout. On initialization, it composes the canvas and navigation toolbar into a single cohesive widget using `QVBoxLayout`, with the canvas positioned above the toolbar. This class serves as a self-contained Qt widget for displaying Matplotlib figures with built-in navigation controls.

**Inherits from**: QWidget

#### Methods

##### __init__(self, parent)

Initializes an instance of `MplwidgetMatrix`, a `QWidget` subclass that embeds a Matplotlib canvas with a navigation toolbar. The constructor calls the parent `QWidget.__init__` with the optional `parent` argument, then instantiates an `MplCanvas` and a `NavigationToolbar` linked to that canvas. Both widgets are arranged vertically using a `QVBoxLayout`, which is set as the layout for this widget.

