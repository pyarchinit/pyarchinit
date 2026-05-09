# gui/remote_storage_dialog.py

## Overview

This file contains 15 documented elements.

## Classes

### RemoteStorageDialog

Dialog for configuring remote storage backends.

Allows users to configure credentials for:
- Google Drive
- Dropbox
- Amazon S3 / Cloudflare R2
- WebDAV
- HTTP/HTTPS
- SFTP

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent)

Initializes the Remote Storage Configuration dialog by calling the parent constructor and setting the window title to `"Remote Storage Configuration"` with minimum dimensions of 500×400 pixels. Instantiates a `QgsSettings` object stored as `self.settings`, then sequentially calls `self.setup_ui()` to build the user interface and `self.load_settings()` to populate it with previously saved values.

##### setup_ui(self)

Set up the user interface

##### setup_cloudinary_tab(self)

Set up Cloudinary configuration tab

##### setup_gdrive_tab(self)

Set up Google Drive configuration tab

##### setup_dropbox_tab(self)

Set up Dropbox configuration tab

##### setup_s3_tab(self)

Set up S3/R2 configuration tab

##### setup_webdav_tab(self)

Set up WebDAV configuration tab

##### setup_http_tab(self)

Set up HTTP/HTTPS configuration tab

##### setup_api_storage_tab(self)

Set up API Storage (File Manager) configuration tab

##### load_settings(self)

Load settings from QGIS settings

##### save_settings(self)

Save settings to QGIS settings

##### test_connection(self)

Test connection to the currently selected backend

##### save_settings_temp(self)

Temporarily save settings for testing

