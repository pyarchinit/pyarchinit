# tabs/Archeozoology.py

## Overview

This file contains 27 documented elements.

## Classes

### pyarchinit_Archeozoology

Archeozoology form for zooarchaeological quantification analysis.

This module provides:
- Data entry and management for archeozoological quantification data
- Geostatistical analysis using R (semivariograms, kriging)
- Statistical visualizations (histograms, boxplots, coplots)
- Integration with QGIS for spatial visualization

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initialize the Archeozoology form.

##### customize_GUI(self)

Customize the GUI elements.

##### charge_list(self)

Load site list from database.

##### set_sito(self)

Set the current site from settings.

##### msg_sito(self)

Show site configuration message if needed.

##### on_pushButton_connect_pressed(self)

Connect to database.

##### charge_records(self)

Load all records from database.

##### fill_fields(self, n)

Fill form fields with record data.

##### empty_fields(self)

Clear all form fields.

##### on_calcola_pressed(self)

Calculate and display semivariogram.

##### on_automap_pressed(self)

Run automated kriging analysis.

##### on_hist_pressed(self)

Generate histogram for selected variable.

##### on_boxplot_pressed(self)

Generate boxplot for selected variable.

##### on_coplot_pressed(self)

Generate conditional plot.

##### on_matrix_pressed(self)

Generate correlation matrix.

##### on_report_pressed(self)

Generate HTML report.

##### on_pushButton_first_rec_pressed(self)

Go to first record.

##### on_pushButton_last_rec_pressed(self)

Go to last record.

##### on_pushButton_prev_rec_pressed(self)

Go to previous record.

##### on_pushButton_next_rec_pressed(self)

Go to next record.

##### on_pushButton_new_rec_pressed(self)

Create a new record.

##### on_pushButton_save_pressed(self)

Save the current record.

##### collect_form_data(self)

Collect data from form fields.

##### on_pushButton_delete_pressed(self)

Delete the current record.

##### on_pushButton_view_all_pressed(self)

View all records.

