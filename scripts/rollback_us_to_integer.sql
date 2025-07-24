-- PyArchInit Rollback Script: Convert US fields back from TEXT to INTEGER
-- WARNING: This will fail if there are non-numeric values in US fields!
-- Author: PyArchInit Team
-- Date: 2025-07-24

-- =====================================================
-- STEP 1: Drop Views
-- =====================================================

DROP VIEW IF EXISTS pyarchinit_quote_view CASCADE;
DROP VIEW IF EXISTS pyarchinit_us_view CASCADE;
DROP VIEW IF EXISTS pyarchinit_uscaratterizzazioni_view CASCADE;

-- =====================================================
-- STEP 2: Convert US fields back to INTEGER
-- =====================================================

-- IMPORTANT: These conversions will fail if any non-numeric values exist!
-- Run this check first:
-- SELECT us FROM us_table WHERE us !~ '^[0-9]+$';

-- 2.1 Main US table
ALTER TABLE us_table 
    ALTER COLUMN us TYPE INTEGER USING us::INTEGER;

-- 2.2 Campioni table
ALTER TABLE campioni_table 
    ALTER COLUMN us TYPE INTEGER USING us::INTEGER;

-- 2.3 Pottery table
ALTER TABLE pottery_table 
    ALTER COLUMN us TYPE INTEGER USING us::INTEGER;

-- 2.4 US import table
ALTER TABLE us_table_toimp 
    ALTER COLUMN us TYPE INTEGER USING us::INTEGER;

-- 2.5 Quote table
ALTER TABLE pyarchinit_quote 
    ALTER COLUMN us_q TYPE INTEGER USING us_q::INTEGER;

-- 2.6 Quote USM table
ALTER TABLE pyarchinit_quote_usm 
    ALTER COLUMN us_q TYPE INTEGER USING us_q::INTEGER;

-- 2.7 Unità stratigrafiche GIS
ALTER TABLE pyunitastratigrafiche 
    ALTER COLUMN us_s TYPE INTEGER USING us_s::INTEGER;

-- 2.8 Unità stratigrafiche USM GIS
ALTER TABLE pyunitastratigrafiche_usm 
    ALTER COLUMN us_s TYPE INTEGER USING us_s::INTEGER;

-- 2.9 US negative
ALTER TABLE pyarchinit_us_negative_doc 
    ALTER COLUMN us_n TYPE INTEGER USING us_n::INTEGER;

-- =====================================================
-- STEP 3: Recreate Original Views
-- =====================================================

-- 3.1 Recreate pyarchinit_quote_view
CREATE VIEW pyarchinit_quote_view AS
SELECT 
    pyarchinit_quote.gid,
    pyarchinit_quote.sito_q, 
    pyarchinit_quote.area_q, 
    pyarchinit_quote.us_q, 
    pyarchinit_quote.unita_misu_q, 
    pyarchinit_quote.quota_q, 
    pyarchinit_quote.the_geom, 
    us_table.id_us, 
    us_table.sito, 
    us_table.area, 
    us_table.us, 
    us_table.struttura, 
    us_table.definizione_stratigrafica, 
    us_table.definizione_interpretativa, 
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
    pyarchinit_quote.sito_q::text = us_table.sito 
    AND pyarchinit_quote.area_q::text = us_table.area::text 
    AND pyarchinit_quote.us_q::text = us_table.us::text;

-- 3.2 Recreate pyarchinit_us_view
CREATE VIEW pyarchinit_us_view AS
SELECT 
    pyunitastratigrafiche.gid, 
    pyunitastratigrafiche.the_geom, 
    pyunitastratigrafiche.tipo_us_s, 
    pyunitastratigrafiche.scavo_s, 
    pyunitastratigrafiche.area_s, 
    pyunitastratigrafiche.us_s, 
    us_table.id_us, 
    us_table.sito, 
    us_table.area, 
    us_table.us, 
    us_table.struttura, 
    us_table.definizione_stratigrafica, 
    us_table.definizione_interpretativa, 
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
    pyunitastratigrafiche.scavo_s::text = us_table.sito 
    AND pyunitastratigrafiche.area_s::text = us_table.area::text 
    AND pyunitastratigrafiche.us_s = us_table.us;

-- 3.3 Recreate pyarchinit_uscaratterizzazioni_view
CREATE VIEW pyarchinit_uscaratterizzazioni_view AS
SELECT 
    pyuscaratterizzazioni.gid, 
    pyuscaratterizzazioni.the_geom, 
    pyuscaratterizzazioni.tipo_us_c, 
    pyuscaratterizzazioni.scavo_c, 
    pyuscaratterizzazioni.area_c, 
    pyuscaratterizzazioni.us_c, 
    us_table.sito, 
    us_table.id_us, 
    us_table.area, 
    us_table.us, 
    us_table.struttura, 
    us_table.definizione_stratigrafica, 
    us_table.definizione_interpretativa, 
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
    pyuscaratterizzazioni.scavo_c::text = us_table.sito 
    AND pyuscaratterizzazioni.area_c::text = us_table.area::text 
    AND pyuscaratterizzazioni.us_c = us_table.us;