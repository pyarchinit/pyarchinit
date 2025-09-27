-- Fix delle tabelle utenti per gestione completa
-- Aggiunge campi mancanti e corregge struttura

-- 1. Aggiungi campi mancanti a pyarchinit_users
ALTER TABLE pyarchinit_users
ADD COLUMN IF NOT EXISTS notes TEXT,
ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);

-- 2. Crea funzione per inizializzare tabelle se non esistono
CREATE OR REPLACE FUNCTION initialize_user_tables()
RETURNS void AS $$
BEGIN
    -- Crea tabella utenti se non esiste
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

    -- Crea tabella permessi se non esiste
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

    -- Crea tabella activity log se non esiste
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

    -- Crea indici
    CREATE INDEX IF NOT EXISTS idx_activity_log_timestamp ON pyarchinit_activity_log(timestamp DESC);
    CREATE INDEX IF NOT EXISTS idx_activity_log_username ON pyarchinit_activity_log(username);
    CREATE INDEX IF NOT EXISTS idx_permissions_user ON pyarchinit_permissions(user_id);
END;
$$ LANGUAGE plpgsql;

-- Esegui inizializzazione
SELECT initialize_user_tables();

-- 3. Inserisci utente admin di default se non esiste
INSERT INTO pyarchinit_users (username, password_hash, role, full_name, email, is_active, notes)
VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin', 'Amministratore', 'admin@pyarchinit.it', true, 'Utente amministratore di default')
ON CONFLICT (username) DO NOTHING;

-- Password di default per admin è 'admin' (SHA256)

-- 4. Crea funzione per gestire permessi di default
CREATE OR REPLACE FUNCTION set_default_permissions(p_user_id INTEGER, p_role VARCHAR)
RETURNS void AS $$
DECLARE
    v_table_name VARCHAR;
    v_tables VARCHAR[] := ARRAY[
        'us_table', 'tma_materiali_archeologici', 'inventario_materiali_table',
        'site_table', 'periodizzazione_table', 'struttura_table', 'tomba_table',
        'individui_table', 'campioni_table', 'documentazione_table',
        'detsesso_table', 'deteta_table', 'archeozoology_table', 'pottery_table'
    ];
BEGIN
    -- Rimuovi permessi esistenti
    DELETE FROM pyarchinit_permissions WHERE user_id = p_user_id;

    -- Aggiungi permessi basati sul ruolo
    FOREACH v_table_name IN ARRAY v_tables
    LOOP
        INSERT INTO pyarchinit_permissions (user_id, table_name, can_view, can_insert, can_update, can_delete)
        VALUES (
            p_user_id,
            v_table_name,
            TRUE,  -- Tutti possono visualizzare
            CASE WHEN p_role IN ('admin', 'responsabile', 'archeologo') THEN TRUE ELSE FALSE END,
            CASE WHEN p_role IN ('admin', 'responsabile') THEN TRUE ELSE FALSE END,
            CASE WHEN p_role = 'admin' THEN TRUE ELSE FALSE END
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 5. Report finale
DO $$
DECLARE
    v_user_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_user_count FROM pyarchinit_users;

    RAISE NOTICE '';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE '✅ SISTEMA GESTIONE UTENTI CONFIGURATO';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE 'Utenti nel sistema: %', v_user_count;
    RAISE NOTICE '';
    RAISE NOTICE 'Per aggiungere un nuovo utente:';
    RAISE NOTICE '  1. Usa il dialog Gestione Utenti in PyArchInit';
    RAISE NOTICE '  2. Oppure usa SQL direttamente';
    RAISE NOTICE '';
    RAISE NOTICE 'Utente admin di default:';
    RAISE NOTICE '  Username: admin';
    RAISE NOTICE '  Password: admin';
    RAISE NOTICE '  (Cambiare la password al primo accesso!)';
    RAISE NOTICE '=====================================================';
END $$;