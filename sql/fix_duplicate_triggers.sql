-- Fix duplicate audit triggers on all tables
-- This removes duplicate triggers that cause "duplicate key" errors

DO $$
DECLARE
    r RECORD;
    trigger_count INTEGER;
BEGIN
    -- Find tables with multiple audit triggers
    FOR r IN
        SELECT
            tgrelid::regclass::text as table_name,
            COUNT(*) as trigger_count
        FROM pg_trigger
        WHERE tgname LIKE '%audit%'
        GROUP BY tgrelid
        HAVING COUNT(*) > 1
    LOOP
        RAISE NOTICE 'Table % has % audit triggers', r.table_name, r.trigger_count;

        -- Drop the older audit_trigger (keep audit_<tablename>)
        EXECUTE format('DROP TRIGGER IF EXISTS audit_trigger ON %I', r.table_name);
        RAISE NOTICE 'Dropped duplicate trigger audit_trigger from %', r.table_name;
    END LOOP;

    -- Also check for any tables that have both old and new style triggers
    FOR r IN
        SELECT DISTINCT
            tgrelid::regclass::text as table_name
        FROM pg_trigger t1
        WHERE EXISTS (
            SELECT 1 FROM pg_trigger t2
            WHERE t2.tgrelid = t1.tgrelid
            AND t2.tgname = 'audit_trigger'
        )
        AND EXISTS (
            SELECT 1 FROM pg_trigger t3
            WHERE t3.tgrelid = t1.tgrelid
            AND t3.tgname LIKE 'audit_%_table'
        )
    LOOP
        -- Drop the generic audit_trigger
        EXECUTE format('DROP TRIGGER IF EXISTS audit_trigger ON %I', r.table_name);
        RAISE NOTICE 'Removed duplicate audit_trigger from %', r.table_name;
    END LOOP;

    RAISE NOTICE 'Duplicate trigger cleanup complete';
END $$;

-- Fix the sequence to be absolutely sure
SELECT setval('audit_log_id_seq', (SELECT COALESCE(MAX(id), 0) + 1000 FROM audit_log), true);

-- Show current status
SELECT
    'Current max audit_log ID: ' || COALESCE(MAX(id), 0) as status
FROM audit_log
UNION ALL
SELECT
    'Current sequence value: ' || last_value
FROM audit_log_id_seq;