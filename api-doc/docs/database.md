# Database layer

SQLAlchemy entities, table structures, migrations, sync, and the central `pyarchinit_db_manager`. Supports both PostgreSQL/PostGIS and SQLite/Spatialite.

**167 modules in this area.**

## Modules

### [`modules/db/add_uuid_support.py`](modules_db_add_uuid_support_py.md)

### [`modules/db/add_versioning_support.py`](modules_db_add_versioning_support_py.md)

### [`modules/db/concurrency_manager.py`](modules_db_concurrency_manager_py.md)

### [`modules/db/connection_reset.py`](modules_db_connection_reset_py.md)

### [`modules/db/create_string.py`](modules_db_create_string_py.md)

### [`modules/db/database_sync.py`](modules_db_database_sync_py.md)

### [`modules/db/db_createdump.py`](modules_db_db_createdump_py.md)

### [`modules/db/db_migrations.py`](modules_db_db_migrations_py.md)

### [`modules/db/db_updater.py`](modules_db_db_updater_py.md)

### [`modules/db/enable-postgis.py`](modules_db_enable-postgis_py.md)

### [`modules/db/entities_ALL.py`](modules_db_entities_ALL_py.md)

### [`modules/db/entities_ARCHEOZOOLOGY.py`](modules_db_entities_ARCHEOZOOLOGY_py.md)

### [`modules/db/entities_ATTREZZATURE.py`](modules_db_entities_ATTREZZATURE_py.md)

### [`modules/db/entities_BUDGET.py`](modules_db_entities_BUDGET_py.md)

### [`modules/db/entities_CAMPIONI.py`](modules_db_entities_CAMPIONI_py.md)

### [`modules/db/entities_COMPUTO_METRICO.py`](modules_db_entities_COMPUTO_METRICO_py.md)

### [`modules/db/entities_DETETA.py`](modules_db_entities_DETETA_py.md)

### [`modules/db/entities_DETSESSO.py`](modules_db_entities_DETSESSO_py.md)

### [`modules/db/entities_DOCUMENTAZIONE.py`](modules_db_entities_DOCUMENTAZIONE_py.md)

### [`modules/db/entities_FAUNA.py`](modules_db_entities_FAUNA_py.md)

### [`modules/db/entities_INVENTARIO_LAPIDEI.py`](modules_db_entities_INVENTARIO_LAPIDEI_py.md)

### [`modules/db/entities_INVENTARIO_MATERIALI_TOIMP.py`](modules_db_entities_INVENTARIO_MATERIALI_TOIMP_py.md)

### [`modules/db/entities_INVENTARIO_MATERIALI.py`](modules_db_entities_INVENTARIO_MATERIALI_py.md)

### [`modules/db/entities_MEDIATOENTITY.py`](modules_db_entities_MEDIATOENTITY_py.md)

### [`modules/db/entities_MEDIAVIEW.py`](modules_db_entities_MEDIAVIEW_py.md)

### [`modules/db/entities_MEDIA_THUMB.py`](modules_db_entities_MEDIA_THUMB_py.md)

### [`modules/db/entities_MEDIA.py`](modules_db_entities_MEDIA_py.md)

### [`modules/db/entities_PDF_ADMINISTRATOR.py`](modules_db_entities_PDF_ADMINISTRATOR_py.md)

### [`modules/db/entities_PERIODIZZAZIONE.py`](modules_db_entities_PERIODIZZAZIONE_py.md)

### [`modules/db/entities_PERSONALE.py`](modules_db_entities_PERSONALE_py.md)

### [`modules/db/entities_POTTERY_EMBEDDING_METADATA.py`](modules_db_entities_POTTERY_EMBEDDING_METADATA_py.md)

### [`modules/db/entities_POTTERY.py`](modules_db_entities_POTTERY_py.md)

### [`modules/db/entities_PRESENZE.py`](modules_db_entities_PRESENZE_py.md)

### [`modules/db/entities_PYARCHINIT_THESAURUS_SIGLE.py`](modules_db_entities_PYARCHINIT_THESAURUS_SIGLE_py.md)

### [`modules/db/entities_PYCAMPIONI.py`](modules_db_entities_PYCAMPIONI_py.md)

### [`modules/db/entities_PYDOCUMENTAZIONE.py`](modules_db_entities_PYDOCUMENTAZIONE_py.md)

### [`modules/db/entities_PYINDIVIDUI.py`](modules_db_entities_PYINDIVIDUI_py.md)

### [`modules/db/entities_PYLINEERIFERIMENTO.py`](modules_db_entities_PYLINEERIFERIMENTO_py.md)

### [`modules/db/entities_PYQUOTEUSM.py`](modules_db_entities_PYQUOTEUSM_py.md)

### [`modules/db/entities_PYQUOTE.py`](modules_db_entities_PYQUOTE_py.md)

### [`modules/db/entities_PYREPERTI.py`](modules_db_entities_PYREPERTI_py.md)

### [`modules/db/entities_PYRIPARTIZIONI_SPAZIALI.py`](modules_db_entities_PYRIPARTIZIONI_SPAZIALI_py.md)

### [`modules/db/entities_PYSEZIONI.py`](modules_db_entities_PYSEZIONI_py.md)

### [`modules/db/entities_PYSITO_POINT.py`](modules_db_entities_PYSITO_POINT_py.md)

### [`modules/db/entities_PYSITO_POLYGON.py`](modules_db_entities_PYSITO_POLYGON_py.md)

### [`modules/db/entities_PYSTRUTTURE.py`](modules_db_entities_PYSTRUTTURE_py.md)

### [`modules/db/entities_PYTOMBA.py`](modules_db_entities_PYTOMBA_py.md)

### [`modules/db/entities_PYUSM.py`](modules_db_entities_PYUSM_py.md)

### [`modules/db/entities_PYUS_NEGATIVE.py`](modules_db_entities_PYUS_NEGATIVE_py.md)

### [`modules/db/entities_PYUS.py`](modules_db_entities_PYUS_py.md)

### [`modules/db/entities_SCHEDAIND.py`](modules_db_entities_SCHEDAIND_py.md)

### [`modules/db/entities_SITE.py`](modules_db_entities_SITE_py.md)

### [`modules/db/entities_STRUTTURA.py`](modules_db_entities_STRUTTURA_py.md)

### [`modules/db/entities_TAFONOMIA.py`](modules_db_entities_TAFONOMIA_py.md)

### [`modules/db/entities_TMA_MATERIALI.py`](modules_db_entities_TMA_MATERIALI_py.md)

### [`modules/db/entities_TMA.py`](modules_db_entities_TMA_py.md)

### [`modules/db/entities_TOMBA.py`](modules_db_entities_TOMBA_py.md)

### [`modules/db/entities_US_TOIMP.py`](modules_db_entities_US_TOIMP_py.md)

### [`modules/db/entities_US.py`](modules_db_entities_US_py.md)

### [`modules/db/entities_UT.py`](modules_db_entities_UT_py.md)

### [`modules/db/media_migration_mapper.py`](modules_db_media_migration_mapper_py.md)

### [`modules/db/permission_handler.py`](modules_db_permission_handler_py.md)

### [`modules/db/postgres_db_updater.py`](modules_db_postgres_db_updater_py.md)

### [`modules/db/pyarchinit_OS_utility.py`](modules_db_pyarchinit_OS_utility_py.md)

### [`modules/db/pyarchinit_conn_strings.py`](modules_db_pyarchinit_conn_strings_py.md)

### [`modules/db/pyarchinit_db_manager.py`](modules_db_pyarchinit_db_manager_py.md)

### [`modules/db/pyarchinit_db_mapper.py`](modules_db_pyarchinit_db_mapper_py.md)

### [`modules/db/pyarchinit_db_update.py`](modules_db_pyarchinit_db_update_py.md)

### [`modules/db/pyarchinit_db_update_thesaurus.py`](modules_db_pyarchinit_db_update_thesaurus_py.md)

### [`modules/db/pyarchinit_utility.py`](modules_db_pyarchinit_utility_py.md)

### [`modules/db/sqlite_db_updater.py`](modules_db_sqlite_db_updater_py.md)

### [`modules/db/structures_Archeozoology_table.py`](modules_db_structures_Archeozoology_table_py.md)

### [`modules/db/structures_Attrezzature_table.py`](modules_db_structures_Attrezzature_table_py.md)

### [`modules/db/structures_Budget_table.py`](modules_db_structures_Budget_table_py.md)

### [`modules/db/structures_Campioni_table.py`](modules_db_structures_Campioni_table_py.md)

### [`modules/db/structures_Computo_metrico_table.py`](modules_db_structures_Computo_metrico_table_py.md)

### [`modules/db/structures_DETETA_table.py`](modules_db_structures_DETETA_table_py.md)

### [`modules/db/structures_DETSESSO_table.py`](modules_db_structures_DETSESSO_table_py.md)

### [`modules/db/structures_Documentazione_table.py`](modules_db_structures_Documentazione_table_py.md)

### [`modules/db/structures_Fauna_table.py`](modules_db_structures_Fauna_table_py.md)

### [`modules/db/structures_Inventario_Lapidei_table.py`](modules_db_structures_Inventario_Lapidei_table_py.md)

### [`modules/db/structures_Inventario_materiali_table.py`](modules_db_structures_Inventario_materiali_table_py.md)

### [`modules/db/structures_Media_table.py`](modules_db_structures_Media_table_py.md)

### [`modules/db/structures_Media_thumb_table.py`](modules_db_structures_Media_thumb_table_py.md)

### [`modules/db/structures_Media_to_Entity_table.py`](modules_db_structures_Media_to_Entity_table_py.md)

### [`modules/db/structures_Media_to_Entity_table_view.py`](modules_db_structures_Media_to_Entity_table_view_py.md)

### [`modules/db/structures_PDF_administrator_table.py`](modules_db_structures_PDF_administrator_table_py.md)

### [`modules/db/structures_Periodizzazione_table.py`](modules_db_structures_Periodizzazione_table_py.md)

### [`modules/db/structures_Personale_table.py`](modules_db_structures_Personale_table_py.md)

### [`modules/db/structures_Pottery_embeddings_metadata_table.py`](modules_db_structures_Pottery_embeddings_metadata_table_py.md)

### [`modules/db/structures_Pottery_table.py`](modules_db_structures_Pottery_table_py.md)

### [`modules/db/structures_Presenze_table.py`](modules_db_structures_Presenze_table_py.md)

### [`modules/db/structures_Pyarchinit_thesaurus_sigle.py`](modules_db_structures_Pyarchinit_thesaurus_sigle_py.md)

### [`modules/db/structures_SCHEDAIND_table.py`](modules_db_structures_SCHEDAIND_table_py.md)

### [`modules/db/structures_Site_table.py`](modules_db_structures_Site_table_py.md)

### [`modules/db/structures_Struttura_table.py`](modules_db_structures_Struttura_table_py.md)

### [`modules/db/structures_TMA_materiali_table_fixed.py`](modules_db_structures_TMA_materiali_table_fixed_py.md)

### [`modules/db/structures_Tafonomia_table.py`](modules_db_structures_Tafonomia_table_py.md)

### [`modules/db/structures_Tma_materiali_table.py`](modules_db_structures_Tma_materiali_table_py.md)

### [`modules/db/structures_Tma_table.py`](modules_db_structures_Tma_table_py.md)

### [`modules/db/structures_Tomba_table.py`](modules_db_structures_Tomba_table_py.md)

### [`modules/db/structures_US_table.py`](modules_db_structures_US_table_py.md)

### [`modules/db/structures_US_table_toimp.py`](modules_db_structures_US_table_toimp_py.md)

### [`modules/db/structures_UT_table.py`](modules_db_structures_UT_table_py.md)

### [`modules/db/structures_metadata_Archeozoology_table.py`](modules_db_structures_metadata_Archeozoology_table_py.md)

### [`modules/db/structures_metadata_Attrezzature_table.py`](modules_db_structures_metadata_Attrezzature_table_py.md)

### [`modules/db/structures_metadata_Budget_table.py`](modules_db_structures_metadata_Budget_table_py.md)

### [`modules/db/structures_metadata_Campioni_table.py`](modules_db_structures_metadata_Campioni_table_py.md)

### [`modules/db/structures_metadata_Computo_metrico_table.py`](modules_db_structures_metadata_Computo_metrico_table_py.md)

### [`modules/db/structures_metadata_DETETA_table.py`](modules_db_structures_metadata_DETETA_table_py.md)

### [`modules/db/structures_metadata_DETSESSO_table.py`](modules_db_structures_metadata_DETSESSO_table_py.md)

### [`modules/db/structures_metadata_Documentazione_table.py`](modules_db_structures_metadata_Documentazione_table_py.md)

### [`modules/db/structures_metadata_Inventario_Lapidei_table.py`](modules_db_structures_metadata_Inventario_Lapidei_table_py.md)

### [`modules/db/structures_metadata_Inventario_materiali_table.py`](modules_db_structures_metadata_Inventario_materiali_table_py.md)

### [`modules/db/structures_metadata_Media_table.py`](modules_db_structures_metadata_Media_table_py.md)

### [`modules/db/structures_metadata_Media_thumb_table.py`](modules_db_structures_metadata_Media_thumb_table_py.md)

### [`modules/db/structures_metadata_Media_to_Entity_table.py`](modules_db_structures_metadata_Media_to_Entity_table_py.md)

### [`modules/db/structures_metadata_Media_to_Entity_table_view.py`](modules_db_structures_metadata_Media_to_Entity_table_view_py.md)

### [`modules/db/structures_metadata_PDF_administrator_table.py`](modules_db_structures_metadata_PDF_administrator_table_py.md)

### [`modules/db/structures_metadata_Periodizzazione_table.py`](modules_db_structures_metadata_Periodizzazione_table_py.md)

### [`modules/db/structures_metadata_Personale_table.py`](modules_db_structures_metadata_Personale_table_py.md)

### [`modules/db/structures_metadata_Pottery_table.py`](modules_db_structures_metadata_Pottery_table_py.md)

### [`modules/db/structures_metadata_Presenze_table.py`](modules_db_structures_metadata_Presenze_table_py.md)

### [`modules/db/structures_metadata_Pyarchinit_thesaurus_sigle.py`](modules_db_structures_metadata_Pyarchinit_thesaurus_sigle_py.md)

### [`modules/db/structures_metadata_SCHEDAIND_table.py`](modules_db_structures_metadata_SCHEDAIND_table_py.md)

### [`modules/db/structures_metadata_Site_table.py`](modules_db_structures_metadata_Site_table_py.md)

### [`modules/db/structures_metadata_Struttura_table.py`](modules_db_structures_metadata_Struttura_table_py.md)

### [`modules/db/structures_metadata_Tafonomia_table.py`](modules_db_structures_metadata_Tafonomia_table_py.md)

### [`modules/db/structures_metadata_Tma_materiali_table.py`](modules_db_structures_metadata_Tma_materiali_table_py.md)

### [`modules/db/structures_metadata_Tma_table.py`](modules_db_structures_metadata_Tma_table_py.md)

### [`modules/db/structures_metadata_Tomba_table.py`](modules_db_structures_metadata_Tomba_table_py.md)

### [`modules/db/structures_metadata_US_table.py`](modules_db_structures_metadata_US_table_py.md)

### [`modules/db/structures_metadata_US_table_toimp.py`](modules_db_structures_metadata_US_table_toimp_py.md)

### [`modules/db/structures_metadata_UT_table.py`](modules_db_structures_metadata_UT_table_py.md)

### [`modules/db/structures_metadata_pycampioni.py`](modules_db_structures_metadata_pycampioni_py.md)

### [`modules/db/structures_metadata_pydocumentazione.py`](modules_db_structures_metadata_pydocumentazione_py.md)

### [`modules/db/structures_metadata_pyindividui.py`](modules_db_structures_metadata_pyindividui_py.md)

### [`modules/db/structures_metadata_pylineeriferimento.py`](modules_db_structures_metadata_pylineeriferimento_py.md)

### [`modules/db/structures_metadata_pyquote.py`](modules_db_structures_metadata_pyquote_py.md)

### [`modules/db/structures_metadata_pyquote_usm.py`](modules_db_structures_metadata_pyquote_usm_py.md)

### [`modules/db/structures_metadata_pyreperti.py`](modules_db_structures_metadata_pyreperti_py.md)

### [`modules/db/structures_metadata_pyripartizioni_spaziali.py`](modules_db_structures_metadata_pyripartizioni_spaziali_py.md)

### [`modules/db/structures_metadata_pysezioni.py`](modules_db_structures_metadata_pysezioni_py.md)

### [`modules/db/structures_metadata_pysito_point.py`](modules_db_structures_metadata_pysito_point_py.md)

### [`modules/db/structures_metadata_pysito_polygon.py`](modules_db_structures_metadata_pysito_polygon_py.md)

### [`modules/db/structures_metadata_pystrutture.py`](modules_db_structures_metadata_pystrutture_py.md)

### [`modules/db/structures_metadata_pytomba.py`](modules_db_structures_metadata_pytomba_py.md)

### [`modules/db/structures_metadata_pyunitastratigrafiche.py`](modules_db_structures_metadata_pyunitastratigrafiche_py.md)

### [`modules/db/structures_metadata_pyunitastratigrafiche_usm.py`](modules_db_structures_metadata_pyunitastratigrafiche_usm_py.md)

### [`modules/db/structures_metadata_pyus_negative.py`](modules_db_structures_metadata_pyus_negative_py.md)

### [`modules/db/structures_pycampioni.py`](modules_db_structures_pycampioni_py.md)

### [`modules/db/structures_pydocumentazione.py`](modules_db_structures_pydocumentazione_py.md)

### [`modules/db/structures_pyindividui.py`](modules_db_structures_pyindividui_py.md)

### [`modules/db/structures_pylineeriferimento.py`](modules_db_structures_pylineeriferimento_py.md)

### [`modules/db/structures_pyquote.py`](modules_db_structures_pyquote_py.md)

### [`modules/db/structures_pyquote_usm.py`](modules_db_structures_pyquote_usm_py.md)

### [`modules/db/structures_pyreperti.py`](modules_db_structures_pyreperti_py.md)

### [`modules/db/structures_pyripartizioni_spaziali.py`](modules_db_structures_pyripartizioni_spaziali_py.md)

### [`modules/db/structures_pysezioni.py`](modules_db_structures_pysezioni_py.md)

### [`modules/db/structures_pysito_point.py`](modules_db_structures_pysito_point_py.md)

### [`modules/db/structures_pysito_polygon.py`](modules_db_structures_pysito_polygon_py.md)

### [`modules/db/structures_pystrutture.py`](modules_db_structures_pystrutture_py.md)

### [`modules/db/structures_pytomba.py`](modules_db_structures_pytomba_py.md)

### [`modules/db/structures_pyunitastratigrafiche.py`](modules_db_structures_pyunitastratigrafiche_py.md)

### [`modules/db/structures_pyunitastratigrafiche_usm.py`](modules_db_structures_pyunitastratigrafiche_usm_py.md)

### [`modules/db/structures_pyus_negative.py`](modules_db_structures_pyus_negative_py.md)

### [`modules/db/sync_postgres_permissions.py`](modules_db_sync_postgres_permissions_py.md)

