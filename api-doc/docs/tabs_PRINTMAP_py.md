# tabs/PRINTMAP.py

## Overview

This file contains 12 documented elements.

## Classes

### pyarchinit_PRINTMAP

*No description available.*
A `QDialog` subclass that provides a map print layout management interface for the pyarchinit QGIS plugin. It allows users to browse, preview, and load QPT print layout templates stored in the plugin's profile directory, configure a layout name and map title, and generate a new `QgsPrintLayout` from the selected template within the current QGIS project. The dialog also supports adding or updating template resources from the plugin's bundled assets and applies theme management via `ThemeManager`.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes the widget by calling the parent constructor, assigning the provided `iface` reference, and setting up the UI via `setupUi`. Applies the application theme using `ThemeManager`, configures widget visibility and context menu policies, and connects signals for list item clicks, button clicks, and custom context menu requests. Completes initialization by calling `customize_GUI()`, disabling `txtLayoutName`, and invoking `run()`.

##### customize_GUI(self)

*No description available.*
Performs post-initialization customization of the graphical user interface by connecting widget signals to their corresponding slots. Specifically, it binds the `itemDoubleClicked` signal of `listWidget_2` to the `opentepmplatePreview` handler, enabling template preview functionality when a list item is double-clicked.

##### loadTemplates(self)

Clears the template list widget and scans the `bin/profile/template` subdirectory within `self.HOME` for template files, creating the directory if it does not exist. It retrieves the current QGIS project title (falling back to the project file's base name if no title is set) and populates `self.txtMapTitle` with that value. Only files with a `.qpt` extension are added to `self.listWidget`, sorted alphabetically by filename without extension.

##### listMenu(self, position)

*No description available.*
Displays a context menu at the specified position when an item is selected in `listWidget`, offering two actions: **'Cancella Template'** and **'Mostra Preview'**. If **'Cancella Template'** is chosen, the method attempts to delete the corresponding `.qpt` template file from the profile template directory and updates `txtLayoutName` with a confirmation or failure message. If **'Mostra Preview'** is chosen, it clears `listWidget_2` and populates it with the selected template's name and its associated `.jpeg` preview image as an icon.

##### opentepmplatePreview(self)

*No description available.*
Clears the secondary list widget (`listWidget_2`) and retrieves the name of the currently selected item from the primary list widget (`listWidget`). Constructs the file path to the corresponding JPEG template image located in the `bin/profile/template` subdirectory of `HOME`. Opens an `ImageViewer` dialog to display the resolved image using `show_image`, executing it modally via `exec()`.

##### addMoreTemplates(self)

Displays a confirmation dialog (in Italian) asking the user whether to overwrite existing files when adding templates and resources such as SVG files and script functions. Based on the user's response, it copies files from the source profile directory (`bin/profile` under `self.HOME`) to the QGIS settings directory, either with overwrite (`Yes`) or without overwrite (`No`), using `copy_tree`. If the user confirms with either `Yes` or `No`, `loadTemplates` is called afterward to reload the available templates; selecting `Cancel` performs no action.

##### suggestLayoutName(self)

*No description available.*
Enables the `txtLayoutName` input field and generates a suggested layout name based on the currently selected item in `listWidget`. If `txtMapTitle` is non-empty, its text is appended to the selected item's text, separated by a space. The resulting string is then set as the text of the `txtLayoutName` field.

##### layout_exists(self, layout_name)

*No description available.*
Checks whether a layout with the specified name exists within the current QGIS project's layout manager. Retrieves all layout names from `QgsProject.instance().layoutManager()` and counts how many layouts match the given `layout_name` string. Returns the count of matching layouts as an integer, or `0` if no match is found.

##### layoutLoader(self, template_source, layout_name, title_text)

Generate the layout 

##### run(self)

Run method that performs all the real work

