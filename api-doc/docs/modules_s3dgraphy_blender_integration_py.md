# modules/s3dgraphy/blender_integration.py

## Overview

This file contains 9 documented elements.

## Classes

### BlenderIntegration

Integrates PyArchInit with Blender for 3D stratigraphic visualization

#### Methods

##### __init__(self)

Initializes a new instance of the Blender integration class with default connection parameters. Sets `host` to `'localhost'`, `port` to `8765` (the default port for the Blender addon), and `socket` to `None`.

##### is_blender_connected(self)

Check if Blender is running with PyArchInit addon

##### send_to_blender(self, data)

Send Extended Matrix data to Blender for 3D visualization

##### export_for_blender_addon(self, matrix_data, output_path)

Export Extended Matrix data for manual import in Blender

### BlenderAddonScript

Generate Blender Python addon script for PyArchInit integration

#### Methods

##### generate_addon()

Generate the Blender addon Python script

##### save_addon(output_path)

Save the Blender addon script to file

