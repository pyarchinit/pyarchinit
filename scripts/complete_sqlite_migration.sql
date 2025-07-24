-- Complete SQLite migration by dropping all dependent views and renaming table

-- Drop all views that depend on us_table
DROP VIEW IF EXISTS pyarchinit_quote_usm_view;
DROP VIEW IF EXISTS pyarchinit_quote_view;
DROP VIEW IF EXISTS pyarchinit_us_view;
DROP VIEW IF EXISTS pyarchinit_usm_view;
DROP VIEW IF EXISTS pyarchinit_uscaratterizzazioni_view;
DROP VIEW IF EXISTS pyarchinit_us_negative_doc_view;
DROP VIEW IF EXISTS mediaentity_view;

-- Now rename the table
ALTER TABLE us_table_new RENAME TO us_table;

-- Verify the migration
SELECT 'Migration completed!';
SELECT 'US field type:';
PRAGMA table_info(us_table);

-- Check TMA table
SELECT '';
SELECT 'TMA table structure:';
PRAGMA table_info(tma_materiali_archeologici);