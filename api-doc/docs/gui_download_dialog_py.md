# gui/download_dialog.py

## Overview

This file contains 14 documented elements.

## Classes

### DownloadThread

Thread for downloading files with progress updates

**Inherits from**: QThread

#### Methods

##### __init__(self, url, save_path)

Initializes a new download worker instance with the specified URL and destination path. Calls the parent class constructor via `super().__init__()`, then assigns `url` and `save_path` to instance attributes and sets `is_cancelled` to `False`.

##### run(self)

Download the file with progress tracking

##### cancel(self)

Cancel the download

### DownloadModelDialog

Dialog for downloading AI models with progress tracking

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent)

Initializes a `DownloadModelDialog` instance by calling the parent `QDialog` constructor with the optional `parent` argument. Sets the instance attributes `save_path` and `save_dir` to empty strings and `download_thread` to `None`. Completes initialization by invoking `setup_ui()` to configure the dialog's user interface.

##### setup_ui(self)

Setup the dialog UI

##### start_download(self)

Start the download process

##### update_progress(self, value)

Update progress bar

##### update_speed(self, text)

Update speed label

##### update_status(self, text)

Update status label

##### download_finished(self, success, message)

Handle download completion

##### cancel_download(self)

Cancel the download

