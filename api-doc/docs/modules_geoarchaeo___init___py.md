# modules/geoarchaeo/__init__.py

## Overview

This file contains 6 documented elements.

## Classes

### DummyPlugin

*No description available.*
A minimal placeholder plugin returned when required dependencies are not satisfied. It implements the mandatory QGIS plugin interface by providing no-op `initGui` and `unload` methods, allowing QGIS to load without error. This class is defined and instantiated inline as a fallback within the plugin entry point, preventing a hard failure when `check_and_install_dependencies()` returns `False`.

#### Methods

##### initGui(self)

*No description available.*
A no-operation placeholder method defined on the `DummyPlugin` class, which is instantiated when required dependencies are not available. It satisfies the expected plugin interface without performing any initialization or registering any GUI elements. This method exists solely to allow the host application to call `initGui` safely in a degraded state where the full plugin cannot be loaded.

##### unload(self)

*No description available.*
A no-operation method defined on the `DummyPlugin` class, which is returned as a fallback when required dependencies are missing. This method performs no actions and exists solely to satisfy the expected plugin interface contract. It accepts no parameters and returns nothing.

## Functions

### check_and_install_dependencies()

Verifica e installa le dipendenze necessarie

### classFactory(iface)

Entry point per QGIS - carica il plugin

**Parameters:**
- `iface`

