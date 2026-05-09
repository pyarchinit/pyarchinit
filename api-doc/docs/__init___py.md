# __init__.py

## Overview

This file contains 33 documented elements.

## Classes

### PipManager

Manages pip installation and updates.

#### Methods

##### update_pip(python_path)

Update pip to the latest available version.

Args:
    python_path: Path to the Python executable to use

##### configure_pip()

Configure and update pip based on the operating system.

### PackageManager

Manages package installation across different operating systems.

#### Methods

##### is_osgeo4w()

Check if running in OSGeo4W environment.

##### get_osgeo4w_python()

Get the path to the OSGeo4W Python executable.

##### get_windows_qgis_python()

Get the path to QGIS Python on Windows (standalone installation).

Dynamically scans for all QGIS versions from 3.22 to 4.x.
Supports both PR (latest) and LTR (Long Term Release) versions.
Result is cached after first call to avoid repeated filesystem scans.

Returns:
    Path to python.exe or sys.executable if not found

##### is_ubuntu()

Check if running on Ubuntu.

##### get_ubuntu_package_name(package)

Map pip package names to Ubuntu package names.

Args:
    package: The pip package name

Returns:
    The corresponding Ubuntu package name or the original name if not found

##### install(package)

Install a package using the appropriate method for the current OS.

Args:
    package: The package to install

##### remove_opencv_directories()

Remove OpenCV directories if they exist on macOS.
Does nothing on other operating systems.

##### check_required_packages(requirements_path)

Check which required packages are missing or have wrong versions.

Searches both standard distributions and the plugin ext_libs directory.

Args:
    requirements_path: Path to the requirements.txt file

Returns:
    List of missing or outdated packages

### Worker

Worker thread for installing packages.

**Inherits from**: QObject

#### Methods

##### install_packages(self, packages)

Install a list of packages and emit progress signals.

Args:
    packages: List of packages to install

### InstallDialog

Dialog for selecting and installing packages.

**Inherits from**: QDialog

#### Methods

##### __init__(self, packages)

Initialize the dialog.

Args:
    packages: List of packages that can be installed

##### initUI(self)

Initialize the UI components.

##### show_splash(self, message)

Show the animated splash screen.

##### update_splash_message(self, message)

Update the splash screen message.

##### hide_splash(self)

Hide the splash screen.

##### set_icon(self, icon_path)

Set the dialog icon.

Args:
    icon_path: Path to the icon file

##### install_selected_packages(self)

Install the packages selected in the table.

##### update_progress(self, value)

Update the progress bar for Windows and Linux.

Args:
    value: The progress value (0-100)

##### update_progress_mac(self, value)

Update the progress bar for macOS with additional event processing.

Args:
    value: The progress value (0-100)

##### finish_install(self)

Called when installation is complete.

### FontManager

Manages font installation.

#### Methods

##### install_fonts()

Install required fonts for the system.

## Functions

### initialize_environment(splash)

Initialize the environment for pyArchInit.

Args:
    splash: Optional splash screen to update messages and keep animation alive

**Parameters:**
- `splash`

**Returns:** `None`

### get_missing_packages()

Check which packages are missing.

Returns:
    List of missing packages

**Returns:** `List[str]`

### check_and_install_dependencies(splash)

Check and install missing dependencies.

Args:
    splash: Optional splash screen (kept for backward compatibility, not used)

**Parameters:**
- `splash`

**Returns:** `None`

### show_install_dialog(packages)

Show the dialog for installing packages.

Args:
    packages: List of packages to install

**Parameters:**
- `packages: List[str]`

**Returns:** `None`

### classFactory(iface)

Load the PyArchInitPlugin class.

Args:
    iface: QGIS interface

Returns:
    PyArchInitPlugin instance

**Parameters:**
- `iface`

