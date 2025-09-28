-- Script to ensure all concurrency columns exist in all tables
-- This script can be run safely multiple times - it only adds columns if they don't exist

-- Function to add concurrency columns to a table if they don't exist
CREATE OR REPLACE FUNCTION add_concurrency_columns_if_missing(target_table text)
RETURNS void AS $$
BEGIN
    -- Add version_number if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns c
        WHERE c.table_schema = 'public'
        AND c.table_name = target_table
        AND c.column_name = 'version_number'
    ) THEN
        EXECUTE format('ALTER TABLE public.%I ADD COLUMN version_number INTEGER DEFAULT 1', target_table);
    END IF;

    -- Add editing_by if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns c
        WHERE c.table_schema = 'public'
        AND c.table_name = target_table
        AND c.column_name = 'editing_by'
    ) THEN
        EXECUTE format('ALTER TABLE public.%I ADD COLUMN editing_by VARCHAR(100)', target_table);
    END IF;

    -- Add editing_since if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns c
        WHERE c.table_schema = 'public'
        AND c.table_name = target_table
        AND c.column_name = 'editing_since'
    ) THEN
        EXECUTE format('ALTER TABLE public.%I ADD COLUMN editing_since TIMESTAMP', target_table);
    END IF;

    -- Add last_modified_by if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns c
        WHERE c.table_schema = 'public'
        AND c.table_name = target_table
        AND c.column_name = 'last_modified_by'
    ) THEN
        EXECUTE format('ALTER TABLE public.%I ADD COLUMN last_modified_by VARCHAR(100) DEFAULT ''system''', target_table);
    END IF;

    -- Add last_modified_timestamp if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns c
        WHERE c.table_schema = 'public'
        AND c.table_name = target_table
        AND c.column_name = 'last_modified_timestamp'
    ) THEN
        EXECUTE format('ALTER TABLE public.%I ADD COLUMN last_modified_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP', target_table);
    END IF;

    RAISE NOTICE 'Concurrency columns checked/added for table: %', target_table;
END;
$$ LANGUAGE plpgsql;

-- Apply to all main tables
DO $$
DECLARE
    tables text[] := ARRAY[
        'us_table',
        'site_table',
        'periodizzazione_table',
        'inventario_materiali_table',
        'struttura_table',
        'tomba_table',
        'schedaind_table',
        'detsesso_table',
        'deteta_table',
        'documentazione_table',
        'campioni_table',
        'inventario_lapidei_table',
        'media_table',
        'media_thumb_table',
        'media_to_entity_table',
        'pyarchinit_thesaurus_sigle',
        'pottery_table',
        'tma_table'
    ];
    t text;
BEGIN
    FOREACH t IN ARRAY tables
    LOOP
        -- Check if table exists before trying to add columns
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = t
        ) THEN
            PERFORM add_concurrency_columns_if_missing(t);
        ELSE
            RAISE NOTICE 'Table % does not exist, skipping', t;
        END IF;
    END LOOP;
END $$;

-- Clean up function after use
DROP FUNCTION IF EXISTS add_concurrency_columns_if_missing(text);