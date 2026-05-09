# tabs/Upd.py

## Overview

This file contains 6 documented elements.

## Classes

### pyarchinit_Upd_Values

*No description available.*
A QDialog subclass that provides a user interface for bulk-updating field values in a specified database table based on features selected in the QGIS layer. On button press, it retrieves the `gid` field positions of selected features, reads the target table name, ID field, field to update, and replacement value from the form inputs, then calls `update_record` for each selected feature ID. The class displays a deprecation warning on connection load, indicating it is scheduled for removal.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes the dialog instance by storing the provided QGIS interface (`iface`) and creating a `Pyarchinit_pyqgis` instance bound to it. Calls `QDialog.__init__` and `setupUi` to set up the base dialog and UI components, then applies the application theme via `ThemeManager` and adds a theme toggle button to the form. Finally, sets `currentLayerId` to `None` and invokes `load_connection` to establish the initial database connection.

##### load_connection(self)

*No description available.*
Displays a deprecation warning dialog informing the user that the system is being discontinued and will soon be removed. It then instantiates a `Connection` object, retrieves its connection string via `conn_str()`, and attempts to initialize the database manager by calling `get_db_manager` with the connection string and singleton mode enabled, assigning the result to `self.DB_MANAGER`. Any exception raised during database manager initialization is silently suppressed.

##### on_pushButton_pressed(self)

*No description available.*
Handles the button press event by retrieving the `gid` field position and collecting the selected features from the QGIS layer, then extracting their integer IDs into a list. Reads the target table name, ID field, field to update, and replacement value from the corresponding UI input fields (`nome_tabellaLineEdit`, `campoIDLineEdit`, `nome_campoLineEdit`, `sostituisci_conLineEdit`). Iterates over each selected feature ID and calls `update_record` to apply the specified field value update to the corresponding record in the database.

##### update_record(self, table_value, id_field_value, id_value_list, table_fields_list, data_list)

*No description available.*
```python
def update_record(self, table_value, id_field_value, id_value_list, table_fields_list, data_list)
```

Delegates an update operation to the underlying `DB_MANAGER`, passing through the target table name, the identifier field, a list of identifier values, the fields to be updated, and the corresponding new values. This method acts as a thin wrapper, forwarding all five parameters directly to `DB_MANAGER.update` without additional processing.

