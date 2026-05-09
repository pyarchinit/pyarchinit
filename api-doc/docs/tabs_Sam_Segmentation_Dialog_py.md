# tabs/Sam_Segmentation_Dialog.py

## Overview

This file contains 24 documented elements.

## Classes

### SamApiWorkerThread

Worker thread to run SAM segmentation via Replicate API using external script

**Inherits from**: QThread

#### Methods

##### __init__(self, input_raster, output_gpkg, api_key, mode)

Initializes a worker thread instance for running SAM segmentation via the Replicate API using an external script. Accepts the path to an input raster file, the path to an output GeoPackage file, an API key for authentication, and an optional processing mode (defaulting to `'auto'`). Stores all provided arguments as instance attributes and calls the parent class constructor via `super().__init__()`.

##### run(self)

Run SAM API segmentation via external subprocess

### SamSegmentationWorkerThread

Worker thread to run SAM segmentation in background using official segment-anything

**Inherits from**: QThread

#### Methods

##### __init__(self, input_raster, output_gpkg, mode, prompts, model)

Initializes a worker thread instance for running SAM (Segment Anything Model) segmentation in the background. Accepts the input raster path, output GeoPackage path, segmentation mode, optional prompts, and the model variant (`vit_b`, `vit_l`, or `vit_h`), storing each as an instance attribute. Calls the parent class constructor via `super().__init__()` to ensure proper thread initialization.

##### run(self)

Run SAM segmentation in subprocess using official segment-anything

### Sam3RoboflowWorkerThread

Worker thread to run SAM3 segmentation via Roboflow API with text prompts

**Inherits from**: QThread

#### Methods

##### __init__(self, input_raster, output_gpkg, api_key, text_prompt)

Initializes a worker thread instance for running SAM3 segmentation via the Roboflow API with text prompts. Accepts the path to an input raster file, the path to an output GeoPackage file, a Roboflow API key, and an optional text prompt string (defaulting to `'stones'`). Stores all provided arguments as instance attributes for use during thread execution.

##### run(self)

Run SAM3 segmentation via Roboflow API

### SamSegmentationDialog

Dialog for SAM-based stone/object segmentation

Allows users to:
- Select a raster layer (orthophoto)
- Choose target layer (pyunitastratigrafiche or _usm)
- Set area and default attributes
- Choose segmentation mode (auto, click, box)
- Run segmentation and add results to target layer

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent)

Initializes a new instance of the SAM Stone Segmentation dialog, accepting an optional database manager and parent widget. Sets up instance attributes including `db_manager`, `worker_thread`, `temp_output`, `map_tool`, `collected_prompts`, and `previous_map_tool`, all initialized to `None` except where the provided arguments are assigned. Completes initialization by calling `initUI()` to build the user interface and `load_settings()` to restore any previously saved configuration.

##### initUI(self)

Initialize the user interface

##### load_settings(self)

Load saved settings

##### save_settings(self)

Save settings

##### get_mode(self)

Get selected segmentation mode

##### get_model(self)

Get selected model

##### is_api_mode(self)

Check if API mode is selected

##### is_sam3_mode(self)

Check if SAM-3 (Roboflow) mode is selected

##### on_segment_clicked(self)

Start segmentation process

##### on_progress(self, message)

Handle progress updates

##### on_segmentation_finished(self, success, message, output_file)

Handle segmentation completion

##### add_polygons_to_target(self, gpkg_path)

Add segmented polygons to the target layer or load as new layer

##### reject(self)

Handle dialog rejection (cancel)

