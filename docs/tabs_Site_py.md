# tabs/Site.py

## Overview

This file contains 237 documented elements.

## Classes

### QgsMapLayerRegistry

### pyarchinit_Site

This class provides to manage the Site Sheet

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### on_pushButton_movecost_pressed(self)

##### on_pushButton_movecost_p_pressed(self)

##### on_pushButton_movebound_pressed(self)

##### on_pushButton_movebound_p_pressed(self)

##### on_pushButton_movecorr_pressed(self)

##### on_pushButton_movecorr_p_pressed(self)

##### on_pushButton_movealloc_pressed(self)

##### on_pushButton_movealloc_p_pressed(self)

##### defaultScriptsFolder(self)

##### on_pushButton_add_script_pressed(self)

##### setPathToSites(self)

##### openSiteDir(self)

##### on_wms_vincoli_pressed(self)

##### internet_on(self)

##### on_basemap_pressed(self)

##### enable_button(self, n)

This method Unable or Enable the GUI buttons on browse modality

##### enable_button_search(self, n)

This method Unable or Enable the GUI buttons on searching modality

##### on_pushButton_connect_pressed(self)

This method establishes a connection between GUI and database

##### charge_list(self)

##### on_pushButton_pdf_pressed(self)

##### on_pushButton_sort_pressed(self)

##### on_pushButton_new_rec_pressed(self)

##### on_pushButton_save_pressed(self)

##### data_error_check(self)

##### insert_new_rec(self)

##### check_record_state(self)

##### on_pushButton_view_all_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_delete_pressed(self)

##### on_pushButton_new_search_pressed(self)

##### msg_sito(self)

##### set_sito(self)

##### on_pushButton_search_go_pressed(self)

##### on_pushButton_test_pressed(self)

##### on_pushButton_draw_pressed(self)

##### on_pushButton_sites_geometry_pressed(self)

##### on_pushButton_draw_sito_pressed(self)

##### on_pushButton_rel_pdf_pressed(self)

##### on_toolButton_draw_siti_toggled(self)

##### on_pushButton_genera_us_pressed(self)

##### update_if(self, msg)

##### charge_records(self)

##### datestrfdate(self)

##### table2dict(self, n)

##### empty_fields(self)

##### fill_fields(self, n)

##### set_rec_counter(self, t, c)

##### check_for_updates(self)

Check if current record has been modified by others

##### closeEvent(self, event)

Handle form close event - stop refresh timer

##### set_LIST_REC_TEMP(self)

##### set_LIST_REC_CORR(self)

##### setComboBoxEnable(self, f, v)

##### setComboBoxEditable(self, f, n)

##### rec_toupdate(self)

##### records_equal_check(self)

##### update_record(self)

##### testing(self, name_file, message)

##### get_config(self, key, default)

##### set_config(self, key, value)

##### reverse(self)

##### reverse_action(self, point)

##### on_pushButton_locate_pressed(self)

##### logMessage(self, msg)

##### get_geocoder_instance(self)

Loads a concrete Geocoder class

##### process_point(self, place, point)

Transforms the point and save

##### save_point(self, point, address)

##### check_settings(self)

### GeoCodeException

**Inherits from**: Exception

### OsmGeoCoder

#### Methods

##### geocode(self, address)

##### reverse(self, lon, lat)

single result

### QgsMapLayerRegistry

### pyarchinit_Site

This class provides to manage the Site Sheet

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### on_pushButton_movecost_pressed(self)

##### on_pushButton_movecost_p_pressed(self)

##### on_pushButton_movebound_pressed(self)

##### on_pushButton_movebound_p_pressed(self)

##### on_pushButton_movecorr_pressed(self)

##### on_pushButton_movecorr_p_pressed(self)

##### on_pushButton_movealloc_pressed(self)

##### on_pushButton_movealloc_p_pressed(self)

##### defaultScriptsFolder(self)

##### on_pushButton_add_script_pressed(self)

##### setPathToSites(self)

##### openSiteDir(self)

##### on_wms_vincoli_pressed(self)

##### internet_on(self)

##### on_basemap_pressed(self)

##### enable_button(self, n)

This method Unable or Enable the GUI buttons on browse modality

##### enable_button_search(self, n)

This method Unable or Enable the GUI buttons on searching modality

##### on_pushButton_connect_pressed(self)

This method establishes a connection between GUI and database

##### charge_list(self)

##### on_pushButton_pdf_pressed(self)

##### on_pushButton_sort_pressed(self)

##### on_pushButton_new_rec_pressed(self)

##### on_pushButton_save_pressed(self)

##### data_error_check(self)

##### insert_new_rec(self)

##### check_record_state(self)

##### on_pushButton_view_all_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_delete_pressed(self)

##### on_pushButton_new_search_pressed(self)

##### msg_sito(self)

##### set_sito(self)

##### on_pushButton_search_go_pressed(self)

##### on_pushButton_test_pressed(self)

##### on_pushButton_draw_pressed(self)

##### on_pushButton_sites_geometry_pressed(self)

##### on_pushButton_draw_sito_pressed(self)

##### on_pushButton_rel_pdf_pressed(self)

##### on_toolButton_draw_siti_toggled(self)

##### on_pushButton_genera_us_pressed(self)

##### update_if(self, msg)

##### charge_records(self)

##### datestrfdate(self)

##### table2dict(self, n)

##### empty_fields(self)

##### fill_fields(self, n)

##### set_rec_counter(self, t, c)

##### check_for_updates(self)

Check if current record has been modified by others

##### closeEvent(self, event)

Handle form close event - stop refresh timer

##### set_LIST_REC_TEMP(self)

##### set_LIST_REC_CORR(self)

##### setComboBoxEnable(self, f, v)

##### setComboBoxEditable(self, f, n)

##### rec_toupdate(self)

##### records_equal_check(self)

##### update_record(self)

##### testing(self, name_file, message)

##### get_config(self, key, default)

##### set_config(self, key, value)

##### reverse(self)

##### reverse_action(self, point)

##### on_pushButton_locate_pressed(self)

##### logMessage(self, msg)

##### get_geocoder_instance(self)

Loads a concrete Geocoder class

##### process_point(self, place, point)

Transforms the point and save

##### save_point(self, point, address)

##### check_settings(self)

### GeoCodeException

**Inherits from**: Exception

### OsmGeoCoder

#### Methods

##### geocode(self, address)

##### reverse(self, lon, lat)

single result

### QgsMapLayerRegistry

### pyarchinit_Site

This class provides to manage the Site Sheet

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### on_pushButton_movecost_pressed(self)

##### on_pushButton_movecost_p_pressed(self)

##### on_pushButton_movebound_pressed(self)

##### on_pushButton_movebound_p_pressed(self)

##### on_pushButton_movecorr_pressed(self)

##### on_pushButton_movecorr_p_pressed(self)

##### on_pushButton_movealloc_pressed(self)

##### on_pushButton_movealloc_p_pressed(self)

##### defaultScriptsFolder(self)

##### on_pushButton_add_script_pressed(self)

##### setPathToSites(self)

##### openSiteDir(self)

##### on_wms_vincoli_pressed(self)

##### internet_on(self)

##### on_basemap_pressed(self)

##### enable_button(self, n)

This method Unable or Enable the GUI buttons on browse modality

##### enable_button_search(self, n)

This method Unable or Enable the GUI buttons on searching modality

##### on_pushButton_connect_pressed(self)

This method establishes a connection between GUI and database

##### charge_list(self)

##### on_pushButton_pdf_pressed(self)

##### on_pushButton_sort_pressed(self)

##### on_pushButton_new_rec_pressed(self)

##### on_pushButton_save_pressed(self)

##### data_error_check(self)

##### insert_new_rec(self)

##### check_record_state(self)

##### on_pushButton_view_all_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_delete_pressed(self)

##### on_pushButton_new_search_pressed(self)

##### msg_sito(self)

##### set_sito(self)

##### on_pushButton_search_go_pressed(self)

##### on_pushButton_test_pressed(self)

##### on_pushButton_draw_pressed(self)

##### on_pushButton_sites_geometry_pressed(self)

##### on_pushButton_draw_sito_pressed(self)

##### on_pushButton_rel_pdf_pressed(self)

##### on_toolButton_draw_siti_toggled(self)

##### on_pushButton_genera_us_pressed(self)

##### update_if(self, msg)

##### charge_records(self)

##### datestrfdate(self)

##### table2dict(self, n)

##### empty_fields(self)

##### fill_fields(self, n)

##### set_rec_counter(self, t, c)

##### check_for_updates(self)

Check if current record has been modified by others

##### closeEvent(self, event)

Handle form close event - stop refresh timer

##### set_LIST_REC_TEMP(self)

##### set_LIST_REC_CORR(self)

##### setComboBoxEnable(self, f, v)

##### setComboBoxEditable(self, f, n)

##### rec_toupdate(self)

##### records_equal_check(self)

##### update_record(self)

##### testing(self, name_file, message)

##### get_config(self, key, default)

##### set_config(self, key, value)

##### reverse(self)

##### reverse_action(self, point)

##### on_pushButton_locate_pressed(self)

##### logMessage(self, msg)

##### get_geocoder_instance(self)

Loads a concrete Geocoder class

##### process_point(self, place, point)

Transforms the point and save

##### save_point(self, point, address)

##### check_settings(self)

### GeoCodeException

**Inherits from**: Exception

### OsmGeoCoder

#### Methods

##### geocode(self, address)

##### reverse(self, lon, lat)

single result

## Functions

### logMessage(msg)

**Parameters:**
- `msg`

### logMessage(msg)

**Parameters:**
- `msg`

### logMessage(msg)

**Parameters:**
- `msg`

