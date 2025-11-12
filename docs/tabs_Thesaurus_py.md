# tabs/Thesaurus.py

## Overview

This file contains 219 documented elements.

## Classes

### pyarchinit_Thesaurus

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### read_api_key(self, path)

##### write_api_key(self, path, api_key)

##### apikey_gpt(self)

##### check_db(self)

##### contenuto(self, b)

##### webview(self)

##### handleComboActivated(self, index)

##### on_suggerimenti_pressed(self)

##### find_text(self)

##### on_pushButton_import_csvthesaurus_pressed(self)

funzione valida solo per sqlite

##### enable_button(self, n)

##### enable_button_search(self, n)

##### on_pushButton_connect_pressed(self)

##### charge_list(self)

##### get_table_name_from_display(self, display_name)

Convert display name to actual table name

##### get_display_name_from_table(self, table_name)

Convert table name to display name

##### charge_n_sigla(self)

##### setup_tma_hierarchy_widgets(self)

Setup hierarchy management widgets for TMA materials.

##### on_tma_tipologia_changed(self)

Handle TMA tipologia change to show hierarchy options.

##### hide_hierarchy_widgets(self)

Hide all hierarchy selection widgets.

##### show_area_parent_widgets(self)

Show widgets for selecting località parent for area.

##### show_settore_parent_widgets(self)

Show widgets for selecting località and area parents for settore.

##### show_area_parent_dialog(self)

Show dialog for selecting località parent for area.

##### show_settore_parent_dialog(self)

Show dialog for selecting località and area parents for settore.

##### create_hierarchy_widgets(self)

Create hierarchy selection widgets dynamically.

##### load_parent_areas(self)

Load available parent areas from thesaurus.

##### load_parent_localita(self)

Load available località from thesaurus.

##### on_parent_localita_changed(self)

When località selection changes, update available areas.

##### on_pushButton_sort_pressed(self)

##### on_pushButton_new_rec_pressed(self)

##### on_pushButton_save_pressed(self)

##### data_error_check(self)

##### insert_new_rec(self)

##### check_synchronized_field(self, sigla_estesa, tipologia_sigla, table_name)

Check if this field should be synchronized across tables

##### synchronize_field_values(self, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, table_name)

Synchronize field values across all related tables

##### check_record_state(self)

##### on_pushButton_view_all_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_delete_pressed(self)

##### on_pushButton_sigle_pressed(self)

##### on_pushButton_new_search_pressed(self)

##### on_pushButton_search_go_pressed(self)

##### on_pushButton_test_pressed(self)

##### on_pushButton_draw_pressed(self)

##### on_pushButton_sites_geometry_pressed(self)

##### on_pushButton_sync_tma_thesaurus_pressed(self)

Sincronizza il thesaurus TMA con inventario materiali e aree

##### on_pushButton_rel_pdf_pressed(self)

##### update_if(self, msg)

##### charge_records(self)

##### datestrfdate(self)

##### table2dict(self, n)

##### empty_fields(self)

##### fill_fields(self, n)

##### set_rec_counter(self, t, c)

##### set_LIST_REC_TEMP(self)

##### set_LIST_REC_CORR(self)

##### setComboBoxEnable(self, f, v)

##### setComboBoxEditable(self, f, n)

##### rec_toupdate(self)

##### records_equal_check(self)

##### update_record(self)

##### testing(self, name_file, message)

### pyarchinit_Thesaurus

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### read_api_key(self, path)

##### write_api_key(self, path, api_key)

##### apikey_gpt(self)

##### check_db(self)

##### contenuto(self, b)

##### webview(self)

##### handleComboActivated(self, index)

##### on_suggerimenti_pressed(self)

##### find_text(self)

##### on_pushButton_import_csvthesaurus_pressed(self)

funzione valida solo per sqlite

##### enable_button(self, n)

##### enable_button_search(self, n)

##### on_pushButton_connect_pressed(self)

##### charge_list(self)

##### get_table_name_from_display(self, display_name)

Convert display name to actual table name

##### get_display_name_from_table(self, table_name)

Convert table name to display name

##### charge_n_sigla(self)

##### setup_tma_hierarchy_widgets(self)

Setup hierarchy management widgets for TMA materials.

##### on_tma_tipologia_changed(self)

Handle TMA tipologia change to show hierarchy options.

##### hide_hierarchy_widgets(self)

Hide all hierarchy selection widgets.

##### show_area_parent_widgets(self)

Show widgets for selecting località parent for area.

##### show_settore_parent_widgets(self)

Show widgets for selecting località and area parents for settore.

##### show_area_parent_dialog(self)

Show dialog for selecting località parent for area.

##### show_settore_parent_dialog(self)

Show dialog for selecting località and area parents for settore.

##### create_hierarchy_widgets(self)

Create hierarchy selection widgets dynamically.

##### load_parent_areas(self)

Load available parent areas from thesaurus.

##### load_parent_localita(self)

Load available località from thesaurus.

##### on_parent_localita_changed(self)

When località selection changes, update available areas.

##### on_pushButton_sort_pressed(self)

##### on_pushButton_new_rec_pressed(self)

##### on_pushButton_save_pressed(self)

##### data_error_check(self)

##### insert_new_rec(self)

##### check_synchronized_field(self, sigla_estesa, tipologia_sigla, table_name)

Check if this field should be synchronized across tables

##### synchronize_field_values(self, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, table_name)

Synchronize field values across all related tables

##### check_record_state(self)

##### on_pushButton_view_all_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_delete_pressed(self)

##### on_pushButton_sigle_pressed(self)

##### on_pushButton_new_search_pressed(self)

##### on_pushButton_search_go_pressed(self)

##### on_pushButton_test_pressed(self)

##### on_pushButton_draw_pressed(self)

##### on_pushButton_sites_geometry_pressed(self)

##### on_pushButton_sync_tma_thesaurus_pressed(self)

Sincronizza il thesaurus TMA con inventario materiali e aree

##### on_pushButton_rel_pdf_pressed(self)

##### update_if(self, msg)

##### charge_records(self)

##### datestrfdate(self)

##### table2dict(self, n)

##### empty_fields(self)

##### fill_fields(self, n)

##### set_rec_counter(self, t, c)

##### set_LIST_REC_TEMP(self)

##### set_LIST_REC_CORR(self)

##### setComboBoxEnable(self, f, v)

##### setComboBoxEditable(self, f, n)

##### rec_toupdate(self)

##### records_equal_check(self)

##### update_record(self)

##### testing(self, name_file, message)

### pyarchinit_Thesaurus

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### read_api_key(self, path)

##### write_api_key(self, path, api_key)

##### apikey_gpt(self)

##### check_db(self)

##### contenuto(self, b)

##### webview(self)

##### handleComboActivated(self, index)

##### on_suggerimenti_pressed(self)

##### find_text(self)

##### on_pushButton_import_csvthesaurus_pressed(self)

funzione valida solo per sqlite

##### enable_button(self, n)

##### enable_button_search(self, n)

##### on_pushButton_connect_pressed(self)

##### charge_list(self)

##### get_table_name_from_display(self, display_name)

Convert display name to actual table name

##### get_display_name_from_table(self, table_name)

Convert table name to display name

##### charge_n_sigla(self)

##### setup_tma_hierarchy_widgets(self)

Setup hierarchy management widgets for TMA materials.

##### on_tma_tipologia_changed(self)

Handle TMA tipologia change to show hierarchy options.

##### hide_hierarchy_widgets(self)

Hide all hierarchy selection widgets.

##### show_area_parent_widgets(self)

Show widgets for selecting località parent for area.

##### show_settore_parent_widgets(self)

Show widgets for selecting località and area parents for settore.

##### show_area_parent_dialog(self)

Show dialog for selecting località parent for area.

##### show_settore_parent_dialog(self)

Show dialog for selecting località and area parents for settore.

##### create_hierarchy_widgets(self)

Create hierarchy selection widgets dynamically.

##### load_parent_areas(self)

Load available parent areas from thesaurus.

##### load_parent_localita(self)

Load available località from thesaurus.

##### on_parent_localita_changed(self)

When località selection changes, update available areas.

##### on_pushButton_sort_pressed(self)

##### on_pushButton_new_rec_pressed(self)

##### on_pushButton_save_pressed(self)

##### data_error_check(self)

##### insert_new_rec(self)

##### check_synchronized_field(self, sigla_estesa, tipologia_sigla, table_name)

Check if this field should be synchronized across tables

##### synchronize_field_values(self, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, table_name)

Synchronize field values across all related tables

##### check_record_state(self)

##### on_pushButton_view_all_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_delete_pressed(self)

##### on_pushButton_sigle_pressed(self)

##### on_pushButton_new_search_pressed(self)

##### on_pushButton_search_go_pressed(self)

##### on_pushButton_test_pressed(self)

##### on_pushButton_draw_pressed(self)

##### on_pushButton_sites_geometry_pressed(self)

##### on_pushButton_sync_tma_thesaurus_pressed(self)

Sincronizza il thesaurus TMA con inventario materiali e aree

##### on_pushButton_rel_pdf_pressed(self)

##### update_if(self, msg)

##### charge_records(self)

##### datestrfdate(self)

##### table2dict(self, n)

##### empty_fields(self)

##### fill_fields(self, n)

##### set_rec_counter(self, t, c)

##### set_LIST_REC_TEMP(self)

##### set_LIST_REC_CORR(self)

##### setComboBoxEnable(self, f, v)

##### setComboBoxEditable(self, f, n)

##### rec_toupdate(self)

##### records_equal_check(self)

##### update_record(self)

##### testing(self, name_file, message)

## Functions

### on_ok()

### on_cancel()

### on_localita_changed()

### on_ok()

### on_cancel()

### on_ok()

### on_cancel()

### on_localita_changed()

### on_ok()

### on_cancel()

### on_ok()

### on_cancel()

### on_localita_changed()

### on_ok()

### on_cancel()

