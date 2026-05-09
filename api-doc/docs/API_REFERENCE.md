# API Reference

---

## Class `PlaceSelectionDialog`

**Description**: Dialog for place selection. Internal details are not documented in source.

**Constructor**:
```python
PlaceSelectionDialog()
```

**Parameters**: (not documented in source)

---

## Class `Worker` *(Search)*

**Description**: Performs the core search work. Takes all search parameters and seeks a match across vector layers.

> *Original docstring*: "Questo fa tutto il lavoro duro. Prende tutti i parametri di ricerca e cerca una corrispondenza attraverso i livelli vettoriali."

**Constructor**:
```python
Worker()
```

**Parameters**: (not documented in source)

**Methods**:

*No description available.*
**Description**: Executes the search operation across vector layers using the configured search parameters.

**Parameters**: None

**Practical Example**:
```python
worker = Worker()
worker.run()
```

**When to Use It**: Call after constructing a `Worker` instance to start the search process across vector layers.

---

*No description available.*
**Description**: Terminates the worker's ongoing operation.

**Parameters**: None

**Practical Example**:
```python
worker = Worker()
worker.run()
# Stop the operation when needed
worker.kill()
```

**When to Use It**: Use to interrupt a running search before it completes.

---

## Class `LayerSearchDialog`

**Description**: Dialog for searching across layers. Internal details are not documented in source.

**Constructor**:
```python
LayerSearchDialog()
```

**Parameters**: (not documented in source)

**Methods**:

*No description available.*
**Description**: Closes the layer search dialog.

**Parameters**: None

**Practical Example**:
```python
dialog = LayerSearchDialog()
dialog.closeDialog()
```

**When to Use It**: Use to programmatically close the dialog after a search operation is complete or cancelled.

---

*No description available.*
**Description**: Updates the list of layers displayed in the dialog.

**Parameters**: None

**Practical Example**:
```python
dialog = LayerSearchDialog()
dialog.updateLayers()
```

**When to Use It**: Call when the available layers have changed and the dialog contents need to reflect the current state.

---

## Class `InstallDialog` *(Layer Search module)*

**Description**: Dialog for selecting and installing packages. Internal details are not documented in source.

**Constructor**:
```python
InstallDialog()
```

**Parameters**: (not documented in source)

**Methods**:

*No description available.*
**Description**: Initialises the user interface components of the dialog.

**Parameters**: None

**Practical Example**:
```python
dialog = InstallDialog()
dialog.initUI()
```

**When to Use It**: Called during dialog setup to build and arrange UI elements.

---

*No description available.*
**Description**: Triggers the installation of the selected packages.

**Parameters**: None

**Practical Example**:
```python
dialog = InstallDialog()
dialog.initUI()
dialog.install_packages()
```

**When to Use It**: Invoke to start the package installation process from within the dialog.

---

## Class `PipManager`

**Description**: Manages pip installation and updates.

**Constructor**: (not documented in source)

**Methods**:

*No description available.*
**Description**: Updates the pip package manager to a newer version.

**Parameters**: None

**Practical Example**:
```python
manager = PipManager()
manager.update_pip()
```

**When to Use It**: Use before installing packages to ensure pip itself is up to date.

---

*No description available.*
**Description**: Configures pip settings for the current environment.

**Parameters**: None

**Practical Example**:
```python
manager = PipManager()
manager.configure_pip()
```

**When to Use It**: Call to apply environment-specific pip configuration prior to package operations.

---

## Class `PackageManager`

**Description**: Manages package installation across different operating systems.

**Constructor**: (not documented in source)

**Methods**:

*No description available.*
**Description**: Determines whether the current environment is an OSGeo4W installation.

**Parameters**: None

**Practical Example**:
```python
pkg_manager = PackageManager()
pkg_manager.is_osgeo4w()
```

**When to Use It**: Use to branch installation logic based on whether the host environment is OSGeo4W.

---

*No description available.*
**Description**: Retrieves the Python executable path for an OSGeo4W environment.

**Parameters**: None

**Practical Example**:
```python
pkg_manager = PackageManager()
pkg_manager.get_osgeo4w_python()
```

**When to Use It**: Call when the environment has been identified as OSGeo4W and the correct Python path is required.

---

*No description available.*
**Description**: Retrieves the Python executable path for a Windows QGIS installation.

**Parameters**: None

**Practical Example**:
```python
pkg_manager = PackageManager()
pkg_manager.get_windows_qgis_python()
```

**When to Use It**: Use on Windows systems where QGIS is installed outside of OSGeo4W.

---

## Class `Worker` *(Package Installation)*

**Description**: Worker thread for installing packages.

**Constructor**: (not documented in source)

**Methods**:

*No description available.*
**Description**: Executes the package installation process in a worker thread.

**Parameters**: None

**Practical Example**:
```python
worker = Worker()
worker.install_packages()
```

**When to Use It**: Use to perform package installation asynchronously, keeping the UI responsive.

---

## Class `InstallDialog` *(Package Installation module)*

**Description**: Dialog for selecting and installing packages.

**Constructor**:
```python
InstallDialog()
```

**Parameters**: (not documented in source)

**Methods**:

*No description available.*
**Description**: Initialises the user interface components of the install dialog.

**Parameters**: None

**Practical Example**:
```python
dialog = InstallDialog()
dialog.initUI()
```

**When to Use It**: Called during dialog construction to set up all UI elements.

---

*No description available.*
**Description**: Displays a splash screen within the install dialog.

**Parameters**: None

**Practical Example**:
```python
dialog = InstallDialog()
dialog.show_splash()
```

**When to Use It**: Use to present a loading or informational splash screen during the installation workflow.

---

## Class `FontManager`

**Description**: Manages font installation.

**Constructor**: (not documented in source)

**Methods**:

*No description available.*
**Description**: Installs the required fonts into the current environment.

**Parameters**: None

**Practical Example**:
```python
font_manager = FontManager()
font_manager.install_fonts()
```

**When to Use It**: Call during environment initialisation to ensure all required fonts are available.

---

## Class `PyArchInitPlugin`

**Description**: Main plugin class. Internal details are not documented in source.

**Constructor**:
```python
PyArchInitPlugin()
```

**Parameters**: (not documented in source)

**Methods**:

*No description available.*
**Description**: Checks whether experimental features are enabled for the plugin.

**Parameters**: None

**Practical Example**:
```python
plugin = PyArchInitPlugin()
plugin.is_experimental_enabled()
```

**When to Use It**: Use to conditionally activate or suppress experimental functionality at runtime.

---

*No description available.*
**Description**: Loads the plugin configuration.

**Parameters**: None

**Practical Example**:
```python
plugin = PyArchInitPlugin()
plugin.load_config()
```

**When to Use It**: Call during plugin initialisation to read and apply stored configuration values.

---

---

## Functions

---

*No description available.*
**Description**: Displays the installation dialog to the user. (Two definitions exist in source; behaviour details are not documented in source.)

**Parameters**: (not documented in source)

**Return Value**: (not documented in source)

**Practical Example**:
```python
show_install_dialog()
```

**When to Use It**: Use to present the package installation interface to the user.

---

*No description available.*
**Description**: Initialises the runtime environment required by the plugin.

**Parameters**: (not documented in source)

**Return Value**: (not documented in source)

**Practical Example**:
```python
initialize_environment()
```

**When to Use It**: Call before performing operations that depend on a correctly configured environment.

---

*No description available.*
**Description**: Identifies packages that are required but not currently installed.

**Parameters**: (not documented in source)

**Return Value**: (not documented in source)

**Practical Example**:
```python
missing = get_missing_packages()
```

**When to Use It**: Use to determine which dependencies must be installed before the plugin can operate correctly.

---

*No description available.*
**Description**: Checks for missing dependencies and installs them if necessary.

**Parameters**: (not documented in source)

**Return Value**: (not documented in source)

**Practical Example**:
```python
check_and_install_dependencies()
```

**When to Use It**: Call during plugin startup to ensure all required packages are present before the plugin loads.

::: tip
Combine `get_missing_packages()` with `check_and_install_dependencies()` to first audit the environment and then resolve any gaps in a single startup sequence.
:::

---

*No description available.*
**Description**: QGIS plugin entry point that instantiates the plugin class.

**Parameters**: (not documented in source)

**Return Value**: (not documented in source)

**Practical Example**:
```python
classFactory()
```

**When to Use It**: This function is called automatically by QGIS when loading the plugin. It should not typically be called directly by user code.

::: note
`classFactory` is a standard QGIS plugin convention. QGIS invokes it automatically during plugin loading.
:::

---

*No description available.*
**Description**: Replaces an image resource within the plugin interface.

**Parameters**: (not documented in source)

**Return Value**: (not documented in source)

**Practical Example**:
```python
replace_image()
```

**When to Use It**: Use when a UI image element needs to be substituted at runtime.

---

*No description available.*
**Description**: Creates a button UI element.

**Parameters**: (not documented in source)

**Return Value**: (not documented in source)

**Practical Example**:
```python
btn = create_button()
```

**When to Use It**: Use to programmatically generate a button for inclusion in a dialog or toolbar.

---

*No description available.*
**Description**: Initialises Qt resource files required by the plugin.

**Parameters**: None

**Return Value**: (not documented in source)

**Practical Example**:
```python
qInitResources()
```

**When to Use It**: Call to register Qt resources (icons, images) before they are accessed by the UI.

---

*No description available.*
**Description**: Releases Qt resource files registered by `qInitResources()`.

**Parameters**: None

**Return Value**: (not documented in source)

**Practical Example**:
```python
qCleanupResources()
```

**When to Use It**: Call during plugin unload or teardown to free Qt resource registrations.

::: warning
Always pair `qCleanupResources()` with a prior call to `qInitResources()`. Calling cleanup without a corresponding initialisation may produce undefined behaviour.
:::