# searchLayers.py

## Overview

This file contains 5 documented elements.

## Classes

### SearchLayers

*No description available.*
A QGIS plugin class that integrates a layer search feature into the QGIS interface. It manages the initialization of a search action connected to `showSearchDialog`, which lazily instantiates and displays a `LayerSearchDialog` on demand. The class holds a reference to the QGIS `iface` object and the single `LayerSearchDialog` instance for the lifetime of the plugin.

#### Methods

##### __init__(self, iface)

Initializes a new instance of the `SearchLayers` class, storing the provided `iface` object as an instance attribute. Sets `self.searchDialog` to `None`, indicating that no search dialog has been created at construction time.

##### initGui(self)

*No description available.*
Initializes the plugin's graphical user interface components within the QGIS environment. Configures the existing `searchAction` by setting its object name to `'searchLayers'` and connecting its `triggered` signal to the `showSearchDialog` slot. Toolbar icon and plugin menu registration are present in the source but currently commented out.

##### showSearchDialog(self)

*No description available.*
Displays the layer search dialog, instantiating a new `LayerSearchDialog` instance if one does not already exist. The dialog is initialized with the plugin's `iface` reference and the main QGIS window as its parent. Once created, the dialog is made visible by calling its `show()` method.

