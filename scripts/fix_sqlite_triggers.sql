-- Fix SQLite database by removing problematic triggers and completing migration

-- Drop all ISO metadata triggers that are causing issues
DROP TRIGGER IF EXISTS ISO_metadata_reference_row_id_value_insert;
DROP TRIGGER IF EXISTS ISO_metadata_reference_row_id_value_update;
DROP TRIGGER IF EXISTS ISO_metadata_reference_row_id_value_delete;

-- Complete the table renaming
ALTER TABLE us_table_new RENAME TO us_table;

-- Verify the migration
SELECT 'US field type in us_table:';
SELECT sql FROM sqlite_master WHERE name = 'us_table' AND type = 'table';

-- Check if TMA table was created
SELECT 'TMA table exists:';
SELECT COUNT(*) FROM sqlite_master WHERE name = 'tma_materiali_archeologici' AND type = 'table';

-- List all tables
SELECT 'Current tables:';
SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name;