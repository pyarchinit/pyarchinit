-- ============================================================================
-- PyArchInit Concurrency Support for PostgreSQL
--
-- This script adds versioning columns to all PyArchInit tables
-- to handle concurrent modifications in multi-user environments
--
-- Created by: Assistant
-- Date: 2024
-- ============================================================================

-- Function to add concurrency columns to a table
CREATE OR REPLACE FUNCTION add_concurrency_support(table_name text)
RETURNS void AS $$
BEGIN
    -- Add last_modified_timestamp column
    EXECUTE format('
        ALTER TABLE %I
        ADD COLUMN IF NOT EXISTS last_modified_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ', table_name);

    -- Add last_modified_by column
    EXECUTE format('
        ALTER TABLE %I
        ADD COLUMN IF NOT EXISTS last_modified_by VARCHAR(100) DEFAULT current_user
    ', table_name);

    -- Add version_number column for optimistic locking
    EXECUTE format('
        ALTER TABLE %I
        ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1
    ', table_name);

    -- Add columns for tracking who's editing (soft lock)
    EXECUTE format('
        ALTER TABLE %I
        ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100)
    ', table_name);

    EXECUTE format('
        ALTER TABLE %I
        ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP
    ', table_name);

    RAISE NOTICE 'Added concurrency support to table %', table_name;
END;
$$ LANGUAGE plpgsql;

-- Function to create update trigger for a table
CREATE OR REPLACE FUNCTION create_update_trigger(table_name text)
RETURNS void AS $$
BEGIN
    -- Create trigger function
    EXECUTE format('
        CREATE OR REPLACE FUNCTION update_%I_versioning()
        RETURNS TRIGGER AS $func$
        BEGIN
            NEW.last_modified_timestamp = CURRENT_TIMESTAMP;
            NEW.last_modified_by = current_user;
            NEW.version_number = COALESCE(OLD.version_number, 0) + 1;
            RETURN NEW;
        END;
        $func$ LANGUAGE plpgsql;
    ', table_name);

    -- Drop existing trigger if exists
    EXECUTE format('
        DROP TRIGGER IF EXISTS %I_versioning_trigger ON %I
    ', table_name, table_name);

    -- Create new trigger
    EXECUTE format('
        CREATE TRIGGER %I_versioning_trigger
        BEFORE UPDATE ON %I
        FOR EACH ROW
        EXECUTE FUNCTION update_%I_versioning()
    ', table_name, table_name, table_name);

    RAISE NOTICE 'Created update trigger for table %', table_name;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Apply to all PyArchInit tables
-- ============================================================================

DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY[
        'us_table',
        'us_table_usm',
        'site_table',
        'periodizzazione_table',
        'inventario_materiali_table',
        'struttura_table',
        'tomba_table',
        'individui_table',
        'campioni_table',
        'documentazione_table',
        'linearizzo_table',
        'ripartizioni_temporali_table',
        'unita_tipo_table',
        'inventario_lapidei_table',
        'tafonomia_table',
        'archeozoology_table',
        'tecnica_muraria_usm_table',
        'tma_table',
        'pottery_table'
    ];
BEGIN
    FOREACH tbl IN ARRAY tables
    LOOP
        -- Check if table exists
        IF EXISTS (SELECT 1 FROM information_schema.tables
                   WHERE table_schema = 'public'
                   AND table_name = tbl) THEN

            -- Add concurrency columns
            PERFORM add_concurrency_support(tbl);

            -- Create update trigger
            PERFORM create_update_trigger(tbl);

        ELSE
            RAISE NOTICE 'Table % does not exist, skipping', tbl;
        END IF;
    END LOOP;

    RAISE NOTICE '========================================';
    RAISE NOTICE 'Concurrency support installation complete!';
    RAISE NOTICE '========================================';
END $$;

-- ============================================================================
-- Create view to monitor active editors
-- ============================================================================

CREATE OR REPLACE VIEW active_editors AS
SELECT
    'us_table' as table_name,
    us as record_identifier,
    sito,
    area,
    editing_by,
    editing_since,
    last_modified_by,
    last_modified_timestamp
FROM us_table
WHERE editing_by IS NOT NULL
AND editing_since > CURRENT_TIMESTAMP - INTERVAL '30 minutes'

UNION ALL

SELECT
    'us_table_usm' as table_name,
    us as record_identifier,
    sito,
    area,
    editing_by,
    editing_since,
    last_modified_by,
    last_modified_timestamp
FROM us_table_usm
WHERE editing_by IS NOT NULL
AND editing_since > CURRENT_TIMESTAMP - INTERVAL '30 minutes'

UNION ALL

SELECT
    'inventario_materiali_table' as table_name,
    numero_inventario::text as record_identifier,
    sito,
    area::text,
    editing_by,
    editing_since,
    last_modified_by,
    last_modified_timestamp
FROM inventario_materiali_table
WHERE editing_by IS NOT NULL
AND editing_since > CURRENT_TIMESTAMP - INTERVAL '30 minutes';

-- ============================================================================
-- Utility functions
-- ============================================================================

-- Function to manually clear stale locks
CREATE OR REPLACE FUNCTION clear_stale_locks()
RETURNS void AS $$
DECLARE
    tbl text;
    tables text[] := ARRAY[
        'us_table',
        'us_table_usm',
        'site_table',
        'periodizzazione_table',
        'inventario_materiali_table',
        'struttura_table',
        'tomba_table',
        'individui_table',
        'campioni_table',
        'documentazione_table'
    ];
BEGIN
    FOREACH tbl IN ARRAY tables
    LOOP
        IF EXISTS (SELECT 1 FROM information_schema.tables
                   WHERE table_schema = 'public'
                   AND table_name = tbl) THEN

            EXECUTE format('
                UPDATE %I
                SET editing_by = NULL, editing_since = NULL
                WHERE editing_since < CURRENT_TIMESTAMP - INTERVAL ''30 minutes''
            ', tbl);

        END IF;
    END LOOP;

    RAISE NOTICE 'Cleared all stale locks older than 30 minutes';
END;
$$ LANGUAGE plpgsql;

-- Schedule periodic cleanup (optional - requires pg_cron extension)
-- SELECT cron.schedule('clear-stale-locks', '*/30 * * * *', 'SELECT clear_stale_locks();');

-- ============================================================================
-- Grant necessary permissions
-- ============================================================================

-- Adjust these grants based on your user setup
-- GRANT SELECT ON active_editors TO pyarchinit_users;
-- GRANT EXECUTE ON FUNCTION clear_stale_locks() TO pyarchinit_users;