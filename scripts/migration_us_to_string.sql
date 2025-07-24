-- PyArchInit Migration Script: Convert US fields from INTEGER to TEXT
-- WARNING: This is a major database change. Make a full backup before running!
-- Author: PyArchInit Team
-- Date: 2025-07-24

-- =====================================================
-- STEP 1: Drop Views that depend on US field
-- =====================================================

DROP VIEW IF EXISTS pyarchinit_quote_view CASCADE;
DROP VIEW IF EXISTS pyarchinit_us_view CASCADE;
DROP VIEW IF EXISTS pyarchinit_uscaratterizzazioni_view CASCADE;

-- =====================================================
-- STEP 2: Convert US fields from INTEGER to TEXT
-- =====================================================

-- 2.1 Main US table
ALTER TABLE us_table 
    ALTER COLUMN us TYPE TEXT USING us::TEXT;

-- 2.2 Campioni table
ALTER TABLE campioni_table 
    ALTER COLUMN us TYPE TEXT USING us::TEXT;

-- 2.3 Pottery table
ALTER TABLE pottery_table 
    ALTER COLUMN us TYPE TEXT USING us::TEXT;

-- 2.4 US import table
ALTER TABLE us_table_toimp 
    ALTER COLUMN us TYPE TEXT USING us::TEXT;

-- 2.5 Quote table
ALTER TABLE pyarchinit_quote 
    ALTER COLUMN us_q TYPE TEXT USING us_q::TEXT;

-- 2.6 Quote USM table
ALTER TABLE pyarchinit_quote_usm 
    ALTER COLUMN us_q TYPE TEXT USING us_q::TEXT;

-- 2.7 Unità stratigrafiche GIS
ALTER TABLE pyunitastratigrafiche 
    ALTER COLUMN us_s TYPE TEXT USING us_s::TEXT;

-- 2.8 Unità stratigrafiche USM GIS
ALTER TABLE pyunitastratigrafiche_usm 
    ALTER COLUMN us_s TYPE TEXT USING us_s::TEXT;

-- 2.9 US negative
ALTER TABLE pyarchinit_us_negative_doc 
    ALTER COLUMN us_n TYPE TEXT USING us_n::TEXT;

-- 2.10 US caratterizzazioni (if exists)
ALTER TABLE pyuscaratterizzazioni 
    ALTER COLUMN us_c TYPE TEXT USING us_c::TEXT;

-- =====================================================
-- STEP 3: Recreate Views with new data types
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
    pyarchinit_quote.sito_q = us_table.sito 
    AND pyarchinit_quote.area_q::TEXT = us_table.area::TEXT 
    AND pyarchinit_quote.us_q = us_table.us;

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
    pyunitastratigrafiche.scavo_s = us_table.sito 
    AND pyunitastratigrafiche.area_s::TEXT = us_table.area::TEXT 
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
    pyuscaratterizzazioni.scavo_c = us_table.sito 
    AND pyuscaratterizzazioni.area_c::TEXT = us_table.area::TEXT 
    AND pyuscaratterizzazioni.us_c = us_table.us;

-- =====================================================
-- STEP 4: Update constraints if needed
-- =====================================================

-- Add any necessary constraints for the new TEXT fields
-- For example, ensuring non-empty values:
ALTER TABLE us_table 
    ADD CONSTRAINT us_not_empty CHECK (us <> '');

-- =====================================================
-- STEP 5: Update indexes if needed
-- =====================================================

-- Drop old indexes on integer fields
DROP INDEX IF EXISTS idx_us_table_us;
DROP INDEX IF EXISTS idx_campioni_us;
DROP INDEX IF EXISTS idx_pottery_us;

-- Create new indexes on text fields
CREATE INDEX idx_us_table_us ON us_table(us);
CREATE INDEX idx_campioni_us ON campioni_table(us);
CREATE INDEX idx_pottery_us ON pottery_table(us);
CREATE INDEX idx_pyarchinit_quote_us_q ON pyarchinit_quote(us_q);
CREATE INDEX idx_pyunitastratigrafiche_us_s ON pyunitastratigrafiche(us_s);

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Run these queries to verify the migration:
/*
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'us_table' AND column_name = 'us';

SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'campioni_table' AND column_name = 'us';

-- Check if views are working
SELECT COUNT(*) FROM pyarchinit_quote_view;
SELECT COUNT(*) FROM pyarchinit_us_view;
*/