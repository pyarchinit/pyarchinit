# Class Diagram

## Architecture Overview

The codebase follows a layered architecture combining dialog-based UI components with background worker threads and manager classes responsible for system-level operations. The recurring pattern of pairing a dialog class (such as `InstallDialog`) with a dedicated `Worker` thread class indicates consistent use of the worker-thread pattern to offload blocking operations away from the UI. Manager classes (`PipManager`, `PackageManager`, `FontManager`) encapsulate distinct resource management concerns, suggesting a separation-of-responsibilities design.

`PackageManager` handles cross-platform package installation and coordinates with `PipManager`, which is specifically scoped to pip-based installation and updates. `FontManager` manages font installation as an independent concern. The two `Worker` classes serve as background execution units — one described as performing heavy search-matching work by accepting search parameters (associated with `LayerSearchDialog` or `PlaceSelectionDialog` context), and the other dedicated to package installation within the `InstallDialog` flow. The two `InstallDialog` classes appear in separate subsystems, one tied to package installation and one whose description is not documented in source.

`PyArchInitPlugin` serves as an entry point or initialization component for the broader plugin, though its internal responsibilities and relationships to the other classes are not documented in source. `LayerSearchDialog` and `PlaceSelectionDialog` are UI dialog components whose specific roles beyond hosting search or selection interactions are not documented in source. Overall, the architecture reflects a plugin system composed of UI dialogs, background workers, and dedicated manager objects, each scoped to a specific operational domain.

```mermaid
classDiagram
    class PlaceSelectionDialog {
        +__init__(self)
    }
    QDialog <|-- PlaceSelectionDialog
    class Worker {
        +__init__(self, vlayers, infield, searchStr, comparisonMode, selectedField, maxResults)
        +run(self)
        +kill(self)
        +searchLayer(self, layer, searchStr, comparisonMode)
        +searchFieldInLayer(self, layer, searchStr, comparisonMode, selectedField)
    }
    QObject <|-- Worker
    class LayerSearchDialog {
        +__init__(self, iface, parent)
        +closeDialog(self)
        +updateLayers(self)
        +select_feature(self)
        +layerSelected(self)
        ... +11 more methods
    }
    QDialog <|-- LayerSearchDialog
    FORM_CLASS <|-- LayerSearchDialog
    class InstallDialog {
        +__init__(self, packages)
        +initUI(self)
        +install_packages(self)
    }
    QDialog <|-- InstallDialog
    class PipManager {
        +update_pip(python_path)
        +configure_pip()
    }
    class PackageManager {
        +is_osgeo4w()
        +get_osgeo4w_python()
        +get_windows_qgis_python()
        +is_ubuntu()
        +get_ubuntu_package_name(package)
        ... +3 more methods
    }
    class Worker {
        +install_packages(self, packages)
    }
    QObject <|-- Worker
    class InstallDialog {
        +__init__(self, packages)
        +initUI(self)
        +show_splash(self, message)
        +update_splash_message(self, message)
        +hide_splash(self)
        ... +5 more methods
    }
    QDialog <|-- InstallDialog
    class FontManager {
        +install_fonts()
    }
    class PyArchInitPlugin {
        +is_experimental_enabled(self)
        +load_config(self)
        +__init__(self, iface)
        +check_and_fix_sqlite_databases(self)
        +fix_single_sqlite_database(self, db_path)
        ... +44 more methods
    }
    class PyarchinitPluginDialog {
        +__init__(self, iface)
        +runSite(self)
        +runPer(self)
        +runStruttura(self)
        +runUS(self)
        ... +28 more methods
    }
    QgsDockWidget <|-- PyarchinitPluginDialog
    MAIN_DIALOG_CLASS <|-- PyarchinitPluginDialog
    class SearchLayers {
        +__init__(self, iface)
        +initGui(self)
        +showSearchDialog(self)
    }
    class pyarchinit_TOPS {
        +__init__(self, iface)
        +setPathinput(self)
        +setPathoutput(self)
        +loadCsv(self, fileName)
        +delete(self)
        ... +3 more methods
    }
    QDialog <|-- pyarchinit_TOPS
    MAIN_DIALOG_CLASS <|-- pyarchinit_TOPS
    class PlaceSelectionDialog {
        +__init__(self)
    }
    QDialog <|-- PlaceSelectionDialog
    class pyarchinit_Upd_Values {
        +__init__(self, iface)
        +load_connection(self)
        +on_pushButton_pressed(self)
        +update_record(self, table_value, id_field_value, id_value_list, table_fields_list, data_list)
    }
    QDialog <|-- pyarchinit_Upd_Values
    MAIN_DIALOG_CLASS <|-- pyarchinit_Upd_Values
    class pyarchinit_Tomba {
        +__init__(self, iface)
        +enable_button(self, n)
        +enable_button_search(self, n)
        +on_pushButton_connect_pressed(self)
        +customize_GUI(self)
        ... +61 more methods
    }
    QDialog <|-- pyarchinit_Tomba
    MAIN_DIALOG_CLASS <|-- pyarchinit_Tomba
    class pyarchinit_Movecost {
        +__init__(self, iface)
        +on_pushButton_movecost_pressed(self)
        +on_pushButton_movecost_p_pressed(self)
        +on_pushButton_movebound_pressed(self)
        +on_pushButton_movebound_p_pressed(self)
        ... +20 more methods
    }
    QDialog <|-- pyarchinit_Movecost
    MAIN_DIALOG_CLASS <|-- pyarchinit_Movecost
    class QgsMapLayerType {
    }
    class pyarchinit_Documentazione {
        +__init__(self, iface)
        +enable_button(self, n)
        +enable_button_search(self, n)
        +on_pushButton_connect_pressed(self)
        +charge_list(self)
        ... +39 more methods
    }
    QDialog <|-- pyarchinit_Documentazione
    MAIN_DIALOG_CLASS <|-- pyarchinit_Documentazione
    class Main {
        +__init__(self)
        +setup_advanced_search(self)
        +toggle_inventario_field(self)
        +toggle_entity_selection(self, checked)
        +clear_search_filters(self)
        ... +94 more methods
    }
    QDialog <|-- Main
    MAIN_DIALOG_CLASS <|-- Main
    class pyarchinit_Cantiere {
        +__init__(self, iface)
        +on_pushButton_connect_pressed(self)
        +charge_list(self)
        +apply_sito_set(self)
        +populate_raster_combos(self)
        ... +14 more methods
    }
    QDialog <|-- pyarchinit_Cantiere
    MAIN_DIALOG_CLASS <|-- pyarchinit_Cantiere
    class pyarchinit_GPKG {
        +__init__(self, iface)
        +setPath(self)
        +on_pushButton_gpkg_pressed(self)
        +on_pushButton_gpkg2_pressed(self)
    }
    QDialog <|-- pyarchinit_GPKG
    MAIN_DIALOG_CLASS <|-- pyarchinit_GPKG
    class pyarchinit_Campioni {
        +__init__(self, iface)
        +enable_button(self, n)
        +enable_button_search(self, n)
        +on_pushButton_connect_pressed(self)
        +charge_list(self)
        ... +38 more methods
    }
    QDialog <|-- pyarchinit_Campioni
    MAIN_DIALOG_CLASS <|-- pyarchinit_Campioni
    class DemSectionViewerDialog {
        +__init__(self, parent, dem_pre_layer, dem_post_layer, diff_raster_path, lang)
    }
    QDialog <|-- DemSectionViewerDialog
    class DemPyVista3dDialog {
        +__init__(self, parent, dem_pre_layer, dem_post_layer, diff_raster_path, lang)
        +closeEvent(self, event)
    }
    QDialog <|-- DemPyVista3dDialog
    class DemPlotly3dDialog {
        +__init__(self, parent, dem_pre_layer, dem_post_layer, diff_raster_path, lang)
    }
    QDialog <|-- DemPlotly3dDialog
    class DemMatplotlib3dDialog {
        +__init__(self, parent, dem_pre_layer, dem_post_layer, diff_raster_path, lang)
    }
    QDialog <|-- DemMatplotlib3dDialog
    class TutorialViewerDialog {
        +__init__(self, parent)
        +detect_language(self)
        +get_tutorials_path(self, lang)
        +setup_ui(self)
        +eventFilter(self, obj, event)
        ... +14 more methods
    }
    QDialog <|-- TutorialViewerDialog
    class pyarchinit_Struttura {
        +__init__(self, iface)
        +is_media_path_remote(self)
        +update_media_button_visibility(self)
        +on_toolButtonPreviewMedia_toggled(self)
        +loadMediaPreviewLocal(self)
        ... +95 more methods
    }
    QDialog <|-- pyarchinit_Struttura
    MAIN_DIALOG_CLASS <|-- pyarchinit_Struttura
    class pyarchinit_Tomba {
        +__init__(self, iface)
        +numero_invetario(self)
        +loadCorredolist(self)
        +enable_button(self, n)
        +enable_button_search(self, n)
        ... +90 more methods
    }
    QDialog <|-- pyarchinit_Tomba
    MAIN_DIALOG_CLASS <|-- pyarchinit_Tomba
    class pyarchinit_Thesaurus {
        +__init__(self, iface)
        +read_api_key(self, path)
        +write_api_key(self, path, api_key)
        +apikey_gpt(self)
        +check_db(self)
        ... +61 more methods
    }
    QDialog <|-- pyarchinit_Thesaurus
    MAIN_DIALOG_CLASS <|-- pyarchinit_Thesaurus
    class pyarchinit_Attrezzature {
        +__init__(self, iface)
        +retranslate_ui(self)
        +enable_button(self, n)
        +enable_button_search(self, n)
        +on_pushButton_connect_pressed(self)
        ... +32 more methods
    }
    QDialog <|-- pyarchinit_Attrezzature
    MAIN_DIALOG_CLASS <|-- pyarchinit_Attrezzature
    class GNAExportDialog {
        +__init__(self, iface, db_manager, ut_records, project_name, parent)
        +get_result(self)
    }
    QDialog <|-- GNAExportDialog
    FORM_CLASS <|-- GNAExportDialog
    class RequestsException {
    }
    Exception <|-- RequestsException
    class RequestsExceptionTimeout {
    }
    RequestsException <|-- RequestsExceptionTimeout
    class RequestsExceptionConnectionError {
    }
    RequestsException <|-- RequestsExceptionConnectionError
    class RequestsExceptionUserAbort {
    }
    RequestsException <|-- RequestsExceptionUserAbort
    class Map {
        +__init__(self)
        +__getattr__(self, attr)
        +__setattr__(self, key, value)
        +__setitem__(self, key, value)
        +__delattr__(self, item)
        ... +1 more methods
    }
    dict <|-- Map
    class Response {
    }
    Map <|-- Response
    class NetworkAccessManager {
        +__init__(self, authid, disable_ssl_certificate_validation, exception_class, debug)
        +msg_log(self, msg)
        +httpResult(self)
        +request(self, url, method, body, headers, redirections, connection_type, blocking)
        +downloadProgress(self, bytesReceived, bytesTotal)
        ... +4 more methods
    }
    class pyarchinit_Budget {
        +__init__(self, iface)
        +retranslate_ui(self)
        +enable_button(self, n)
        +enable_button_search(self, n)
        +on_pushButton_connect_pressed(self)
        ... +39 more methods
    }
    QDialog <|-- pyarchinit_Budget
    MAIN_DIALOG_CLASS <|-- pyarchinit_Budget
    class Dem3dViewerDialog {
        +__init__(self, parent, terrain_layer, drape_layer, mesh_pre_layer, mesh_post_layer, lang)
    }
    QDialog <|-- Dem3dViewerDialog
    class Comparision {
        +__init__(self)
        +connection(self)
        +on_pushButton_chose_dir_pressed(self)
        +on_pushButton_chose_file_pressed(self)
        +on_pushButton_run_pressed(self)
        ... +3 more methods
    }
    QDialog <|-- Comparision
    MAIN_DIALOG_CLASS <|-- Comparision
    class pyarchinit_Schedaind {
        +__init__(self, iface)
        +numero_invetario(self)
        +enable_button(self, n)
        +enable_button_search(self, n)
        +on_pushButton_connect_pressed(self)
        ... +50 more methods
    }
    QDialog <|-- pyarchinit_Schedaind
    MAIN_DIALOG_CLASS <|-- pyarchinit_Schedaind
    class pyarchinit_Fauna {
        +__init__(self, iface)
        +connect_to_db(self)
        +setup_ui(self)
        +create_toolbar(self)
        +create_tab_identificativi(self)
        ... +48 more methods
    }
    QDialog <|-- pyarchinit_Fauna
    class pyarchinit_Deteta {
        +__init__(self, iface)
        +enable_button(self, n)
        +enable_button_search(self, n)
        +enable_button_Suchey_Brooks(self, n)
        +enable_button_Kimmerle_m(self, n)
        ... +94 more methods
    }
    QDialog <|-- pyarchinit_Deteta
    MAIN_DIALOG_CLASS <|-- pyarchinit_Deteta
    class pyarchinit_Pottery {
        +__init__(self, iface)
        +get_images_for_entities(self, entity_ids, log_signal)
        +setnone(self)
        +generate_list_foto(self)
        +on_pushButton_print_pressed(self)
        ... +146 more methods
    }
    QDialog <|-- pyarchinit_Pottery
    MAIN_DIALOG_CLASS <|-- pyarchinit_Pottery
    class KhutmTrainingDialog {
        +__init__(self, db_manager, parent)
        +initUI(self)
        +browse_training_folder(self)
        +browse_output_folder(self)
        +start_training(self)
        ... +3 more methods
    }
    QDialog <|-- KhutmTrainingDialog
    class DatasetPreparationDialog {
        +__init__(self, db_manager, parent)
        +initUI(self)
        +browse_output(self)
        +get_grouping_field(self)
        +analyze_database(self)
        ... +1 more methods
    }
    QDialog <|-- DatasetPreparationDialog
    class PotteryFilterDialog {
        +__init__(self, db_manager, parent, site_filter)
        +initUI(self)
        +natural_sort_key(self, text)
        +populate_years_and_ids(self)
        +on_year_changed(self, index)
        ... +11 more methods
    }
    QDialog <|-- PotteryFilterDialog
    class pyarchinit_Interactive_Matrix {
        +__init__(self, iface, data_list, id_us_dict)
        +DB_connect(self)
        +urlify(self, s)
        +generate_matrix_2(self)
        +generate_matrix(self)
    }
    QDialog <|-- pyarchinit_Interactive_Matrix
    MAIN_DIALOG_CLASS <|-- pyarchinit_Interactive_Matrix
    class pyarchinit_view_Matrix {
        +__init__(self, iface, data_list, id_us_dict)
        +DB_connect(self)
        +urlify(self, s)
        +generate_matrix(self)
    }
    QDialog <|-- pyarchinit_view_Matrix
    MAIN_DIALOG_CLASS <|-- pyarchinit_view_Matrix
    class pyarchinit_view_Matrix_pre {
        +__init__(self, iface, data_list, id_us_dict)
        +DB_connect(self)
        +urlify(self, s)
        +generate_matrix_3(self)
    }
    QDialog <|-- pyarchinit_view_Matrix_pre
    MAIN_DIALOG_CLASS <|-- pyarchinit_view_Matrix_pre
    class pyarchinit_Images_directory_export {
        +build_media_path(base_path, path_resize)
        +__init__(self, parent, db)
        +connect(self)
        +on_pushButton_open_dir_pressed(self)
        +charge_list(self)
        ... +2 more methods
    }
    QDialog <|-- pyarchinit_Images_directory_export
    MAIN_DIALOG_CLASS <|-- pyarchinit_Images_directory_export
    class pyarchinit_Archeozoology {
        +__init__(self, iface)
        +customize_GUI(self)
        +charge_list(self)
        +set_sito(self)
        +msg_sito(self)
        ... +20 more methods
    }
    QDialog <|-- pyarchinit_Archeozoology
    MAIN_DIALOG_CLASS <|-- pyarchinit_Archeozoology
    class pyarchinit_Image_Search {
        +__init__(self, iface, parent)
        +connect_to_db(self)
        +setup_connections(self)
        +setup_context_menu(self)
        +show_context_menu(self, pos)
        ... +16 more methods
    }
    QDialog <|-- pyarchinit_Image_Search
    MAIN_DIALOG_CLASS <|-- pyarchinit_Image_Search
    class pyarchinit_UT {
        +__init__(self, iface)
        +enable_button(self, n)
        +enable_button_search(self, n)
        +on_pushButton_connect_pressed(self)
        +customize_GUI(self)
        ... +62 more methods
    }
    QDialog <|-- pyarchinit_UT
    MAIN_DIALOG_CLASS <|-- pyarchinit_UT
    class pyarchinit_Detsesso {
        +__init__(self, iface)
        +enable_button(self, n)
        +enable_button_search(self, n)
        +on_pushButton_connect_pressed(self)
        +customize_GUI(self)
        ... +56 more methods
    }
    QDialog <|-- pyarchinit_Detsesso
    MAIN_DIALOG_CLASS <|-- pyarchinit_Detsesso
    class QgsMapLayerRegistry {
    }
    class pyarchinit_Site {
        +__init__(self, iface)
        +setPathToSites(self)
        +openSiteDir(self)
        +on_wms_vincoli_pressed(self)
        +internet_on(self)
        ... +56 more methods
    }
    QDialog <|-- pyarchinit_Site
    MAIN_DIALOG_CLASS <|-- pyarchinit_Site
    class GeoCodeException {
    }
    Exception <|-- GeoCodeException
    class OsmGeoCoder {
        +geocode(self, address)
        +reverse(self, lon, lat)
    }
    class pyarchinit_Inventario_reperti {
        +__init__(self, iface)
        +get_images_for_entities(self, entity_ids, log_signal)
        +setnone(self)
        +on_pushButtonQuant_pressed(self)
        +parameter_quant_creator(self, par_list, n_rec)
        ... +129 more methods
    }
    QDialog <|-- pyarchinit_Inventario_reperti
    MAIN_DIALOG_CLASS <|-- pyarchinit_Inventario_reperti
    class InventarioFilterDialog {
        +__init__(self, db_manager, parent, site_filter)
        +initUI(self)
        +natural_sort_key(self, text)
        +populate_data(self)
        +on_filter_type_changed(self, index)
        ... +13 more methods
    }
    QDialog <|-- InventarioFilterDialog
    class ZoomableGraphicsView {
        +__init__(self, parent)
        +wheelEvent(self, event)
    }
    QGraphicsView <|-- ZoomableGraphicsView
    class pyarchinit_Gis_Time_Controller {
        +__init__(self, iface)
        +connect(self)
        +update_selected_layers(self)
        +update_layers(self, layers)
        +set_max_num(self)
        ... +16 more methods
    }
    QDialog <|-- pyarchinit_Gis_Time_Controller
    MAIN_DIALOG_CLASS <|-- pyarchinit_Gis_Time_Controller
    class pyarchinit_Presenze {
        +__init__(self, iface)
        +quick_register(self, reg_type)
        +retranslate_ui(self)
        +enable_button(self, n)
        +enable_button_search(self, n)
        ... +37 more methods
    }
    QDialog <|-- pyarchinit_Presenze
    MAIN_DIALOG_CLASS <|-- pyarchinit_Presenze
    class SamApiWorkerThread {
        +__init__(self, input_raster, output_gpkg, api_key, mode)
        +run(self)
    }
    QThread <|-- SamApiWorkerThread
    class SamSegmentationWorkerThread {
        +__init__(self, input_raster, output_gpkg, mode, prompts, model)
        +run(self)
    }
    QThread <|-- SamSegmentationWorkerThread
    class Sam3RoboflowWorkerThread {
        +__init__(self, input_raster, output_gpkg, api_key, text_prompt)
        +run(self)
    }
    QThread <|-- Sam3RoboflowWorkerThread
    class SamSegmentationDialog {
        +__init__(self, db_manager, parent)
        +initUI(self)
        +load_settings(self)
        +save_settings(self)
        +get_mode(self)
        ... +8 more methods
    }
    QDialog <|-- SamSegmentationDialog
    class pyarchinit_excel_export {
        +__init__(self, iface)
        +connect(self)
        +charge_list(self)
        +set_home_path(self)
        +on_pushButton_open_dir_pressed(self)
        ... +3 more methods
    }
    QDialog <|-- pyarchinit_excel_export
    MAIN_DIALOG_CLASS <|-- pyarchinit_excel_export
    class PotteryToolsDialog {
        +__init__(self, iface)
        +is_cache_valid(self)
        +update_cache(self, package, status)
        +get_cached_status(self, package)
        +setup_pottery_venv(self, retry_count)
        ... +67 more methods
    }
    QDialog <|-- PotteryToolsDialog
    MAIN_DIALOG_CLASS <|-- PotteryToolsDialog
    class pyarchinit_PDFAdministrator {
        +__init__(self, parent, db)
        +enable_button(self, n)
        +enable_button_search(self, n)
        +connect(self)
        +cellchanged(self)
        ... +29 more methods
    }
    QDialog <|-- pyarchinit_PDFAdministrator
    MAIN_DIALOG_CLASS <|-- pyarchinit_PDFAdministrator
    class Setting_Matrix {
        +__init__(self)
    }
    QDialog <|-- Setting_Matrix
    MAIN_DIALOG_CLASS <|-- Setting_Matrix
    class pyarchinit_pdf_export {
        +__init__(self, iface)
        +connect(self)
        +charge_list(self)
        +set_home_path(self)
        +on_pushButton_open_dir_pressed(self)
        ... +10 more methods
    }
    QDialog <|-- pyarchinit_pdf_export
    MAIN_DIALOG_CLASS <|-- pyarchinit_pdf_export
    class pyarchinit_Periodizzazione {
        +__init__(self, iface)
        +enable_button(self, n)
        +enable_button_search(self, n)
        +on_pushButton_connect_pressed(self)
        +read_epoche(self)
        ... +46 more methods
    }
    QDialog <|-- pyarchinit_Periodizzazione
    MAIN_DIALOG_CLASS <|-- pyarchinit_Periodizzazione
    class pyarchinit_PRINTMAP {
        +__init__(self, iface)
        +customize_GUI(self)
        +loadTemplates(self)
        +listMenu(self, position)
        +opentepmplatePreview(self)
        ... +5 more methods
    }
    QDialog <|-- pyarchinit_PRINTMAP
    MAIN_DIALOG_CLASS <|-- pyarchinit_PRINTMAP
    class pyarchinit_Tma {
        +__init__(self, iface)
        +add_custom_toolbar_buttons(self)
        +customize_GUI(self)
        +enable_button(self, n)
        +enable_button_search(self, n)
        ... +109 more methods
    }
    QDialog <|-- pyarchinit_Tma
    MAIN_DIALOG_CLASS <|-- pyarchinit_Tma
    class MaterialData {
        +__init__(self, row_data)
    }
    class pyarchinit_Inventario_Lapidei {
        +__init__(self, iface)
        +plot_chart(self, d, t, yl)
        +on_pushButton_connect_pressed(self)
        +customize_gui(self)
        +openWide_image(self)
        ... +43 more methods
    }
    QDialog <|-- pyarchinit_Inventario_Lapidei
    MAIN_DIALOG_CLASS <|-- pyarchinit_Inventario_Lapidei
    class pyarchinit_doc_preview {
        +__init__(self, iface, docstr)
        +DB_connect(self)
        +draw_preview(self)
        +testing(self, name_file, message)
    }
    QDialog <|-- pyarchinit_doc_preview
    MAIN_DIALOG_CLASS <|-- pyarchinit_doc_preview
    class pyarchinit_Personale {
        +__init__(self, iface)
        +retranslate_ui(self)
        +enable_button(self, n)
        +enable_button_search(self, n)
        +on_pushButton_connect_pressed(self)
        ... +32 more methods
    }
    QDialog <|-- pyarchinit_Personale
    MAIN_DIALOG_CLASS <|-- pyarchinit_Personale
    class FileInfo {
    }
    BaseModel <|-- FileInfo
    class Node {
        +__init__(self)
        +initFromString(self, line)
        +getLabel(self, conf, multiline)
        +getLabelWidth(self, conf, multiline)
        +complementAttributes(self, node)
        ... +4 more methods
    }
    class Edge {
        +__init__(self)
        +initFromString(self, line)
        +getLabel(self, nodes, conf)
        +complementAttributes(self, edge)
        +exportDot(self, o, nodes, conf)
        ... +3 more methods
    }
    class Node {
        +__init__(self)
        +initFromString(self, line)
        +getLabel(self, conf, multiline)
        +getLabelWidth(self, conf, multiline)
        +complementAttributes(self, node)
        ... +5 more methods
    }
    class Edge {
        +__init__(self)
        +initFromString(self, line)
        +getLabel(self, nodes, conf)
        +complementAttributes(self, edge)
        +exportDot(self, o, nodes, conf)
        ... +3 more methods
    }
    class Node {
        +__init__(self)
        +initFromString(self, line)
        +getLabel(self, conf, multiline)
        +getLabelWidth(self, conf, multiline)
        +complementAttributes(self, node)
        ... +5 more methods
    }
    class Edge {
        +__init__(self)
        +initFromString(self, line)
        +getLabel(self, nodes, conf)
        +complementAttributes(self, edge)
        +exportDot(self, o, nodes, conf)
        ... +3 more methods
    }
    class TSTranslator {
        +__init__(self, api_key, dry_run)
        +translate_batch(self, texts, target_lang, target_code, check_mode)
        +process_ts_file(self, lang_key, check_existing)
        +run(self, languages, check_mode)
    }
    class TSTranslator {
        +__init__(self, api_key, dry_run)
        +apply_terminology(self, text, terminology)
        +translate_single(self, source_text, target_lang, target_code, terminology)
        +process_ts_file(self, lang_key, limit)
        +mark_skip_terms(self, lang_key)
        ... +1 more methods
    }
    class TMAThesaurusSync {
        +__init__(self)
        +get_tma_areas(self)
        +get_tma_settori(self)
        +sync_areas_to_tables(self)
        +sync_settori_to_tables(self)
        ... +3 more methods
    }
    class Handler {
        +do_GET(self)
        +do_POST(self)
        +log_message(self, format)
    }
    BaseHTTPRequestHandler <|-- Handler
    class TwinConv {
        +__init__(self, convin_pretrained, convin_curr)
        +forward(self, x)
    }
    torch.nn.Module <|-- TwinConv
    class Pix2Pix_Turbo {
        +__init__(self, pretrained_path)
        +set_eval(self)
        +set_train(self)
        +forward(self, c_t, prompt, prompt_tokens, deterministic, r, noise_map)
    }
    torch.nn.Module <|-- Pix2Pix_Turbo
    class GitHubIssueManager {
        +__init__(self, owner, repo, token)
        +fetch_issues(self, state, labels)
        +save_issues_locally(self, issues)
        +load_local_issues(self)
        +get_resolved_issue_ids(self)
        ... +3 more methods
    }
    class IssueTrackerGUI {
        +__init__(self, manager)
        +initUI(self)
        +load_issues(self)
        +populate_table(self, issues)
        +filter_issues(self, filter_text)
        ... +6 more methods
    }
    QMainWindow <|-- IssueTrackerGUI
    class PyArchInitDBUpdater {
        +__init__(self, db_path)
        +connect(self)
        +check_column_exists(self, table_name, column_name)
        +check_table_exists(self, table_name)
        +add_column(self, table_name, column_name, column_type, default_value)
        ... +12 more methods
    }
    class TMATableInstaller {
        +__init__(self, db_type, connection_params)
        +connect(self)
        +disconnect(self)
        +check_table_exists(self)
        +drop_table_if_exists(self)
        ... +10 more methods
    }
    class SortPanelMain {
        +__init__(self, parent, db)
        +closeEvent(self, event)
        +on_pushButtonSort_pressed(self)
        +on_pushButtonRight_pressed(self)
        +on_pushButtonLeft_pressed(self)
        ... +1 more methods
    }
    QDialog <|-- SortPanelMain
    MAIN_DIALOG_CLASS <|-- SortPanelMain
    class DownloadThread {
        +__init__(self, url, save_path)
        +run(self)
        +cancel(self)
    }
    QThread <|-- DownloadThread
    class DownloadModelDialog {
        +__init__(self, parent)
        +setup_ui(self)
        +start_download(self)
        +update_progress(self, value)
        +update_speed(self, text)
        ... +3 more methods
    }
    QDialog <|-- DownloadModelDialog
    class QuantPanelMain {
        +__init__(self, parent, db)
        +on_pushButtonQuant_pressed(self)
        +on_pushButtonRight_pressed(self)
        +on_pushButtonLeft_pressed(self)
        +insertItems(self, lv)
    }
    QDialog <|-- QuantPanelMain
    MAIN_DIALOG_CLASS <|-- QuantPanelMain
    class QuantPanelMain {
        +__init__(self, parent, db)
        +on_pushButtonQuant_pressed(self)
        +on_pushButtonRight_pressed(self)
        +on_pushButtonLeft_pressed(self)
        +insertItems(self, lv)
    }
    QDialog <|-- QuantPanelMain
    MAIN_DIALOG_CLASS <|-- QuantPanelMain
    class UserManagementDialog {
        +__init__(self, db_manager, parent)
        +tr_(self, key)
        +check_admin_access(self)
        +init_ui(self)
        +create_users_tab(self)
        ... +22 more methods
    }
    QDialog <|-- UserManagementDialog
    class BackupThread {
        +__init__(self, command, env, file_path)
        +run(self)
    }
    QThread <|-- BackupThread
    class pyarchinit_dbmanagment {
        +__init__(self, iface)
        +load_db_config(self)
        +setup_gui_by_db_type(self)
        +enable_button(self, n)
        +enable_button_search(self, n)
        ... +12 more methods
    }
    QDialog <|-- pyarchinit_dbmanagment
    MAIN_DIALOG_CLASS <|-- pyarchinit_dbmanagment
    class RemoteStorageDialog {
        +__init__(self, parent)
        +setup_ui(self)
        +setup_cloudinary_tab(self)
        +setup_gdrive_tab(self)
        +setup_dropbox_tab(self)
        ... +8 more methods
    }
    QDialog <|-- RemoteStorageDialog
    class Particle {
        +__init__(self, w, h)
    }
    class OrbitalRing {
        +__init__(self, radius, speed, tilt, width, dot_count)
    }
    class FuturisticSplashWidget {
        +__init__(self, parent)
        +start_animation(self)
        +stop_animation(self)
        +set_status(self, text)
        +paintEvent(self, event)
    }
    QWidget <|-- FuturisticSplashWidget
    class PyArchInitSplash {
        +__init__(self, parent, message, modal)
        +init_ui(self, message)
        +center_on_screen(self)
        +set_message(self, message)
        +showEvent(self, event)
        ... +2 more methods
    }
    QDialog <|-- PyArchInitSplash
    class ImageViewer {
        +__init__(self, parent, origPixmap)
        +show_image(self, path, flags)
        +export_image(self)
    }
    QDialog <|-- ImageViewer
    IMAGE_VIEWER <|-- ImageViewer
    class ImageViewClass {
        +__init__(self, parent, origPixmap)
        +wheelEvent(self, event)
    }
    QGraphicsView <|-- ImageViewClass
    class pyArchInitDialog_Info {
        +__init__(self, parent, db)
        +open_link(self, url)
    }
    QDialog <|-- pyArchInitDialog_Info
    MAIN_DIALOG_CLASS <|-- pyArchInitDialog_Info
    class BackupWorker {
        +__init__(self, command, env)
        +run(self)
    }
    QThread <|-- BackupWorker
    class BackupRestoreDialog {
        +__init__(self, parent)
        +init_ui(self)
        +load_settings(self)
        +load_backup_info(self)
        +save_backup_info(self)
        ... +12 more methods
    }
    QDialog <|-- BackupRestoreDialog
    class ImportWorker {
        +__init__(self, import_manager, files, use_festos_parser)
        +run(self)
    }
    QThread <|-- ImportWorker
    class TMAImportDialog {
        +__init__(self, db_manager, parent)
        +init_ui(self)
        +add_files(self, filter_str)
        +remove_selected_files(self)
        +clear_files(self)
        ... +12 more methods
    }
    QDialog <|-- TMAImportDialog
    class QueueDialog {
        +__init__(self, queue, parent)
    }
    QDialog <|-- QueueDialog
    class StratiGraphSyncPanel {
        +__init__(self, orchestrator, parent)
    }
    QDockWidget <|-- StratiGraphSyncPanel
    class MplCanvas {
        +__init__(self)
    }
    FigureCanvas <|-- MplCanvas
    class Mplwidget {
        +__init__(self, parent)
    }
    QWidget <|-- Mplwidget
    class MplCanvas {
        +__init__(self)
    }
    FigureCanvas <|-- MplCanvas
    class MplwidgetMatrix {
        +__init__(self, parent)
    }
    QWidget <|-- MplwidgetMatrix
    class AnimatedGearWidget {
        +__init__(self, parent)
        +start_animation(self)
        +stop_animation(self)
        +update_animation(self)
        +paintEvent(self, event)
    }
    QWidget <|-- AnimatedGearWidget
    class PyArchInitSplash {
        +__init__(self, parent, message)
        +init_ui(self, message)
        +center_on_screen(self)
        +set_message(self, message)
        +showEvent(self, event)
        ... +2 more methods
    }
    QDialog <|-- PyArchInitSplash
    class PyArchInitLogger {
        +__init__(self)
        +log(self, message)
        +log_exception(self, function_name, exception)
        +clear_log(self)
    }
    class pyArchInitDialog_Config {
        +__init__(self, parent, db)
        +setup_admin_features(self)
        +setup_db_connection_profiles(self)
        +setup_supabase_sync_tab(self)
        +setup_rust_acceleration_tab(self)
        ... +80 more methods
    }
    QDialog <|-- pyArchInitDialog_Config
    MAIN_DIALOG_CLASS <|-- pyArchInitDialog_Config
    class RSessionManager {
        +__new__(cls)
        +get_instance(cls)
        +__init__(self)
        +is_available(self)
        +get_session(self)
        ... +10 more methods
    }
    class ArcheozooRAnalysis {
        +__init__(self)
        +is_r_available(self)
        +connect_to_database(self, db_type, host, port, database, user, password)
        +load_data(self, site_filter)
        +calculate_semivariogram(self, variables, model, psill, range_val, nugget, output_path)
        ... +8 more methods
    }
    class UTAnalysisLabels {
        +get_labels(cls, lang)
        +get_score_level(cls, score, lang)
    }
    class UTPotentialCalculator {
        +__init__(self, db_manager, weights)
        +log_message(self, message, level)
        +calculate_potential(self, ut_record, geometry)
        +to_json(self, result)
        +from_json(json_str)
    }
    class UTHeatmapGenerator {
        +__init__(self, output_dir, crs)
        +log_message(self, message, level)
        +generate_heatmap(self, points, values, method, cell_size, bandwidth, power, search_radius, extent, map_type)
        +generate_vector_grid(self, points, values, cell_size, extent, value_field, map_type)
        +generate_masked_heatmap(self, points, values, mask_polygon, method, cell_size, classification_scheme, map_type)
        ... +1 more methods
    }
    class SpatialGroupingManager {
        +__init__(self)
        +create_area_based_groups(self, us_data)
        +create_sector_based_groups(self, us_data)
        +create_structure_based_groups(self, us_data)
        +create_custom_groups(self, us_data, custom_rules)
        ... +1 more methods
    }
    class SpatialGroupingDialog {
        +__init__(self, us_data, parent)
        +setupUI(self)
        +on_grouping_type_changed(self)
        +preview_groupings(self)
        +update_preview_list(self)
        ... +5 more methods
    }
    QDialog <|-- SpatialGroupingDialog
    class UTRiskAssessor {
        +__init__(self, db_manager, weights, potential_calculator)
        +log_message(self, message, level)
        +calculate_risk(self, ut_record, geometry, potential_score)
        +to_json(self, result)
        +from_json(json_str)
    }
    class S3DGraphyIntegration {
        +__init__(self, db_manager)
        +is_available(self)
        +create_stratigraphic_graph(self, site_name)
        +add_virtual_reconstruction(self, vr_data)
        +add_stratigraphic_unit(self, us_data)
        ... +10 more methods
    }
    class PyArchInitS3DGraphyDialog {
        +__init__(self, parent, db_manager)
        +export_to_extended_matrix(self, site, area, output_path)
    }
    class QgsMessageLog {
        +logMessage(msg, tag, level)
    }
    class Qgis {
    }
    class GraphvizVisualizer {
        +__init__(self)
        +create_graph_image(self, graph_data, output_path)
    }
    class MatrixVisualizerQGIS {
        +__init__(self, iface)
        +visualize_extended_matrix(self, graph_data, chronological_sequence)
    }
    class CIDOCCRMMapper {
        +__init__(self)
        +map_node_to_cidoc(self, node_data)
        +map_edge_to_cidoc(self, edge_data)
        +export_to_cidoc_jsonld(self, graph_data, filepath)
        +export_to_rdf_turtle(self, graph_data, filepath)
    }
    class PlotlyMatrixVisualizer {
        +__init__(self, qgis_integration)
        +create_interactive_graph(self, graph_data, output_path)
    }
    class SimpleGraphVisualizer {
        +__init__(self)
        +create_graph_image(self, graph_data, output_path)
    }
    class BlenderIntegration {
        +__init__(self)
        +is_blender_connected(self)
        +send_to_blender(self, data)
        +export_for_blender_addon(self, matrix_data, output_path)
    }
    class BlenderAddonScript {
        +generate_addon()
        +save_addon(output_path)
    }
    class S3DGraphyDotBridge {
        +__init__(self, db_manager)
        +s3dgraphy_to_dot(self, site, area)
        +export_integrated_matrix(self, site, area, output_dir, formats)
    }
    class S3DGraphyExportDialog {
        +__init__(self, parent, db_manager, site, area)
        +setupUI(self)
        +on_export(self)
    }
    QDialog <|-- S3DGraphyExportDialog
    class S3DGraphyExportDialog {
        +__init__(self)
    }
    class Options {
        +__init__(self)
    }
    class DropboxBackend {
        +storage_type(self)
        +__init__(self, base_path, credentials)
        +connect(self)
        +disconnect(self)
        +read(self, filename)
        ... +8 more methods
    }
    StorageBackend <|-- DropboxBackend
    class GraphMLSpatialEnhancer {
        +__init__(self)
        +enhance_graphml_with_groups(self, graphml_file, groupings, output_file)
        +create_hierarchical_groups(self, graphml_file, hierarchy, output_file)
    }
    class MatrixGraphVisualizer {
        +__init__(self)
        +create_interactive_graph(self, graph_data, output_path)
        +export_to_dot(self, graph_data, output_path)
    }
    class StorageManager {
        +__init__(self, credentials_manager)
        +register_backend(cls, storage_type, backend_class)
        +detect_storage_type(self, path)
        +parse_path(self, path)
        +get_backend(self, path, connect)
        ... +8 more methods
    }
    class LocalBackend {
        +storage_type(self)
        +connect(self)
        +disconnect(self)
        +read(self, filename)
        +write(self, filename, data)
        ... +9 more methods
    }
    StorageBackend <|-- LocalBackend
    class CloudinaryAIResult {
        +__post_init__(self)
    }
    class CloudinaryBackend {
        +storage_type(self)
        +__init__(self, base_path, credentials)
        +connect(self)
        +disconnect(self)
        +read(self, filename)
        ... +16 more methods
    }
    StorageBackend <|-- CloudinaryBackend
    class S3Backend {
        +__init__(self, base_path, credentials)
        +storage_type(self)
        +connect(self)
        +disconnect(self)
        +read(self, filename)
        ... +11 more methods
    }
    StorageBackend <|-- S3Backend
    class CredentialSource {
    }
    Enum <|-- CredentialSource
    class StorageCredentials {
        +get(self, key, default)
        +__getitem__(self, key)
        +__contains__(self, key)
    }
    class CredentialsManager {
        +__init__(self, plugin_path)
        +get_credentials(self, storage_type)
        +set_credentials(self, storage_type, credentials)
        +save_to_qgis_settings(self, storage_type, credentials)
        +save_to_json_file(self, storage_type, credentials)
        ... +3 more methods
    }
    class WebDAVBackend {
        +storage_type(self)
        +__init__(self, base_path, credentials)
        +connect(self)
        +disconnect(self)
        +read(self, filename)
        ... +9 more methods
    }
    StorageBackend <|-- WebDAVBackend
    class HTTPBackend {
        +storage_type(self)
        +__init__(self, base_path, credentials)
        +connect(self)
        +disconnect(self)
        +read(self, filename)
        ... +7 more methods
    }
    StorageBackend <|-- HTTPBackend
    class GDriveBackend {
        +storage_type(self)
        +__init__(self, base_path, credentials)
        +connect(self)
        +disconnect(self)
        +read(self, filename)
        ... +7 more methods
    }
    StorageBackend <|-- GDriveBackend
    class UniboFileManagerBackend {
        +storage_type(self)
        +__init__(self, base_path, credentials)
        +connect(self)
        +disconnect(self)
        +read(self, filename)
        ... +9 more methods
    }
    StorageBackend <|-- UniboFileManagerBackend
    class StorageType {
    }
    Enum <|-- StorageType
    class StorageFile {
        +__repr__(self)
    }
    class StorageConfig {
    }
    class StorageBackend {
        +__init__(self, base_path, credentials)
        +storage_type(self)
        +is_remote(self)
        +connect(self)
        +disconnect(self)
        ... +14 more methods
    }
    ABC <|-- StorageBackend
    class GNAFieldMapper {
        +__init__(self, language)
        +map_ut_record_to_mosi(self, ut_record, geometry)
        +validate_mosi_record(self, mosi_record)
        +get_mopr_fields(self, project_info)
    }
    class GNAVocabularyMapper {
        +__init__(self, language)
        +map_def_ut_to_ama(self, def_ut_value)
        +map_survey_type_to_mtdm(self, survey_type_value)
        +map_vegetation_to_vgtc(self, vegetation_value)
        +map_gps_method_to_gpmt(self, gps_value)
        ... +9 more methods
    }
    class GNAExporter {
        +__init__(self, db_manager, project_name, output_path, crs, language)
        +export(self, project_polygon, ut_records, options)
        +validate_geopackage(gpkg_path)
    }
    class pyarchinit_OS_Utility {
        +create_dir(self, d)
        +copy_file_img(self, f, d)
        +copy_file(self, f, d)
    }
    class PyArchInitFormMixin {
        +setup_refresh_timer(self)
        +stop_refresh_timer(self)
        +closeEvent(self, event)
        +hideEvent(self, event)
        +showEvent(self, event)
        ... +4 more methods
    }
    class FormStateManager {
        +__init__(self, form)
        +capture_state(self)
        +has_changes(self)
        +set_loading(self, loading)
    }
    class MediaMigrationMapper {
        +__init__(self)
        +add_id_mapping(self, table_name, old_id, new_id)
        +get_new_id(self, table_name, old_id)
        +get_new_entity_id(self, entity_type, old_id)
        +get_new_media_id(self, old_media_id)
        ... +3 more methods
    }
    class PostgresDbUpdater {
        +__init__(self, db_manager, parent)
        +log_message(self, message, level)
        +run_essential_migrations(self)
        +check_and_update_database(self)
        +column_exists(self, table_name, column_name)
        ... +28 more methods
    }
    class DB_update {
        +__init__(self, conn_str)
        +update_table(self)
        +fix_invalid_geometries(self)
        +rebuild_geometry_tables(self)
    }
    class ResultWrapper {
        +__init__(self, rows)
        +fetchall(self)
        +fetchone(self)
        +__iter__(self)
    }
    class PermissionHandler {
        +__init__(self, parent_form, language)
        +set_db_manager(self, db_manager)
        +has_permission(self, table_name, permission_type)
        +handle_permission_error(self, error, operation, show_message)
        +handle_database_error(self, error, context, show_message)
    }
    class VersioningSupport {
        +__init__(self)
        +get_all_tables(self)
        +add_versioning_columns(self, table_name)
        +update_all_tables(self)
    }
    class DatabaseMigrations {
        +__init__(self, db_manager)
        +check_and_migrate(self)
        +table_exists(self, table_name)
        +migrate_fauna_table(self)
        +migrate_fauna_thesaurus(self)
    }
    class DbConnectionSingleton {
        +get_instance(cls, conn_str)
        +clear_instances(cls)
        +force_db_recheck(cls)
    }
    class Pyarchinit_db_management {
        +__init__(self, c, _singleton)
        +clear_cache(self)
        +load_spatialite(self, dbapi_conn, connection_record)
        +connection(self)
        +session_scope(self)
        ... +143 more methods
    }
    class ANSI {
        +background(code)
        +style_text(code)
        +color_text(code)
    }
    class ResultWrapper {
        +__init__(self, rows)
        +fetchall(self)
        +fetchone(self)
        +scalar(self)
        +__iter__(self)
    }
    class SQLiteDBUpdater {
        +__init__(self, db_path, parent)
        +log_message(self, message, level)
        +check_and_update_database(self)
        +needs_update(self)
        +backup_database(self)
        ... +28 more methods
    }
    class PostgresPermissionSync {
        +__init__(self, db_manager)
        +create_postgres_user(self, username, password, role)
        +sync_table_permissions(self, username, table_name, can_view, can_insert, can_update, can_delete)
        +sync_all_permissions(self)
        +apply_role_based_permissions(self, username, role)
    }
    class DatabaseUpdater {
        +__init__(self, db_manager)
        +check_and_update_triggers(self)
        +update_create_doc_trigger(self)
    }
    class ConcurrencyManager {
        +__init__(self, parent)
        +check_version_conflict(self, table_name, record_id, current_version, db_manager, id_field)
        +handle_conflict(self, table_name, record_data, conflict_info)
        +lock_record(self, table_name, record_id, db_manager)
        +unlock_record(self, table_name, record_id, db_manager)
        ... +3 more methods
    }
    class ConflictResolutionDialog {
        +__init__(self, parent, table_name, record_data, last_modified_by, last_modified_timestamp)
        +init_ui(self, table_name, record_data, last_modified_by, last_modified_timestamp)
        +reload_choice(self)
        +overwrite_choice(self)
        +cancel_choice(self)
        ... +1 more methods
    }
    QDialog <|-- ConflictResolutionDialog
    class RecordLockIndicator {
        +__init__(self, parent_widget)
        +show_lock_status(self, editors)
        +clear_lock_status(self)
    }
    class PyArchInitConnLogger {
        +__init__(self)
        +log(self, message)
        +log_exception(self, exc, context)
    }
    class Connection {
        +__init__(self)
        +conn_str(self)
        +databasename(self)
        +datauser(self)
        +datahost(self)
        ... +6 more methods
    }
    class UUIDSupport {
        +__init__(self, engine)
        +get_tables_to_update(self)
        +add_uuid_column(self, table_name)
        +populate_existing_uuids(self, table_name)
        +update_all_tables(self)
    }
    class TableDiff {
    }
    class SyncConfig {
    }
    class DatabaseAdapter {
        +get_table_count(self, table)
        +get_primary_key(self, table)
        +get_record_ids(self, table, pk)
        +get_table_columns(self, table)
        +is_view(self, table)
        ... +6 more methods
    }
    ABC <|-- DatabaseAdapter
    class PostgreSQLAdapter {
        +__init__(self, host, port, database, user, password, engine)
        +get_table_count(self, table)
        +get_primary_key(self, table)
        +get_record_ids(self, table, pk)
        +get_table_columns(self, table)
        ... +7 more methods
    }
    DatabaseAdapter <|-- PostgreSQLAdapter
    class SQLiteAdapter {
        +__init__(self, db_path)
        +close(self)
        +get_table_count(self, table)
        +get_primary_key(self, table)
        +get_record_ids(self, table, pk)
        ... +8 more methods
    }
    DatabaseAdapter <|-- SQLiteAdapter
    class SyncAnalyzer {
        +__init__(self, config, parent)
        +cancel(self)
        +run(self)
    }
    QThread <|-- SyncAnalyzer
    class SyncWorker {
        +__init__(self, operation, config, tables_to_sync, parent)
        +cancel(self)
        +run(self)
    }
    QThread <|-- SyncWorker
    class DatabaseSyncManager {
        +__init__(self, parent)
        +configure(self, local_config, remote_config, tables)
        +analyze_differences(self)
        +download_from_remote(self, tables, differential)
        +upload_to_remote(self, tables, differential)
        ... +2 more methods
    }
    QObject <|-- DatabaseSyncManager
    class PyArchInitDBLogger {
        +__init__(self)
        +log(self, message)
        +log_exception(self, exc, context)
    }
    class SchemaDump {
        +__init__(self, db_url, schema_file_path)
        +dump_shema(self)
    }
    class RestoreSchema {
        +__init__(self, db_url, schema_file_path)
        +restore_schema(self)
        +update_geom_srid(self, schema, crs)
        +set_owner(self, owner)
        +update_geom_srid_sl(self, crs)
    }
    class CreateDatabase {
        +__init__(self, db_name, db_host, db_port, db_user, db_passwd, sslmode)
        +createdb(self)
    }
    class DropDatabase {
        +__init__(self, db_url)
        +dropdb(self)
    }
    class Utility {
        +pos_none_in_list(self, l)
        +tup_2_list(self, t, s, i)
        +tup_2_list_II(self, l)
        +tup_2_list_III(self, l)
        +list_tup_2_list(self, l)
        ... +15 more methods
    }
    class pyquote {
    }
    class Pottery_table {
    }
    class pyunitastratigrafiche {
    }
    class Media_table {
    }
    class Tma_materiali_table {
    }
    class Media_to_Entity_table {
    }
    class Periodizzazione_table {
    }
    class pydocumentazione {
    }
    class Tma_table {
    }
    class Media_thumb_table {
    }
    class pyripartizioni_spaziali {
    }
    class pycampioni {
    }
    class DETSESSO_table {
    }
    class Pyarchinit_thesaurus_sigle {
    }
    class Documentazione_table {
    }
    class Computo_metrico_table {
    }
    class pysito_point {
    }
    class pyindividui {
    }
    class Pottery_embeddings_metadata_table {
    }
    class pyunitastratigrafiche_usm {
    }
    class Struttura_table {
    }
    class Tma_materiali_table {
    }
    class pyreperti {
    }
    class Inventario_materiali_table {
    }
    class SCHEDAIND_table {
    }
    class pytomba {
    }
    class Budget_table {
    }
    class Media_to_Entity_table_view {
    }
    class Inventario_Lapidei_table {
    }
    class pylineeriferimento {
    }
    class pysito_polygon {
    }
    class Site_table {
    }
    class Personale_table {
    }
    class US_table_toimp {
    }
    class Campioni_table {
    }
    class pyquote_usm {
    }
    class Archeozoology_table {
    }
    class Attrezzature_table {
    }
    class UT_table {
    }
    class pysezioni {
    }
    class DETETA_table {
    }
    class Presenze_table {
    }
    class US_table {
    }
    class Tomba_table {
    }
    class pyus_negative {
    }
    class Fauna_table {
    }
    class Tomba_table {
    }
    class pystrutture {
    }
    class PDF_administrator_table {
    }
    class STRUTTURA {
        +__init__(self, id_struttura, sito, sigla_struttura, numero_struttura, categoria_struttura, tipologia_struttura, definizione_struttura, descrizione, interpretazione, periodo_iniziale, fase_iniziale, periodo_finale, fase_finale, datazione_estesa, materiali_impiegati, elementi_strutturali, rapporti_struttura, misure_struttura, data_compilazione, nome_compilatore, stato_conservazione, quota, relazione_topografica, prospetto_ingresso, orientamento_ingresso, articolazione, n_ambienti, orientamento_ambienti, sviluppo_planimetrico, elementi_costitutivi, motivo_decorativo, potenzialita_archeologica, manufatti, elementi_datanti, fasi_funzionali, entity_uuid)
        +__repr__(self)
    }
    class PYQUOTE {
        +__init__(self, id, sito_q, area_q, us_q, unita_misu_q, quota_q, data, disegnatore, rilievo_originale, the_geom, unita_tipo_q)
        +__repr__(self)
    }
    class DOCUMENTAZIONE {
        +__init__(self, id_documentazione, sito, nome_doc, data, tipo_documentazione, sorgente, scala, disegnatore, note, entity_uuid)
        +__repr__(self)
    }
    class TOMBA {
        +__init__(self, id_tomba, sito, nr_scheda_taf, sigla_struttura, nr_struttura, nr_individuo, rito, descrizione_taf, interpretazione_taf, segnacoli, canale_libatorio_si_no, oggetti_rinvenuti_esterno, stato_di_conservazione, copertura_tipo, tipo_contenitore_resti, orientamento_asse, orientamento_azimut, corredo_presenza, corredo_tipo, corredo_descrizione, lunghezza_scheletro, posizione_scheletro, posizione_cranio, posizione_arti_superiori, posizione_arti_inferiori, completo_si_no, disturbato_si_no, in_connessione_si_no, caratteristiche, periodo_iniziale, fase_iniziale, periodo_finale, fase_finale, datazione_estesa, misure_tomba)
        +__repr__(self)
    }
    class MEDIA {
        +__init__(self, id_media, mediatype, filename, filetype, filepath, descrizione, tags, entity_uuid)
        +__repr__(self)
    }
    class COMPUTO_METRICO {
        +__init__(self, id_computo, sito, nome_calcolo, tipo_calcolo, dem_pre, dem_post, layer_poligono, area_mq, volume_mc, quota_min, quota_max, data_calcolo, fase_scavo, note, entity_uuid)
        +__repr__(self)
    }
    class PYUS {
        +__init__(self, gid, area_s, scavo_s, us_s, stratigraph_index_us, tipo_us_s, rilievo_originale, disegnatore, data, tipo_doc, nome_doc, coord, the_geom, unita_tipo_s)
        +__repr__(self)
    }
    class CAMPIONI {
        +__init__(self, id_campione, sito, nr_campione, tipo_campione, descrizione, area, us, numero_inventario_materiale, nr_cassa, luogo_conservazione, entity_uuid)
        +__repr__(self)
    }
    class PYDOCUMENTAZIONE {
        +__init__(self, pkuid, sito, nome_doc, tipo_doc, path_qgis_pj, the_geom)
        +__repr__(self)
    }
    class PYARCHINIT_THESAURUS_SIGLE {
        +__init__(self, id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, order_layer, id_parent, parent_sigla, hierarchy_level, n_tipologia, n_sigla)
        +__repr__(self)
    }
    class PYRIPARTIZIONI_SPAZIALI {
        +__init__(self, id, id_rs, sito_rs, tip_rip, descr_rs, the_geom)
        +__repr__(self)
    }
    class PYCAMPIONI {
        +__init__(self, id, id_campion, sito, tipo_camp, dataz, cronologia, link_immag, sigla_camp, the_geom)
        +__repr__(self)
    }
    class TOMBA {
        +__init__(self, id_tomba, sito, area, nr_scheda_taf, sigla_struttura, nr_struttura, nr_individuo, rito, descrizione_taf, interpretazione_taf, segnacoli, canale_libatorio_si_no, oggetti_rinvenuti_esterno, stato_di_conservazione, copertura_tipo, tipo_contenitore_resti, tipo_deposizione, tipo_sepoltura, corredo_presenza, corredo_tipo, corredo_descrizione, periodo_iniziale, fase_iniziale, periodo_finale, fase_finale, datazione_estesa, misure_tomba, entity_uuid)
        +__repr__(self)
    }
    class ATTREZZATURE {
        +__init__(self, id_attrezzatura, sito, codice_inventario, nome, categoria, marca, modello, numero_serie, proprieta, data_acquisto, costo_acquisto, costo_noleggio_giorno, stato, assegnato_a, data_ultima_manutenzione, data_prossima_manutenzione, note, entity_uuid)
        +__repr__(self)
    }
    class BUDGET {
        +__init__(self, id_budget, sito, anno, categoria, descrizione, importo_previsto, importo_effettivo, data_registrazione, data_spesa, fornitore, numero_fattura, note, entity_uuid)
        +__repr__(self)
    }
    class TMA_MATERIALI {
        +__init__(self, id, id_tma, madi, macc, macl, macp, macd, cronologia_mac, macq, peso, created_at, updated_at, created_by, updated_by, entity_uuid)
        +__repr__(self)
    }
    class INVENTARIO_MATERIALI_TOIMP {
        +__init__(self, id_invmat, sito, numero_inventario, tipo_reperto, criterio_schedatura, definizione, descrizione, area, us, lavato, nr_cassa, luogo_conservazione, stato_conservazione, datazione_reperto, elementi_reperto, misurazioni, rif_biblio, tecnologie, forme_minime, forme_massime, totale_frammenti, corpo_ceramico, rivestimento)
        +__repr__(self)
    }
    class MEDIAVIEW {
        +__init__(self, id_media_thumb, id_media, filepath, path_resize, entity_type, id_media_m, id_entity)
        +__repr__(self)
    }
    class SCHEDAIND {
        +__init__(self, id_scheda_ind, sito, area, us, nr_individuo, data_schedatura, schedatore, sesso, eta_min, eta_max, classi_eta, osservazioni, sigla_struttura, nr_struttura, completo_si_no, disturbato_si_no, in_connessione_si_no, lunghezza_scheletro, posizione_scheletro, posizione_cranio, posizione_arti_superiori, posizione_arti_inferiori, orientamento_asse, orientamento_azimut, entity_uuid)
        +__repr__(self)
    }
    class PYSITO_POINT {
        +__init__(self, gid, sito_nome, the_geom)
        +__repr__(self)
    }
    class PYINDIVIDUI {
        +__init__(self, id, sito, sigla_struttura, note, id_individuo, the_geom)
        +__repr__(self)
    }
    class FAUNA {
        +__init__(self, id_fauna, id_us, sito, area, saggio, us, datazione_us, responsabile_scheda, data_compilazione, documentazione_fotografica, metodologia_recupero, contesto, descrizione_contesto, resti_connessione_anatomica, tipologia_accumulo, deposizione, numero_stimato_resti, numero_minimo_individui, specie, parti_scheletriche, specie_psi, misure_ossa, stato_frammentazione, tracce_combustione, combustione_altri_materiali_us, tipo_combustione, segni_tafonomici_evidenti, caratterizzazione_segni_tafonomici, stato_conservazione, alterazioni_morfologiche, note_terreno_giacitura, campionature_effettuate, affidabilita_stratigrafica, classi_reperti_associazione, osservazioni, interpretazione, entity_uuid)
        +__repr__(self)
    }
    class DETETA {
        +__init__(self, id_det_eta, sito, nr_individuo, sinf_min, sinf_max, sinf_min_2, sinf_max_2, SSPIA, SSPIB, SSPIC, SSPID, sup_aur_min, sup_aur_max, sup_aur_min_2, sup_aur_max_2, ms_sup_min, ms_sup_max, ms_inf_min, ms_inf_max, usura_min, usura_max, Id_endo, Is_endo, IId_endo, IIs_endo, IIId_endo, IIIs_endo, IV_endo, V_endo, VI_endo, VII_endo, VIIId_endo, VIIIs_endo, IXd_endo, IXs_endo, Xd_endo, Xs_endo, endo_min, endo_max, volta_1, volta_2, volta_3, volta_4, volta_5, volta_6, volta_7, lat_6, lat_7, lat_8, lat_9, lat_10, volta_min, volta_max, ant_lat_min, ant_lat_max, ecto_min, ecto_max)
        +__repr__(self)
    }
    class UT {
        +__init__(self, id_ut, progetto, nr_ut, ut_letterale, def_ut, descrizione_ut, interpretazione_ut, nazione, regione, provincia, comune, frazione, localita, indirizzo, nr_civico, carta_topo_igm, carta_ctr, coord_geografiche, coord_piane, quota, andamento_terreno_pendenza, utilizzo_suolo_vegetazione, descrizione_empirica_suolo, descrizione_luogo, metodo_rilievo_e_ricognizione, geometria, bibliografia, data, ora_meteo, responsabile, dimensioni_ut, rep_per_mq, rep_datanti, periodo_I, datazione_I, interpretazione_I, periodo_II, datazione_II, interpretazione_II, documentazione, enti_tutela_vincoli, indagini_preliminari, visibility_percent, vegetation_coverage, gps_method, coordinate_precision, survey_type, surface_condition, accessibility, photo_documentation, weather_conditions, team_members, foglio_catastale, potential_score, risk_score, potential_factors, risk_factors, analysis_date, analysis_method, entity_uuid)
        +__repr__(self)
    }
    class ALL {
    }
    class ARCHEOZOOLOGY {
        +__init__(self, id_archzoo, sito, area, us, quadrato, coord_x, coord_y, coord_z, bos_bison, calcinati, camoscio, capriolo, cervo, combusto, coni, pdi, stambecco, strie, canidi, ursidi, megacero, entity_uuid)
        +__repr__(self)
    }
    class PYREPERTI {
        +__init__(self, id, id_rep, siti, link, the_geom)
        +__repr__(self)
    }
    class PYSITO_POLYGON {
        +__init__(self, pkuid, sito_id, the_geom)
        +__repr__(self)
    }
    class PYTOMBA {
        +__init__(self, id, sito, nr_scheda, the_geom)
        +__repr__(self)
    }
    class PYUSM {
        +__init__(self, gid, area_s, scavo_s, us_s, stratigraph_index_us, tipo_us_s, rilievo_originale, disegnatore, data, tipo_doc, nome_doc, coord, the_geom, unita_tipo_s)
        +__repr__(self)
    }
    class DETSESSO {
        +__init__(self, id_det_sesso, sito, num_individuo, glab_grado_imp, pmast_grado_imp, pnuc_grado_imp, pzig_grado_imp, arcsop_grado_imp, tub_grado_imp, pocc_grado_imp, inclfr_grado_imp, zig_grado_imp, msorb_grado_imp, glab_valori, pmast_valori, pnuc_valori, pzig_valori, arcsop_valori, tub_valori, pocc_valori, inclfr_valori, zig_valori, msorb_valori, palato_grado_imp, mfmand_grado_imp, mento_grado_imp, anmand_grado_imp, minf_grado_imp, brmont_grado_imp, condm_grado_imp, palato_valori, mfmand_valori, mento_valori, anmand_valori, minf_valori, brmont_valori, condm_valori, sex_cr_tot, ind_cr_sex, sup_p_I, sup_p_II, sup_p_III, sup_p_sex, in_isch_I, in_isch_II, in_isch_III, in_isch_sex, arco_c_sex, ramo_ip_I, ramo_ip_II, ramo_ip_III, ramo_ip_sex, prop_ip_sex, ind_bac_sex)
        +__repr__(self)
    }
    class PYLINEERIFERIMENTO {
        +__init__(self, id, sito, definizion, descrizion, the_geom)
        +__repr__(self)
    }
    class SITE {
        +__init__(self, id_sito, sito, nazione, regione, comune, descrizione, provincia, definizione_sito, sito_path, find_check, entity_uuid)
        +__repr__(self)
    }
    class POTTERY {
        +__init__(self, id_rep, id_number, sito, area, us, box, photo, drawing, anno, fabric, percent, material, form, specific_form, ware, munsell, surf_trat, exdeco, intdeco, wheel_made, descrip_ex_deco, descrip_in_deco, note, diametro_max, qty, diametro_rim, diametro_bottom, diametro_height, diametro_preserved, specific_shape, bag, sector, decoration_type, decoration_motif, decoration_position, datazione, entity_uuid)
        +__repr__(self)
    }
    class US {
        +__init__(self, id_us, sito, area, us, d_stratigrafica, d_interpretativa, descrizione, interpretazione, periodo_iniziale, fase_iniziale, periodo_finale, fase_finale, scavato, attivita, anno_scavo, metodo_di_scavo, inclusi, campioni, rapporti, data_schedatura, schedatore, formazione, stato_di_conservazione, colore, consistenza, struttura, cont_per, order_layer, documentazione, unita_tipo, settore, quad_par, ambient, saggio, elem_datanti, funz_statica, lavorazione, spess_giunti, letti_posa, alt_mod, un_ed_riass, reimp, posa_opera, quota_min_usm, quota_max_usm, cons_legante, col_legante, aggreg_legante, con_text_mat, col_materiale, inclusi_materiali_usm, n_catalogo_generale, n_catalogo_interno, n_catalogo_internazionale, soprintendenza, quota_relativa, quota_abs, ref_tm, ref_ra, ref_n, posizione, criteri_distinzione, modo_formazione, componenti_organici, componenti_inorganici, lunghezza_max, altezza_max, altezza_min, profondita_max, profondita_min, larghezza_media, quota_max_abs, quota_max_rel, quota_min_abs, quota_min_rel, osservazioni, datazione, flottazione, setacciatura, affidabilita, direttore_us, responsabile_us, cod_ente_schedatore, data_rilevazione, data_rielaborazione, lunghezza_usm, altezza_usm, spessore_usm, tecnica_muraria_usm, modulo_usm, campioni_malta_usm, campioni_mattone_usm, campioni_pietra_usm, provenienza_materiali_usm, criteri_distinzione_usm, uso_primario_usm, tipologia_opera, sezione_muraria, superficie_analizzata, orientamento, materiali_lat, lavorazione_lat, consistenza_lat, forma_lat, colore_lat, impasto_lat, forma_p, colore_p, taglio_p, posa_opera_p, inerti_usm, tipo_legante_usm, rifinitura_usm, materiale_p, consistenza_p, rapporti2, doc_usv, entity_uuid)
        +__repr__(self)
    }
    class PYQUOTEUSM {
        +__init__(self, id, sito_q, area_q, us_q, unita_misu_q, quota_q, data, disegnatore, rilievo_originale, the_geom, unita_tipo_q)
        +__repr__(self)
    }
    class PRESENZE {
        +__init__(self, id_presenza, sito, id_personale, data, ora_ingresso, ora_uscita, ore_ordinarie, ore_straordinario, tipo_giornata, turno, area_lavoro, note, costo_giornata, entity_uuid)
        +__repr__(self)
    }
    class INVENTARIO_MATERIALI {
        +__init__(self, id_invmat, sito, numero_inventario, tipo_reperto, criterio_schedatura, definizione, descrizione, area, us, lavato, nr_cassa, luogo_conservazione, stato_conservazione, datazione_reperto, elementi_reperto, misurazioni, rif_biblio, tecnologie, forme_minime, forme_massime, totale_frammenti, corpo_ceramico, rivestimento, diametro_orlo, peso, tipo, eve_orlo, repertato, diagnostico, n_reperto, tipo_contenitore, struttura, years, schedatore, date_scheda, punto_rinv, negativo_photo, diapositiva, quota_usm, unita_misura_quota, photo_id, drawing_id, entity_uuid, sub_inv)
        +__repr__(self)
    }
    class MEDIA_THUMB {
        +__init__(self, id_media_thumb, id_media, mediatype, media_filename, media_thumb_filename, filetype, filepath, path_resize, entity_uuid)
        +__repr__(self)
    }
    class PYSEZIONI {
        +__init__(self, id, id_sezione, sito, area, descr, the_geom, tipo_doc, nome_doc)
        +__repr__(self)
    }
    class TMA {
        +__init__(self, id, sito, area, localita, settore, inventario, ogtm, ldct, ldcn, vecchia_collocazione, cassetta, scan, saggio, vano_locus, dscd, dscu, rcgd, rcgz, aint, aind, dtzg, deso, nsc, ftap, ftan, drat, dran, draa, created_at, updated_at, created_by, updated_by, entity_uuid)
        +__repr__(self)
    }
    class POTTERY_EMBEDDING_METADATA {
        +__init__(self, id_embedding, id_rep, id_media, image_hash, model_name, search_type, embedding_version, created_at)
        +__repr__(self)
        +as_dict(self)
    }
    class MEDIATOENTITY {
        +__init__(self, id_mediaToEntity, id_entity, entity_type, table_name, id_media, filepath, media_name, entity_uuid)
        +__repr__(self)
    }
    class PDF_ADMINISTRATOR {
        +__init__(self, id_pdf_administrator, table_name, schema_griglia, schema_fusione_celle, modello)
        +__repr__(self)
    }
    class PYUS_NEGATIVE {
        +__init__(self, pkuid, sito_n, area_n, us_n, tipo_doc_n, nome_doc_n, the_geom)
        +__repr__(self)
    }
    class PERIODIZZAZIONE {
        +__init__(self, id_perfas, sito, periodo, fase, cron_iniziale, cron_finale, descrizione, datazione_estesa, cont_per, entity_uuid)
        +__repr__(self)
    }
    class US_TOIMP {
        +__init__(self, id_us, sito, area, us, d_stratigrafica, d_interpretativa, descrizione, interpretazione, periodo_iniziale, fase_iniziale, periodo_finale, fase_finale, scavato, attivita, anno_scavo, metodo_di_scavo, inclusi, campioni, rapporti, data_schedatura, schedatore, formazione, stato_di_conservazione, colore, consistenza, struttura)
        +__repr__(self)
    }
    class PYSTRUTTURE {
        +__init__(self, id, sito, id_strutt, per_iniz, per_fin, dataz_ext, fase_iniz, fase_fin, descrizione, the_geom, sigla_strut, nr_strut)
        +__repr__(self)
    }
    class INVENTARIO_LAPIDEI {
        +__init__(self, id_invlap, sito, scheda_numero, collocazione, oggetto, tipologia, materiale, d_letto_posa, d_letto_attesa, toro, spessore, larghezza, lunghezza, h, descrizione, lavorazione_e_stato_di_conservazione, confronti, cronologia, bibliografia, compilatore, entity_uuid)
        +__repr__(self)
    }
    class pyquote {
        +define_table(cls, metadata)
    }
    class PERSONALE {
        +__init__(self, id_personale, sito, nome, cognome, ruolo, qualifica, codice_fiscale, email, telefono, data_nascita, indirizzo, tipo_contratto, data_inizio_contratto, data_fine_contratto, tariffa_oraria, tariffa_giornaliera, iban, note, attivo, entity_uuid)
        +__repr__(self)
    }
    class pyunitastratigrafiche {
        +define_table(cls, metadata)
    }
    class PotteryTable {
        +define_table(cls, metadata)
    }
    class Periodizzazione_table {
        +define_table(cls, metadata)
    }
    class Media_to_Entity_table {
        +define_table(cls, metadata)
    }
    class Media_table {
        +define_table(cls, metadata)
    }
    class Tma_table {
        +define_table(cls, metadata)
    }
    class pydocumentazione {
        +define_table(cls, metadata)
    }
    class Media_thumb_table {
        +define_table(cls, metadata)
    }
    class Pyarchinit_thesaurus_sigle {
        +define_table(cls, metadata)
    }
    class pyripartizioni_spaziali {
        +define_table(cls, metadata)
    }
    class pycampioni {
        +define_table(cls, metadata)
    }
    class Documentazione_table {
        +define_table(cls, metadata)
    }
    class DETSESSO_table {
        +define_table(cls, metadata)
    }
    class pysito_point {
        +define_table(cls, metadata)
    }
    class pyindividui {
        +define_table(cls, metadata)
    }
    class Computo_metrico_table {
        +define_table(cls, metadata)
    }
    class Struttura_table {
        +define_table(cls, metadata)
    }
    class pyunitastratigrafiche_usm {
        +define_table(cls, metadata)
    }
    class Tma_materiali_table {
        +define_table(cls, metadata)
    }
    class SCHEDAIND_table {
        +define_table(cls, metadata)
    }
    class pyreperti {
        +define_table(cls, metadata)
    }
    class pytomba {
        +define_table(cls, metadata)
    }
    class Inventario_materiali_table {
        +define_table(cls, metadata)
    }
    class Budget_table {
        +define_table(cls, metadata)
    }
    class pysito_polygon {
        +define_table(cls, metadata)
    }
    class Inventario_Lapidei_table {
        +define_table(cls, metadata)
    }
    class Media_to_Entity_table_view {
        +define_table(self, metadata)
    }
    class US_table_toimp {
    }
    class pylineeriferimento {
        +define_table(cls, metadata)
    }
    class Site_table {
        +define_table(cls, metadata)
    }
    class Personale_table {
        +define_table(cls, metadata)
    }
    class Campioni_table {
        +define_table(cls, metadata)
    }
    class pysezioni {
        +define_table(cls, metadata)
    }
    class pyquote_usm {
        +define_table(cls, metadata)
    }
    class UT_table {
        +define_table(cls, metadata)
    }
    class Attrezzature_table {
        +define_table(cls, metadata)
    }
    class DETETA_table {
        +define_table(cls, metadata)
    }
    class Tomba_table {
    }
    class Presenze_table {
        +define_table(cls, metadata)
    }
    class US_table {
        +define_table(cls, metadata)
    }
    class pystrutture {
        +define_table(cls, metadata)
    }
    class pyus_negative {
        +define_table(cls, metadata)
    }
    class PDF_administrator_table {
    }
    class Tomba_table {
        +define_table(cls, metadata)
    }
    class GeoArchaeoPlugin {
        +__init__(self, iface)
        +initGui(self)
        +toggle_dock(self)
        +quick_variogram(self)
        +quick_kriging(self)
        ... +5 more methods
    }
    class DummyPlugin {
        +initGui(self)
        +unload(self)
    }
    class GeoArchaeoProvider {
        +__init__(self, engine)
        +loadAlgorithms(self)
        +id(self)
        +name(self)
        +icon(self)
    }
    QgsProcessingProvider <|-- GeoArchaeoProvider
    class VariogramAlgorithm {
        +__init__(self, engine)
        +name(self)
        +displayName(self)
        +createInstance(self)
        +initAlgorithm(self, config)
        ... +1 more methods
    }
    QgsProcessingAlgorithm <|-- VariogramAlgorithm
    class OrdinaryKrigingAlgorithm {
        +__init__(self, engine)
        +name(self)
        +displayName(self)
        +createInstance(self)
        +initAlgorithm(self, config)
        ... +1 more methods
    }
    QgsProcessingAlgorithm <|-- OrdinaryKrigingAlgorithm
    class CoKrigingAlgorithm {
        +__init__(self, engine)
        +name(self)
        +displayName(self)
        +createInstance(self)
        +initAlgorithm(self, config)
        ... +1 more methods
    }
    QgsProcessingAlgorithm <|-- CoKrigingAlgorithm
    class SpatioTemporalKrigingAlgorithm {
        +__init__(self, engine)
        +name(self)
        +displayName(self)
        +createInstance(self)
        +initAlgorithm(self, config)
        ... +1 more methods
    }
    QgsProcessingAlgorithm <|-- SpatioTemporalKrigingAlgorithm
    class CompositionalAnalysisAlgorithm {
        +__init__(self, engine)
        +name(self)
        +displayName(self)
        +createInstance(self)
        +initAlgorithm(self, config)
        ... +1 more methods
    }
    QgsProcessingAlgorithm <|-- CompositionalAnalysisAlgorithm
    class MLPatternRecognitionAlgorithm {
        +__init__(self, engine)
        +name(self)
        +displayName(self)
        +createInstance(self)
        +initAlgorithm(self, config)
        ... +1 more methods
    }
    QgsProcessingAlgorithm <|-- MLPatternRecognitionAlgorithm
    class BatchKrigingAlgorithm {
        +__init__(self, engine)
        +name(self)
        +displayName(self)
        +createInstance(self)
        +initAlgorithm(self, config)
        ... +1 more methods
    }
    QgsProcessingAlgorithm <|-- BatchKrigingAlgorithm
    class OptimalSamplingAlgorithm {
        +__init__(self, engine)
        +name(self)
        +displayName(self)
        +createInstance(self)
        +initAlgorithm(self, config)
        ... +1 more methods
    }
    QgsProcessingAlgorithm <|-- OptimalSamplingAlgorithm
    class GeostatEngine {
        +__init__(self)
        +calculate_variogram(self, points, values, max_distance, model_type, check_anisotropy)
        +ordinary_kriging(self, points, values, extent, pixel_size, variogram_params)
        +co_kriging(self, primary_points, primary_values, secondary_data, extent, pixel_size)
        +spatiotemporal_kriging(self, space_time_data, target_time, extent)
        ... +17 more methods
    }
    class DummyBBox {
        +__init__(self, xmin, xmax, ymin, ymax)
        +xMinimum(self)
        +xMaximum(self)
        +yMinimum(self)
        +yMaximum(self)
        ... +2 more methods
    }
    class BundleCreator {
        +__init__(self, output_dir, site_name, user, organization, tool_version, ontology_references)
        +add_data_file(self, source_path, relative_path)
        +add_media_file(self, source_path, relative_path)
        +add_directory(self, source_dir, bundle_subdir, extensions)
        +build(self)
    }
    class ConnectivityMonitor {
        +__init__(self, parent, check_interval_ms, debounce_count)
        +is_online(self)
        +start(self)
        +stop(self)
        +check_now(self)
        ... +1 more methods
    }
    QObject <|-- ConnectivityMonitor
    class AnalysisThread {
        +__init__(self, engine, method, params)
        +cancel(self)
        +run(self)
    }
    QThread <|-- AnalysisThread
    class GeoArchaeoDockWidget {
        +__init__(self, parent)
        +switch_to_tab(self, tab_name)
        +generate_full_report(self)
    }
    QDockWidget <|-- GeoArchaeoDockWidget
    class QueueEntry {
    }
    class SyncQueue {
        +__init__(self, db_path)
        +enqueue(self, bundle_path, bundle_hash, metadata)
        +dequeue(self)
        +mark_completed(self, entry_id)
        +mark_failed(self, entry_id, error)
        ... +5 more methods
    }
    class BundleManifest {
        +__init__(self, tool_version, user, organization, ontology_references)
        +add_file(self, filepath, relative_path)
        +generate(self)
        +to_json(self, indent)
        +write(self, filepath)
    }
    class ValidationLevel {
    }
    class ValidationResult {
        +__init__(self, level, code, message, context)
        +__repr__(self)
        +to_dict(self)
    }
    class BundleValidator {
        +validate_directory(self, bundle_dir)
        +validate_zip(self, zip_path)
    }
    class SyncState {
    }
    Enum <|-- SyncState
    class SyncStateMachine {
        +__init__(self, parent)
        +current_state(self)
        +transition(self, new_state, context)
        +get_transition_history(self, limit)
        +reset(self)
    }
    QObject <|-- SyncStateMachine
    class SyncOrchestrator {
        +__init__(self, parent)
        +start(self)
        +stop(self)
        +export_bundle(self, site_name)
        +sync_now(self)
        ... +1 more methods
    }
    QObject <|-- SyncOrchestrator
    class SamPointMapTool {
        +__init__(self, canvas, raster_layer, on_points_collected, on_point_added, on_cancelled)
        +canvasPressEvent(self, event)
        +keyPressEvent(self, event)
        +deactivate(self)
        +get_points(self)
        ... +1 more methods
    }
    QgsMapToolEmitPoint <|-- SamPointMapTool
    class SamBoxMapTool {
        +__init__(self, canvas, raster_layer, on_box_drawn, on_cancelled)
        +canvasPressEvent(self, event)
        +canvasMoveEvent(self, event)
        +canvasReleaseEvent(self, event)
        +keyPressEvent(self, event)
        ... +1 more methods
    }
    QgsMapTool <|-- SamBoxMapTool
    class SamPolygonMapTool {
        +__init__(self, canvas, raster_layer, on_polygon_drawn, on_cancelled)
        +canvasPressEvent(self, event)
        +canvasDoubleClickEvent(self, event)
        +canvasMoveEvent(self, event)
        +keyPressEvent(self, event)
        ... +1 more methods
    }
    QgsMapTool <|-- SamPolygonMapTool
    class Text2SQLWidget {
        +__init__(self, parent)
        +setup_ui(self)
        +on_generate_clicked(self)
        +on_explain_clicked(self)
        +on_clear_clicked(self)
        ... +2 more methods
    }
    QWidget <|-- Text2SQLWidget
    class MakeSQL {
        +schema_to_text(metadata)
        +get_api_key(parent)
        +make_openai_request(prompt, db_type, parent)
        +explain_openai_request(sql_query, parent)
        +get_anthropic_api_key(parent)
        ... +10 more methods
    }
    class Pyarchinit_pyqgis {
        +__init__(self, iface)
        +remove_USlayer_from_registry(self)
        +charge_individui_us(self, data)
        +charge_vector_layers(self, data)
        +charge_vector_layers_periodo(self, cont_per)
        ... +5 more methods
    }
    QDialog <|-- Pyarchinit_pyqgis
    class Order_layers {
        +__init__(self, lr)
        +main(self)
        +add_values_to_lista_us(self)
        +loop_on_lista_us(self)
        +check_position(self, n)
        ... +1 more methods
    }
    class MyError {
        +__init__(self, value)
        +__str__(self)
    }
    Exception <|-- MyError
    class TMAThesaurusSync {
        +__init__(self, db_manager)
        +sync_settore_to_thesaurus(self, settore, sito, source_table)
        +sync_area_to_thesaurus(self, area, sito, source_table)
        +sync_material_value_to_thesaurus(self, value, field_type)
        +sync_from_inventory_materials(self, inventory_record)
        ... +6 more methods
    }
    class Pyarchinit_OS_Utility {
        +create_dir(self, d)
        +copy_file_img(self, f, d)
        +copy_file(self, f, d)
        +checkgraphvizinstallation()
        +checkpostgresinstallation()
        ... +2 more methods
    }
    class Pyarchinit_pyqgis {
        +__init__(self, iface)
        +create_us_nested_symbology(self, layer, site_filter)
        +load_us_view_with_sketched_sketched_sketched(self, db_path, view_name, filter_expr, srid, layer_name, use_sketched_sketched_sketched)
        +remove_USlayer_from_registry(self)
        +charge_individui_us(self, data)
        ... +32 more methods
    }
    QDialog <|-- Pyarchinit_pyqgis
    class Order_layer_v2 {
        +__init__(self, dbconn, SITOol, AREAol)
        +center_on_screen(self, widget)
        +main_order_layer(self)
        +find_base_matrix(self)
        +create_list_values(self, rapp_type_list, value_list, ar, si)
        ... +4 more methods
    }
    class LogHandler {
        +__init__(self, text_widget)
        +emit(self, record)
    }
    logging.Handler <|-- LogHandler
    class Order_layer_graph {
        +__init__(self, dbconn, SITOol, AREAol)
        +center_on_screen(self, widget)
        +main_order_layer(self, reverse_order)
        +update_database_with_order(self, db_manager, mapper_table_class, id_table, sito, area)
        +close_progress_widget(self)
        ... +6 more methods
    }
    class MyError {
        +__init__(self, value)
        +__str__(self)
    }
    Exception <|-- MyError
    class ProgressDialog {
        +__init__(self)
        +setValue(self, value)
        +closeEvent(self, event)
    }
    class ThemeManager {
        +__new__(cls)
        +__init__(self)
        +get_saved_theme(cls)
        +save_theme(cls, theme)
        +get_current_theme(cls)
        ... +7 more methods
    }
    class Cronology_convertion {
        +sum_list_of_tuples_for_value(self, l)
        +convert_data(self, datazione_reperto)
        +found_intervallo_per_forma(self, data)
        +calc_percent(self, val_parz, val_totale)
        +media_ponderata_perc_intervallo(self, lista_dati, valore)
        ... +3 more methods
    }
    class TooltipListView {
        +__init__(self, parent)
        +viewportEvent(self, event)
    }
    QListView <|-- TooltipListView
    class TooltipComboBox {
        +__init__(self, parent)
        +addItem(self, text, userData)
        +showPopup(self)
    }
    QComboBox <|-- TooltipComboBox
    class ComboBoxDelegate {
        +__init__(self, values, parent)
        +def_values(self, values)
        +def_editable(self, editable)
        +createEditor(self, parent, option, index)
        +setEditorData(self, editor, index)
        ... +1 more methods
    }
    QItemDelegate <|-- ComboBoxDelegate
    class TooltipListView {
        +__init__(self, parent)
        +viewportEvent(self, event)
    }
    QListView <|-- TooltipListView
    class TooltipComboBox {
        +__init__(self, parent)
        +addItem(self, text, userData)
        +showPopup(self)
    }
    QComboBox <|-- TooltipComboBox
    class ComboBoxDelegate {
        +__init__(self, values, parent)
        +def_values(self, values)
        +def_editable(self, editable)
        +createEditor(self, parent, option, index)
        +setEditorData(self, editor, index)
        ... +1 more methods
    }
    QItemDelegate <|-- ComboBoxDelegate
    class Print_utility {
        +__init__(self, iface, data)
        +first_batch_try(self, server)
        +converter_1_20(self, n)
        +test_bbox(self)
        +getMapExtentFromMapCanvas(self, mapWidth, mapHeight, scale)
        ... +6 more methods
    }
    QObject <|-- Print_utility
    class ArchaeologicalDataMapper {
        +__init__(self, iface, parent)
        +initUI(self)
        +open_file(self, link)
        +get_input_file(self)
        +get_output_file(self)
        ... +4 more methods
    }
    QWidget <|-- ArchaeologicalDataMapper
    class NumberedCanvas_Invlapsheet {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_Invlapsheet
    class single_Invlap_pdf_sheet {
        +__init__(self, data)
        +datestrfdate(self)
        +create_sheet(self)
        +create_sheet_de(self)
        +create_sheet_en(self)
    }
    class generate_reperti_pdf {
        +datestrfdate(self)
        +build_Invlap_sheets(self, records)
        +build_Invlap_sheets_de(self, records)
        +build_Invlap_sheets_en(self, records)
    }
    class CollapsibleSection {
        +__init__(self, title, parent)
        +toggle_content(self)
        +add_widget(self, widget)
        +add_layout(self, layout)
    }
    QWidget <|-- CollapsibleSection
    class ReportGeneratorDialog {
        +__init__(self, parent)
        +get_llm_config(self)
        +get_selected_language(self)
        +get_streaming_enabled(self)
        +validate_data(self)
        ... +7 more methods
    }
    QDialog <|-- ReportGeneratorDialog
    class CheckableComboBox {
        +__init__(self)
        +add_item(self, text, checked)
        +items_checked(self)
        +handle_item_pressed(self, index)
    }
    QComboBox <|-- CheckableComboBox
    class ReportDialog {
        +__init__(self, content, parent)
        +update_content(self, new_content)
        +append_streaming_token(self, token)
        +handle_mouse_press(self, event)
        +log_to_terminal(self, message, msg_type)
        ... +10 more methods
    }
    QDialog <|-- ReportDialog
    class GenerateReportThread {
        +__init__(self, custom_prompt, descriptions_text, api_key, selected_model, selected_tables, analysis_steps, agent, us_data, materials_data, pottery_data, site_data, py_dialog, output_language, tomba_data, periodizzazione_data, struttura_data, tma_data, enable_streaming, llm_config)
        +create_vector_db(self, data, table_name)
        +retrieve_relevant_data(self, vector_store, query, k)
        +create_rag_chain(self, vector_store, llm)
        +count_tokens(self, text)
        ... +24 more methods
    }
    QThread <|-- GenerateReportThread
    class RAGRebuildWorker {
        +__init__(self, db_manager, parent_dialog)
        +run(self)
    }
    QThread <|-- RAGRebuildWorker
    class RAGQueryDialog {
        +__init__(self, db_manager, parent)
        +setup_ui(self)
        +check_and_rebuild_rag(self)
        +on_rebuild_progress(self, message)
        +on_rebuild_complete(self, result)
        ... +27 more methods
    }
    QDialog <|-- RAGQueryDialog
    class RAGQueryWorker {
        +__init__(self, query, db_manager, api_key, model, conversation_history, parent, enable_streaming, force_reload, llm_config)
        +get_media_thumbnail_path(self, media_record)
        +get_media_resize_path(self, media_record)
        +run(self)
        +load_all_database_data(self)
        ... +13 more methods
    }
    QThread <|-- RAGQueryWorker
    class ProgressDialog {
        +__init__(self, title, total_items)
        +setValue(self, value, label_text)
        +close(self)
        +setLabelText(self, text)
        +closeEvent(self, event)
    }
    class pyarchinit_US {
        +natural_sort_key(text)
        +__init__(self, iface)
        +get_images_for_entities(self, entity_ids, log_signal, entity_type)
        +count_tokens(self, text)
        +create_vector_db(self, data, table_name)
        ... +271 more methods
    }
    QDialog <|-- pyarchinit_US
    MAIN_DIALOG_CLASS <|-- pyarchinit_US
    class SQLPromptDialog {
        +__init__(self, iface, parent)
        +clear_fields(self)
        +clear_results_table(self)
        +on_prompt_selected(self, index)
        +update_prompt_ui(self)
        ... +19 more methods
    }
    QDialog <|-- SQLPromptDialog
    class MplCanvas {
        +__init__(self, parent)
    }
    FigureCanvas <|-- MplCanvas
    class GraphWindow {
        +__init__(self)
        +plot(self, data)
    }
    QDockWidget <|-- GraphWindow
    class USFilterDialog {
        +__init__(self, db_manager, parent, site_filter)
        +initUI(self)
        +natural_sort_key(self, text)
        +populate_list_with_us(self)
        +update_list_widget(self, records)
        ... +3 more methods
    }
    QDialog <|-- USFilterDialog
    class IntegerDelegate {
        +__init__(self, parent)
        +createEditor(self, parent, option, index)
    }
    QtWidgets.QStyledItemDelegate <|-- IntegerDelegate
    class SimpleGPT5Wrapper {
        +__init__(self, llm, vectorstore, parent_thread, enable_streaming, raw_data)
        +invoke(self, input_dict)
    }
    class GPT5DirectWrapper {
        +__init__(self, llm, tools, system_message, parent_thread)
        +invoke(self, input_dict, config)
    }
    class StreamingHandler {
        +__init__(self, parent_thread)
        +on_llm_new_token(self, token)
    }
    BaseCallbackHandler <|-- StreamingHandler
    class OverviewStreamHandler {
        +__init__(self, parent_thread)
        +on_llm_new_token(self, token)
    }
    BaseCallbackHandler <|-- OverviewStreamHandler
    class StreamHandler {
        +__init__(self, parent_thread)
        +on_llm_new_token(self, token)
    }
    BaseCallbackHandler <|-- StreamHandler
    class FakeMatch {
        +group(self, n)
    }
    class SimplifiedStreamHandler {
        +__init__(self, parent_thread)
        +on_llm_new_token(self, token)
    }
    BaseCallbackHandler <|-- SimplifiedStreamHandler
    class NumberedCanvas_Findssheet {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_Findssheet
    class NumberedCanvas_FINDSindex {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_FINDSindex
    class NumberedCanvas_CASSEindex {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_CASSEindex
    class single_Finds_pdf_sheet {
        +__init__(self, data)
        +datestrfdate(self)
        +create_sheet(self)
        +create_sheet_de(self)
        +create_sheet_en(self)
        ... +4 more methods
    }
    class Box_labels_Finds_pdf_sheet {
        +__init__(self, data, sito)
        +datestrfdate(self)
        +create_sheet(self)
        +create_sheet_de(self)
        +create_sheet_en(self)
    }
    class CASSE_index_pdf_sheet {
        +__init__(self, data)
        +getTable(self)
        +getTable_de(self)
        +getTable_en(self)
        +makeStyles(self)
    }
    class FINDS_index_pdf_sheet {
        +__init__(self, data)
        +getTable(self)
        +getTable_de(self)
        +getTable_en(self)
        +makeStyles(self)
    }
    class FOTO_index_pdf_sheet {
        +__init__(self, data)
        +getTable(self)
        +getTable_en(self)
        +getTable_de(self)
        +makeStyles(self)
    }
    class FOTO_index_pdf_sheet_2 {
        +__init__(self, data)
        +getTable(self)
        +getTable_en(self)
        +getTable_de(self)
        +makeStyles(self)
    }
    class generate_reperti_pdf {
        +datestrfdate(self)
        +build_index_Foto(self, records, sito)
        +build_index_Foto_en(self, records, sito)
        +build_index_Foto_de(self, records, sito)
        +build_index_Foto_2(self, records, sito)
        ... +18 more methods
    }
    class Worker {
        +__init__(self, headers, params, url, is_image, image_width, image_height)
        +run(self)
    }
    QThread <|-- Worker
    class GPTWindow {
        +__init__(self, selected_images, dbmanager, main_class)
        +analyze_selected_images(self)
        +extract_and_display_links(self, response)
        +set_icon(self, icon_path)
        +start_worker(self, headers, params, url, is_image)
        ... +51 more methods
    }
    QMainWindow <|-- GPTWindow
    class NumberedCanvas_Individuisheet {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_Individuisheet
    class single_pdf_sheet {
        +__init__(self, data)
        +datestrfdate(self)
        +create_sheet(self)
    }
    class generate_pdf {
        +datestrfdate(self)
        +build_Individui_sheets(self, records)
    }
    class Window {
        +__init__(self, rows, columns)
        +handleItemClicked(self, item)
    }
    QWidget <|-- Window
    class NumberedCanvas_Individuisheet {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_Individuisheet
    class NumberedCanvas_Individuiindex {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_Individuiindex
    class Individui_index_pdf_sheet {
        +__init__(self, data)
        +getTable(self)
        +getTable_de(self)
        +getTable_en(self)
        +makeStyles(self)
    }
    class single_Individui_pdf_sheet {
        +__init__(self, data)
        +datestrfdate(self)
        +create_sheet(self)
        +create_sheet_de(self)
        +create_sheet_en(self)
    }
    class generate_pdf {
        +datestrfdate(self)
        +build_Individui_sheets(self, records)
        +build_Individui_sheets_de(self, records)
        +build_Individui_sheets_en(self, records)
        +build_index_individui(self, records, sito)
        ... +2 more methods
    }
    class NumberedCanvas_USsheet {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_USsheet
    class NumberedCanvas_USindex {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_USindex
    class single_US_pdf_sheet {
        +escape_html(text)
        +__init__(self, data)
        +unzip_componenti(self)
        +unzip_rapporti_stratigrafici(self)
        +unzip_rapporti_stratigrafici_de(self)
        ... +16 more methods
    }
    class US_index_pdf_sheet {
        +__init__(self, data)
        +unzip_rapporti_stratigrafici(self)
        +getTable(self)
        +unzip_rapporti_stratigrafici_en(self)
        +getTable_en(self)
        ... +3 more methods
    }
    class FOTO_index_pdf_sheet {
        +__init__(self, data)
        +getTable(self)
        +getTable_en(self)
        +getTable_de(self)
        +makeStyles(self)
    }
    class FOTO_index_pdf_sheet_2 {
        +__init__(self, data)
        +getTable(self)
        +getTable_en(self)
        +getTable_de(self)
        +getTable_fr(self)
        ... +4 more methods
    }
    class generate_US_pdf {
        +datestrfdate(self)
        +build_US_sheets(self, records)
        +build_US_sheets_en(self, records)
        +build_US_sheets_de(self, records)
        +build_US_sheets_fr(self, records)
        ... +12 more methods
    }
    class NumberedCanvas_TOMBAsheet {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_TOMBAsheet
    class NumberedCanvas_TOMBAindex {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_TOMBAindex
    class Tomba_index_pdf_sheet {
        +__init__(self, data)
        +getTable(self)
        +getTable_de(self)
        +getTable_en(self)
        +makeStyles(self)
    }
    class Tomba_index_II_pdf_sheet {
        +__init__(self, data)
        +getTable(self)
        +getTable_de(self)
        +getTable_en(self)
        +makeStyles(self)
    }
    class single_Tomba_pdf_sheet {
        +__init__(self, data)
        +datestrfdate(self)
        +create_sheet(self)
        +create_sheet_de(self)
        +create_sheet_en(self)
    }
    class generate_tomba_pdf {
        +datestrfdate(self)
        +build_Tomba_sheets(self, records)
        +build_Tomba_sheets_de(self, records)
        +build_Tomba_sheets_en(self, records)
        +build_index_Tomba(self, records, sito)
    }
    class DatabaseSchemaKnowledge {
        +get_full_schema()
        +get_schema_prompt()
        +get_table_list()
        +get_table_fields(table_name)
        +get_geometry_tables()
    }
    class VideoPlayerWindow {
        +__init__(self, parent, db_manager, icon_list_widget, main_class)
        +set_video(self, file_path)
        +play_pause(self)
        +update_frame(self)
        +display_frame(self, frame)
        ... +15 more methods
    }
    QMainWindow <|-- VideoPlayerWindow
    class PDFExtractor {
        +__init__(self)
        +extract_from_images(self, image_paths, output_dir, auto_detect, confidence, kernel_size, iterations)
        +load_yolo_model(self)
        +detect_and_extract_pottery(self, image_path, confidence, kernel_size, iterations)
        +extract(self, pdf_path, output_dir, split_pages, auto_detect, confidence, kernel_size, iterations)
    }
    class LayoutGenerator {
        +__init__(self)
        +get_font(self, size)
        +create_preview(self, images, mode, page_size, rows, cols)
        +generate(self, images, output_path, mode, page_size, rows, cols, add_captions, add_scale, scale_cm)
    }
    class ImageProcessor {
        +__init__(self)
        +enhance_image(self, image_path, output_path, brightness, contrast, sharpness)
        +remove_background(self, image_path, output_path, threshold)
    }
    class PotteryInkProcessor {
        +__init__(self, venv_python)
        +is_available(self)
        +load_model(self, model_path)
        +enhance_drawing(self, input_image_path, output_path, prompt, contrast_scale, patch_size, overlap, apply_preprocessing, model_path, use_ml, manual_contrast, manual_brightness, background_mode, bg_threshold)
        +extract_elements(self, image_path, output_dir, min_area)
        ... +6 more methods
    }
    class ThesaurusStyler {
        +__init__(self, default_style_path)
        +load_default_style(self)
        +get_style(self, sigla)
        +apply_style_to_layer(self, layer, d_stratigrafica_field, thesaurus_mapping)
    }
    class USViewStyler {
        +__init__(self, connection, sito)
        +ask_user_style_preference(self)
        +ask_user_categorization_field(self, layer)
        +load_style_from_db(self, layer)
        +load_style_from_db_new(self, layer)
        ... +4 more methods
    }
    class NumberedCanvas_TMAsheet {
        +__init__(self)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_TMAsheet
    class generate_tma_pdf {
        +__init__(self, data)
        +datestrfdate(self)
        +create_sheet(self)
        +create_sheet_it(self)
        +create_sheet_de(self)
        ... +5 more methods
    }
    class DocumentProcessor {
        +__init__(self)
        +process_document(self, doc_path, output_path)
        +process_content_to_paragraphs(self, content, doc)
        +quick_fix_document(doc_path)
    }
    class CloudinarySync {
        +get_instance(cls)
        +__init__(self)
        +is_enabled(self)
        +get_backend(self)
        +sync_file(self, local_path, cloudinary_folder, auto_tag)
        ... +6 more methods
    }
    class Media_utility {
        +resample_images(self, mid, ip, i, o, ts)
    }
    class Media_utility_resize {
        +resample_images(self, mid, ip, i, o, ts)
    }
    class Video_utility {
        +resample_images(self, mid, ip, i, o, ts)
    }
    class Video_utility_resize {
        +resample_images(self, mid, ip, i, o, ts)
    }
    class MplCanvas {
        +__init__(self)
    }
    FigureCanvas <|-- MplCanvas
    class Mplwidget {
        +__init__(self, parent)
    }
    QWidget <|-- Mplwidget
    class NumberedCanvas_Campionisheet {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_Campionisheet
    class NumberedCanvas_Campioniindex {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_Campioniindex
    class NumberedCanvas_CASSEindex {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_CASSEindex
    class single_Campioni_pdf_sheet {
        +__init__(self, data)
        +datestrfdate(self)
        +create_sheet(self)
        +create_sheet_de(self)
        +create_sheet_en(self)
    }
    class Box_labels_Campioni_pdf_sheet {
        +__init__(self, data, sito)
        +datestrfdate(self)
        +create_sheet(self)
        +create_sheet_de(self)
        +create_sheet_en(self)
    }
    class CASSE_index_pdf_sheet {
        +__init__(self, data)
        +getTable(self)
        +getTable_de(self)
        +getTable_en(self)
        +makeStyles(self)
    }
    class Campioni_index_pdf_sheet {
        +__init__(self, data)
        +getTable(self)
        +getTable_de(self)
        +getTable_en(self)
        +makeStyles(self)
    }
    class generate_campioni_pdf {
        +datestrfdate(self)
        +build_Champ_sheets(self, records)
        +build_Champ_sheets_de(self, records)
        +build_Champ_sheets_en(self, records)
        +build_index_Campioni(self, records, sito)
        ... +8 more methods
    }
    class LLMProvider {
    }
    Enum <|-- LLMProvider
    class LLMConfig {
        +__post_init__(self)
        +is_local(self)
        +needs_api_key(self)
    }
    class LLMProviderManager {
        +is_provider_available(provider, timeout)
        +discover_models(provider, timeout)
        +discover_embedding_models(provider, timeout)
        +discover_all_models(provider, timeout)
        +filter_vision_models(provider, models)
        ... +8 more methods
    }
    class VideoPlayerWindow {
        +__init__(self, parent, db_manager, icon_list_widget, main_class)
        +set_video(self, file_path)
        +play_pause(self)
        +update_frame(self)
        +display_frame(self, frame)
        ... +15 more methods
    }
    QMainWindow <|-- VideoPlayerWindow
    class NumberedCanvas_STRUTTURAindex {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_STRUTTURAindex
    class NumberedCanvas_STRUTTURAsheet {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_STRUTTURAsheet
    class Struttura_index_pdf_sheet {
        +__init__(self, data)
        +getTable(self)
        +getTable_de(self)
        +getTable_en(self)
        +getTable_fr(self)
        ... +4 more methods
    }
    class single_Struttura_pdf_sheet {
        +__init__(self, data)
        +datestrfdate(self)
        +create_sheet(self)
        +create_sheet_de(self)
        +create_sheet_en(self)
        ... +4 more methods
    }
    class generate_struttura_pdf {
        +datestrfdate(self)
        +build_Struttura_sheets(self, records)
        +build_index_Struttura(self, records, sito)
        +build_Struttura_sheets_de(self, records)
        +build_index_Struttura_de(self, records, sito)
        ... +10 more methods
    }
    class NumberedCanvas_Documentazionesheet {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_Documentazionesheet
    class NumberedCanvas_Documentazioneindex {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_Documentazioneindex
    class single_Documentazione_pdf_sheet {
        +__init__(self, data)
        +datestrfdate(self)
        +create_sheet(self)
        +create_sheet_de(self)
        +create_sheet_en(self)
    }
    class Documentazione_index_pdf_sheet {
        +__init__(self, data)
        +getTable(self)
        +getTable_de(self)
        +getTable_en(self)
        +makeStyles(self)
    }
    class generate_documentazione_pdf {
        +datestrfdate(self)
        +build_Documentazione_sheets(self, records)
        +build_Documentazione_sheets_de(self, records)
        +build_Documentazione_sheets_en(self, records)
        +build_index_Documentazione(self, records, sito)
        ... +2 more methods
    }
    class UTF8Recoder {
        +__init__(self, f, encoding)
        +__iter__(self)
        +__next__(self)
    }
    class UnicodeReader {
        +__init__(self, f, dialect, encoding)
        +__next__(self)
        +__iter__(self)
    }
    class UnicodeWriter {
        +__init__(self, f, dialect, encoding)
        +writerow(self, row)
        +writerows(self, rows)
    }
    class TMALabelPDF {
        +__init__(self, label_format, page_size)
        +calculate_label_positions(self)
        +get_color_for_site(self, site_name)
        +draw_area_symbol(self, c, center_x, center_y, area, size)
        +generate_qr_code(self, data, size, color)
        ... +6 more methods
    }
    class FestosInventoryParser {
        +__init__(self)
        +parse_file(self, file_path, sito)
    }
    class NumberedCanvas_InventarioA5 {
        +__init__(self)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
        +draw_headers(self)
    }
    canvas.Canvas <|-- NumberedCanvas_InventarioA5
    class generate_inventario_pdf_a5 {
        +datestrfdate(self)
        +build_Inventario_a5(self, records, sito, left_title, right_title)
    }
    class single_Inventario_pdf_sheet_a5 {
        +__init__(self, data, left_title, right_title)
        +parse_measurements(self)
        +parse_elementi(self)
        +get_first_image(self)
        +create_sheet(self)
        ... +1 more methods
    }
    class CustomCanvas {
        +__init__(self)
    }
    NumberedCanvas_InventarioA5 <|-- CustomCanvas
    class TMAFieldMapping {
        +find_field_mapping(cls, field_name)
        +validate_field_value(cls, field, value)
    }
    class BaseParser {
        +__init__(self, file_path)
        +parse(self)
        +validate_required_fields(self, record)
        +clean_value(self, value)
    }
    ABC <|-- BaseParser
    class ExcelParser {
        +parse(self)
    }
    BaseParser <|-- ExcelParser
    class CSVParser {
        +__init__(self, file_path, delimiter, encoding)
        +parse(self)
    }
    BaseParser <|-- CSVParser
    class JSONParser {
        +parse(self)
    }
    BaseParser <|-- JSONParser
    class XMLParser {
        +parse(self)
    }
    BaseParser <|-- XMLParser
    class DOCXParser {
        +__init__(self, file_path, use_festos_parser, db_session)
        +parse(self)
    }
    BaseParser <|-- DOCXParser
    class TMAImportManager {
        +__init__(self, db_manager)
        +import_file(self, file_path, custom_mapping, use_festos_parser)
        +import_batch(self, file_paths)
    }
    class TMAInventoryParser {
        +__init__(self)
        +parse_docx_inventory(self, file_path, sito)
    }
    class TMAInventoryImportDialog {
        +__init__(self, parent)
        +get_completion_data(self, records)
    }
    class DocumentStyleAgent {
        +__init__(self)
        +analyze_document(self, paragraphs)
        +correct_document_styles(self, paragraphs)
        +get_style_statistics(self, corrections)
    }
    class pyarchinit_Folder_installation {
        +install_dir(self)
        +installConfigFile(self, path)
    }
    class ClickTool {
        +__init__(self, iface, callback)
        +canvasReleaseEvent(self, e)
    }
    QgsMapTool <|-- ClickTool
    class NumberedCanvas_Faunasheet {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_Faunasheet
    class NumberedCanvas_Faunaindex {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_Faunaindex
    class single_Fauna_pdf_sheet {
        +__init__(self, data)
        +datestrfdate(self)
        +create_sheet(self)
        +create_sheet_de(self)
        +create_sheet_en(self)
        ... +4 more methods
    }
    class generate_fauna_pdf {
        +datestrfdate(self)
        +build_Fauna_sheets(self, records)
        +build_Fauna_sheets_de(self, records)
        +build_Fauna_sheets_en(self, records)
        +build_Fauna_sheets_fr(self, records)
        ... +3 more methods
    }
    class Settings {
        +__init__(self, s)
        +set_configuration(self)
    }
    class TMAImportManagerExtended {
        +__init__(self, db_manager)
        +import_file(self, file_path, custom_mapping, use_festos_parser)
    }
    TMAImportManager <|-- TMAImportManagerExtended
    class NumberedCanvas_Individuisheet {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_Individuisheet
    class single_pdf_sheet {
        +__init__(self, data)
        +datestrfdate(self)
        +create_sheet(self)
    }
    class generate_pdf {
        +datestrfdate(self)
        +build_Individui_sheets(self, records)
    }
    class Error_check {
        +data_is_empty(self, d)
        +data_is_int(self, d)
        +data_lenght(self, d, l)
        +data_is_float(self, d)
        +checkIfDuplicates_3(listOfElems)
    }
    class NumberedCanvas_TOMBAsheet {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_TOMBAsheet
    class NumberedCanvas_TOMBAindex {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_TOMBAindex
    class Tomba_index_pdf_sheet {
        +__init__(self, data)
        +getTable(self)
        +getTable_en(self)
        +getTable_de(self)
        +makeStyles(self)
    }
    class Tomba_index_II_pdf_sheet {
        +__init__(self, data)
        +getTable(self)
        +getTable_de(self)
        +getTable_en(self)
        +makeStyles(self)
    }
    class single_Tomba_pdf_sheet {
        +__init__(self, data)
        +datestrfdate(self)
        +create_sheet(self)
        +create_sheet_de(self)
        +create_sheet_en(self)
        ... +4 more methods
    }
    class generate_tomba_pdf {
        +datestrfdate(self)
        +build_Tomba_sheets(self, records)
        +build_Tomba_sheets_de(self, records)
        +build_Tomba_sheets_en(self, records)
        +build_Tomba_sheets_fr(self, records)
        ... +4 more methods
    }
    class Cronology_convertion {
        +sum_list_of_tuples_for_value(self, l)
        +convert_data(self, datazione_reperto)
        +found_intervallo_per_forma(self, data)
        +calc_percent(self, val_parz, val_totale)
        +media_ponderata_perc_intervallo(self, lista_dati, valore)
        ... +3 more methods
    }
    class VideoPlayerWindow {
        +__init__(self, parent, db_manager, icon_list_widget, main_class)
        +set_video(self, file_path)
        +play_pause(self)
        +update_frame(self)
        +display_frame(self, frame)
        ... +15 more methods
    }
    QMainWindow <|-- VideoPlayerWindow
    class HarrisMatrix {
        +__init__(self, sequence, negative, conteporene, connection, connection_to, periodi)
        +export_matrix(self)
        +export_matrix_2(self)
    }
    class ViewHarrisMatrix {
        +__init__(self, sequence, negative, conteporene, connection, connection_to, periodi)
        +export_matrix(self)
        +export_matrix_3(self)
    }
    class NumberedCanvas_Periodizzazioneindex {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_Periodizzazioneindex
    class NumberedCanvas_Periodizzazionesheet {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_Periodizzazionesheet
    class Periodizzazione_index_pdf_sheet {
        +__init__(self, data)
        +getTable(self)
        +getTable_de(self)
        +getTable_en(self)
        +makeStyles(self)
    }
    class single_Periodizzazione_pdf_sheet {
        +__init__(self, data)
        +datestrfdate(self)
        +create_sheet(self)
        +create_sheet_de(self)
        +create_sheet_en(self)
    }
    class generate_Periodizzazione_pdf {
        +datestrfdate(self)
        +build_Periodizzazione_sheets(self, records)
        +build_Periodizzazione_sheets_de(self, records)
        +build_Periodizzazione_sheets_en(self, records)
        +build_index_Periodizzazione(self, records, sito)
        ... +2 more methods
    }
    class NumberedCanvas_Struttura_AR {
        +__init__(self)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_Struttura_AR
    class single_Struttura_AR_pdf_sheet {
        +__init__(self, data)
        +datestrfdate(self)
        +safe_str(self, val)
        +parse_table_data(self, data_str)
        +get_first_image(self)
        ... +3 more methods
    }
    class generate_struttura_AR_pdf {
        +datestrfdate(self)
        +build_Struttura_AR_sheets(self, records)
        +build_Struttura_AR_sheets_en(self, records)
        +build_Struttura_AR_sheets_de(self, records)
    }
    class ResponseSQL {
        +__init__(self)
        +execute_sql_and_display_results(con_string, sql, results_widget)
    }
    class ComboBoxDelegate {
        +__init__(self, values, parent)
        +def_values(self, values)
        +def_editable(self, editable)
        +createEditor(self, parent, option, index)
        +setEditorData(self, editor, index)
        ... +1 more methods
    }
    QItemDelegate <|-- ComboBoxDelegate
    class NumberedCanvas {
        +__init__(self)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas
    class single_UT_pdf_sheet {
        +__init__(self, data)
        +create_sheet(self, lang)
    }
    class generate_pdf {
        +__init__(self)
        +build_UT_sheets(self, records, lang)
        +build_UT_sheets_en(self, records)
        +build_UT_sheets_de(self, records)
        +build_UT_sheets_fr(self, records)
        ... +4 more methods
    }
    class NumberedCanvas_USsheet {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_USsheet
    class NumberedCanvas_USindex {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_USindex
    class single_pottery_pdf_sheet {
        +__init__(self, data)
        +datestrfdate(self)
        +create_sheet(self)
        +makeStyles(self)
        +create_sheet_it(self)
        ... +6 more methods
    }
    class FOTO_index_pdf_sheet_2 {
        +__init__(self, data)
        +getTable(self)
        +makeStyles(self)
    }
    class FOTO_index_pdf_sheet {
        +__init__(self, data)
        +getTable(self)
        +makeStyles(self)
    }
    class POTTERY_index_pdf {
        +__init__(self, data)
        +getTable(self)
        +makeStyles(self)
    }
    class generate_POTTERY_pdf {
        +datestrfdate(self)
        +build_POTTERY_sheets(self, records)
        +build_POTTERY_sheets_it(self, records)
        +build_POTTERY_sheets_de(self, records)
        +build_POTTERY_sheets_en(self, records)
        ... +7 more methods
    }
    class LLMSelectorWidget {
        +__init__(self, parent, scope, vision_only, title)
        +get_config(self)
        +set_provider(self, provider)
    }
    QWidget <|-- LLMSelectorWidget
    class NumberedCanvas_USsheet {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_USsheet
    class NumberedCanvas_USindex {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_USindex
    class single_US_pdf_sheet {
        +__init__(self, data)
        +unzip_rapporti_stratigrafici(self)
        +unzip_documentazione(self)
        +datestrfdate(self)
        +create_sheet(self)
    }
    class US_index_pdf_sheet {
        +__init__(self, data)
        +unzip_rapporti_stratigrafici(self)
        +getTable(self)
        +makeStyles(self)
    }
    class generate_US_pdf {
        +datestrfdate(self)
        +build_US_sheets(self, records)
        +build_index_US(self, records, sito)
    }
    class Worker {
        +__init__(self, headers, params, is_image, image_width, image_height)
        +run(self)
    }
    QThread <|-- Worker
    class GPTWindow {
        +__init__(self, selected_images, dbmanager, main_class)
        +analyze_selected_images(self)
        +extract_and_display_links(self, response)
        +set_icon(self, icon_path)
        +start_worker(self, headers, params, is_image)
        ... +40 more methods
    }
    QMainWindow <|-- GPTWindow
    class MyApp {
        +__init__(self, parent)
        +ask_gpt(self, prompt, apikey, model)
        +ask_with_config(self, prompt, config)
        +is_connected(self)
    }
    QWidget <|-- MyApp
    class RemoteImageLoader {
        +set_storage_credentials(cls, credentials)
        +set_unibo_credentials(cls, credentials)
        +is_remote_url(cls, path)
        +is_unibo_path(cls, path)
        +is_cloudinary_path(cls, path)
        ... +6 more methods
    }
    class NumberedCanvas_Findssheet {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_Findssheet
    class NumberedCanvas_USindex {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_USindex
    class single_Finds_pdf_sheet {
        +__init__(self, data)
        +datestrfdate(self)
        +create_sheet(self)
    }
    class generate_pdf {
        +datestrfdate(self)
        +build_Finds_sheets(self, records)
        +build_index_US(self, records, sito)
    }
    class NumberedCanvas_Relazione {
        +__init__(self)
        +define_position(self, pos)
        +showPage(self)
        +save(self)
        +draw_page_number(self, page_count)
    }
    canvas.Canvas <|-- NumberedCanvas_Relazione
    class exp_rel_pdf {
        +__init__(self, sito)
        +connection_db(self)
        +search_records(self, f, v, m)
        +extract_id_list(self, rec, idf)
        +load_data_sorted(self, id_list, sort_fields_list, sort_mode, mapper_table_class, id_table)
        ... +2 more methods
    }
    class VideoPlayerWindow {
        +__init__(self, parent, db_manager, icon_list_widget, main_class)
        +set_video(self, file_path)
        +play_pause(self)
        +update_frame(self)
        +display_frame(self, frame)
        ... +15 more methods
    }
    QMainWindow <|-- VideoPlayerWindow
    class PotterySimilaritySearchEngine {
        +__init__(self, db_manager)
        +search_similar(self, query_image_path, model_name, search_type, threshold, auto_crop, edge_preprocessing, segment_decoration, remove_background, custom_prompt, return_top_scores)
        +search_similar_by_pottery_id(self, pottery_id, model_name, search_type, threshold)
        +search_by_text(self, text_query, model_name, search_type, threshold, return_top_scores)
        +build_index_for_model(self, model_name, search_type, progress_callback)
        ... +2 more methods
    }
    class PotterySimilarityWorker {
        +__init__(self, search_engine, operation)
        +run(self)
        +cancel(self)
    }
    QThread <|-- PotterySimilarityWorker
    class PotterySimilarityWorker {
        +__init__(self)
    }
    class EmbeddingModel {
        +get_embedding(self, image_path, search_type, auto_crop, edge_preprocessing)
        +get_embedding_dimension(self)
        +model_name(self)
        +supported_search_types(self)
        +normalize_similarity(self, raw_score)
    }
    ABC <|-- EmbeddingModel
    class CLIPEmbeddingModel {
        +__init__(self, venv_python)
        +model_name(self)
        +supported_search_types(self)
        +get_embedding_dimension(self)
        +get_embedding(self, image_path, search_type, auto_crop, edge_preprocessing, segment_decoration, remove_background, custom_prompt)
        ... +1 more methods
    }
    EmbeddingModel <|-- CLIPEmbeddingModel
    class DINOv2EmbeddingModel {
        +__init__(self, venv_python)
        +model_name(self)
        +supported_search_types(self)
        +get_embedding_dimension(self)
        +get_embedding(self, image_path, search_type, auto_crop, edge_preprocessing, segment_decoration, remove_background, custom_prompt)
        ... +1 more methods
    }
    EmbeddingModel <|-- DINOv2EmbeddingModel
    class OpenAIVisionEmbeddingModel {
        +__init__(self, api_key)
        +model_name(self)
        +supported_search_types(self)
        +get_embedding_dimension(self)
        +get_embedding(self, image_path, search_type, auto_crop, edge_preprocessing, segment_decoration, remove_background, custom_prompt)
        ... +1 more methods
    }
    EmbeddingModel <|-- OpenAIVisionEmbeddingModel
    class KhutmCLIPEmbeddingModel {
        +__init__(self, venv_python, model_dir)
        +model_name(self)
        +supported_search_types(self)
        +get_embedding_dimension(self)
        +is_available(self)
        ... +2 more methods
    }
    EmbeddingModel <|-- KhutmCLIPEmbeddingModel
    class EmbeddingIndexUpdater {
        +__init__(self, db_manager, enabled, models, search_types)
        +set_enabled(self, enabled)
        +set_models(self, models)
        +on_image_added(self, pottery_id, media_id, image_path, async_update)
        +on_image_removed(self, pottery_id, media_id, async_update)
        ... +2 more methods
    }
    <ast.IfExp object at 0x10f321b80> <|-- EmbeddingIndexUpdater
    class EmbeddingUpdateWorker {
        +__init__(self, updater, operation)
        +run(self)
    }
    QThread <|-- EmbeddingUpdateWorker
    class PotterySimilarityIndexManager {
        +__init__(self, db_manager)
        +get_index(self, model_name, search_type)
        +add_embedding(self, model_name, search_type, embedding, pottery_id, media_id, image_hash)
        +search(self, model_name, search_type, query_embedding, threshold, max_results)
        +get_top_scores(self, model_name, search_type, query_embedding, top_k)
        ... +9 more methods
    }
```
