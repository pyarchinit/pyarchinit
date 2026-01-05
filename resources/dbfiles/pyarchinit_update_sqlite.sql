
CREATE TABLE IF NOT EXISTS"pyarchinit_us_negative_doc" (
"pkuid" integer PRIMARY KEY AUTOINCREMENT,
"sito_n" text,
"area_n" text,
"us_n" integer,
"tipo_doc_n" text,
"nome_doc_n" text, "the_geom" LINESTRING);

-- =====================================================
-- UT_TABLE - New survey fields (v4.9.21+)
-- =====================================================
-- SQLite doesn't support IF NOT EXISTS for ALTER TABLE ADD COLUMN
-- These will fail silently if columns already exist

ALTER TABLE ut_table ADD COLUMN visibility_percent INTEGER;
ALTER TABLE ut_table ADD COLUMN vegetation_coverage VARCHAR(255);
ALTER TABLE ut_table ADD COLUMN gps_method VARCHAR(100);
ALTER TABLE ut_table ADD COLUMN coordinate_precision FLOAT;
ALTER TABLE ut_table ADD COLUMN survey_type VARCHAR(100);
ALTER TABLE ut_table ADD COLUMN surface_condition VARCHAR(255);
ALTER TABLE ut_table ADD COLUMN accessibility VARCHAR(255);
ALTER TABLE ut_table ADD COLUMN photo_documentation INTEGER;
ALTER TABLE ut_table ADD COLUMN weather_conditions VARCHAR(255);
ALTER TABLE ut_table ADD COLUMN team_members TEXT;
ALTER TABLE ut_table ADD COLUMN foglio_catastale VARCHAR(100);

-- =====================================================
-- FAUNA_TABLE - Create if not exists (v4.9.21+)
-- =====================================================
CREATE TABLE IF NOT EXISTS fauna_table (
    id_fauna INTEGER PRIMARY KEY AUTOINCREMENT,
    id_us INTEGER,
    sito TEXT,
    area TEXT,
    saggio TEXT,
    us TEXT,
    datazione_us TEXT,
    responsabile_scheda TEXT DEFAULT '',
    data_compilazione TEXT,
    documentazione_fotografica TEXT DEFAULT '',
    metodologia_recupero TEXT DEFAULT '',
    contesto TEXT DEFAULT '',
    descrizione_contesto TEXT DEFAULT '',
    resti_connessione_anatomica TEXT DEFAULT '',
    tipologia_accumulo TEXT DEFAULT '',
    deposizione TEXT DEFAULT '',
    numero_stimato_resti TEXT DEFAULT '',
    numero_minimo_individui INTEGER DEFAULT 0,
    specie TEXT DEFAULT '',
    parti_scheletriche TEXT DEFAULT '',
    specie_psi TEXT DEFAULT '',
    misure_ossa TEXT DEFAULT '',
    stato_frammentazione TEXT DEFAULT '',
    tracce_combustione TEXT DEFAULT '',
    combustione_altri_materiali_us INTEGER DEFAULT 0,
    tipo_combustione TEXT DEFAULT '',
    segni_tafonomici_evidenti TEXT DEFAULT '',
    caratterizzazione_segni_tafonomici TEXT DEFAULT '',
    stato_conservazione TEXT DEFAULT '',
    alterazioni_morfologiche TEXT DEFAULT '',
    note_terreno_giacitura TEXT DEFAULT '',
    campionature_effettuate TEXT DEFAULT '',
    affidabilita_stratigrafica TEXT DEFAULT '',
    classi_reperti_associazione TEXT DEFAULT '',
    osservazioni TEXT DEFAULT '',
    interpretazione TEXT DEFAULT '',
    UNIQUE (sito, area, us, id_fauna)
)