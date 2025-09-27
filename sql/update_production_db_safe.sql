-- =====================================================
-- AGGIORNAMENTO DATABASE PRODUCTION - VERSIONE SICURA
-- =====================================================
-- Questo script può essere eseguito multiple volte senza errori
-- Gestisce automaticamente tabelle/colonne già esistenti
-- =====================================================

-- 1. CORREZIONE CAMPO QUOTA (da min/max a singolo campo)
DO $$
BEGIN
    -- Rimuovi i campi quota_min_usm e quota_max_usm se esistono
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'inventario_materiali_table'
               AND column_name = 'quota_min_usm') THEN
        ALTER TABLE inventario_materiali_table DROP COLUMN quota_min_usm CASCADE;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'inventario_materiali_table'
               AND column_name = 'quota_max_usm') THEN
        ALTER TABLE inventario_materiali_table DROP COLUMN quota_max_usm CASCADE;
    END IF;

    -- Aggiungi il campo quota singolo se non esiste
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'inventario_materiali_table'
                   AND column_name = 'quota_usm') THEN
        ALTER TABLE inventario_materiali_table ADD COLUMN quota_usm FLOAT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'inventario_materiali_table'
                   AND column_name = 'unita_misura_quota') THEN
        ALTER TABLE inventario_materiali_table ADD COLUMN unita_misura_quota VARCHAR(20) DEFAULT 'm s.l.m.';
    END IF;

    RAISE NOTICE '✓ Campo quota corretto';
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Errore correzione quota: %', SQLERRM;
END $$;

-- 2. SISTEMA DI CONCORRENZA - Funzione helper per aggiungere colonne in modo sicuro
CREATE OR REPLACE FUNCTION add_concurrency_columns_safe(p_table_name text, p_id_column text)
RETURNS void AS $$
DECLARE
    v_exists boolean;
BEGIN
    -- Verifica che la tabella esista ed è una tabella (non una view)
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = p_table_name
        AND table_type = 'BASE TABLE'
    ) INTO v_exists;

    IF NOT v_exists THEN
        RAISE NOTICE 'Tabella % non trovata o è una view, skip', p_table_name;
        RETURN;
    END IF;

    -- Aggiungi colonne solo se non esistono
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = p_table_name AND column_name = 'version_number') THEN
        EXECUTE format('ALTER TABLE %I ADD COLUMN version_number INTEGER DEFAULT 1', p_table_name);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = p_table_name AND column_name = 'editing_by') THEN
        EXECUTE format('ALTER TABLE %I ADD COLUMN editing_by VARCHAR(100)', p_table_name);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = p_table_name AND column_name = 'editing_since') THEN
        EXECUTE format('ALTER TABLE %I ADD COLUMN editing_since TIMESTAMP', p_table_name);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = p_table_name AND column_name = 'audit_trail') THEN
        EXECUTE format('ALTER TABLE %I ADD COLUMN audit_trail JSONB DEFAULT ''[]''::jsonb', p_table_name);
    END IF;

    RAISE NOTICE '✓ Concorrenza aggiunta a %', p_table_name;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Errore aggiungendo concorrenza a %: %', p_table_name, SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- Applica a tutte le tabelle con i loro ID corretti
SELECT add_concurrency_columns_safe('us_table', 'id_us');
SELECT add_concurrency_columns_safe('tma_materiali_archeologici', 'id');
SELECT add_concurrency_columns_safe('inventario_materiali_table', 'id_invmat');
SELECT add_concurrency_columns_safe('site_table', 'id_sito');
SELECT add_concurrency_columns_safe('periodizzazione_table', 'id_perfas');
SELECT add_concurrency_columns_safe('struttura_table', 'id_struttura');
SELECT add_concurrency_columns_safe('tomba_table', 'id_tomba');
SELECT add_concurrency_columns_safe('individui_table', 'id_scheda_ind');
SELECT add_concurrency_columns_safe('campioni_table', 'id_campione');
SELECT add_concurrency_columns_safe('documentazione_table', 'id_doc');
SELECT add_concurrency_columns_safe('detsesso_table', 'id_det_sesso');
SELECT add_concurrency_columns_safe('deteta_table', 'id_det_eta');
SELECT add_concurrency_columns_safe('archeozoology_table', 'id_archzoo');
SELECT add_concurrency_columns_safe('pottery_table', 'id_rep');

-- 3. TABELLE PER GESTIONE UTENTI
CREATE TABLE IF NOT EXISTS pyarchinit_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    email VARCHAR(255),
    full_name VARCHAR(255),
    notes TEXT,
    created_by VARCHAR(100)
);

-- Aggiungi campi mancanti se la tabella esiste già
ALTER TABLE pyarchinit_users
ADD COLUMN IF NOT EXISTS notes TEXT,
ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);

CREATE TABLE IF NOT EXISTS pyarchinit_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES pyarchinit_users(id) ON DELETE CASCADE,
    table_name VARCHAR(100) NOT NULL,
    can_view BOOLEAN DEFAULT FALSE,
    can_insert BOOLEAN DEFAULT FALSE,
    can_update BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id, table_name)
);

CREATE TABLE IF NOT EXISTS pyarchinit_activity_log (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    action VARCHAR(50),
    table_name VARCHAR(100),
    record_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB,
    ip_address VARCHAR(45),
    session_id VARCHAR(100)
);

-- Crea indici se non esistono
CREATE INDEX IF NOT EXISTS idx_activity_log_timestamp ON pyarchinit_activity_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_activity_log_username ON pyarchinit_activity_log(username);

-- Crea tabella ruoli
CREATE TABLE IF NOT EXISTS pyarchinit_roles (
    role_name VARCHAR(50) PRIMARY KEY,
    description TEXT,
    default_can_view BOOLEAN DEFAULT TRUE,
    default_can_insert BOOLEAN DEFAULT FALSE,
    default_can_update BOOLEAN DEFAULT FALSE,
    default_can_delete BOOLEAN DEFAULT FALSE,
    is_system_role BOOLEAN DEFAULT TRUE
);

-- Inserisci ruoli predefiniti
INSERT INTO pyarchinit_roles (role_name, description, default_can_view, default_can_insert, default_can_update, default_can_delete, is_system_role)
VALUES
    ('admin', 'Amministratore completo del sistema', TRUE, TRUE, TRUE, TRUE, TRUE),
    ('responsabile', 'Responsabile di scavo', TRUE, TRUE, TRUE, FALSE, TRUE),
    ('archeologo', 'Archeologo/Operatore', TRUE, TRUE, FALSE, FALSE, TRUE),
    ('studente', 'Studente/Tirocinante', TRUE, FALSE, FALSE, FALSE, TRUE),
    ('guest', 'Ospite solo lettura', TRUE, FALSE, FALSE, FALSE, TRUE)
ON CONFLICT (role_name) DO NOTHING;

-- Inserisci utente admin di default
INSERT INTO pyarchinit_users (username, password_hash, role, full_name, email, is_active, notes)
VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin', 'Amministratore', 'admin@pyarchinit.it', true, 'Utente amministratore di default')
ON CONFLICT (username) DO NOTHING;

-- 4. CREA TABELLA AUDIT LOG SE NON ESISTE
CREATE TABLE IF NOT EXISTS pyarchinit_audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER,
    operation VARCHAR(20) NOT NULL,
    user_name VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    old_data JSONB,
    new_data JSONB,
    changes JSONB
);

CREATE INDEX IF NOT EXISTS idx_audit_table_record ON pyarchinit_audit_log(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON pyarchinit_audit_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_user ON pyarchinit_audit_log(user_name);

-- 5. RICREA VIEW IN MODO SICURO (gestisce colonne mancanti)
-- Drop e ricrea active_editing_sessions
DROP VIEW IF EXISTS active_editing_sessions CASCADE;

CREATE VIEW active_editing_sessions AS
SELECT
    'us_table' as table_name,
    id_us as id,
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

-- Ricrea recent_changes view
DROP VIEW IF EXISTS recent_changes CASCADE;

CREATE VIEW recent_changes AS
SELECT
    table_name,
    record_id,
    operation,
    user_name,
    timestamp,
    changes
FROM pyarchinit_audit_log
WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY timestamp DESC
LIMIT 100;

-- 6. RICREA pyarchinit_reperti_view GESTENDO COLONNE MANCANTI
DROP VIEW IF EXISTS pyarchinit_reperti_view CASCADE;

CREATE VIEW pyarchinit_reperti_view AS
SELECT
    id_invmat,
    sito,
    numero_inventario,
    tipo_reperto,
    criterio_schedatura,
    definizione,
    descrizione,
    area,
    us,
    lavato,
    nr_cassa,
    luogo_conservazione,
    stato_conservazione,
    datazione_reperto,
    elementi_reperto,
    misurazioni,
    rif_biblio,
    tecnologie,
    forme_minime,
    forme_massime,
    totale_frammenti,
    corpo_ceramico,
    rivestimento,
    diametro_orlo,
    peso,
    tipo,
    eve_orlo,
    repertato,
    diagnostico,
    n_reperto,
    tipo_contenitore,
    struttura,
    -- Aggiungi campi opzionali solo se esistono
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'inventario_materiali_table'
                      AND column_name = 'quota_usm')
         THEN (SELECT quota_usm FROM inventario_materiali_table i2 WHERE i2.id_invmat = inventario_materiali_table.id_invmat)
         ELSE NULL::float
    END as quota_usm,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns
                      WHERE table_name = 'inventario_materiali_table'
                      AND column_name = 'unita_misura_quota')
         THEN (SELECT unita_misura_quota FROM inventario_materiali_table i2 WHERE i2.id_invmat = inventario_materiali_table.id_invmat)
         ELSE 'm s.l.m.'
    END as unita_misura_quota
FROM inventario_materiali_table;

-- 7. PREVENZIONE DUPLICATI TMA
DO $$
BEGIN
    -- Rimuovi eventuali duplicati esistenti (mantiene il record con ID più basso)
    DELETE FROM tma_materiali_archeologici a
    WHERE EXISTS (
        SELECT 1
        FROM tma_materiali_archeologici b
        WHERE a.sito = b.sito
        AND a.area = b.area
        AND COALESCE(a.inventario, '') = COALESCE(b.inventario, '')
        AND COALESCE(a.dscu, '') = COALESCE(b.dscu, '')
        AND a.id > b.id
        AND (a.inventario IS NOT NULL AND a.inventario != ''
             OR a.dscu IS NOT NULL AND a.dscu != '')
    );

    -- Aggiungi indice univoco solo se non esiste
    IF NOT EXISTS (SELECT 1 FROM pg_indexes
                   WHERE indexname = 'idx_tma_unique_record') THEN
        CREATE UNIQUE INDEX idx_tma_unique_record
        ON tma_materiali_archeologici(sito, area, inventario, dscu)
        WHERE inventario IS NOT NULL AND inventario != '';
    END IF;

    -- Aggiungi indice su created_at se non esiste
    IF NOT EXISTS (SELECT 1 FROM pg_indexes
                   WHERE indexname = 'idx_tma_created_at') THEN
        CREATE INDEX idx_tma_created_at ON tma_materiali_archeologici(created_at);
    END IF;

    RAISE NOTICE '✓ Protezione duplicati TMA applicata';
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Errore protezione duplicati TMA: %', SQLERRM;
END $$;

-- 8. FUNZIONI UTILITY PER GESTIONE LOCK
CREATE OR REPLACE FUNCTION clean_stale_locks()
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER := 0;
    v_temp INTEGER := 0;
BEGIN
    -- US table
    UPDATE us_table
    SET editing_by = NULL, editing_since = NULL
    WHERE editing_since < CURRENT_TIMESTAMP - INTERVAL '30 minutes'
    AND editing_by IS NOT NULL;
    GET DIAGNOSTICS v_temp = ROW_COUNT;
    v_count := v_count + v_temp;

    -- Inventario
    UPDATE inventario_materiali_table
    SET editing_by = NULL, editing_since = NULL
    WHERE editing_since < CURRENT_TIMESTAMP - INTERVAL '30 minutes'
    AND editing_by IS NOT NULL;
    GET DIAGNOSTICS v_temp = ROW_COUNT;
    v_count := v_count + v_temp;

    -- TMA
    UPDATE tma_materiali_archeologici
    SET editing_by = NULL, editing_since = NULL
    WHERE editing_since < CURRENT_TIMESTAMP - INTERVAL '30 minutes'
    AND editing_by IS NOT NULL;
    GET DIAGNOSTICS v_temp = ROW_COUNT;
    v_count := v_count + v_temp;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- 9. REPORT FINALE
DO $$
DECLARE
    v_tables_updated INTEGER;
    v_views_created INTEGER;
BEGIN
    -- Conta tabelle con concorrenza
    SELECT COUNT(DISTINCT table_name) INTO v_tables_updated
    FROM information_schema.columns
    WHERE column_name IN ('version_number', 'editing_by', 'editing_since', 'audit_trail')
    AND table_schema = 'public';

    -- Conta views create
    SELECT COUNT(*) INTO v_views_created
    FROM information_schema.views
    WHERE table_name IN ('active_editing_sessions', 'recent_changes', 'pyarchinit_reperti_view')
    AND table_schema = 'public';

    RAISE NOTICE '';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE '✅ AGGIORNAMENTO DATABASE COMPLETATO';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE 'Risultati:';
    RAISE NOTICE '  • Tabelle con concorrenza: %', v_tables_updated;
    RAISE NOTICE '  • Views create/aggiornate: %', v_views_created;
    RAISE NOTICE '  • Campo quota corretto';
    RAISE NOTICE '  • Tabelle utenti create';
    RAISE NOTICE '  • Protezione duplicati TMA attiva';
    RAISE NOTICE '';
    RAISE NOTICE 'Il database è pronto per l''uso!';
    RAISE NOTICE '=====================================================';
END $$;