-- =====================================================
-- TRIGGER PER TRACKING AUTOMATICO ATTIVITA'
-- Funziona indipendentemente dalla versione del plugin
-- =====================================================

-- =====================================================
-- 0. CREAZIONE TABELLA ACCESS LOG (se non esiste)
-- =====================================================

CREATE TABLE IF NOT EXISTS pyarchinit_access_log (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    action VARCHAR(50),
    table_accessed VARCHAR(100),
    operation VARCHAR(50),
    record_id TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    details TEXT
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_access_log_username ON pyarchinit_access_log(username);
CREATE INDEX IF NOT EXISTS idx_access_log_timestamp ON pyarchinit_access_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_access_log_table ON pyarchinit_access_log(table_accessed);

-- =====================================================
-- 0b. AGGIUNGI COLONNE CONCURRENCY ALLE TABELLE
-- =====================================================

-- Funzione per aggiungere colonne di concurrency a una tabella
CREATE OR REPLACE FUNCTION add_concurrency_columns(p_table_name TEXT)
RETURNS VOID AS $$
BEGIN
    -- Add editing_by column if not exists
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100)', p_table_name);
    -- Add editing_since column if not exists
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP', p_table_name);
    -- Add version_number column if not exists
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1', p_table_name);
    -- Add last_modified_by column if not exists
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS last_modified_by VARCHAR(100)', p_table_name);
    -- Add last_modified_timestamp column if not exists
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS last_modified_timestamp TIMESTAMP', p_table_name);
EXCEPTION WHEN OTHERS THEN
    -- Ignore errors (table might not exist)
    RAISE NOTICE 'Could not add columns to %: %', p_table_name, SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- Apply to all main tables
SELECT add_concurrency_columns('us_table');
SELECT add_concurrency_columns('pottery_table');
SELECT add_concurrency_columns('inventario_materiali_table');
SELECT add_concurrency_columns('tma_materiali_archeologici');
SELECT add_concurrency_columns('site_table');
SELECT add_concurrency_columns('periodizzazione_table');
SELECT add_concurrency_columns('struttura_table');
SELECT add_concurrency_columns('tomba_table');
SELECT add_concurrency_columns('individui_table');
SELECT add_concurrency_columns('campioni_table');
SELECT add_concurrency_columns('documentazione_table');
SELECT add_concurrency_columns('archeozoology_table');

-- =====================================================
-- 1. FUNZIONE PER LOG ACCESSI
-- =====================================================

CREATE OR REPLACE FUNCTION log_table_access()
RETURNS TRIGGER AS $$
DECLARE
    v_action TEXT;
    v_record_id TEXT;
    v_username TEXT;
    v_rec RECORD;
BEGIN
    -- Get current database user
    v_username := current_user;
    v_action := TG_OP;

    -- Get record based on operation
    IF TG_OP = 'DELETE' THEN
        v_rec := OLD;
    ELSE
        v_rec := NEW;
    END IF;

    -- Determine record ID based on table name
    CASE TG_TABLE_NAME
        WHEN 'us_table' THEN v_record_id := v_rec.id_us::text;
        WHEN 'pottery_table' THEN v_record_id := v_rec.id_rep::text;
        WHEN 'inventario_materiali_table' THEN v_record_id := v_rec.id_invmat::text;
        WHEN 'tma_materiali_archeologici' THEN v_record_id := v_rec.id::text;
        WHEN 'site_table' THEN v_record_id := v_rec.id_sito::text;
        WHEN 'periodizzazione_table' THEN v_record_id := v_rec.id_perfas::text;
        WHEN 'struttura_table' THEN v_record_id := v_rec.id_struttura::text;
        WHEN 'tomba_table' THEN v_record_id := v_rec.id_tomba::text;
        WHEN 'individui_table' THEN v_record_id := v_rec.id_scheda_ind::text;
        WHEN 'campioni_table' THEN v_record_id := v_rec.id_campione::text;
        WHEN 'documentazione_table' THEN v_record_id := v_rec.id_documentazione::text;
        WHEN 'archeozoology_table' THEN v_record_id := v_rec.id_archzoo::text;
        ELSE v_record_id := 'unknown';
    END CASE;

    -- Insert into access log
    BEGIN
        INSERT INTO pyarchinit_access_log (
            username,
            action,
            table_accessed,
            operation,
            record_id,
            timestamp,
            success
        ) VALUES (
            v_username,
            v_action,
            TG_TABLE_NAME,
            v_action,
            v_record_id,
            CURRENT_TIMESTAMP,
            TRUE
        );
    EXCEPTION WHEN OTHERS THEN
        -- Don't fail the main operation if logging fails
        RAISE NOTICE 'Could not log access: %', SQLERRM;
    END;

    -- Return appropriate record
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 2. FUNZIONE PER TRACKING EDITING (chi sta modificando)
-- =====================================================

CREATE OR REPLACE FUNCTION track_editing_user()
RETURNS TRIGGER AS $$
BEGIN
    -- Only update if the columns exist and we're doing an UPDATE
    IF TG_OP = 'UPDATE' THEN
        -- Set editing_by to current user and editing_since to now
        -- This marks who is currently editing the record
        NEW.editing_by := current_user;
        NEW.editing_since := CURRENT_TIMESTAMP;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 3. FUNZIONE PER CLEAR EDITING (dopo il salvataggio)
-- Opzionale: pulisce i campi editing dopo un certo tempo
-- =====================================================

CREATE OR REPLACE FUNCTION clear_stale_editing_locks()
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER := 0;
    v_rows INTEGER;
    v_table TEXT;
    v_tables TEXT[] := ARRAY[
        'us_table', 'pottery_table', 'inventario_materiali_table',
        'tma_materiali_archeologici', 'site_table', 'periodizzazione_table',
        'struttura_table', 'tomba_table', 'individui_table', 'campioni_table',
        'documentazione_table', 'archeozoology_table'
    ];
BEGIN
    -- Clear locks older than 30 minutes (considered stale)
    FOREACH v_table IN ARRAY v_tables LOOP
        BEGIN
            EXECUTE format('
                UPDATE %I
                SET editing_by = NULL, editing_since = NULL
                WHERE editing_since < CURRENT_TIMESTAMP - INTERVAL ''30 minutes''
                AND editing_by IS NOT NULL
            ', v_table);
            GET DIAGNOSTICS v_rows = ROW_COUNT;
            v_count := v_count + v_rows;
        EXCEPTION WHEN OTHERS THEN
            -- Table might not have the columns, skip
            NULL;
        END;
    END LOOP;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 4. CREAZIONE TRIGGER PER LOGGING SU TABELLE PRINCIPALI
-- =====================================================

-- US Table
DROP TRIGGER IF EXISTS trg_us_table_access_log ON us_table;
CREATE TRIGGER trg_us_table_access_log
    AFTER INSERT OR UPDATE OR DELETE ON us_table
    FOR EACH ROW EXECUTE FUNCTION log_table_access();

-- Pottery Table
DROP TRIGGER IF EXISTS trg_pottery_table_access_log ON pottery_table;
CREATE TRIGGER trg_pottery_table_access_log
    AFTER INSERT OR UPDATE OR DELETE ON pottery_table
    FOR EACH ROW EXECUTE FUNCTION log_table_access();

-- Inventario Materiali Table
DROP TRIGGER IF EXISTS trg_inventario_materiali_access_log ON inventario_materiali_table;
CREATE TRIGGER trg_inventario_materiali_access_log
    AFTER INSERT OR UPDATE OR DELETE ON inventario_materiali_table
    FOR EACH ROW EXECUTE FUNCTION log_table_access();

-- TMA Materiali Archeologici
DROP TRIGGER IF EXISTS trg_tma_materiali_access_log ON tma_materiali_archeologici;
CREATE TRIGGER trg_tma_materiali_access_log
    AFTER INSERT OR UPDATE OR DELETE ON tma_materiali_archeologici
    FOR EACH ROW EXECUTE FUNCTION log_table_access();

-- Site Table
DROP TRIGGER IF EXISTS trg_site_table_access_log ON site_table;
CREATE TRIGGER trg_site_table_access_log
    AFTER INSERT OR UPDATE OR DELETE ON site_table
    FOR EACH ROW EXECUTE FUNCTION log_table_access();

-- Periodizzazione Table
DROP TRIGGER IF EXISTS trg_periodizzazione_access_log ON periodizzazione_table;
CREATE TRIGGER trg_periodizzazione_access_log
    AFTER INSERT OR UPDATE OR DELETE ON periodizzazione_table
    FOR EACH ROW EXECUTE FUNCTION log_table_access();

-- Struttura Table
DROP TRIGGER IF EXISTS trg_struttura_access_log ON struttura_table;
CREATE TRIGGER trg_struttura_access_log
    AFTER INSERT OR UPDATE OR DELETE ON struttura_table
    FOR EACH ROW EXECUTE FUNCTION log_table_access();

-- Tomba Table
DROP TRIGGER IF EXISTS trg_tomba_access_log ON tomba_table;
CREATE TRIGGER trg_tomba_access_log
    AFTER INSERT OR UPDATE OR DELETE ON tomba_table
    FOR EACH ROW EXECUTE FUNCTION log_table_access();

-- Individui Table
DROP TRIGGER IF EXISTS trg_individui_access_log ON individui_table;
CREATE TRIGGER trg_individui_access_log
    AFTER INSERT OR UPDATE OR DELETE ON individui_table
    FOR EACH ROW EXECUTE FUNCTION log_table_access();

-- Campioni Table
DROP TRIGGER IF EXISTS trg_campioni_access_log ON campioni_table;
CREATE TRIGGER trg_campioni_access_log
    AFTER INSERT OR UPDATE OR DELETE ON campioni_table
    FOR EACH ROW EXECUTE FUNCTION log_table_access();

-- Documentazione Table
DROP TRIGGER IF EXISTS trg_documentazione_access_log ON documentazione_table;
CREATE TRIGGER trg_documentazione_access_log
    AFTER INSERT OR UPDATE OR DELETE ON documentazione_table
    FOR EACH ROW EXECUTE FUNCTION log_table_access();

-- Archeozoology Table
DROP TRIGGER IF EXISTS trg_archeozoology_access_log ON archeozoology_table;
CREATE TRIGGER trg_archeozoology_access_log
    AFTER INSERT OR UPDATE OR DELETE ON archeozoology_table
    FOR EACH ROW EXECUTE FUNCTION log_table_access();

-- =====================================================
-- 5. CREAZIONE TRIGGER PER EDITING TRACKING
-- Questi trigger aggiornano editing_by/editing_since
-- automaticamente quando un record viene modificato
-- =====================================================

-- US Table
DROP TRIGGER IF EXISTS trg_us_table_editing ON us_table;
CREATE TRIGGER trg_us_table_editing
    BEFORE UPDATE ON us_table
    FOR EACH ROW EXECUTE FUNCTION track_editing_user();

-- Pottery Table
DROP TRIGGER IF EXISTS trg_pottery_table_editing ON pottery_table;
CREATE TRIGGER trg_pottery_table_editing
    BEFORE UPDATE ON pottery_table
    FOR EACH ROW EXECUTE FUNCTION track_editing_user();

-- Inventario Materiali Table
DROP TRIGGER IF EXISTS trg_inventario_materiali_editing ON inventario_materiali_table;
CREATE TRIGGER trg_inventario_materiali_editing
    BEFORE UPDATE ON inventario_materiali_table
    FOR EACH ROW EXECUTE FUNCTION track_editing_user();

-- TMA Materiali Archeologici
DROP TRIGGER IF EXISTS trg_tma_materiali_editing ON tma_materiali_archeologici;
CREATE TRIGGER trg_tma_materiali_editing
    BEFORE UPDATE ON tma_materiali_archeologici
    FOR EACH ROW EXECUTE FUNCTION track_editing_user();

-- Site Table
DROP TRIGGER IF EXISTS trg_site_table_editing ON site_table;
CREATE TRIGGER trg_site_table_editing
    BEFORE UPDATE ON site_table
    FOR EACH ROW EXECUTE FUNCTION track_editing_user();

-- Periodizzazione Table
DROP TRIGGER IF EXISTS trg_periodizzazione_editing ON periodizzazione_table;
CREATE TRIGGER trg_periodizzazione_editing
    BEFORE UPDATE ON periodizzazione_table
    FOR EACH ROW EXECUTE FUNCTION track_editing_user();

-- Struttura Table
DROP TRIGGER IF EXISTS trg_struttura_editing ON struttura_table;
CREATE TRIGGER trg_struttura_editing
    BEFORE UPDATE ON struttura_table
    FOR EACH ROW EXECUTE FUNCTION track_editing_user();

-- Tomba Table
DROP TRIGGER IF EXISTS trg_tomba_editing ON tomba_table;
CREATE TRIGGER trg_tomba_editing
    BEFORE UPDATE ON tomba_table
    FOR EACH ROW EXECUTE FUNCTION track_editing_user();

-- Individui Table
DROP TRIGGER IF EXISTS trg_individui_editing ON individui_table;
CREATE TRIGGER trg_individui_editing
    BEFORE UPDATE ON individui_table
    FOR EACH ROW EXECUTE FUNCTION track_editing_user();

-- Campioni Table
DROP TRIGGER IF EXISTS trg_campioni_editing ON campioni_table;
CREATE TRIGGER trg_campioni_editing
    BEFORE UPDATE ON campioni_table
    FOR EACH ROW EXECUTE FUNCTION track_editing_user();

-- Documentazione Table
DROP TRIGGER IF EXISTS trg_documentazione_editing ON documentazione_table;
CREATE TRIGGER trg_documentazione_editing
    BEFORE UPDATE ON documentazione_table
    FOR EACH ROW EXECUTE FUNCTION track_editing_user();

-- Archeozoology Table
DROP TRIGGER IF EXISTS trg_archeozoology_editing ON archeozoology_table;
CREATE TRIGGER trg_archeozoology_editing
    BEFORE UPDATE ON archeozoology_table
    FOR EACH ROW EXECUTE FUNCTION track_editing_user();

-- =====================================================
-- 6. VIEW PER MONITOR SESSIONI ATTIVE
-- Mostra chi sta modificando cosa in tutte le tabelle
-- =====================================================

CREATE OR REPLACE VIEW active_editing_sessions AS
SELECT 'us_table' as table_name, id_us as record_id, editing_by, editing_since FROM us_table WHERE editing_by IS NOT NULL
UNION ALL
SELECT 'pottery_table', id_rep, editing_by, editing_since FROM pottery_table WHERE editing_by IS NOT NULL
UNION ALL
SELECT 'inventario_materiali_table', id_invmat, editing_by, editing_since FROM inventario_materiali_table WHERE editing_by IS NOT NULL
UNION ALL
SELECT 'tma_materiali_archeologici', id, editing_by, editing_since FROM tma_materiali_archeologici WHERE editing_by IS NOT NULL
UNION ALL
SELECT 'site_table', id_sito, editing_by, editing_since FROM site_table WHERE editing_by IS NOT NULL
UNION ALL
SELECT 'periodizzazione_table', id_perfas, editing_by, editing_since FROM periodizzazione_table WHERE editing_by IS NOT NULL
UNION ALL
SELECT 'struttura_table', id_struttura, editing_by, editing_since FROM struttura_table WHERE editing_by IS NOT NULL
UNION ALL
SELECT 'tomba_table', id_tomba, editing_by, editing_since FROM tomba_table WHERE editing_by IS NOT NULL
UNION ALL
SELECT 'individui_table', id_scheda_ind, editing_by, editing_since FROM individui_table WHERE editing_by IS NOT NULL
UNION ALL
SELECT 'campioni_table', id_campione, editing_by, editing_since FROM campioni_table WHERE editing_by IS NOT NULL
UNION ALL
SELECT 'documentazione_table', id_documentazione, editing_by, editing_since FROM documentazione_table WHERE editing_by IS NOT NULL
UNION ALL
SELECT 'archeozoology_table', id_archzoo, editing_by, editing_since FROM archeozoology_table WHERE editing_by IS NOT NULL;

-- =====================================================
-- 7. VERIFICA
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=== TRIGGER CREATI CON SUCCESSO ===';
    RAISE NOTICE 'Trigger di logging creati per 12 tabelle:';
    RAISE NOTICE '  us_table, pottery_table, inventario_materiali_table, tma_materiali_archeologici,';
    RAISE NOTICE '  site_table, periodizzazione_table, struttura_table, tomba_table,';
    RAISE NOTICE '  individui_table, campioni_table, documentazione_table, archeozoology_table';
    RAISE NOTICE '';
    RAISE NOTICE 'Trigger di editing tracking creati per tutte le 12 tabelle';
    RAISE NOTICE '';
    RAISE NOTICE 'View active_editing_sessions creata per monitorare sessioni attive';
    RAISE NOTICE '';
    RAISE NOTICE 'Per pulire lock stalli: SELECT clear_stale_editing_locks();';
    RAISE NOTICE 'Per vedere sessioni attive: SELECT * FROM active_editing_sessions;';
END $$;
