# resources/resources_rc.py

## Overview

This file contains 2 documented elements.

## Functions

### qInitResources()

*No description available.*
Registers the embedded Qt resource data with the Qt resource system by calling `QtCore.qRegisterResourceData` with the module-level `rcc_version`, `qt_resource_struct`, `qt_resource_name`, and `qt_resource_data` values. The `rcc_version` used is determined at module load time, selecting between version 1 and version 2 resource structures accordingly. This function is called automatically upon module import.

### qCleanupResources()

*No description available.*
Unregisters the module's compiled-in Qt resource data by calling `QtCore.qUnregisterResourceData` with the `rcc_version`, `qt_resource_struct`, `qt_resource_name`, and `qt_resource_data` arguments. This is the counterpart to `qInitResources`, which registers the same resource data on module load. Call this function to remove the resources from Qt's resource system when they are no longer needed.

