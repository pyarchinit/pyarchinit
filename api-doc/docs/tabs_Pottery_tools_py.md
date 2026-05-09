# tabs/Pottery_tools.py

## Overview

This file contains 76 documented elements.

## Classes

### PotteryToolsDialog

Main dialog for Pottery Tools functionality

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes a `PotteryToolsDialog` instance by calling the parent `QDialog` constructor, storing the provided `iface` reference, and setting up the UI via `setupUi`. Initializes internal state variables including `DB_MANAGER`, `extracted_images`, a package cache with a 300-second validity duration, and several Python environment path attributes, then sequentially sets up the virtual environment, configures the external Python environment via a non-blocking `QTimer` callback, establishes the database connection, connects signals, and initializes the UI state. Startup progress is reported through `progressBar` value updates and `log_message` calls, with final completion logged to `QgsMessageLog` at `Qgis.Info` level.

##### is_cache_valid(self)

Check if package cache is still valid

##### update_cache(self, package, status)

Update package cache

##### get_cached_status(self, package)

Get cached package status

##### setup_pottery_venv(self, retry_count)

Setup virtual environment for Pottery Tools

##### check_venv_packages(self)

Check if required packages are installed in virtual environment

##### upgrade_venv_pip(self)

Upgrade pip in the virtual environment

##### auto_install_packages(self)

Automatically install packages in virtual environment without user interaction

##### install_venv_packages(self)

Install required packages in the virtual environment

##### check_pottery_ink_status(self)

Check PotteryInk availability and status using virtual environment

##### setup_database(self)

Setup database connection

##### connect_signals(self)

Connect UI signals to slots

##### init_ui_state(self)

Initialize UI state

##### log_message(self, message, level)

Log message to both QGIS log and UI text edit

##### browse_pdf(self)

Browse for PDF or image files

##### update_confidence_label(self, value)

Update confidence label with slider value

##### extract_from_pdf(self)

Extract pottery images from PDF or image file

##### display_extracted_images(self)

Display extracted images in list widget

##### open_extracted_image(self, item)

Open extracted image when double-clicked

##### open_mask_image(self, item)

Open mask image when double-clicked

##### open_pottery_card(self, item)

Open pottery card when double-clicked

##### open_processed_image(self, item)

Open processed image when double-clicked

##### open_image_with_system(self, img_path)

Open image with system default viewer

##### enhance_single_pottery_card(self, card_path)

Enhance a single pottery card using PotteryInk

##### batch_enhance_with_pottery_ink(self, image_folder, output_folder)

Batch enhance images using PotteryInk

##### reset_manual_adjustments(self)

Reset manual contrast and brightness to default values

##### download_pottery_ink_models(self)

Download PotteryInk models from HuggingFace

##### toggle_pottery_ink_options(self, checked)

Toggle PotteryInk options based on checkbox state

##### batch_enhance_dialog(self)

Show dialog for batch enhancement with PotteryInk

##### create_pottery_ink_ui(self)

Dynamically create complete PotteryInk tab with all features

##### toggle_image_source(self)

Toggle image source options

##### browse_folder(self)

Browse for image folder

##### load_folder_images(self, folder_path)

Load images from folder

##### update_layout_options(self)

Update layout options based on mode

##### preview_layout(self)

Preview the layout

##### generate_layout(self)

Generate final layout

##### gather_images_for_layout(self)

Gather images based on selected source

##### load_sites(self)

Load sites from database

##### update_area_filter(self)

Update area filter based on selected site

##### toggle_record_type(self)

Toggle between pottery and inventory records

##### load_records(self)

Load records from database

##### select_all_records(self)

Select all records in table

##### deselect_all_records(self)

Deselect all records in table

##### add_selected_to_layout(self)

Add selected database records to layout

##### get_selected_db_images(self)

Get images for selected database records

##### setup_external_python(self)

Setup external Python using virtual environment only

##### check_ultralytics_async(self)

Check if ultralytics is installed in virtual environment (non-blocking)

##### detect_gpu(self)

Detect if GPU is available for YOLO inference using virtual environment

##### check_model_status(self)

Check if YOLO model is installed

##### download_yolo_model(self)

Download YOLO model from PyPotteryLens repository

##### test_model_loading(self)

Test if the model can be loaded

##### apply_model_to_images(self)

Apply YOLO model to detect pottery in images

##### create_yolo_runner_script(self)

Create a standalone YOLO runner script in ~/pyarchinit/bin

##### find_python_executable(self)

Find appropriate Python executable with ultralytics installed

##### install_ultralytics(self, python_exe)

Attempt to install ultralytics using pip with streaming output

##### get_clean_environment(self)

Get a clean environment for subprocess without QGIS paths

##### display_detection_results(self)

Display detection results with masks overlay

##### extract_pottery_instances(self)

Extract each detected pottery as a separate image

##### display_pottery_cards(self)

Display extracted pottery cards

##### init_tabular_data(self)

Initialize tabular data for pottery cards

##### save_tabular_data(self)

Save tabular data to CSV

##### process_all_pottery(self)

Apply post-processing to all pottery cards

##### display_processed_cards(self)

Display processed pottery cards

##### load_from_pottery_lens(self)

Load processed images from PotteryLens

##### clear_pottery_ink_input(self)

Clear input list

##### send_to_layout(self)

Send enhanced images to layout creator

##### add_pottery_ink_files(self)

Add files to PotteryInk processing queue

##### clear_pottery_ink_files(self)

Clear all files from PotteryInk input list

##### run_pottery_ink_enhancement(self)

Run PotteryInk AI enhancement on selected files

##### save_pottery_ink_results(self)

Save enhanced results to a specified folder

##### run_pottery_ink_diagnostic(self)

Run diagnostic analysis on selected images

##### export_pottery_ink_to_layout(self)

Export enhanced images to the layout creator

## Functions

### install_in_background()

Install packages in background thread

### progress_callback(current, total, message)

*No description available.*
Updates a modal `QProgressDialog` during a long-running operation by computing the percentage completion from `current` and `total`, setting the dialog's label to `message`, and processing pending UI events via `QCoreApplication.processEvents()`. Returns `False` if the user has clicked the Cancel button, signalling the caller to abort the operation, or `True` to indicate that processing should continue.

**Parameters:**
- `current`
- `total`
- `message`

