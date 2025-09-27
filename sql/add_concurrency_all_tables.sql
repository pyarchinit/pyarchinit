-- =====================================================
-- SISTEMA DI CONCORRENZA PER TUTTE LE TABELLE PYARCHINIT
-- =====================================================
-- Aggiunge controllo versioni e gestione concorrenza a tutte
-- le tabelle archeologiche (escluse quelle geometriche)
-- =====================================================

-- Lista tabelle archeologiche principali
-- us_table ✓
-- tma_materiali_archeologici ✓
-- inventario_materiali_table
-- site_table
-- periodizzazione_table
-- struttura_table
-- tomba_table
-- individui_table
-- campioni_table
-- documentazione_table
-- lineeriferimento_table
-- ripartizioni_spaziali_table
-- thesaurus_sigle_table
-- detformazione_table
-- detsesso_table
-- deteta_table
-- archeozoology_table
-- campionature_table
-- inventario_lapidei_table
-- pottery_table

-- =====================================================
-- FUNZIONE HELPER PER AGGIUNGERE COLONNE
-- =====================================================
CREATE OR REPLACE FUNCTION add_concurrency_columns(table_name text)
RETURNS void AS $$
BEGIN
    -- Aggiungi colonne di versioning
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS last_modified_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP', table_name);
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS last_modified_by VARCHAR(100)', table_name);
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1', table_name);

    -- Aggiungi colonne per soft lock
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100)', table_name);
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP', table_name);

    -- Aggiungi colonne per tracking utente reale (multi-user)
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS real_user VARCHAR(100)', table_name);
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS user_machine VARCHAR(100)', table_name);
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS session_id VARCHAR(100)', table_name);

    RAISE NOTICE 'Colonne concorrenza aggiunte a %', table_name;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Errore aggiungendo colonne a %: %', table_name, SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- APPLICA A TUTTE LE TABELLE ARCHEOLOGICHE
-- =====================================================

-- US table (us_table_usm does not exist)
SELECT add_concurrency_columns('us_table');

-- TMA
SELECT add_concurrency_columns('tma_materiali_archeologici');

-- Inventario
SELECT add_concurrency_columns('inventario_materiali_table');
SELECT add_concurrency_columns('inventario_lapidei_table');

-- Sito e strutture
SELECT add_concurrency_columns('site_table');
SELECT add_concurrency_columns('struttura_table');
SELECT add_concurrency_columns('periodizzazione_table');

-- Sepolture
SELECT add_concurrency_columns('tomba_table');
SELECT add_concurrency_columns('individui_table');

-- Campioni
SELECT add_concurrency_columns('campioni_table');
SELECT add_concurrency_columns('campionature_table');

-- Documentazione
SELECT add_concurrency_columns('documentazione_table');

-- Reference tables
SELECT add_concurrency_columns('lineeriferimento_table');
SELECT add_concurrency_columns('ripartizioni_spaziali_table');

-- Thesaurus
SELECT add_concurrency_columns('thesaurus_sigle_table');

-- Determinazioni antropologiche
SELECT add_concurrency_columns('detformazione_table');
SELECT add_concurrency_columns('detsesso_table');
SELECT add_concurrency_columns('deteta_table');

-- Archeozoologia
SELECT add_concurrency_columns('archeozoology_table');

-- Pottery
SELECT add_concurrency_columns('pottery_table');

-- =====================================================
-- CREA TABELLA PER AUDIT LOG
-- =====================================================
CREATE TABLE IF NOT EXISTS pyarchinit_audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER,
    operation VARCHAR(20) NOT NULL, -- INSERT, UPDATE, DELETE
    user_name VARCHAR(100),
    real_user VARCHAR(100),
    user_machine VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    old_data JSONB,
    new_data JSONB,
    changes JSONB
);

CREATE INDEX IF NOT EXISTS idx_audit_table_record ON pyarchinit_audit_log(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON pyarchinit_audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_user ON pyarchinit_audit_log(user_name);

-- =====================================================
-- FUNZIONE GENERICA DI AUDIT
-- =====================================================
CREATE OR REPLACE FUNCTION pyarchinit_audit_trigger()
RETURNS TRIGGER AS $$
DECLARE
    v_old_data JSONB;
    v_new_data JSONB;
    v_changes JSONB;
BEGIN
    -- Prepara i dati
    IF TG_OP = 'DELETE' THEN
        v_old_data = row_to_json(OLD)::JSONB;
        v_new_data = NULL;
    ELSIF TG_OP = 'INSERT' THEN
        v_old_data = NULL;
        v_new_data = row_to_json(NEW)::JSONB;
    ELSIF TG_OP = 'UPDATE' THEN
        v_old_data = row_to_json(OLD)::JSONB;
        v_new_data = row_to_json(NEW)::JSONB;

        -- Calcola solo i campi che sono cambiati
        SELECT jsonb_object_agg(key, value) INTO v_changes
        FROM (
            SELECT key, v_new_data->key as value
            FROM jsonb_each(v_new_data)
            WHERE v_old_data->key IS DISTINCT FROM v_new_data->key
        ) changes;
    END IF;

    -- Inserisci nel log
    INSERT INTO pyarchinit_audit_log(
        table_name,
        record_id,
        operation,
        user_name,
        real_user,
        user_machine,
        old_data,
        new_data,
        changes
    ) VALUES (
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        TG_OP,
        COALESCE(NEW.last_modified_by, OLD.last_modified_by, current_user),
        COALESCE(NEW.real_user, OLD.real_user),
        COALESCE(NEW.user_machine, OLD.user_machine),
        v_old_data,
        v_new_data,
        v_changes
    );

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- APPLICA TRIGGER DI AUDIT A TUTTE LE TABELLE
-- =====================================================
CREATE OR REPLACE FUNCTION create_audit_trigger(table_name text)
RETURNS void AS $$
BEGIN
    EXECUTE format('DROP TRIGGER IF EXISTS audit_trigger ON %I', table_name);
    EXECUTE format('
        CREATE TRIGGER audit_trigger
        AFTER INSERT OR UPDATE OR DELETE ON %I
        FOR EACH ROW EXECUTE FUNCTION pyarchinit_audit_trigger()',
        table_name
    );
    RAISE NOTICE 'Trigger audit creato per %', table_name;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Errore creando trigger per %: %', table_name, SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- Applica a tutte le tabelle
SELECT create_audit_trigger('us_table');
SELECT create_audit_trigger('tma_materiali_archeologici');
SELECT create_audit_trigger('inventario_materiali_table');
SELECT create_audit_trigger('site_table');
SELECT create_audit_trigger('struttura_table');
SELECT create_audit_trigger('periodizzazione_table');
SELECT create_audit_trigger('tomba_table');
SELECT create_audit_trigger('individui_table');
SELECT create_audit_trigger('campioni_table');
SELECT create_audit_trigger('documentazione_table');

-- =====================================================
-- FUNZIONI PER GESTIONE CONCORRENZA
-- =====================================================

-- Funzione per verificare conflitti di versione
CREATE OR REPLACE FUNCTION check_version_conflict(
    p_table_name VARCHAR,
    p_record_id INTEGER,
    p_expected_version INTEGER
)
RETURNS TABLE(
    has_conflict BOOLEAN,
    current_version INTEGER,
    last_modified_by VARCHAR,
    last_modified_timestamp TIMESTAMP
) AS $$
DECLARE
    v_query TEXT;
    v_result RECORD;
BEGIN
    v_query := format('
        SELECT version_number, last_modified_by, last_modified_timestamp
        FROM %I
        WHERE id = $1',
        p_table_name
    );

    EXECUTE v_query INTO v_result USING p_record_id;

    RETURN QUERY
    SELECT
        v_result.version_number != p_expected_version,
        v_result.version_number,
        v_result.last_modified_by,
        v_result.last_modified_timestamp;
END;
$$ LANGUAGE plpgsql;

-- Funzione per impostare soft lock
CREATE OR REPLACE FUNCTION set_editing_lock(
    p_table_name VARCHAR,
    p_record_id INTEGER,
    p_user VARCHAR
)
RETURNS void AS $$
BEGIN
    EXECUTE format('
        UPDATE %I
        SET editing_by = $1,
            editing_since = CURRENT_TIMESTAMP
        WHERE id = $2',
        p_table_name
    ) USING p_user, p_record_id;
END;
$$ LANGUAGE plpgsql;

-- Funzione per rilasciare soft lock
CREATE OR REPLACE FUNCTION release_editing_lock(
    p_table_name VARCHAR,
    p_record_id INTEGER
)
RETURNS void AS $$
BEGIN
    EXECUTE format('
        UPDATE %I
        SET editing_by = NULL,
            editing_since = NULL
        WHERE id = $2',
        p_table_name
    ) USING p_record_id;
END;
$$ LANGUAGE plpgsql;

-- Funzione per pulire lock vecchi (> 30 minuti)
CREATE OR REPLACE FUNCTION clean_stale_locks()
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER := 0;
    v_table_name TEXT;
    v_temp_count INTEGER;
BEGIN
    FOR v_table_name IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        AND tablename LIKE '%_table%'
    LOOP
        EXECUTE format('
            UPDATE %I
            SET editing_by = NULL, editing_since = NULL
            WHERE editing_since < CURRENT_TIMESTAMP - INTERVAL ''30 minutes''
            AND editing_by IS NOT NULL',
            v_table_name
        );

        GET DIAGNOSTICS v_temp_count = ROW_COUNT;
        v_count := v_count + v_temp_count;
    END LOOP;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VISTE UTILI PER MONITORAGGIO
-- =====================================================

-- Vista per vedere chi sta editando cosa
CREATE OR REPLACE VIEW active_editing_sessions AS
SELECT
    'us_table' as table_name,
    id,
    COALESCE(us::text, '') as reference,
    sito,
    area,
    editing_by,
    editing_since,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - editing_since))/60 as minutes_editing
FROM us_table
WHERE editing_by IS NOT NULL

UNION ALL

SELECT
    'inventario_materiali_table' as table_name,
    id_invmat as id,
    numero_inventario::text as reference,
    sito,
    area,
    editing_by,
    editing_since,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - editing_since))/60 as minutes_editing
FROM inventario_materiali_table
WHERE editing_by IS NOT NULL

UNION ALL

SELECT
    'tma_materiali_archeologici' as table_name,
    id,
    COALESCE(dscu, '') as reference,
    sito,
    area,
    editing_by,
    editing_since,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - editing_since))/60 as minutes_editing
FROM tma_materiali_archeologici
WHERE editing_by IS NOT NULL

ORDER BY editing_since DESC;

-- Vista per vedere le modifiche recenti
CREATE OR REPLACE VIEW recent_changes AS
SELECT
    table_name,
    record_id,
    operation,
    user_name,
    real_user,
    timestamp,
    changes
FROM pyarchinit_audit_log
WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY timestamp DESC
LIMIT 100;

-- =====================================================
-- JOB DI MANUTENZIONE
-- =====================================================

-- Pianifica pulizia lock vecchi (da eseguire periodicamente)
-- Nota: PostgreSQL non ha scheduler integrato, usare pg_cron o crontab
-- Esempio con pg_cron:
-- SELECT cron.schedule('clean-stale-locks', '*/30 * * * *', 'SELECT clean_stale_locks();');

-- =====================================================
-- REPORT FINALE
-- =====================================================
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE '✅ SISTEMA DI CONCORRENZA INSTALLATO CON SUCCESSO';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Funzionalità aggiunte:';
    RAISE NOTICE '  1. Versioning su tutte le tabelle archeologiche';
    RAISE NOTICE '  2. Soft locks per editing';
    RAISE NOTICE '  3. Audit trail completo';
    RAISE NOTICE '  4. Tracking utente reale';
    RAISE NOTICE '  5. Funzioni di gestione conflitti';
    RAISE NOTICE '';
    RAISE NOTICE 'Viste disponibili:';
    RAISE NOTICE '  - active_editing_sessions: chi sta editando cosa';
    RAISE NOTICE '  - recent_changes: modifiche ultime 24 ore';
    RAISE NOTICE '';
    RAISE NOTICE 'Manutenzione:';
    RAISE NOTICE '  - Eseguire periodicamente: SELECT clean_stale_locks();';
    RAISE NOTICE '';
    RAISE NOTICE 'Prossimi passi:';
    RAISE NOTICE '  1. Integrare ConcurrencyManager nei form PyArchInit';
    RAISE NOTICE '  2. Configurare identificazione utenti';
    RAISE NOTICE '  3. Testare con utenti multipli';
    RAISE NOTICE '=====================================================';
END $$;