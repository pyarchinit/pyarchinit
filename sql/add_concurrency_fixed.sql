-- =====================================================
-- SISTEMA DI CONCORRENZA SEMPLIFICATO PER PYARCHINIT
-- =====================================================
-- Versione corretta con i nomi delle colonne ID reali
-- =====================================================

-- 1. Aggiungi colonne di concorrenza a tutte le tabelle principali
-- US table (id_us)
ALTER TABLE us_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- TMA table (id)
ALTER TABLE tma_materiali_archeologici
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Inventario materiali (id_invmat)
ALTER TABLE inventario_materiali_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Site table (id_sito)
ALTER TABLE site_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Periodizzazione (id_perfas)
ALTER TABLE periodizzazione_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Struttura (id_struttura)
ALTER TABLE struttura_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Tomba (id_tomba)
ALTER TABLE tomba_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Individui (id_scheda_ind)
ALTER TABLE individui_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Campioni (id_campione)
ALTER TABLE campioni_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Documentazione (id_doc)
ALTER TABLE documentazione_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Detsesso (id_det_sesso)
ALTER TABLE detsesso_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Deteta (id_det_eta)
ALTER TABLE deteta_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Archeozoology (id_archzoo)
ALTER TABLE archeozoology_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Pottery (id_rep)
ALTER TABLE pottery_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- 2. Crea tabella per audit log
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

-- 3. Crea vista per sessioni di editing attive (TUTTE LE TABELLE)
CREATE OR REPLACE VIEW active_editing_sessions AS
SELECT 'us_table'::text AS table_name, id_us AS id, COALESCE(us::text, '') AS reference, sito, area, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 AS minutes_editing FROM us_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'pottery_table'::text, id_rep, id_number::text, sito, area, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM pottery_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'inventario_materiali_table'::text, id_invmat, numero_inventario::text, sito, area, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM inventario_materiali_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'tma_materiali_archeologici'::text, id, COALESCE(dscu, ''), sito, area, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM tma_materiali_archeologici WHERE editing_by IS NOT NULL
UNION ALL SELECT 'archeozoology_table'::text, id_archzoo, id_archzoo::text, sito, area, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM archeozoology_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'campioni_table'::text, id_campione, nr_campione::text, sito, area, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM campioni_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'individui_table'::text, id_scheda_ind, nr_individuo::text, sito, area, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM individui_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'tomba_table'::text, id_tomba, nr_scheda_taf::text, sito, area, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM tomba_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'periodizzazione_table'::text, id_perfas, (periodo::text || '.' || fase::text), sito, area, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM periodizzazione_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'struttura_table'::text, id_struttura, sigla_struttura, sito, ''::text, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM struttura_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'documentazione_table'::text, id_documentazione, nome_doc, sito, ''::text, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM documentazione_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'site_table'::text, id_sito, sito, sito, ''::text, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM site_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'inventario_lapidei_table'::text, id_invlap, scheda_numero::text, sito, ''::text, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM inventario_lapidei_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'deteta_table'::text, id_det_eta, id_det_eta::text, sito, ''::text, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM deteta_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'detsesso_table'::text, id_det_sesso, id_det_sesso::text, sito, ''::text, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM detsesso_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'pyarchinit_thesaurus_sigle'::text, id_thesaurus_sigle, sigla, ''::text, ''::text, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM pyarchinit_thesaurus_sigle WHERE editing_by IS NOT NULL
ORDER BY 7 DESC;

-- 4. Funzione per pulire lock vecchi (> 30 minuti)
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

-- 5. Funzioni base per gestione lock
CREATE OR REPLACE FUNCTION set_editing_lock_us(p_record_id INTEGER, p_user VARCHAR)
RETURNS void AS $$
BEGIN
    UPDATE us_table
    SET editing_by = p_user,
        editing_since = CURRENT_TIMESTAMP
    WHERE id_us = p_record_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION release_editing_lock_us(p_record_id INTEGER)
RETURNS void AS $$
BEGIN
    UPDATE us_table
    SET editing_by = NULL,
        editing_since = NULL
    WHERE id_us = p_record_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION set_editing_lock_tma(p_record_id INTEGER, p_user VARCHAR)
RETURNS void AS $$
BEGIN
    UPDATE tma_materiali_archeologici
    SET editing_by = p_user,
        editing_since = CURRENT_TIMESTAMP
    WHERE id = p_record_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION release_editing_lock_tma(p_record_id INTEGER)
RETURNS void AS $$
BEGIN
    UPDATE tma_materiali_archeologici
    SET editing_by = NULL,
        editing_since = NULL
    WHERE id = p_record_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION set_editing_lock_inv(p_record_id INTEGER, p_user VARCHAR)
RETURNS void AS $$
BEGIN
    UPDATE inventario_materiali_table
    SET editing_by = p_user,
        editing_since = CURRENT_TIMESTAMP
    WHERE id_invmat = p_record_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION release_editing_lock_inv(p_record_id INTEGER)
RETURNS void AS $$
BEGIN
    UPDATE inventario_materiali_table
    SET editing_by = NULL,
        editing_since = NULL
    WHERE id_invmat = p_record_id;
END;
$$ LANGUAGE plpgsql;

-- 6. Vista per modifiche recenti
CREATE OR REPLACE VIEW recent_changes AS
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

-- Report finale
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
    RAISE NOTICE '  4. Viste per monitoraggio attività';
    RAISE NOTICE '';
    RAISE NOTICE 'Per pulire lock vecchi eseguire:';
    RAISE NOTICE '  SELECT clean_stale_locks();';
    RAISE NOTICE '=====================================================';
END $$;