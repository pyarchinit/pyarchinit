# tabs/GNA_export.py

## Overview

This file contains 4 documented elements.

## Classes

### GNAExportDialog

Dialog for exporting UT data to GNA GeoPackage.

**Inherits from**: QDialog, FORM_CLASS

#### Methods

##### __init__(self, iface, db_manager, ut_records, project_name, parent)

Initialize the GNA export dialog.

Args:
    iface: QGIS interface
    db_manager: PyArchInit database manager
    ut_records: List of UT records to export
    project_name: Current project name
    parent: Parent widget

##### get_result(self)

Get export result.

