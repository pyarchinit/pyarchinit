-- Script per aggiornare il database di produzione con tutte le modifiche necessarie
-- Eseguire questi comandi sul database reale

-- 1. CORREZIONE CAMPO QUOTA (da min/max a singolo campo)
-- Rimuovi i campi quota_min_usm e quota_max_usm se esistono
ALTER TABLE inventario_materiali_table
DROP COLUMN IF EXISTS quota_min_usm CASCADE,
DROP COLUMN IF EXISTS quota_max_usm CASCADE;

-- Aggiungi il campo quota singolo e unità di misura
ALTER TABLE inventario_materiali_table
ADD COLUMN IF NOT EXISTS quota_usm FLOAT,
ADD COLUMN IF NOT EXISTS unita_misura_quota VARCHAR(20) DEFAULT 'm s.l.m.';

-- 2. SISTEMA DI CONCORRENZA - Aggiungi campi per gestione concorrenza a TUTTE le tabelle
-- Per ogni tabella archeologica, aggiungi i campi di concorrenza

-- US table (nota: us_table_usm non esiste)
ALTER TABLE us_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Site table
ALTER TABLE site_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Periodizzazione table
ALTER TABLE periodizzazione_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Inventario materiali table
ALTER TABLE inventario_materiali_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Struttura table
ALTER TABLE struttura_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Tomba table
ALTER TABLE tomba_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Individui table
ALTER TABLE individui_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Campioni table
ALTER TABLE campioni_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Documentazione table
ALTER TABLE documentazione_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Detsesso table
ALTER TABLE detsesso_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Deteta table
ALTER TABLE deteta_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Archeozoology table
ALTER TABLE archeozoology_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- Pottery table
ALTER TABLE pottery_table
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

-- TMA table
ALTER TABLE tma_materiali_archeologici
ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP,
ADD COLUMN IF NOT EXISTS audit_trail JSONB DEFAULT '[]'::jsonb;

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
    full_name VARCHAR(255)
);

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

-- 4. PREVENZIONE DUPLICATI TMA
-- Rimuovi eventuali duplicati esistenti (mantiene il record con ID più basso)
DELETE FROM tma_materiali_archeologici a
WHERE EXISTS (
    SELECT 1
    FROM tma_materiali_archeologici b
    WHERE a.sito = b.sito
    AND a.area = b.area
    AND a.inventario = b.inventario
    AND a.dscu = b.dscu
    AND a.id > b.id
    AND a.inventario IS NOT NULL
    AND a.inventario != ''
);

-- Aggiungi indice univoco per prevenire duplicati futuri
CREATE UNIQUE INDEX IF NOT EXISTS idx_tma_unique_record
ON tma_materiali_archeologici(sito, area, inventario, dscu)
WHERE inventario IS NOT NULL AND inventario != '';

-- Aggiungi indice su created_at per performance
CREATE INDEX IF NOT EXISTS idx_tma_created_at
ON tma_materiali_archeologici(created_at);

-- Trigger per prevenire inserimenti rapidi duplicati (entro 2 secondi)
CREATE OR REPLACE FUNCTION prevent_rapid_tma_insert()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM tma_materiali_archeologici
        WHERE sito = NEW.sito
        AND area = NEW.area
        AND (inventario = NEW.inventario OR dscu = NEW.dscu)
        AND created_at > NOW() - INTERVAL '2 seconds'
        AND id != COALESCE(NEW.id, -1)
    ) THEN
        RAISE EXCEPTION 'Un record simile è stato inserito di recente. Attendere prima di inserire di nuovo.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trig_prevent_rapid_tma_insert ON tma_materiali_archeologici;
CREATE TRIGGER trig_prevent_rapid_tma_insert
BEFORE INSERT ON tma_materiali_archeologici
FOR EACH ROW
EXECUTE FUNCTION prevent_rapid_tma_insert();

-- Trigger per aggiornare automaticamente i timestamp
CREATE OR REPLACE FUNCTION update_tma_timestamps()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        NEW.created_at = COALESCE(NEW.created_at, NOW());
        NEW.updated_at = NOW();
    ELSIF TG_OP = 'UPDATE' THEN
        NEW.updated_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trig_update_tma_timestamps ON tma_materiali_archeologici;
CREATE TRIGGER trig_update_tma_timestamps
BEFORE INSERT OR UPDATE ON tma_materiali_archeologici
FOR EACH ROW
EXECUTE FUNCTION update_tma_timestamps();

-- 5. INDICI PER PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_us_version ON us_table(version_number);
CREATE INDEX IF NOT EXISTS idx_us_editing_by ON us_table(editing_by);
CREATE INDEX IF NOT EXISTS idx_site_version ON site_table(version_number);
CREATE INDEX IF NOT EXISTS idx_inventario_version ON inventario_materiali_table(version_number);
CREATE INDEX IF NOT EXISTS idx_activity_log_timestamp ON pyarchinit_activity_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_activity_log_username ON pyarchinit_activity_log(username);

-- 6. AGGIORNA LA VIEW pyarchinit_reperti_view per includere il nuovo campo quota
-- Prima droppa la view esistente se esiste
DROP VIEW IF EXISTS pyarchinit_reperti_view;

-- Ricrea la view con il nuovo campo quota_usm
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
    quadrato,
    coord_x,
    coord_y,
    coord_z,
    reperto_doc,
    oggetto,
    stato_oss,
    oss,
    data,
    schedatore,
    disegnatore,
    anno,
    fase_us,
    sezione,
    periodo_iniziale,
    fase_iniziale,
    periodo_finale,
    fase_finale,
    quota_usm,                     -- Nuovo campo quota singolo
    unita_misura_quota,            -- Nuovo campo unità di misura
    the_geom,
    residuo,
    datazione
FROM inventario_materiali_table;

-- Messaggio finale
DO $$
BEGIN
    RAISE NOTICE 'Aggiornamento database completato con successo!';
    RAISE NOTICE 'Modifiche applicate:';
    RAISE NOTICE '1. Campo quota corretto (da min/max a singolo)';
    RAISE NOTICE '2. Sistema di concorrenza aggiunto a tutte le tabelle';
    RAISE NOTICE '3. Tabelle gestione utenti create';
    RAISE NOTICE '4. Protezione duplicati TMA implementata';
    RAISE NOTICE '5. Indici di performance aggiunti';
    RAISE NOTICE '6. View pyarchinit_reperti_view aggiornata';
END $$;