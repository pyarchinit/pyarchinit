-- PyArchInit Migration Script for SQLite: Convert US fields from INTEGER to TEXT
-- WARNING: This is a major database change. Make a full backup before running!
-- Author: PyArchInit Team
-- Date: 2025-07-24

-- Note: SQLite doesn't support direct ALTER COLUMN TYPE
-- We need to recreate tables with the new schema

-- =====================================================
-- STEP 1: Drop Views that depend on US field
-- =====================================================

DROP VIEW IF EXISTS pyarchinit_quote_view;
DROP VIEW IF EXISTS pyarchinit_us_view;
DROP VIEW IF EXISTS pyarchinit_uscaratterizzazioni_view;

-- =====================================================
-- STEP 2: Migrate us_table
-- =====================================================

-- Create temporary table with new schema
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
    organici TEXT,
    inorganici TEXT,
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

-- Copy data from old table
INSERT INTO us_table_new SELECT 
    id_us,
    sito,
    area,
    CAST(us AS TEXT),  -- Convert INTEGER to TEXT
    d_stratigrafica,
    d_interpretativa,
    descrizione,
    interpretazione,
    periodo_iniziale,
    fase_iniziale,
    periodo_finale,
    fase_finale,
    scavato,
    attivita,
    anno_scavo,
    metodo_di_scavo,
    inclusi,
    campioni,
    rapporti,
    organici,
    inorganici,
    data_schedatura,
    schedatore,
    formazione,
    stato_di_conservazione,
    colore,
    consistenza,
    struttura,
    cont_per,
    order_layer,
    documentazione,
    unita_tipo,
    settore,
    quad_par,
    ambient,
    saggio,
    elem_datanti,
    funz_statica,
    lavorazione,
    spess_giunti,
    letti_posa,
    alt_mod,
    un_ed_riass,
    reimp,
    posa_opera,
    quota_min_usm,
    quota_max_usm,
    cons_legante,
    col_legante,
    aggreg_legante,
    con_text_mat,
    col_materiale,
    inclusi_materiali_usm,
    n_catalogo_generale,
    n_catalogo_interno,
    n_catalogo_internazionale,
    soprintendenza,
    quota_relativa,
    quota_abs,
    ref_tm,
    ref_ra,
    ref_n,
    posizione,
    criteri_distinzione,
    modo_formazione,
    componenti_organici,
    componenti_inorganici,
    lunghezza_max,
    altezza_max,
    altezza_min,
    profondita_max,
    profondita_min,
    larghezza_media,
    quota_max_abs,
    quota_max_rel,
    quota_min_abs,
    quota_min_rel,
    osservazioni,
    datazione,
    flottazione,
    setacciatura,
    affidabilita,
    direttore_us,
    responsabile_us,
    cod_ente_schedatore,
    data_rilevazione,
    data_rielaborazione,
    lunghezza_usm,
    altezza_usm,
    spessore_usm,
    tecnica_muraria_usm,
    modulo_usm,
    campioni_malta_usm,
    campioni_mattone_usm,
    campioni_pietra_usm,
    provenienza_materiali_usm,
    criteri_distinzione_usm,
    uso_primario_usm
FROM us_table;

-- Drop old table and rename new one
DROP TABLE us_table;
ALTER TABLE us_table_new RENAME TO us_table;

-- =====================================================
-- STEP 3: Migrate campioni_table
-- =====================================================

CREATE TABLE campioni_table_new (
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

INSERT INTO campioni_table_new SELECT 
    id_campione,
    sito,
    tipo_campione,
    descrizione_campione,
    area,
    CAST(us AS TEXT),
    numero_campione,
    nr_cassa,
    luogo_conservazione
FROM campioni_table;

DROP TABLE campioni_table;
ALTER TABLE campioni_table_new RENAME TO campioni_table;

-- =====================================================
-- STEP 4: Migrate pottery_table
-- =====================================================

CREATE TABLE pottery_table_new (
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

INSERT INTO pottery_table_new SELECT 
    id_rep,
    id_number,
    sito,
    area,
    CAST(us AS TEXT),
    box,
    photo,
    drawing,
    anno,
    fabric,
    percent,
    material,
    form,
    specific_form,
    ware,
    munsell,
    surf_trat,
    exdeco,
    intdeco,
    wheel_made,
    descrip_ex_deco,
    descrip_in_deco,
    note,
    diametro_max,
    qty,
    diametro_rim,
    diametro_bottom,
    diametro_height,
    diametro_preserved,
    specific_shape,
    bag
FROM pottery_table;

DROP TABLE pottery_table;
ALTER TABLE pottery_table_new RENAME TO pottery_table;

-- =====================================================
-- STEP 5: Recreate Views
-- =====================================================

CREATE VIEW pyarchinit_quote_view AS
SELECT 
    pyarchinit_quote.sito_q, 
    pyarchinit_quote.area_q, 
    pyarchinit_quote.us_q, 
    pyarchinit_quote.unita_misu, 
    pyarchinit_quote.quota_q, 
    pyarchinit_quote.geometry, 
    us_table.id_us, 
    us_table.sito, 
    us_table.area, 
    us_table.us, 
    us_table.struttura, 
    us_table.d_stratigrafica AS definizione_stratigrafica, 
    us_table.d_interpretativa AS definizione_interpretativa, 
    us_table.descrizione, 
    us_table.interpretazione, 
    us_table.rapporti, 
    us_table.periodo_iniziale, 
    us_table.fase_iniziale, 
    us_table.periodo_finale, 
    us_table.fase_finale, 
    us_table.anno_scavo
FROM pyarchinit_quote
JOIN us_table ON 
    pyarchinit_quote.sito_q = us_table.sito 
    AND pyarchinit_quote.area_q = us_table.area 
    AND CAST(pyarchinit_quote.us_q AS TEXT) = us_table.us;

CREATE VIEW pyarchinit_us_view AS 
SELECT 
    pyunitastratigrafiche.PK_UID, 
    pyunitastratigrafiche.geometry, 
    pyunitastratigrafiche.tipo_us_s, 
    pyunitastratigrafiche.scavo_s, 
    pyunitastratigrafiche.area_s, 
    pyunitastratigrafiche.us_s, 
    us_table.id_us, 
    us_table.sito, 
    us_table.area, 
    us_table.us, 
    us_table.struttura, 
    us_table.d_stratigrafica AS definizione_stratigrafica, 
    us_table.d_interpretativa AS definizione_interpretativa, 
    us_table.descrizione, 
    us_table.interpretazione, 
    us_table.rapporti, 
    us_table.periodo_iniziale, 
    us_table.fase_iniziale, 
    us_table.periodo_finale, 
    us_table.fase_finale, 
    us_table.anno_scavo
FROM pyunitastratigrafiche
JOIN us_table ON 
    pyunitastratigrafiche.scavo_s = us_table.sito 
    AND pyunitastratigrafiche.area_s = us_table.area 
    AND CAST(pyunitastratigrafiche.us_s AS TEXT) = us_table.us;

CREATE VIEW pyarchinit_uscaratterizzazioni_view AS
SELECT 
    pyuscaratterizzazioni.geometry, 
    pyuscaratterizzazioni.tipo_us_c, 
    pyuscaratterizzazioni.scavo_c, 
    pyuscaratterizzazioni.area_c, 
    pyuscaratterizzazioni.us_c, 
    us_table.sito, 
    us_table.id_us, 
    us_table.area, 
    us_table.us, 
    us_table.struttura, 
    us_table.d_stratigrafica AS definizione_stratigrafica, 
    us_table.d_interpretativa AS definizione_interpretativa, 
    us_table.descrizione, 
    us_table.interpretazione, 
    us_table.rapporti, 
    us_table.periodo_iniziale, 
    us_table.fase_iniziale, 
    us_table.periodo_finale, 
    us_table.fase_finale, 
    us_table.anno_scavo
FROM pyuscaratterizzazioni
JOIN us_table ON 
    pyuscaratterizzazioni.scavo_c = us_table.sito 
    AND pyuscaratterizzazioni.area_c = us_table.area 
    AND CAST(pyuscaratterizzazioni.us_c AS TEXT) = us_table.us;

-- =====================================================
-- STEP 6: Create indexes
-- =====================================================

CREATE INDEX idx_us_table_us ON us_table(us);
CREATE INDEX idx_campioni_us ON campioni_table(us);
CREATE INDEX idx_pottery_us ON pottery_table(us);

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Run these queries to verify the migration:
/*
SELECT sql FROM sqlite_master WHERE name = 'us_table';
SELECT sql FROM sqlite_master WHERE name = 'campioni_table';
SELECT sql FROM sqlite_master WHERE name = 'pottery_table';

-- Check if views are working
SELECT COUNT(*) FROM pyarchinit_quote_view;
SELECT COUNT(*) FROM pyarchinit_us_view;
*/