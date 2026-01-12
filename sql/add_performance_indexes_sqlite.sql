-- Performance indexes for pyArchInit SQLite/Spatialite database
-- These indexes improve query performance on frequently searched columns
-- Safe to run multiple times (uses IF NOT EXISTS)

-- Index on us_table.sito for stratigraphic unit queries
CREATE INDEX IF NOT EXISTS idx_us_table_sito ON us_table(sito);

-- Index on inventario_materiali_table.sito for materials inventory queries
CREATE INDEX IF NOT EXISTS idx_inventario_sito ON inventario_materiali_table(sito);

-- Index on site_table.sito for site queries
CREATE INDEX IF NOT EXISTS idx_site_table_sito ON site_table(sito);

-- Index on pyarchinit_thesaurus_sigle.tipologia_sigla for thesaurus lookups
CREATE INDEX IF NOT EXISTS idx_thesaurus_tipologia ON pyarchinit_thesaurus_sigle(tipologia_sigla);

-- Composite index on pyarchinit_quote for elevation queries
CREATE INDEX IF NOT EXISTS idx_quote_sito ON pyarchinit_quote(sito_q, area_q, us_q);

-- Index on pyarchinit_reperti.siti for finds queries
CREATE INDEX IF NOT EXISTS idx_reperti_siti ON pyarchinit_reperti(siti);

-- Additional useful indexes for common queries

-- Index on us_table for area queries
CREATE INDEX IF NOT EXISTS idx_us_table_area ON us_table(area);

-- Composite index on us_table for sito+area queries
CREATE INDEX IF NOT EXISTS idx_us_table_sito_area ON us_table(sito, area);

-- Index on inventario_materiali_table for area queries
CREATE INDEX IF NOT EXISTS idx_inventario_area ON inventario_materiali_table(area);

-- Index on tomba_table for site queries
CREATE INDEX IF NOT EXISTS idx_tomba_sito ON tomba_table(sito);

-- Index on periodizzazione_table for site queries
CREATE INDEX IF NOT EXISTS idx_periodizzazione_sito ON periodizzazione_table(sito);

-- Index on struttura_table for site queries
CREATE INDEX IF NOT EXISTS idx_struttura_sito ON struttura_table(sito);

-- Index on documentazione_table for site queries
CREATE INDEX IF NOT EXISTS idx_documentazione_sito ON documentazione_table(sito);

-- Index on campioni_table for site queries
CREATE INDEX IF NOT EXISTS idx_campioni_sito ON campioni_table(sito);

-- Run ANALYZE to update statistics (SQLite syntax)
ANALYZE;
