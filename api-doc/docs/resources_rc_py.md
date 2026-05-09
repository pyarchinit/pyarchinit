# resources_rc.py

## Overview

This file contains 2 documented elements.

## Functions

### qInitResources()

*No description available.*
Registers the embedded Qt resource data with the Qt resource system by calling `QtCore.qRegisterResourceData` with the module-level `rcc_version`, `qt_resource_struct`, `qt_resource_name`, and `qt_resource_data` values. The `rcc_version` used is determined at module load time, selecting between version 1 and version 2 resource structures accordingly. This function is called automatically upon module import.

### qCleanupResources()

*No description available.*
Unregisters the module's compiled-in Qt resource data by calling `QtCore.qUnregisterResourceData` with the module-level constants `rcc_version`, `qt_resource_struct`, `qt_resource_name`, and `qt_resource_data`. This function serves as the counterpart to `qInitResources`, which registers the same resource data on module load. It should be called when the registered resources are no longer needed to remove them from Qt's resource system.

