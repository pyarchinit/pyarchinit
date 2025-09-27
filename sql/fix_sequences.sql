-- Fix all sequences after database restore
-- Run this script if you get duplicate key errors after a restore

-- Fix audit_log sequence
DO $$
DECLARE
    max_id INTEGER;
BEGIN
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM audit_log;
    PERFORM setval('audit_log_id_seq', max_id + 1, false);
    RAISE NOTICE 'audit_log_id_seq reset to %', max_id + 1;
END $$;

-- Fix all table sequences
DO $$
DECLARE
    seq_record RECORD;
    table_name TEXT;
    column_name TEXT;
    max_val BIGINT;
    seq_val BIGINT;
BEGIN
    -- Loop through all sequences
    FOR seq_record IN
        SELECT
            sequence_schema,
            sequence_name,
            regexp_replace(sequence_name, '_id_seq$|_seq$', '') as base_name
        FROM information_schema.sequences
        WHERE sequence_schema = 'public'
    LOOP
        BEGIN
            -- Try to find the table and column this sequence belongs to
            SELECT
                t.table_name,
                c.column_name
            INTO
                table_name,
                column_name
            FROM information_schema.columns c
            JOIN information_schema.tables t ON c.table_name = t.table_name
            WHERE c.column_default LIKE '%' || seq_record.sequence_name || '%'
                AND t.table_schema = 'public'
            LIMIT 1;

            IF table_name IS NOT NULL AND column_name IS NOT NULL THEN
                -- Get max value from table
                EXECUTE format('SELECT COALESCE(MAX(%I), 0) FROM %I', column_name, table_name)
                INTO max_val;

                -- Get current sequence value
                SELECT last_value INTO seq_val
                FROM pg_sequences
                WHERE schemaname = seq_record.sequence_schema
                    AND sequencename = seq_record.sequence_name;

                -- If max value is greater than sequence, update sequence
                IF max_val >= seq_val THEN
                    EXECUTE format('SELECT setval(''%I.%I'', %s)',
                        seq_record.sequence_schema,
                        seq_record.sequence_name,
                        max_val + 1);
                    RAISE NOTICE 'Fixed sequence %.% to %',
                        seq_record.sequence_schema,
                        seq_record.sequence_name,
                        max_val + 1;
                END IF;
            END IF;
        EXCEPTION
            WHEN OTHERS THEN
                -- Skip if there's any error with this sequence
                NULL;
        END;
    END LOOP;
END $$;

-- Specifically fix known PyArchInit sequences
SELECT setval('pyarchinit_users_id_seq', (SELECT COALESCE(MAX(id), 0) + 1 FROM pyarchinit_users), false)
WHERE EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'pyarchinit_users');

SELECT setval('pyarchinit_user_permissions_id_seq', (SELECT COALESCE(MAX(id), 0) + 1 FROM pyarchinit_user_permissions), false)
WHERE EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'pyarchinit_user_permissions');

SELECT setval('pyarchinit_activity_log_id_seq', (SELECT COALESCE(MAX(id), 0) + 1 FROM pyarchinit_activity_log), false)
WHERE EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'pyarchinit_activity_log');

SELECT setval('audit_log_id_seq', (SELECT COALESCE(MAX(id), 0) + 1 FROM audit_log), false)
WHERE EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'audit_log');

-- Final notice
DO $$
BEGIN
    RAISE NOTICE 'All sequences have been checked and fixed where necessary';
END $$;