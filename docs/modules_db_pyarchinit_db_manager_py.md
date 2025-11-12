# modules/db/pyarchinit_db_manager.py

## Overview

This file contains 504 documented elements.

## Classes

### Pyarchinit_db_management

**Inherits from**: object

#### Methods

##### __init__(self, c)

##### load_spatialite(self, dbapi_conn, connection_record)

##### connection(self)

##### ensure_tma_tables_exist(self)

Ensure TMA tables are created if they don't exist

##### fix_macc_field_sqlite(self)

Fix macc field in tma_materiali_ripetibili table for SQLite databases

##### insert_pottery_values(self)

Istanzia la classe POTTERY da pyarchinit_db_mapper

##### insert_pyus(self)

##### insert_pyusm(self)

##### insert_pysito_point(self)

##### insert_pysito_polygon(self)

##### insert_pyquote(self)

##### insert_pyquote_usm(self)

##### insert_pyus_negative(self)

##### insert_pystrutture(self)

##### insert_pyreperti(self)

##### insert_pyindividui(self)

##### insert_pycampioni(self)

##### insert_pytomba(self)

##### insert_pydocumentazione(self)

##### insert_pylineeriferimento(self)

##### insert_pyripartizioni_spaziali(self)

##### insert_pysezioni(self)

##### insert_values(self)

Istanzia la classe US da pyarchinit_db_mapper

##### insert_ut_values(self)

Istanzia la classe UT da pyarchinit_db_mapper

##### insert_site_values(self)

Istanzia la classe SITE da pyarchinit_db_mapper

##### insert_periodizzazione_values(self)

Istanzia la classe Periodizzazione da pyarchinit_db_mapper

##### insert_values_reperti(self)

Istanzia la classe Reperti da pyarchinit_db_mapper

##### insert_struttura_values(self)

Istanzia la classe Struttura da pyarchinit_db_mapper

##### insert_values_ind(self)

Istanzia la classe SCHEDAIND da pyarchinit_db_mapper

##### insert_values_detsesso(self)

Istanzia la classe DETSESSO da pyarchinit_db_mapper

##### insert_values_deteta(self)

Istanzia la classe DETETA da pyarchinit_db_mapper

##### insert_media_values(self)

Istanzia la classe MEDIA da pyarchinit_db_mapper

##### insert_mediathumb_values(self)

Istanzia la classe MEDIA da pyarchinit_db_mapper

##### insert_media2entity_values(self)

Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper

##### insert_media2entity_view_values(self)

Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper

##### insert_values_tomba(self)

Istanzia la classe TOMBA da pyarchinit_db_mapper

##### insert_values_campioni(self)

Istanzia la classe CAMPIONI da pyarchinit_db_mapper

##### insert_values_thesaurus(self)

Istanzia la classe PYARCHINIT_THESAURUS_SIGLE da pyarchinit_db_mapper

##### insert_values_Lapidei(self)

Istanzia la classe Inventario_Lapidei da pyarchinit_db_mapper

##### insert_values_documentazione(self)

Istanzia la classe DOCUMENTAZIONE da pyarchinit_db_mapper

##### insert_pdf_administrator_values(self)

Istanzia la classe PDF_ADMINISTRATOR da pyarchinit_db_mapper

##### insert_campioni_values(self)

Istanzia la classe CAMPIONI da pyarchinit_db_mapper

##### insert_tma_values(self)

Istanzia la classe TMA da pyarchinit_db_mapper

##### insert_tma_materiali_values(self)

Istanzia la classe TMA_MATERIALI da pyarchinit_db_mapper

##### insert_media_to_entity_values(self)

Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper

##### execute_sql_create_db(self)

##### execute_sql_create_spatialite_db(self)

##### execute_sql_create_layers(self)

##### execute_sql(self, query_string, params)

Execute a raw SQL query and return results

##### query(self, n)

##### query_limit_offset(self, table_name, filter_text, limit, offset)

##### count_total_images(self, table_name, filter_text)

##### query_bool_us(self, params, table_class)

##### query_bool_like(self, params, table, join_operator)

##### query_bool_postgres(self, params, table)

##### query_sql(self, query)

Execute raw SQL query and return results

##### query_bool(self, params, table_class_name)

##### select_mediapath_from_id(self, media_id)

##### query_all_us(self, table_class_str, column_name)

Retrieve all records from a specified table and return values of a specific column.

:param table_class_str: The name of the table class as a string.
:param column_name: The name of the column to retrieve values from.
:return: A list of values from the specified column of all records.

##### query_all(self, table_class_str)

Retrieve all records from a specified table.

:param table_class_str: The name of the table class as a string.
:return: A list of all records from the specified table.

##### query_bool_special(self, params, table)

##### query_operator(self, params, table)

##### query_distinct(self, table, query_params, distinct_field_name_params)

##### query_distinct_sql(self, table, query_params, distinct_field_name_params)

##### insert_data_session(self, data)

##### insert_data_conflict(self, data)

##### update(self, table_class_str, id_table_str, value_id_list, columns_name_list, values_update_list)

Receives 5 values then putted in a list. The values must be passed
in this order: table name->string, column_name_where->list containin'
one value
('site_table', 'id_sito', [1], ['sito', 'nazione', 'regione', 'comune', 'descrizione', 'provincia'], ['Sito archeologico 1', 'Italiauiodsds', 'Emilia-Romagna', 'Riminijk', 'Sito di epoca altomedievale....23', 'Riminikljlks'])
self.set_update = arg
#self.connection()
table = Table(self.set_update[0], self.metadata, autoload=True)
changes_dict= {}
u = Utility()
set_update_4 = u.deunicode_list(self.set_update[4])

u.add_item_to_dict(changes_dict,zip(self.set_update[3], set_update_4))

f = open("test_update.txt", "w")
f.write(str(self.set_update))
f.close()

exec_str = ('%s%s%s%s%s%s%s') % ("table.update(table.c.",
                                  self.set_update[1],
                                 " == '",
                                 self.set_update[2][0],
                                 "').execute(",
                                 changes_dict ,")")

#session.query(SITE).filter(and_(SITE.id_sito == '1')).update(values = {SITE.sito:"updatetest"})

##### update_tomba_dating_from_periodizzazione(self, site_name)

##### update_us_dating_from_periodizzazione(self, site_name)

##### update_find_check(self, table_class_str, id_table_str, value_id, find_check_value)

##### empty_find_check(self, table_class_str, find_check_value)

##### delete_one_record(self, tn, id_col, id_rec)

##### delete_record_by_field(self, table_name, field_name, field_value)

Delete records from a table where field matches value

##### max_num_id(self, tc, f)

##### dir_query(self)

##### fields_list(self, t, s)

return the list of columns in a table. If s is set a int,
return only one column

##### query_in_idus(self, id_list)

##### query_sort(self, id_list, op, to, tc, idn)

##### run(self, stmt)

##### update_for(self)

table = Table('us_table_toimp', self.metadata, autoload=True)
s = table.select(table.c.id_us > 0)
res_list = self.run(s)
cont = 11900
for i in res_list:
    self.update('US_toimp', 'id_us', [i], ['id_us'], [cont])
    cont = cont+1

##### group_by(self, tn, fn, CD)

Group by the values by table name - string, field name - string, table class DB from mapper - string

##### query_where_text(self, c, v)

##### update_cont_per(self, s)

##### remove_alltags_from_db_sql(self, s)

##### remove_tags_from_db_sql(self, s)

##### remove_tags_from_db_sql_scheda(self, s, n)

##### delete_thumb_from_db_sql(self, s)

##### select_medianame_from_st_sql(self, sito, sigla, numero)

##### select_medianame_from_db_sql(self, sito, area)

##### select_medianame_tb_from_db_sql(self, sito, area)

##### select_medianame_pot_from_db_sql(self, sito, area, us)

##### select_medianame_ra_from_db_sql(self, sito, area, us)

##### select_medianame_2_from_db_sql(self, sito, area, us)

##### get_total_pages(self, filter_query, page_size)

##### select_thumb(self, page_number, page_size)

##### select_original(self, page_number, page_size)

##### select_ra_from_db_sql(self, sito, area, us)

##### select_coord_from_db_sql(self, sito, area, us)

##### select_medianame_3_from_db_sql(self, sito, area, us)

##### select_thumbnail_from_db_sql(self, sito)

##### select_quote_from_db_sql(self, sito, area, us)

##### select_us_from_db_sql(self, sito, area, us, stratigraph_index_us)

##### select_us_doc_from_db_sql(self, sito, tipo_doc, nome_doc)

##### select_usneg_doc_from_db_sql(self, sito, tipo_doc, nome_doc)

##### select_db_sql(self, table)

##### select_db_sql_2(self, sito, area, us, d_stratigrafica)

##### test_ut_sql(self, unita_tipo)

##### query_in_contains_onlysqlite(self, value_list, sitof, areaf, chunk_size)

Esegue una query suddividendo la lista dei valori in chunk per evitare il limite di profondità di SQLite.

Args:
    value_list (list): Lista di valori da cercare.
    sitof (str): Valore per il filtro 'sito'.
    areaf (str): Valore per il filtro 'area'.
    chunk_size (int): Dimensione dei chunk. Default è 100.

Returns:
    list: Lista dei risultati della query.

##### query_in_contains(self, value_list, sitof, areaf)

##### insert_arbitrary_number_of_us_records(self, us_range, sito, area, n_us, unita_tipo)

##### insert_number_of_rapporti_records(self, sito, area, n_us, n_rapporti, unita_tipo)

##### insert_number_of_us_records(self, sito, area, n_us, unita_tipo)

##### insert_number_of_reperti_records(self, sito, numero_inventario)

##### insert_number_of_pottery_records(self, id_number, sito, area, us)

##### insert_number_of_tomba_records(self, sito, nr_scheda_taf)

##### insert_struttura_records(self, sito, sigla_struttura, numero_struttura)

##### select_like_from_db_sql(self, rapp_list, us_rapp_list)

##### select_not_like_from_db_sql(self, sitof, areaf)

##### query_in_idusb(self)

### ANSI

#### Methods

##### background(code)

##### style_text(code)

##### color_text(code)

### Pyarchinit_db_management

**Inherits from**: object

#### Methods

##### __init__(self, c)

##### load_spatialite(self, dbapi_conn, connection_record)

##### connection(self)

##### ensure_tma_tables_exist(self)

Ensure TMA tables are created if they don't exist

##### fix_macc_field_sqlite(self)

Fix macc field in tma_materiali_ripetibili table for SQLite databases

##### insert_pottery_values(self)

Istanzia la classe POTTERY da pyarchinit_db_mapper

##### insert_pyus(self)

##### insert_pyusm(self)

##### insert_pysito_point(self)

##### insert_pysito_polygon(self)

##### insert_pyquote(self)

##### insert_pyquote_usm(self)

##### insert_pyus_negative(self)

##### insert_pystrutture(self)

##### insert_pyreperti(self)

##### insert_pyindividui(self)

##### insert_pycampioni(self)

##### insert_pytomba(self)

##### insert_pydocumentazione(self)

##### insert_pylineeriferimento(self)

##### insert_pyripartizioni_spaziali(self)

##### insert_pysezioni(self)

##### insert_values(self)

Istanzia la classe US da pyarchinit_db_mapper

##### insert_ut_values(self)

Istanzia la classe UT da pyarchinit_db_mapper

##### insert_site_values(self)

Istanzia la classe SITE da pyarchinit_db_mapper

##### insert_periodizzazione_values(self)

Istanzia la classe Periodizzazione da pyarchinit_db_mapper

##### insert_values_reperti(self)

Istanzia la classe Reperti da pyarchinit_db_mapper

##### insert_struttura_values(self)

Istanzia la classe Struttura da pyarchinit_db_mapper

##### insert_values_ind(self)

Istanzia la classe SCHEDAIND da pyarchinit_db_mapper

##### insert_values_detsesso(self)

Istanzia la classe DETSESSO da pyarchinit_db_mapper

##### insert_values_deteta(self)

Istanzia la classe DETETA da pyarchinit_db_mapper

##### insert_media_values(self)

Istanzia la classe MEDIA da pyarchinit_db_mapper

##### insert_mediathumb_values(self)

Istanzia la classe MEDIA da pyarchinit_db_mapper

##### insert_media2entity_values(self)

Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper

##### insert_media2entity_view_values(self)

Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper

##### insert_values_tomba(self)

Istanzia la classe TOMBA da pyarchinit_db_mapper

##### insert_values_campioni(self)

Istanzia la classe CAMPIONI da pyarchinit_db_mapper

##### insert_values_thesaurus(self)

Istanzia la classe PYARCHINIT_THESAURUS_SIGLE da pyarchinit_db_mapper

##### insert_values_Lapidei(self)

Istanzia la classe Inventario_Lapidei da pyarchinit_db_mapper

##### insert_values_documentazione(self)

Istanzia la classe DOCUMENTAZIONE da pyarchinit_db_mapper

##### insert_pdf_administrator_values(self)

Istanzia la classe PDF_ADMINISTRATOR da pyarchinit_db_mapper

##### insert_campioni_values(self)

Istanzia la classe CAMPIONI da pyarchinit_db_mapper

##### insert_tma_values(self)

Istanzia la classe TMA da pyarchinit_db_mapper

##### insert_tma_materiali_values(self)

Istanzia la classe TMA_MATERIALI da pyarchinit_db_mapper

##### insert_media_to_entity_values(self)

Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper

##### execute_sql_create_db(self)

##### execute_sql_create_spatialite_db(self)

##### execute_sql_create_layers(self)

##### execute_sql(self, query_string, params)

Execute a raw SQL query and return results

##### query(self, n)

##### query_limit_offset(self, table_name, filter_text, limit, offset)

##### count_total_images(self, table_name, filter_text)

##### query_bool_us(self, params, table_class)

##### query_bool_like(self, params, table, join_operator)

##### query_bool_postgres(self, params, table)

##### query_sql(self, query)

Execute raw SQL query and return results

##### query_bool(self, params, table_class_name)

##### select_mediapath_from_id(self, media_id)

##### query_all_us(self, table_class_str, column_name)

Retrieve all records from a specified table and return values of a specific column.

:param table_class_str: The name of the table class as a string.
:param column_name: The name of the column to retrieve values from.
:return: A list of values from the specified column of all records.

##### query_all(self, table_class_str)

Retrieve all records from a specified table.

:param table_class_str: The name of the table class as a string.
:return: A list of all records from the specified table.

##### query_bool_special(self, params, table)

##### query_operator(self, params, table)

##### query_distinct(self, table, query_params, distinct_field_name_params)

##### query_distinct_sql(self, table, query_params, distinct_field_name_params)

##### insert_data_session(self, data)

##### insert_data_conflict(self, data)

##### update(self, table_class_str, id_table_str, value_id_list, columns_name_list, values_update_list)

Receives 5 values then putted in a list. The values must be passed
in this order: table name->string, column_name_where->list containin'
one value
('site_table', 'id_sito', [1], ['sito', 'nazione', 'regione', 'comune', 'descrizione', 'provincia'], ['Sito archeologico 1', 'Italiauiodsds', 'Emilia-Romagna', 'Riminijk', 'Sito di epoca altomedievale....23', 'Riminikljlks'])
self.set_update = arg
#self.connection()
table = Table(self.set_update[0], self.metadata, autoload=True)
changes_dict= {}
u = Utility()
set_update_4 = u.deunicode_list(self.set_update[4])

u.add_item_to_dict(changes_dict,zip(self.set_update[3], set_update_4))

f = open("test_update.txt", "w")
f.write(str(self.set_update))
f.close()

exec_str = ('%s%s%s%s%s%s%s') % ("table.update(table.c.",
                                  self.set_update[1],
                                 " == '",
                                 self.set_update[2][0],
                                 "').execute(",
                                 changes_dict ,")")

#session.query(SITE).filter(and_(SITE.id_sito == '1')).update(values = {SITE.sito:"updatetest"})

##### update_tomba_dating_from_periodizzazione(self, site_name)

##### update_us_dating_from_periodizzazione(self, site_name)

##### update_find_check(self, table_class_str, id_table_str, value_id, find_check_value)

##### empty_find_check(self, table_class_str, find_check_value)

##### delete_one_record(self, tn, id_col, id_rec)

##### delete_record_by_field(self, table_name, field_name, field_value)

Delete records from a table where field matches value

##### max_num_id(self, tc, f)

##### dir_query(self)

##### fields_list(self, t, s)

return the list of columns in a table. If s is set a int,
return only one column

##### query_in_idus(self, id_list)

##### query_sort(self, id_list, op, to, tc, idn)

##### run(self, stmt)

##### update_for(self)

table = Table('us_table_toimp', self.metadata, autoload=True)
s = table.select(table.c.id_us > 0)
res_list = self.run(s)
cont = 11900
for i in res_list:
    self.update('US_toimp', 'id_us', [i], ['id_us'], [cont])
    cont = cont+1

##### group_by(self, tn, fn, CD)

Group by the values by table name - string, field name - string, table class DB from mapper - string

##### query_where_text(self, c, v)

##### update_cont_per(self, s)

##### remove_alltags_from_db_sql(self, s)

##### remove_tags_from_db_sql(self, s)

##### remove_tags_from_db_sql_scheda(self, s, n)

##### delete_thumb_from_db_sql(self, s)

##### select_medianame_from_st_sql(self, sito, sigla, numero)

##### select_medianame_from_db_sql(self, sito, area)

##### select_medianame_tb_from_db_sql(self, sito, area)

##### select_medianame_pot_from_db_sql(self, sito, area, us)

##### select_medianame_ra_from_db_sql(self, sito, area, us)

##### select_medianame_2_from_db_sql(self, sito, area, us)

##### get_total_pages(self, filter_query, page_size)

##### select_thumb(self, page_number, page_size)

##### select_original(self, page_number, page_size)

##### select_ra_from_db_sql(self, sito, area, us)

##### select_coord_from_db_sql(self, sito, area, us)

##### select_medianame_3_from_db_sql(self, sito, area, us)

##### select_thumbnail_from_db_sql(self, sito)

##### select_quote_from_db_sql(self, sito, area, us)

##### select_us_from_db_sql(self, sito, area, us, stratigraph_index_us)

##### select_us_doc_from_db_sql(self, sito, tipo_doc, nome_doc)

##### select_usneg_doc_from_db_sql(self, sito, tipo_doc, nome_doc)

##### select_db_sql(self, table)

##### select_db_sql_2(self, sito, area, us, d_stratigrafica)

##### test_ut_sql(self, unita_tipo)

##### query_in_contains_onlysqlite(self, value_list, sitof, areaf, chunk_size)

Esegue una query suddividendo la lista dei valori in chunk per evitare il limite di profondità di SQLite.

Args:
    value_list (list): Lista di valori da cercare.
    sitof (str): Valore per il filtro 'sito'.
    areaf (str): Valore per il filtro 'area'.
    chunk_size (int): Dimensione dei chunk. Default è 100.

Returns:
    list: Lista dei risultati della query.

##### query_in_contains(self, value_list, sitof, areaf)

##### insert_arbitrary_number_of_us_records(self, us_range, sito, area, n_us, unita_tipo)

##### insert_number_of_rapporti_records(self, sito, area, n_us, n_rapporti, unita_tipo)

##### insert_number_of_us_records(self, sito, area, n_us, unita_tipo)

##### insert_number_of_reperti_records(self, sito, numero_inventario)

##### insert_number_of_pottery_records(self, id_number, sito, area, us)

##### insert_number_of_tomba_records(self, sito, nr_scheda_taf)

##### insert_struttura_records(self, sito, sigla_struttura, numero_struttura)

##### select_like_from_db_sql(self, rapp_list, us_rapp_list)

##### select_not_like_from_db_sql(self, sitof, areaf)

##### query_in_idusb(self)

### ANSI

#### Methods

##### background(code)

##### style_text(code)

##### color_text(code)

### Pyarchinit_db_management

**Inherits from**: object

#### Methods

##### __init__(self, c)

##### load_spatialite(self, dbapi_conn, connection_record)

##### connection(self)

##### ensure_tma_tables_exist(self)

Ensure TMA tables are created if they don't exist

##### fix_macc_field_sqlite(self)

Fix macc field in tma_materiali_ripetibili table for SQLite databases

##### insert_pottery_values(self)

Istanzia la classe POTTERY da pyarchinit_db_mapper

##### insert_pyus(self)

##### insert_pyusm(self)

##### insert_pysito_point(self)

##### insert_pysito_polygon(self)

##### insert_pyquote(self)

##### insert_pyquote_usm(self)

##### insert_pyus_negative(self)

##### insert_pystrutture(self)

##### insert_pyreperti(self)

##### insert_pyindividui(self)

##### insert_pycampioni(self)

##### insert_pytomba(self)

##### insert_pydocumentazione(self)

##### insert_pylineeriferimento(self)

##### insert_pyripartizioni_spaziali(self)

##### insert_pysezioni(self)

##### insert_values(self)

Istanzia la classe US da pyarchinit_db_mapper

##### insert_ut_values(self)

Istanzia la classe UT da pyarchinit_db_mapper

##### insert_site_values(self)

Istanzia la classe SITE da pyarchinit_db_mapper

##### insert_periodizzazione_values(self)

Istanzia la classe Periodizzazione da pyarchinit_db_mapper

##### insert_values_reperti(self)

Istanzia la classe Reperti da pyarchinit_db_mapper

##### insert_struttura_values(self)

Istanzia la classe Struttura da pyarchinit_db_mapper

##### insert_values_ind(self)

Istanzia la classe SCHEDAIND da pyarchinit_db_mapper

##### insert_values_detsesso(self)

Istanzia la classe DETSESSO da pyarchinit_db_mapper

##### insert_values_deteta(self)

Istanzia la classe DETETA da pyarchinit_db_mapper

##### insert_media_values(self)

Istanzia la classe MEDIA da pyarchinit_db_mapper

##### insert_mediathumb_values(self)

Istanzia la classe MEDIA da pyarchinit_db_mapper

##### insert_media2entity_values(self)

Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper

##### insert_media2entity_view_values(self)

Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper

##### insert_values_tomba(self)

Istanzia la classe TOMBA da pyarchinit_db_mapper

##### insert_values_campioni(self)

Istanzia la classe CAMPIONI da pyarchinit_db_mapper

##### insert_values_thesaurus(self)

Istanzia la classe PYARCHINIT_THESAURUS_SIGLE da pyarchinit_db_mapper

##### insert_values_Lapidei(self)

Istanzia la classe Inventario_Lapidei da pyarchinit_db_mapper

##### insert_values_documentazione(self)

Istanzia la classe DOCUMENTAZIONE da pyarchinit_db_mapper

##### insert_pdf_administrator_values(self)

Istanzia la classe PDF_ADMINISTRATOR da pyarchinit_db_mapper

##### insert_campioni_values(self)

Istanzia la classe CAMPIONI da pyarchinit_db_mapper

##### insert_tma_values(self)

Istanzia la classe TMA da pyarchinit_db_mapper

##### insert_tma_materiali_values(self)

Istanzia la classe TMA_MATERIALI da pyarchinit_db_mapper

##### insert_media_to_entity_values(self)

Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper

##### execute_sql_create_db(self)

##### execute_sql_create_spatialite_db(self)

##### execute_sql_create_layers(self)

##### execute_sql(self, query_string, params)

Execute a raw SQL query and return results

##### query(self, n)

##### query_limit_offset(self, table_name, filter_text, limit, offset)

##### count_total_images(self, table_name, filter_text)

##### query_bool_us(self, params, table_class)

##### query_bool_like(self, params, table, join_operator)

##### query_bool_postgres(self, params, table)

##### query_sql(self, query)

Execute raw SQL query and return results

##### query_bool(self, params, table_class_name)

##### select_mediapath_from_id(self, media_id)

##### query_all_us(self, table_class_str, column_name)

Retrieve all records from a specified table and return values of a specific column.

:param table_class_str: The name of the table class as a string.
:param column_name: The name of the column to retrieve values from.
:return: A list of values from the specified column of all records.

##### query_all(self, table_class_str)

Retrieve all records from a specified table.

:param table_class_str: The name of the table class as a string.
:return: A list of all records from the specified table.

##### query_bool_special(self, params, table)

##### query_operator(self, params, table)

##### query_distinct(self, table, query_params, distinct_field_name_params)

##### query_distinct_sql(self, table, query_params, distinct_field_name_params)

##### insert_data_session(self, data)

##### insert_data_conflict(self, data)

##### update(self, table_class_str, id_table_str, value_id_list, columns_name_list, values_update_list)

Receives 5 values then putted in a list. The values must be passed
in this order: table name->string, column_name_where->list containin'
one value
('site_table', 'id_sito', [1], ['sito', 'nazione', 'regione', 'comune', 'descrizione', 'provincia'], ['Sito archeologico 1', 'Italiauiodsds', 'Emilia-Romagna', 'Riminijk', 'Sito di epoca altomedievale....23', 'Riminikljlks'])
self.set_update = arg
#self.connection()
table = Table(self.set_update[0], self.metadata, autoload=True)
changes_dict= {}
u = Utility()
set_update_4 = u.deunicode_list(self.set_update[4])

u.add_item_to_dict(changes_dict,zip(self.set_update[3], set_update_4))

f = open("test_update.txt", "w")
f.write(str(self.set_update))
f.close()

exec_str = ('%s%s%s%s%s%s%s') % ("table.update(table.c.",
                                  self.set_update[1],
                                 " == '",
                                 self.set_update[2][0],
                                 "').execute(",
                                 changes_dict ,")")

#session.query(SITE).filter(and_(SITE.id_sito == '1')).update(values = {SITE.sito:"updatetest"})

##### update_tomba_dating_from_periodizzazione(self, site_name)

##### update_us_dating_from_periodizzazione(self, site_name)

##### update_find_check(self, table_class_str, id_table_str, value_id, find_check_value)

##### empty_find_check(self, table_class_str, find_check_value)

##### delete_one_record(self, tn, id_col, id_rec)

##### delete_record_by_field(self, table_name, field_name, field_value)

Delete records from a table where field matches value

##### max_num_id(self, tc, f)

##### dir_query(self)

##### fields_list(self, t, s)

return the list of columns in a table. If s is set a int,
return only one column

##### query_in_idus(self, id_list)

##### query_sort(self, id_list, op, to, tc, idn)

##### run(self, stmt)

##### update_for(self)

table = Table('us_table_toimp', self.metadata, autoload=True)
s = table.select(table.c.id_us > 0)
res_list = self.run(s)
cont = 11900
for i in res_list:
    self.update('US_toimp', 'id_us', [i], ['id_us'], [cont])
    cont = cont+1

##### group_by(self, tn, fn, CD)

Group by the values by table name - string, field name - string, table class DB from mapper - string

##### query_where_text(self, c, v)

##### update_cont_per(self, s)

##### remove_alltags_from_db_sql(self, s)

##### remove_tags_from_db_sql(self, s)

##### remove_tags_from_db_sql_scheda(self, s, n)

##### delete_thumb_from_db_sql(self, s)

##### select_medianame_from_st_sql(self, sito, sigla, numero)

##### select_medianame_from_db_sql(self, sito, area)

##### select_medianame_tb_from_db_sql(self, sito, area)

##### select_medianame_pot_from_db_sql(self, sito, area, us)

##### select_medianame_ra_from_db_sql(self, sito, area, us)

##### select_medianame_2_from_db_sql(self, sito, area, us)

##### get_total_pages(self, filter_query, page_size)

##### select_thumb(self, page_number, page_size)

##### select_original(self, page_number, page_size)

##### select_ra_from_db_sql(self, sito, area, us)

##### select_coord_from_db_sql(self, sito, area, us)

##### select_medianame_3_from_db_sql(self, sito, area, us)

##### select_thumbnail_from_db_sql(self, sito)

##### select_quote_from_db_sql(self, sito, area, us)

##### select_us_from_db_sql(self, sito, area, us, stratigraph_index_us)

##### select_us_doc_from_db_sql(self, sito, tipo_doc, nome_doc)

##### select_usneg_doc_from_db_sql(self, sito, tipo_doc, nome_doc)

##### select_db_sql(self, table)

##### select_db_sql_2(self, sito, area, us, d_stratigrafica)

##### test_ut_sql(self, unita_tipo)

##### query_in_contains_onlysqlite(self, value_list, sitof, areaf, chunk_size)

Esegue una query suddividendo la lista dei valori in chunk per evitare il limite di profondità di SQLite.

Args:
    value_list (list): Lista di valori da cercare.
    sitof (str): Valore per il filtro 'sito'.
    areaf (str): Valore per il filtro 'area'.
    chunk_size (int): Dimensione dei chunk. Default è 100.

Returns:
    list: Lista dei risultati della query.

##### query_in_contains(self, value_list, sitof, areaf)

##### insert_arbitrary_number_of_us_records(self, us_range, sito, area, n_us, unita_tipo)

##### insert_number_of_rapporti_records(self, sito, area, n_us, n_rapporti, unita_tipo)

##### insert_number_of_us_records(self, sito, area, n_us, unita_tipo)

##### insert_number_of_reperti_records(self, sito, numero_inventario)

##### insert_number_of_pottery_records(self, id_number, sito, area, us)

##### insert_number_of_tomba_records(self, sito, nr_scheda_taf)

##### insert_struttura_records(self, sito, sigla_struttura, numero_struttura)

##### select_like_from_db_sql(self, rapp_list, us_rapp_list)

##### select_not_like_from_db_sql(self, sitof, areaf)

##### query_in_idusb(self)

### ANSI

#### Methods

##### background(code)

##### style_text(code)

##### color_text(code)

### Pyarchinit_db_management

**Inherits from**: object

#### Methods

##### __init__(self, c)

##### load_spatialite(self, dbapi_conn, connection_record)

##### connection(self)

##### ensure_tma_tables_exist(self)

Ensure TMA tables are created if they don't exist

##### fix_macc_field_sqlite(self)

Fix macc field in tma_materiali_ripetibili table for SQLite databases

##### insert_pottery_values(self)

Istanzia la classe POTTERY da pyarchinit_db_mapper

##### insert_pyus(self)

##### insert_pyusm(self)

##### insert_pysito_point(self)

##### insert_pysito_polygon(self)

##### insert_pyquote(self)

##### insert_pyquote_usm(self)

##### insert_pyus_negative(self)

##### insert_pystrutture(self)

##### insert_pyreperti(self)

##### insert_pyindividui(self)

##### insert_pycampioni(self)

##### insert_pytomba(self)

##### insert_pydocumentazione(self)

##### insert_pylineeriferimento(self)

##### insert_pyripartizioni_spaziali(self)

##### insert_pysezioni(self)

##### insert_values(self)

Istanzia la classe US da pyarchinit_db_mapper

##### insert_ut_values(self)

Istanzia la classe UT da pyarchinit_db_mapper

##### insert_site_values(self)

Istanzia la classe SITE da pyarchinit_db_mapper

##### insert_periodizzazione_values(self)

Istanzia la classe Periodizzazione da pyarchinit_db_mapper

##### insert_values_reperti(self)

Istanzia la classe Reperti da pyarchinit_db_mapper

##### insert_struttura_values(self)

Istanzia la classe Struttura da pyarchinit_db_mapper

##### insert_values_ind(self)

Istanzia la classe SCHEDAIND da pyarchinit_db_mapper

##### insert_values_detsesso(self)

Istanzia la classe DETSESSO da pyarchinit_db_mapper

##### insert_values_deteta(self)

Istanzia la classe DETETA da pyarchinit_db_mapper

##### insert_media_values(self)

Istanzia la classe MEDIA da pyarchinit_db_mapper

##### insert_mediathumb_values(self)

Istanzia la classe MEDIA da pyarchinit_db_mapper

##### insert_media2entity_values(self)

Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper

##### insert_media2entity_view_values(self)

Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper

##### insert_values_tomba(self)

Istanzia la classe TOMBA da pyarchinit_db_mapper

##### insert_values_campioni(self)

Istanzia la classe CAMPIONI da pyarchinit_db_mapper

##### insert_values_thesaurus(self)

Istanzia la classe PYARCHINIT_THESAURUS_SIGLE da pyarchinit_db_mapper

##### insert_values_Lapidei(self)

Istanzia la classe Inventario_Lapidei da pyarchinit_db_mapper

##### insert_values_documentazione(self)

Istanzia la classe DOCUMENTAZIONE da pyarchinit_db_mapper

##### insert_pdf_administrator_values(self)

Istanzia la classe PDF_ADMINISTRATOR da pyarchinit_db_mapper

##### insert_campioni_values(self)

Istanzia la classe CAMPIONI da pyarchinit_db_mapper

##### insert_tma_values(self)

Istanzia la classe TMA da pyarchinit_db_mapper

##### insert_tma_materiali_values(self)

Istanzia la classe TMA_MATERIALI da pyarchinit_db_mapper

##### insert_media_to_entity_values(self)

Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper

##### execute_sql_create_db(self)

##### execute_sql_create_spatialite_db(self)

##### execute_sql_create_layers(self)

##### execute_sql(self, query_string, params)

Execute a raw SQL query and return results

##### query(self, n)

##### query_limit_offset(self, table_name, filter_text, limit, offset)

##### count_total_images(self, table_name, filter_text)

##### query_bool_us(self, params, table_class)

##### query_bool_like(self, params, table, join_operator)

##### query_bool_postgres(self, params, table)

##### query_sql(self, query)

Execute raw SQL query and return results

##### query_bool(self, params, table_class_name)

##### select_mediapath_from_id(self, media_id)

##### query_all_us(self, table_class_str, column_name)

Retrieve all records from a specified table and return values of a specific column.

:param table_class_str: The name of the table class as a string.
:param column_name: The name of the column to retrieve values from.
:return: A list of values from the specified column of all records.

##### query_all(self, table_class_str)

Retrieve all records from a specified table.

:param table_class_str: The name of the table class as a string.
:return: A list of all records from the specified table.

##### query_bool_special(self, params, table)

##### query_operator(self, params, table)

##### query_distinct(self, table, query_params, distinct_field_name_params)

##### query_distinct_sql(self, table, query_params, distinct_field_name_params)

##### insert_data_session(self, data)

##### insert_data_conflict(self, data)

##### update(self, table_class_str, id_table_str, value_id_list, columns_name_list, values_update_list)

Receives 5 values then putted in a list. The values must be passed
in this order: table name->string, column_name_where->list containin'
one value
('site_table', 'id_sito', [1], ['sito', 'nazione', 'regione', 'comune', 'descrizione', 'provincia'], ['Sito archeologico 1', 'Italiauiodsds', 'Emilia-Romagna', 'Riminijk', 'Sito di epoca altomedievale....23', 'Riminikljlks'])
self.set_update = arg
#self.connection()
table = Table(self.set_update[0], self.metadata, autoload=True)
changes_dict= {}
u = Utility()
set_update_4 = u.deunicode_list(self.set_update[4])

u.add_item_to_dict(changes_dict,zip(self.set_update[3], set_update_4))

f = open("test_update.txt", "w")
f.write(str(self.set_update))
f.close()

exec_str = ('%s%s%s%s%s%s%s') % ("table.update(table.c.",
                                  self.set_update[1],
                                 " == '",
                                 self.set_update[2][0],
                                 "').execute(",
                                 changes_dict ,")")

#session.query(SITE).filter(and_(SITE.id_sito == '1')).update(values = {SITE.sito:"updatetest"})

##### update_tomba_dating_from_periodizzazione(self, site_name)

##### update_us_dating_from_periodizzazione(self, site_name)

##### update_find_check(self, table_class_str, id_table_str, value_id, find_check_value)

##### empty_find_check(self, table_class_str, find_check_value)

##### delete_one_record(self, tn, id_col, id_rec)

##### delete_record_by_field(self, table_name, field_name, field_value)

Delete records from a table where field matches value

##### max_num_id(self, tc, f)

##### dir_query(self)

##### fields_list(self, t, s)

return the list of columns in a table. If s is set a int,
return only one column

##### query_in_idus(self, id_list)

##### query_sort(self, id_list, op, to, tc, idn)

##### run(self, stmt)

##### update_for(self)

table = Table('us_table_toimp', self.metadata, autoload=True)
s = table.select(table.c.id_us > 0)
res_list = self.run(s)
cont = 11900
for i in res_list:
    self.update('US_toimp', 'id_us', [i], ['id_us'], [cont])
    cont = cont+1

##### group_by(self, tn, fn, CD)

Group by the values by table name - string, field name - string, table class DB from mapper - string

##### query_where_text(self, c, v)

##### update_cont_per(self, s)

##### remove_alltags_from_db_sql(self, s)

##### remove_tags_from_db_sql(self, s)

##### remove_tags_from_db_sql_scheda(self, s, n)

##### delete_thumb_from_db_sql(self, s)

##### select_medianame_from_st_sql(self, sito, sigla, numero)

##### select_medianame_from_db_sql(self, sito, area)

##### select_medianame_tb_from_db_sql(self, sito, area)

##### select_medianame_pot_from_db_sql(self, sito, area, us)

##### select_medianame_ra_from_db_sql(self, sito, area, us)

##### select_medianame_2_from_db_sql(self, sito, area, us)

##### get_total_pages(self, filter_query, page_size)

##### select_thumb(self, page_number, page_size)

##### select_original(self, page_number, page_size)

##### select_ra_from_db_sql(self, sito, area, us)

##### select_coord_from_db_sql(self, sito, area, us)

##### select_medianame_3_from_db_sql(self, sito, area, us)

##### select_thumbnail_from_db_sql(self, sito)

##### select_quote_from_db_sql(self, sito, area, us)

##### select_us_from_db_sql(self, sito, area, us, stratigraph_index_us)

##### select_us_doc_from_db_sql(self, sito, tipo_doc, nome_doc)

##### select_usneg_doc_from_db_sql(self, sito, tipo_doc, nome_doc)

##### select_db_sql(self, table)

##### select_db_sql_2(self, sito, area, us, d_stratigrafica)

##### test_ut_sql(self, unita_tipo)

##### query_in_contains_onlysqlite(self, value_list, sitof, areaf, chunk_size)

Esegue una query suddividendo la lista dei valori in chunk per evitare il limite di profondità di SQLite.

Args:
    value_list (list): Lista di valori da cercare.
    sitof (str): Valore per il filtro 'sito'.
    areaf (str): Valore per il filtro 'area'.
    chunk_size (int): Dimensione dei chunk. Default è 100.

Returns:
    list: Lista dei risultati della query.

##### query_in_contains(self, value_list, sitof, areaf)

##### insert_arbitrary_number_of_us_records(self, us_range, sito, area, n_us, unita_tipo)

##### insert_number_of_rapporti_records(self, sito, area, n_us, n_rapporti, unita_tipo)

##### insert_number_of_us_records(self, sito, area, n_us, unita_tipo)

##### insert_number_of_reperti_records(self, sito, numero_inventario)

##### insert_number_of_pottery_records(self, id_number, sito, area, us)

##### insert_number_of_tomba_records(self, sito, nr_scheda_taf)

##### insert_struttura_records(self, sito, sigla_struttura, numero_struttura)

##### select_like_from_db_sql(self, rapp_list, us_rapp_list)

##### select_not_like_from_db_sql(self, sitof, areaf)

##### query_in_idusb(self)

### ANSI

#### Methods

##### background(code)

##### style_text(code)

##### color_text(code)

## Functions

### log_debug(msg)

**Parameters:**
- `msg`

### log_debug(msg)

**Parameters:**
- `msg`

### log_debug(msg)

**Parameters:**
- `msg`

### log_debug(msg)

**Parameters:**
- `msg`

