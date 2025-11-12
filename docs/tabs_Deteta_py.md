# tabs/Deteta.py

## Overview

This file contains 306 documented elements.

## Classes

### pyarchinit_Deteta

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### enable_button(self, n)

##### enable_button_search(self, n)

##### enable_button_Suchey_Brooks(self, n)

##### enable_button_Kimmerle_m(self, n)

##### enable_button_Kimmerle_f(self, n)

##### on_pushButton_connect_pressed(self)

##### customize_GUI(self)

##### loadMapPreview(self, mode)

##### charge_list(self)

##### msg_sito(self)

##### set_sito(self)

##### charge_periodo_list(self)

##### charge_fase_iniz_list(self)

##### charge_fase_fin_list(self)

##### generate_list_pdf(self)

##### on_toolButtonPan_toggled(self)

##### on_pushButton_sort_pressed(self)

##### on_toolButtonGis_toggled(self)

##### on_toolButtonPreview_toggled(self)

##### on_pushButton_new_rec_pressed(self)

##### on_pushButton_save_pressed(self)

##### data_error_check(self)

##### insert_new_rec(self)

##### check_record_state(self)

##### on_pushButton_insert_row_rapporti_pressed(self)

##### on_pushButton_insert_row_inclusi_pressed(self)

##### on_pushButton_insert_row_campioni_pressed(self)

##### on_pushButton_view_all_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_delete_pressed(self)

##### on_pushButton_new_search_pressed(self)

##### on_pushButton_search_go_pressed(self)

##### update_if(self, msg)

##### charge_records(self)

##### datestrfdate(self)

##### table2dict(self, n)

##### tableInsertData(self, t, d)

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### empty_fields(self)

##### fill_fields(self, n)

##### set_rec_counter(self, t, c)

##### set_LIST_REC_TEMP(self)

##### set_LIST_REC_CORR(self)

##### records_equal_check(self)

##### setComboBoxEditable(self, f, n)

##### setComboBoxEnable(self, f, v)

##### update_record(self)

##### rec_toupdate(self)

##### charge_id_us_for_individuo(self)

##### on_pushButton_openSinfisi_pubica_pressed(self)

##### on_pushButton_openSinfisi_pubica_2_pressed(self)

##### sex_from_individuo_table(self)

##### on_pushButton_SSPIA_pressed(self)

##### on_pushButton_SSPIB_pressed(self)

##### on_pushButton_SSPIC_pressed(self)

##### on_pushButton_SSPID_pressed(self)

##### on_pushButton_mascellare_superiore_pressed(self)

##### on_pushButton_mascellare_inferiore_pressed(self)

##### on_pushButton_suture_endocraniche_pressed(self)

##### on_pushButton_suture_ectocraniche_pressed(self)

##### open_tables_det_eta(self, n)

##### on_pushButton_I_fase_pressed(self)

##### on_pushButton_II_fase_pressed(self)

##### on_pushButton_III_fase_pressed(self)

##### on_pushButton_IV_fase_pressed(self)

##### on_pushButton_V_fase_pressed(self)

##### on_pushButton_VI_fase_pressed(self)

##### on_pushButton_f_1_pressed(self)

##### on_pushButton_f_2_pressed(self)

##### on_pushButton_f_3_pressed(self)

##### on_pushButton_f_4_pressed(self)

##### on_pushButton_f_5_pressed(self)

##### on_pushButton_f_6_pressed(self)

##### on_pushButton_f_7_pressed(self)

##### on_pushButton_f_8_pressed(self)

##### on_pushButton_sup_aur_pressed(self)

##### on_pushButton_ms_sup_12_18_pressed(self)

##### on_pushButton_ms_sup_16_20_pressed(self)

##### on_pushButton_ms_sup_18_22_pressed(self)

##### on_pushButton_ms_sup_20_24_pressed(self)

##### on_pushButton_ms_sup_24_30_pressed(self)

##### on_pushButton_ms_sup_30_35_pressed(self)

##### on_pushButton_ms_sup_35_40_pressed(self)

##### on_pushButton_ms_sup_40_50_pressed(self)

##### on_pushButton_ms_inf_12_18_pressed(self)

##### on_pushButton_ms_inf_16_20_pressed(self)

##### on_pushButton_ms_inf_18_22_pressed(self)

##### on_pushButton_ms_inf_20_24_pressed(self)

##### on_pushButton_ms_inf_24_30_pressed(self)

##### on_pushButton_ms_inf_30_35_pressed(self)

##### on_pushButton_ms_inf_35_40_pressed(self)

##### on_pushButton_ms_inf_40_45_pressed(self)

##### on_pushButton_ms_inf_45_55_pressed(self)

##### on_pushButton_range_sut_end_pressed(self)

##### on_pushButton_calcola_volta_ant_lat_clicked(self)

##### testing(self, name_file, message)

### pyarchinit_Deteta

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### enable_button(self, n)

##### enable_button_search(self, n)

##### enable_button_Suchey_Brooks(self, n)

##### enable_button_Kimmerle_m(self, n)

##### enable_button_Kimmerle_f(self, n)

##### on_pushButton_connect_pressed(self)

##### customize_GUI(self)

##### loadMapPreview(self, mode)

##### charge_list(self)

##### msg_sito(self)

##### set_sito(self)

##### charge_periodo_list(self)

##### charge_fase_iniz_list(self)

##### charge_fase_fin_list(self)

##### generate_list_pdf(self)

##### on_toolButtonPan_toggled(self)

##### on_pushButton_sort_pressed(self)

##### on_toolButtonGis_toggled(self)

##### on_toolButtonPreview_toggled(self)

##### on_pushButton_new_rec_pressed(self)

##### on_pushButton_save_pressed(self)

##### data_error_check(self)

##### insert_new_rec(self)

##### check_record_state(self)

##### on_pushButton_insert_row_rapporti_pressed(self)

##### on_pushButton_insert_row_inclusi_pressed(self)

##### on_pushButton_insert_row_campioni_pressed(self)

##### on_pushButton_view_all_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_delete_pressed(self)

##### on_pushButton_new_search_pressed(self)

##### on_pushButton_search_go_pressed(self)

##### update_if(self, msg)

##### charge_records(self)

##### datestrfdate(self)

##### table2dict(self, n)

##### tableInsertData(self, t, d)

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### empty_fields(self)

##### fill_fields(self, n)

##### set_rec_counter(self, t, c)

##### set_LIST_REC_TEMP(self)

##### set_LIST_REC_CORR(self)

##### records_equal_check(self)

##### setComboBoxEditable(self, f, n)

##### setComboBoxEnable(self, f, v)

##### update_record(self)

##### rec_toupdate(self)

##### charge_id_us_for_individuo(self)

##### on_pushButton_openSinfisi_pubica_pressed(self)

##### on_pushButton_openSinfisi_pubica_2_pressed(self)

##### sex_from_individuo_table(self)

##### on_pushButton_SSPIA_pressed(self)

##### on_pushButton_SSPIB_pressed(self)

##### on_pushButton_SSPIC_pressed(self)

##### on_pushButton_SSPID_pressed(self)

##### on_pushButton_mascellare_superiore_pressed(self)

##### on_pushButton_mascellare_inferiore_pressed(self)

##### on_pushButton_suture_endocraniche_pressed(self)

##### on_pushButton_suture_ectocraniche_pressed(self)

##### open_tables_det_eta(self, n)

##### on_pushButton_I_fase_pressed(self)

##### on_pushButton_II_fase_pressed(self)

##### on_pushButton_III_fase_pressed(self)

##### on_pushButton_IV_fase_pressed(self)

##### on_pushButton_V_fase_pressed(self)

##### on_pushButton_VI_fase_pressed(self)

##### on_pushButton_f_1_pressed(self)

##### on_pushButton_f_2_pressed(self)

##### on_pushButton_f_3_pressed(self)

##### on_pushButton_f_4_pressed(self)

##### on_pushButton_f_5_pressed(self)

##### on_pushButton_f_6_pressed(self)

##### on_pushButton_f_7_pressed(self)

##### on_pushButton_f_8_pressed(self)

##### on_pushButton_sup_aur_pressed(self)

##### on_pushButton_ms_sup_12_18_pressed(self)

##### on_pushButton_ms_sup_16_20_pressed(self)

##### on_pushButton_ms_sup_18_22_pressed(self)

##### on_pushButton_ms_sup_20_24_pressed(self)

##### on_pushButton_ms_sup_24_30_pressed(self)

##### on_pushButton_ms_sup_30_35_pressed(self)

##### on_pushButton_ms_sup_35_40_pressed(self)

##### on_pushButton_ms_sup_40_50_pressed(self)

##### on_pushButton_ms_inf_12_18_pressed(self)

##### on_pushButton_ms_inf_16_20_pressed(self)

##### on_pushButton_ms_inf_18_22_pressed(self)

##### on_pushButton_ms_inf_20_24_pressed(self)

##### on_pushButton_ms_inf_24_30_pressed(self)

##### on_pushButton_ms_inf_30_35_pressed(self)

##### on_pushButton_ms_inf_35_40_pressed(self)

##### on_pushButton_ms_inf_40_45_pressed(self)

##### on_pushButton_ms_inf_45_55_pressed(self)

##### on_pushButton_range_sut_end_pressed(self)

##### on_pushButton_calcola_volta_ant_lat_clicked(self)

##### testing(self, name_file, message)

### pyarchinit_Deteta

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### enable_button(self, n)

##### enable_button_search(self, n)

##### enable_button_Suchey_Brooks(self, n)

##### enable_button_Kimmerle_m(self, n)

##### enable_button_Kimmerle_f(self, n)

##### on_pushButton_connect_pressed(self)

##### customize_GUI(self)

##### loadMapPreview(self, mode)

##### charge_list(self)

##### msg_sito(self)

##### set_sito(self)

##### charge_periodo_list(self)

##### charge_fase_iniz_list(self)

##### charge_fase_fin_list(self)

##### generate_list_pdf(self)

##### on_toolButtonPan_toggled(self)

##### on_pushButton_sort_pressed(self)

##### on_toolButtonGis_toggled(self)

##### on_toolButtonPreview_toggled(self)

##### on_pushButton_new_rec_pressed(self)

##### on_pushButton_save_pressed(self)

##### data_error_check(self)

##### insert_new_rec(self)

##### check_record_state(self)

##### on_pushButton_insert_row_rapporti_pressed(self)

##### on_pushButton_insert_row_inclusi_pressed(self)

##### on_pushButton_insert_row_campioni_pressed(self)

##### on_pushButton_view_all_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_delete_pressed(self)

##### on_pushButton_new_search_pressed(self)

##### on_pushButton_search_go_pressed(self)

##### update_if(self, msg)

##### charge_records(self)

##### datestrfdate(self)

##### table2dict(self, n)

##### tableInsertData(self, t, d)

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### empty_fields(self)

##### fill_fields(self, n)

##### set_rec_counter(self, t, c)

##### set_LIST_REC_TEMP(self)

##### set_LIST_REC_CORR(self)

##### records_equal_check(self)

##### setComboBoxEditable(self, f, n)

##### setComboBoxEnable(self, f, v)

##### update_record(self)

##### rec_toupdate(self)

##### charge_id_us_for_individuo(self)

##### on_pushButton_openSinfisi_pubica_pressed(self)

##### on_pushButton_openSinfisi_pubica_2_pressed(self)

##### sex_from_individuo_table(self)

##### on_pushButton_SSPIA_pressed(self)

##### on_pushButton_SSPIB_pressed(self)

##### on_pushButton_SSPIC_pressed(self)

##### on_pushButton_SSPID_pressed(self)

##### on_pushButton_mascellare_superiore_pressed(self)

##### on_pushButton_mascellare_inferiore_pressed(self)

##### on_pushButton_suture_endocraniche_pressed(self)

##### on_pushButton_suture_ectocraniche_pressed(self)

##### open_tables_det_eta(self, n)

##### on_pushButton_I_fase_pressed(self)

##### on_pushButton_II_fase_pressed(self)

##### on_pushButton_III_fase_pressed(self)

##### on_pushButton_IV_fase_pressed(self)

##### on_pushButton_V_fase_pressed(self)

##### on_pushButton_VI_fase_pressed(self)

##### on_pushButton_f_1_pressed(self)

##### on_pushButton_f_2_pressed(self)

##### on_pushButton_f_3_pressed(self)

##### on_pushButton_f_4_pressed(self)

##### on_pushButton_f_5_pressed(self)

##### on_pushButton_f_6_pressed(self)

##### on_pushButton_f_7_pressed(self)

##### on_pushButton_f_8_pressed(self)

##### on_pushButton_sup_aur_pressed(self)

##### on_pushButton_ms_sup_12_18_pressed(self)

##### on_pushButton_ms_sup_16_20_pressed(self)

##### on_pushButton_ms_sup_18_22_pressed(self)

##### on_pushButton_ms_sup_20_24_pressed(self)

##### on_pushButton_ms_sup_24_30_pressed(self)

##### on_pushButton_ms_sup_30_35_pressed(self)

##### on_pushButton_ms_sup_35_40_pressed(self)

##### on_pushButton_ms_sup_40_50_pressed(self)

##### on_pushButton_ms_inf_12_18_pressed(self)

##### on_pushButton_ms_inf_16_20_pressed(self)

##### on_pushButton_ms_inf_18_22_pressed(self)

##### on_pushButton_ms_inf_20_24_pressed(self)

##### on_pushButton_ms_inf_24_30_pressed(self)

##### on_pushButton_ms_inf_30_35_pressed(self)

##### on_pushButton_ms_inf_35_40_pressed(self)

##### on_pushButton_ms_inf_40_45_pressed(self)

##### on_pushButton_ms_inf_45_55_pressed(self)

##### on_pushButton_range_sut_end_pressed(self)

##### on_pushButton_calcola_volta_ant_lat_clicked(self)

##### testing(self, name_file, message)

