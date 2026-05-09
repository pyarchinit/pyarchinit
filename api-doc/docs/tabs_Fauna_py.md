# tabs/Fauna.py

## Overview

This file contains 57 documented elements.

## Classes

### pyarchinit_Fauna

Fauna form for SCHEDA FR (Fauna Record Sheet).

This module provides:
- Data entry and management for fauna/archaeozoological data
- Integration with pyArchInit database
- Support for both SQLite and PostgreSQL

**Inherits from**: QDialog

#### Methods

##### __init__(self, iface)

Initializes the instance by calling the parent constructor, storing the provided `iface` reference, and instantiating a `Pyarchinit_OS_Utility` object. Attempts to establish a database connection via `connect_to_db()`, displaying a localized warning dialog (supporting Italian, German, French, Spanish, and English) if the connection fails. Completes setup by invoking `setup_ui()`, applying the application theme via `ThemeManager`, and loading initial data through `charge_list()`, `set_sito()`, and `fill_fields()`.

##### connect_to_db(self)

Connect to the pyArchInit database.

##### setup_ui(self)

Setup the user interface.

##### create_toolbar(self)

Create the main toolbar.

##### create_tab_identificativi(self)

Create the identification data tab.

##### create_tab_archeozoologici(self)

Create the archaeozoological data tab.

##### create_tab_tafonomici(self)

Create the taphonomic data tab.

##### create_tab_contestuali(self)

Create the contextual data tab.

##### set_sito(self)

Filter records by selected site.

##### setComboBoxEnable(self, combo_box_list, enabled)

Enable/disable combo boxes.

##### charge_list(self)

Load list values for combo boxes.

##### charge_thesaurus_combos(self)

Load thesaurus values for Fauna comboboxes

##### charge_us_combo(self, sito, area)

Load US data into comboBox_us_select with format 'sito - area - us'

##### on_us_selected(self, index)

Handle US selection - auto-populate sito, area, saggio, datazione fields

##### on_sito_changed(self, index)

Handle site selection change - update area and US combos

##### on_area_changed(self, index)

Handle area selection change - update US combo

##### on_pushButton_new_search_pressed(self)

Start a new search - clear form and set to search mode

##### on_pushButton_search_go_pressed(self)

Execute the search with current form values as filters

##### fill_fields(self, n)

Fill form fields with current record data.

##### set_rec_counter(self, t, c)

Update record counter display.

Args:
    t: Total number of records
    c: Current record number (1-based for display)

Note: REC_CORR is 0-based index, c is 1-based display value.
This method only updates display labels, not REC_CORR.

##### add_specie_psi_row(self)

Aggiunge una riga alla tabella Specie/PSI

##### remove_specie_psi_row(self)

Rimuove la riga selezionata dalla tabella Specie/PSI

##### get_specie_psi_data(self)

Estrae i dati dalla tabella Specie/PSI come lista di liste

##### set_specie_psi_data(self, data)

Popola la tabella Specie/PSI da una lista di liste

##### add_misura_row(self)

Aggiunge una riga alla tabella Misure

##### remove_misura_row(self)

Rimuove la riga selezionata dalla tabella Misure

##### get_misure_data(self)

Estrae i dati dalla tabella Misure come lista di liste

##### set_misure_data(self, data)

Popola la tabella Misure da una lista di liste

##### empty_fields(self)

Clear all form fields.

##### on_pushButton_first_rec_pressed(self)

*No description available.*
Navigates to the first record in `DATA_LIST` by resetting the current record index (`REC_CORR`) to `0`. If `DATA_LIST` is non-empty, it populates the form fields with the first record's data by calling `fill_fields(0)` and updates the record counter display via `set_rec_counter`, reflecting position `1` of the total number of records.

##### on_pushButton_prev_rec_pressed(self)

Navigates to the previous record in `DATA_LIST` by decrementing the current record index `REC_CORR` by one, provided the list is non-empty and the current index is greater than zero. It then repopulates the UI fields with the data at the updated index by calling `fill_fields`, and refreshes the record counter display via `set_rec_counter`.

##### on_pushButton_next_rec_pressed(self)

*No description available.*
Advances to the next record in `DATA_LIST` when the "next record" button is pressed. If `DATA_LIST` is non-empty and the current record index (`REC_CORR`) is not already at the last position, it increments `REC_CORR` by one, repopulates the fields via `fill_fields`, and updates the record counter display via `set_rec_counter`.

##### on_pushButton_last_rec_pressed(self)

*No description available.*
Navigates to the last record in `DATA_LIST` when the list is non-empty. Sets `REC_CORR` to the index of the final element (`len(DATA_LIST) - 1`), then calls `fill_fields` to populate the UI fields with that record's data. Updates the record counter display via `set_rec_counter` to reflect the total number of records and the current position.

##### on_pushButton_new_rec_pressed(self)

Sets the browse status to `"n"` and updates the status label with the corresponding value from `self.STATUS_ITEMS`. Clears all input fields by calling `self.empty_fields()`, preparing the form for a new record entry.

##### on_pushButton_save_pressed(self)

Save current record.

##### on_pushButton_delete_pressed(self)

Delete current record.

##### on_pushButton_view_all_pressed(self)

Load all records.

##### create_tab_statistiche(self)

Create the statistics tab with summary reports.

##### get_all_fauna_records(self)

Get all fauna records as dictionaries.

##### update_statistics(self)

Calculate and display comprehensive statistics.

##### export_statistics_excel(self)

Export statistics to Excel (CSV) format.

##### export_statistics_pdf(self)

Export statistics to PDF format.

##### on_pushButton_exp_pdf_sheet_pressed(self)

Export Fauna records to PDF sheets.

##### generate_list_pdf(self)

Generate data list for PDF export.

##### data_error_check(self)

Check for data errors before save.

##### charge_records(self)

Load all records from database.

##### records_equal_check(self)

Check if record has been modified.

##### set_LIST_REC_TEMP(self)

Store current form data for comparison.

##### set_LIST_REC_CORR(self)

Store current database record for comparison.

##### update_if(self, msg)

Handle update confirmation.

##### update_record(self, id_fauna)

Update record in database.

##### rec_toupdate(self)

Return list of current field values for update.

##### insert_new_rec(self)

Insert new record into database.

## Functions

### load_thesaurus(tipologia_sigla, use_sigla)

*No description available.*
An inner helper function defined within `charge_combo_thesaurus` that queries the `PYARCHINIT_THESAURUS_SIGLE` database table to retrieve thesaurus values for a given typology code (`tipologia_sigla`) filtered by language and table name `'fauna_table'`. If the initial language-filtered query returns no results, a fallback query is performed without the language filter. Returns a sorted, deduplicated list of either abbreviated (`sigla`) or extended (`sigla_estesa`) label values depending on the `use_sigla` flag; returns an empty list if an exception occurs.

**Parameters:**
- `tipologia_sigla`
- `use_sigla`

### count_values(field_name, label, top_n)

Counts the occurrences of each unique non-empty value for a specified field across all records, then appends the results to `stats_text` as a labeled distribution summary. Results are sorted in descending order by count, limited to the top `top_n` entries (default 10), and each entry is displayed with its absolute count and percentage relative to the total number of records. If no valid values are found for the field, a "no data" message is appended instead.

**Parameters:**
- `field_name`
- `label`
- `top_n`

