-- =====================================================
-- AGGIORNAMENTO SCHEMA PYARCHINIT
-- Aggiunge quota e sistema di concorrenza
-- =====================================================

-- 1. CAMPO QUOTA PER INVENTARIO MATERIALI
-- =====================================================
ALTER TABLE inventario_materiali_table
ADD COLUMN IF NOT EXISTS quota_usm FLOAT,
ADD COLUMN IF NOT EXISTS unita_misura_quota VARCHAR(20) DEFAULT 'm s.l.m.';

COMMENT ON COLUMN inventario_materiali_table.quota_usm IS 'Quota US/USM (può essere negativa)';
COMMENT ON COLUMN inventario_materiali_table.unita_misura_quota IS 'Unità di misura quota (es: m s.l.m., m, cm)';

-- 2. CAMPI CONCORRENZA PER TUTTE LE TABELLE
-- =====================================================

-- Funzione helper per aggiungere campi concorrenza
CREATE OR REPLACE FUNCTION add_concurrency_columns(table_name text)
RETURNS void AS $$
BEGIN
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS last_modified_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP', table_name);
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS last_modified_by VARCHAR(100)', table_name);
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1', table_name);
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100)', table_name);
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP', table_name);
    RAISE NOTICE 'Colonne concorrenza aggiunte a %', table_name;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Errore aggiungendo colonne a %: %', table_name, SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- Applica a tutte le tabelle principali
SELECT add_concurrency_columns('us_table');
SELECT add_concurrency_columns('tma_materiali_archeologici');
SELECT add_concurrency_columns('inventario_materiali_table');
SELECT add_concurrency_columns('site_table');
SELECT add_concurrency_columns('struttura_table');
SELECT add_concurrency_columns('periodizzazione_table');
SELECT add_concurrency_columns('tomba_table');
SELECT add_concurrency_columns('individui_table');
SELECT add_concurrency_columns('campioni_table');
SELECT add_concurrency_columns('documentazione_table');
SELECT add_concurrency_columns('detsesso_table');
SELECT add_concurrency_columns('deteta_table');
SELECT add_concurrency_columns('archeozoology_table');
SELECT add_concurrency_columns('pottery_table');

-- 3. SISTEMA GESTIONE UTENTI
-- =====================================================

-- Tabella utenti
CREATE TABLE IF NOT EXISTS pyarchinit_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'archeologo',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    last_login TIMESTAMP,
    last_ip VARCHAR(50),
    notes TEXT
);

-- Tabella permessi
CREATE TABLE IF NOT EXISTS pyarchinit_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES pyarchinit_users(id) ON DELETE CASCADE,
    table_name VARCHAR(100) NOT NULL,
    can_insert BOOLEAN DEFAULT FALSE,
    can_update BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    can_view BOOLEAN DEFAULT TRUE,
    site_filter VARCHAR(100),
    area_filter VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    UNIQUE(user_id, table_name)
);

-- Tabella ruoli
CREATE TABLE IF NOT EXISTS pyarchinit_roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    default_can_insert BOOLEAN DEFAULT FALSE,
    default_can_update BOOLEAN DEFAULT FALSE,
    default_can_delete BOOLEAN DEFAULT FALSE,
    default_can_view BOOLEAN DEFAULT TRUE,
    is_system_role BOOLEAN DEFAULT FALSE
);

-- Tabella log accessi
CREATE TABLE IF NOT EXISTS pyarchinit_access_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES pyarchinit_users(id),
    username VARCHAR(50),
    action VARCHAR(50),
    table_accessed VARCHAR(100),
    operation VARCHAR(20),
    record_id INTEGER,
    ip_address VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN,
    error_message TEXT
);

-- Inserisci ruoli predefiniti
INSERT INTO pyarchinit_roles (role_name, description, default_can_insert, default_can_update, default_can_delete, default_can_view, is_system_role) VALUES
('admin', 'Amministratore - Accesso completo', TRUE, TRUE, TRUE, TRUE, TRUE),
('responsabile', 'Responsabile scavo - Può modificare tutto', TRUE, TRUE, TRUE, TRUE, FALSE),
('archeologo', 'Archeologo - Può inserire e modificare', TRUE, TRUE, FALSE, TRUE, FALSE),
('studente', 'Studente - Solo inserimento', TRUE, FALSE, FALSE, TRUE, FALSE),
('guest', 'Ospite - Solo visualizzazione', FALSE, FALSE, FALSE, TRUE, FALSE)
ON CONFLICT (role_name) DO NOTHING;

-- 4. AUDIT LOG
-- =====================================================

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
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON pyarchinit_audit_log(timestamp);

-- 5. FUNZIONI GESTIONE CONCORRENZA
-- =====================================================

-- Check version conflict
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

-- Clean stale locks
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

-- 6. VISTE AGGIORNATE
-- =====================================================

-- Vista reperti con quota
DROP VIEW IF EXISTS pyarchinit_reperti_view CASCADE;

CREATE OR REPLACE VIEW pyarchinit_reperti_view AS
SELECT
    im.id_invmat,
    im.sito,
    im.numero_inventario,
    im.tipo_reperto,
    im.criterio_schedatura,
    im.definizione,
    im.descrizione,
    im.area,
    im.us,
    im.lavato,
    im.nr_cassa,
    im.luogo_conservazione,
    im.stato_conservazione,
    im.datazione_reperto,
    im.elementi_reperto,
    im.misurazioni,
    im.rif_biblio,
    im.tecnologie,
    im.forme_minime,
    im.forme_massime,
    im.totale_frammenti,
    im.corpo_ceramico,
    im.rivestimento,
    im.diametro_orlo,
    im.peso,
    im.tipo,
    im.eve_orlo,
    im.repertato,
    im.diagnostico,
    im.quota_usm,
    im.unita_misura_quota,
    im.last_modified_timestamp,
    im.last_modified_by,
    im.version_number
FROM inventario_materiali_table im;

-- Vista sessioni editing attive
CREATE OR REPLACE VIEW active_editing_sessions AS
SELECT
    'us_table' as table_name,
    id_us as id,
    COALESCE(us::text, '') as reference,
    sito,
    area,
    editing_by,
    editing_since,
    CASE
        WHEN editing_since IS NOT NULL
        THEN EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - editing_since))/60
        ELSE 0
    END as minutes_editing
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
    CASE
        WHEN editing_since IS NOT NULL
        THEN EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - editing_since))/60
        ELSE 0
    END as minutes_editing
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
    CASE
        WHEN editing_since IS NOT NULL
        THEN EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - editing_since))/60
        ELSE 0
    END as minutes_editing
FROM tma_materiali_archeologici
WHERE editing_by IS NOT NULL

ORDER BY editing_since DESC;

-- 7. VINCOLI UNIQUE PER PREVENIRE DUPLICATI
-- =====================================================

-- TMA
ALTER TABLE tma_materiali_archeologici
DROP CONSTRAINT IF EXISTS tma_unique_key;
ALTER TABLE tma_materiali_archeologici
ADD CONSTRAINT tma_unique_key UNIQUE (dscu, sito, area, saggio);

-- US
ALTER TABLE us_table
DROP CONSTRAINT IF EXISTS us_unique_key;
ALTER TABLE us_table
ADD CONSTRAINT us_unique_key UNIQUE (sito, area, us);

-- Inventario (già esistente ma verifichiamo)
ALTER TABLE inventario_materiali_table
DROP CONSTRAINT IF EXISTS "ID_invmat_unico";
ALTER TABLE inventario_materiali_table
ADD CONSTRAINT "ID_invmat_unico" UNIQUE (sito, numero_inventario);

-- Site
ALTER TABLE site_table
DROP CONSTRAINT IF EXISTS site_unique_key;
ALTER TABLE site_table
ADD CONSTRAINT site_unique_key UNIQUE (sito);

-- Periodizzazione
ALTER TABLE periodizzazione_table
DROP CONSTRAINT IF EXISTS period_unique_key;
ALTER TABLE periodizzazione_table
ADD CONSTRAINT period_unique_key UNIQUE (sito, periodo, fase);

-- Struttura
ALTER TABLE struttura_table
DROP CONSTRAINT IF EXISTS struttura_unique_key;
ALTER TABLE struttura_table
ADD CONSTRAINT struttura_unique_key UNIQUE (sito, sigla_struttura, numero_struttura);

-- Individui
ALTER TABLE individui_table
DROP CONSTRAINT IF EXISTS individui_unique_key;
ALTER TABLE individui_table
ADD CONSTRAINT individui_unique_key UNIQUE (sito, nr_individuo);

-- Campioni
ALTER TABLE campioni_table
DROP CONSTRAINT IF EXISTS campioni_unique_key;
ALTER TABLE campioni_table
ADD CONSTRAINT campioni_unique_key UNIQUE (sito, nr_campione);

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE '✅ SCHEMA PYARCHINIT AGGIORNATO';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Aggiunte:';
    RAISE NOTICE '  1. Campo quota (quota_usm) in inventario_materiali_table';
    RAISE NOTICE '  2. Sistema di concorrenza su tutte le tabelle';
    RAISE NOTICE '  3. Gestione utenti e permessi';
    RAISE NOTICE '  4. Sistema di audit';
    RAISE NOTICE '  5. Vincoli UNIQUE per prevenire duplicati';
    RAISE NOTICE '';
    RAISE NOTICE 'Eseguire SELECT clean_stale_locks() periodicamente';
    RAISE NOTICE '=====================================================';
END $$;