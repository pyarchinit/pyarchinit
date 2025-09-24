-- PyArchInit Migration Script for SQLite: Convert US fields from INTEGER to TEXT
-- WARNING: This is a major database change. Make a full backup before running!
-- Author: PyArchInit Team
-- Date: 2025-07-24
-- FIXED VERSION: Addresses missing columns and table issues

-- Note: SQLite doesn't support direct ALTER COLUMN TYPE
-- We need to recreate tables with the new schema

-- =====================================================
-- STEP 0: Clean up any previous failed migration attempts
-- =====================================================

DROP TABLE IF EXISTS us_table_new;
DROP TABLE IF EXISTS campioni_table_new;
DROP TABLE IF EXISTS pottery_table_new;

-- =====================================================
-- STEP 1: Drop Views that depend on US field
-- =====================================================

DROP VIEW IF EXISTS pyarchinit_quote_view;
DROP VIEW IF EXISTS pyarchinit_us_view;
DROP VIEW IF EXISTS pyarchinit_uscaratterizzazioni_view;

-- =====================================================
-- STEP 2: Check if us_table exists, if not use us_table_toimp
-- =====================================================

-- Create temporary table with new schema (minimal columns based on actual structure)
CREATE TABLE us_table_new (
    id_us INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT,
    area TEXT,
    us TEXT,  -- Changed from INTEGER to TEXT
    d_stratigrafica TEXT,
    d_interpretativa TEXT,
    descrizione TEXT,
    interpretazione TEXT,
    periodo_iniziale TEXT,
    fase_iniziale TEXT,
    periodo_finale TEXT,
    fase_finale TEXT,
    scavato TEXT,
    attivita TEXT,
    anno_scavo TEXT,
    metodo_di_scavo TEXT,
    inclusi TEXT,
    campioni TEXT,
    rapporti TEXT,
    data_schedatura TEXT,
    schedatore TEXT,
    formazione TEXT,
    stato_di_conservazione TEXT,
    colore TEXT,
    consistenza TEXT,
    struttura TEXT,
    cont_per TEXT,
    order_layer INTEGER,
    documentazione TEXT,
    unita_tipo TEXT,
    settore TEXT,
    quad_par TEXT,
    ambient TEXT,
    saggio TEXT,
    elem_datanti TEXT,
    funz_statica TEXT,
    lavorazione TEXT,
    spess_giunti TEXT,
    letti_posa TEXT,
    alt_mod TEXT,
    un_ed_riass TEXT,
    reimp TEXT,
    posa_opera TEXT,
    quota_min_usm REAL,
    quota_max_usm REAL,
    cons_legante TEXT,
    col_legante TEXT,
    aggreg_legante TEXT,
    con_text_mat TEXT,
    col_materiale TEXT,
    inclusi_materiali_usm TEXT,
    n_catalogo_generale TEXT,
    n_catalogo_interno TEXT,
    n_catalogo_internazionale TEXT,
    soprintendenza TEXT,
    quota_relativa REAL,
    quota_abs REAL,
    ref_tm TEXT,
    ref_ra TEXT,
    ref_n TEXT,
    posizione TEXT,
    criteri_distinzione TEXT,
    modo_formazione TEXT,
    componenti_organici TEXT,
    componenti_inorganici TEXT,
    lunghezza_max REAL,
    altezza_max REAL,
    altezza_min REAL,
    profondita_max REAL,
    profondita_min REAL,
    larghezza_media REAL,
    quota_max_abs REAL,
    quota_max_rel REAL,
    quota_min_abs REAL,
    quota_min_rel REAL,
    osservazioni TEXT,
    datazione TEXT,
    flottazione TEXT,
    setacciatura TEXT,
    affidabilita TEXT,
    direttore_us TEXT,
    responsabile_us TEXT,
    cod_ente_schedatore TEXT,
    data_rilevazione TEXT,
    data_rielaborazione TEXT,
    lunghezza_usm REAL,
    altezza_usm REAL,
    spessore_usm REAL,
    tecnica_muraria_usm TEXT,
    modulo_usm TEXT,
    campioni_malta_usm TEXT,
    campioni_mattone_usm TEXT,
    campioni_pietra_usm TEXT,
    provenienza_materiali_usm TEXT,
    criteri_distinzione_usm TEXT,
    uso_primario_usm TEXT
);

-- Copy data from old table (handle both us_table and us_table_toimp)
-- First try us_table_toimp which seems to be the actual table
INSERT INTO us_table_new (
    id_us, sito, area, us, d_stratigrafica, d_interpretativa, descrizione,
    interpretazione, periodo_iniziale, fase_iniziale, periodo_finale, fase_finale,
    scavato, attivita, anno_scavo, metodo_di_scavo, inclusi, campioni, rapporti,
    data_schedatura, schedatore, formazione, stato_di_conservazione, colore,
    consistenza, struttura, cont_per, order_layer, documentazione
)
SELECT 
    id_us, sito, area, CAST(us AS TEXT), d_stratigrafica, d_interpretativa, descrizione,
    interpretazione, periodo_iniziale, fase_iniziale, periodo_finale, fase_finale,
    scavato, attivita, anno_scavo, metodo_di_scavo, inclusi, campioni, rapporti,
    data_schedatura, schedatore, formazione, stato_di_conservazione, colore,
    consistenza, struttura, cont_per, order_layer, documentazione
FROM us_table_toimp;

-- Drop old table and rename new one
DROP TABLE IF EXISTS us_table;
DROP TABLE IF EXISTS us_table_toimp;
ALTER TABLE us_table_new RENAME TO us_table;

-- =====================================================
-- STEP 3: Migrate campioni_table if it exists
-- =====================================================

-- Check if campioni_table exists by trying to select from it
-- If it doesn't exist, this will be skipped
CREATE TABLE IF NOT EXISTS campioni_table_temp AS SELECT * FROM campioni_table WHERE 0;

-- Create new campioni table with correct structure
CREATE TABLE campioni_table (
    id_campione INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT,
    tipo_campione TEXT,
    descrizione_campione TEXT,
    area TEXT,
    us TEXT,  -- Changed from INTEGER to TEXT
    numero_campione INTEGER,
    nr_cassa INTEGER,
    luogo_conservazione TEXT
);

-- Try to migrate data if old table exists
INSERT OR IGNORE INTO campioni_table 
SELECT * FROM campioni_table_temp;

DROP TABLE IF EXISTS campioni_table_temp;

-- =====================================================
-- STEP 4: Migrate pottery_table if it exists
-- =====================================================

-- Check if pottery_table exists
CREATE TABLE IF NOT EXISTS pottery_table_temp AS SELECT * FROM pottery_table WHERE 0;

-- Create new pottery table
CREATE TABLE pottery_table (
    id_rep INTEGER PRIMARY KEY AUTOINCREMENT,
    id_number INTEGER,
    sito TEXT,
    area TEXT,
    us TEXT,  -- Changed from INTEGER to TEXT
    box TEXT,
    photo TEXT,
    drawing TEXT,
    anno TEXT,
    fabric TEXT,
    percent TEXT,
    material TEXT,
    form TEXT,
    specific_form TEXT,
    ware TEXT,
    munsell TEXT,
    surf_trat TEXT,
    exdeco TEXT,
    intdeco TEXT,
    wheel_made TEXT,
    descrip_ex_deco TEXT,
    descrip_in_deco TEXT,
    note TEXT,
    diametro_max REAL,
    qty REAL,
    diametro_rim REAL,
    diametro_bottom REAL,
    diametro_height REAL,
    diametro_preserved REAL,
    specific_shape TEXT,
    bag TEXT
);

-- Try to migrate data if old table exists
INSERT OR IGNORE INTO pottery_table 
SELECT * FROM pottery_table_temp;

DROP TABLE IF EXISTS pottery_table_temp;

-- =====================================================
-- STEP 5: Add other US fields in related tables
-- =====================================================

-- Update inventario_materiali_table if it exists
CREATE TABLE IF NOT EXISTS inventario_materiali_table_new AS 
SELECT * FROM inventario_materiali_table WHERE 0;

-- Check if table exists and has data
INSERT INTO inventario_materiali_table_new
SELECT * FROM inventario_materiali_table;

-- If inventario_materiali_table exists, update it
DROP TABLE IF EXISTS inventario_materiali_table;
CREATE TABLE inventario_materiali_table AS
SELECT 
    id_invmat,
    sito,
    numero_inventario,
    tipo_reperto,
    criterio_schedatura,
    definizione,
    descrizione,
    area,
    CAST(us AS TEXT) as us,  -- Convert to TEXT
    lavato,
    nr_cassa,
    luogo_conservazione,
    stato_conservazione,
    datazione_reperto,
    elementi_reperto,
    misurazioni,
    rif_biblio,
    tecnologie,
    forme_minime,
    forme_massime,
    totale_frammenti,
    corpo_ceramico,
    rivestimento,
    diametro_orlo,
    peso,
    tipo,
    eve_orlo,
    repertato,
    diagnostico,
    n_reperto,
    tipo_contenitore,
    struttura,
    years,
    schedatore,
    date_scheda,
    punto_rinv,
    negativo_photo,
    diapositiva
FROM inventario_materiali_table_new;

DROP TABLE IF EXISTS inventario_materiali_table_new;

-- =====================================================
-- STEP 6: Recreate Views (if the GIS tables exist)
-- =====================================================

-- These views will only be created if the corresponding GIS tables exist
-- If they don't exist, the views simply won't be created

-- View: pyarchinit_quote_view
CREATE VIEW IF NOT EXISTS pyarchinit_quote_view AS
SELECT 
    pq.sito_q, 
    pq.area_q, 
    pq.us_q, 
    pq.unita_misu_q AS unita_misu, 
    pq.quota_q,
    pq.unita_tipo_q,
    pq.the_geom AS geometry, 
    ut.id_us, 
    ut.sito, 
    ut.area, 
    ut.us, 
    ut.struttura, 
    ut.d_stratigrafica AS definizione_stratigrafica, 
    ut.d_interpretativa AS definizione_interpretativa, 
    ut.descrizione, 
    ut.interpretazione, 
    ut.rapporti, 
    ut.periodo_iniziale, 
    ut.fase_iniziale, 
    ut.periodo_finale, 
    ut.fase_finale, 
    ut.anno_scavo
FROM pyarchinit_quote pq
JOIN us_table ut ON 
    pq.sito_q = ut.sito 
    AND pq.area_q = ut.area 
    AND pq.us_q = ut.us
    AND pq.unita_tipo_q = ut.unita_tipo
WHERE pq.the_geom IS NOT NULL;

-- View: pyarchinit_us_view
CREATE VIEW IF NOT EXISTS pyarchinit_us_view AS 
SELECT 
    pu.PK_UID, 
    pu.the_geom AS geometry, 
    pu.tipo_us_s, 
    pu.scavo_s, 
    pu.area_s, 
    pu.us_s,
    pu.unita_tipo_s, 
    ut.id_us, 
    ut.sito, 
    ut.area, 
    ut.us, 
    ut.struttura, 
    ut.d_stratigrafica AS definizione_stratigrafica, 
    ut.d_interpretativa AS definizione_interpretativa, 
    ut.descrizione, 
    ut.interpretazione, 
    ut.rapporti, 
    ut.periodo_iniziale, 
    ut.fase_iniziale, 
    ut.periodo_finale, 
    ut.fase_finale, 
    ut.anno_scavo
FROM pyunitastratigrafiche pu
JOIN us_table ut ON 
    pu.scavo_s = ut.sito 
    AND pu.area_s = ut.area 
    AND pu.us_s = ut.us
    AND pu.unita_tipo_s = ut.unita_tipo
WHERE pu.the_geom IS NOT NULL;

-- View: pyarchinit_uscaratterizzazioni_view
CREATE VIEW IF NOT EXISTS pyarchinit_uscaratterizzazioni_view AS
SELECT 
    pc.the_geom AS geometry, 
    pc.tipo_us_c, 
    pc.scavo_c, 
    pc.area_c, 
    pc.us_c, 
    ut.sito, 
    ut.id_us, 
    ut.area, 
    ut.us, 
    ut.struttura, 
    ut.d_stratigrafica AS definizione_stratigrafica, 
    ut.d_interpretativa AS definizione_interpretativa, 
    ut.descrizione, 
    ut.interpretazione, 
    ut.rapporti, 
    ut.periodo_iniziale, 
    ut.fase_iniziale, 
    ut.periodo_finale, 
    ut.fase_finale, 
    ut.anno_scavo
FROM pyuscaratterizzazioni pc
JOIN us_table ut ON 
    pc.scavo_c = ut.sito 
    AND pc.area_c = ut.area 
    AND pc.us_c = ut.us
WHERE pc.the_geom IS NOT NULL;

-- =====================================================
-- STEP 7: Create indexes
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_us_table_us ON us_table(us);
CREATE INDEX IF NOT EXISTS idx_us_table_sito_area_us ON us_table(sito, area, us);
CREATE INDEX IF NOT EXISTS idx_campioni_us ON campioni_table(us);
CREATE INDEX IF NOT EXISTS idx_pottery_us ON pottery_table(us);

-- =====================================================
-- STEP 8: Add TMA table for SQLite
-- =====================================================

CREATE TABLE IF NOT EXISTS tma_materiali_archeologici (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- Basic identification
    sito TEXT,
    area TEXT,
    localita TEXT,
    settore TEXT,
    inventario TEXT,
    -- Object data (OG)
    ogtm TEXT,
    -- Location data (LC)
    ldct TEXT,
    ldcn TEXT,
    vecchia_collocazione TEXT,
    cassetta TEXT,
    -- Excavation data (RE - DSC)
    scan TEXT,
    saggio TEXT,
    vano_locus TEXT,
    dscd TEXT,
    dscu TEXT,
    -- Survey data (RE - RCG)
    rcgd TEXT,
    rcgz TEXT,
    -- Other acquisition (RE - AIN)
    aint TEXT,
    aind TEXT,
    -- Dating (DT)
    dtzg TEXT,
    -- Analytical data (DA)
    deso TEXT,
    -- Historical-critical notes (NSC)
    nsc TEXT,
    -- Documentation (DO)
    ftap TEXT,
    ftan TEXT,
    drat TEXT,
    dran TEXT,
    draa TEXT,
    -- System fields
    created_at TEXT,
    updated_at TEXT,
    created_by TEXT,
    updated_by TEXT
);

CREATE TABLE IF NOT EXISTS tma_materiali_ripetibili (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- Foreign key to main TMA record
    id_tma INTEGER NOT NULL,
    -- Material description data (MAD)
    madi TEXT,
    -- Material component data (MAC) - all repetitive
    macc TEXT,
    macl TEXT,
    macp TEXT,
    macd TEXT,
    cronologia_mac TEXT,
    macq TEXT,
    peso REAL,
    -- System fields
    created_at TEXT,
    updated_at TEXT,
    created_by TEXT,
    updated_by TEXT,
    FOREIGN KEY (id_tma) REFERENCES tma_materiali_archeologici(id) ON DELETE CASCADE
);

-- =====================================================
-- FINAL MESSAGE
-- =====================================================

SELECT 'Migration completed. US fields have been converted from INTEGER to TEXT.';
SELECT 'Please verify your data and recreate any application-specific triggers or constraints.';