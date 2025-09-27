-- =====================================================
-- SISTEMA COMPLETO GESTIONE UTENTI E PERMESSI PYARCHINIT
-- =====================================================

-- 1. TABELLA UTENTI APPLICAZIONE
CREATE TABLE IF NOT EXISTS pyarchinit_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'archeologo', -- admin, responsabile, archeologo, guest
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    last_login TIMESTAMP,
    last_ip VARCHAR(50),
    notes TEXT
);

-- 2. TABELLA PERMESSI PER TABELLA
CREATE TABLE IF NOT EXISTS pyarchinit_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES pyarchinit_users(id) ON DELETE CASCADE,
    table_name VARCHAR(100) NOT NULL,
    can_insert BOOLEAN DEFAULT FALSE,
    can_update BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    can_view BOOLEAN DEFAULT TRUE,
    -- Filtri opzionali
    site_filter VARCHAR(100), -- Limita a specifico sito
    area_filter VARCHAR(100), -- Limita a specifica area
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    UNIQUE(user_id, table_name)
);

-- 3. TABELLA RUOLI PREDEFINITI
CREATE TABLE IF NOT EXISTS pyarchinit_roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    -- Permessi di default per il ruolo
    default_can_insert BOOLEAN DEFAULT FALSE,
    default_can_update BOOLEAN DEFAULT FALSE,
    default_can_delete BOOLEAN DEFAULT FALSE,
    default_can_view BOOLEAN DEFAULT TRUE,
    is_system_role BOOLEAN DEFAULT FALSE -- Non modificabile
);

-- 4. TABELLA LOG ACCESSI
CREATE TABLE IF NOT EXISTS pyarchinit_access_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES pyarchinit_users(id),
    username VARCHAR(50),
    action VARCHAR(50), -- login, logout, denied
    table_accessed VARCHAR(100),
    operation VARCHAR(20), -- insert, update, delete, view
    record_id INTEGER,
    ip_address VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN,
    error_message TEXT
);

-- 5. INSERISCI RUOLI PREDEFINITI
INSERT INTO pyarchinit_roles (role_name, description, default_can_insert, default_can_update, default_can_delete, default_can_view, is_system_role) VALUES
('admin', 'Amministratore - Accesso completo', TRUE, TRUE, TRUE, TRUE, TRUE),
('responsabile', 'Responsabile scavo - Può modificare tutto', TRUE, TRUE, TRUE, TRUE, FALSE),
('archeologo', 'Archeologo - Può inserire e modificare', TRUE, TRUE, FALSE, TRUE, FALSE),
('studente', 'Studente - Solo inserimento', TRUE, FALSE, FALSE, TRUE, FALSE),
('guest', 'Ospite - Solo visualizzazione', FALSE, FALSE, FALSE, TRUE, FALSE)
ON CONFLICT (role_name) DO NOTHING;

-- 6. CREA UTENTE ADMIN DI DEFAULT
INSERT INTO pyarchinit_users (username, password_hash, full_name, role, is_active, created_by) VALUES
('admin', '$2b$12$YourHashHere', 'Amministratore Sistema', 'admin', TRUE, 'system')
ON CONFLICT (username) DO NOTHING;

-- 7. FUNZIONI PER GESTIONE PERMESSI

-- Funzione per verificare permessi
CREATE OR REPLACE FUNCTION check_user_permission(
    p_username VARCHAR,
    p_table_name VARCHAR,
    p_operation VARCHAR -- insert, update, delete, view
)
RETURNS BOOLEAN AS $$
DECLARE
    v_has_permission BOOLEAN;
    v_user_role VARCHAR;
BEGIN
    -- Admin ha sempre tutti i permessi
    SELECT role INTO v_user_role
    FROM pyarchinit_users
    WHERE username = p_username AND is_active = TRUE;

    IF v_user_role = 'admin' THEN
        RETURN TRUE;
    END IF;

    -- Controlla permessi specifici per tabella
    SELECT CASE p_operation
        WHEN 'insert' THEN can_insert
        WHEN 'update' THEN can_update
        WHEN 'delete' THEN can_delete
        WHEN 'view' THEN can_view
        ELSE FALSE
    END INTO v_has_permission
    FROM pyarchinit_permissions p
    JOIN pyarchinit_users u ON p.user_id = u.id
    WHERE u.username = p_username
    AND p.table_name = p_table_name;

    -- Se non ci sono permessi specifici, usa i default del ruolo
    IF v_has_permission IS NULL THEN
        SELECT CASE p_operation
            WHEN 'insert' THEN default_can_insert
            WHEN 'update' THEN default_can_update
            WHEN 'delete' THEN default_can_delete
            WHEN 'view' THEN default_can_view
            ELSE FALSE
        END INTO v_has_permission
        FROM pyarchinit_roles r
        JOIN pyarchinit_users u ON r.role_name = u.role
        WHERE u.username = p_username;
    END IF;

    RETURN COALESCE(v_has_permission, FALSE);
END;
$$ LANGUAGE plpgsql;

-- Funzione per creare nuovo utente
CREATE OR REPLACE FUNCTION create_pyarchinit_user(
    p_username VARCHAR,
    p_password_hash VARCHAR,
    p_full_name VARCHAR,
    p_email VARCHAR,
    p_role VARCHAR,
    p_created_by VARCHAR
)
RETURNS INTEGER AS $$
DECLARE
    v_user_id INTEGER;
BEGIN
    INSERT INTO pyarchinit_users (username, password_hash, full_name, email, role, created_by)
    VALUES (p_username, p_password_hash, p_full_name, p_email, p_role, p_created_by)
    RETURNING id INTO v_user_id;

    -- Log della creazione
    INSERT INTO pyarchinit_access_log (username, action, timestamp, success)
    VALUES (p_username, 'user_created', CURRENT_TIMESTAMP, TRUE);

    RETURN v_user_id;
END;
$$ LANGUAGE plpgsql;

-- Funzione per impostare permessi
CREATE OR REPLACE FUNCTION set_user_permission(
    p_username VARCHAR,
    p_table_name VARCHAR,
    p_can_insert BOOLEAN,
    p_can_update BOOLEAN,
    p_can_delete BOOLEAN,
    p_can_view BOOLEAN,
    p_set_by VARCHAR
)
RETURNS BOOLEAN AS $$
DECLARE
    v_user_id INTEGER;
BEGIN
    SELECT id INTO v_user_id FROM pyarchinit_users WHERE username = p_username;

    IF v_user_id IS NULL THEN
        RETURN FALSE;
    END IF;

    INSERT INTO pyarchinit_permissions (
        user_id, table_name, can_insert, can_update, can_delete, can_view, created_by
    ) VALUES (
        v_user_id, p_table_name, p_can_insert, p_can_update, p_can_delete, p_can_view, p_set_by
    )
    ON CONFLICT (user_id, table_name) DO UPDATE SET
        can_insert = EXCLUDED.can_insert,
        can_update = EXCLUDED.can_update,
        can_delete = EXCLUDED.can_delete,
        can_view = EXCLUDED.can_view,
        created_by = EXCLUDED.created_by;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 8. TRIGGER PER APPLICARE PERMESSI

-- Trigger per verificare permessi prima di INSERT
CREATE OR REPLACE FUNCTION enforce_insert_permission()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT check_user_permission(current_user, TG_TABLE_NAME, 'insert') THEN
        RAISE EXCEPTION 'Permesso negato: non puoi inserire in %', TG_TABLE_NAME;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger per verificare permessi prima di UPDATE
CREATE OR REPLACE FUNCTION enforce_update_permission()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT check_user_permission(current_user, TG_TABLE_NAME, 'update') THEN
        RAISE EXCEPTION 'Permesso negato: non puoi modificare in %', TG_TABLE_NAME;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger per verificare permessi prima di DELETE
CREATE OR REPLACE FUNCTION enforce_delete_permission()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT check_user_permission(current_user, TG_TABLE_NAME, 'delete') THEN
        RAISE EXCEPTION 'Permesso negato: non puoi eliminare da %', TG_TABLE_NAME;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- 9. VISTE PER GESTIONE

-- Vista utenti attivi
CREATE OR REPLACE VIEW active_users_view AS
SELECT
    u.id,
    u.username,
    u.full_name,
    u.email,
    u.role,
    r.description as role_description,
    u.last_login,
    u.is_active,
    COUNT(DISTINCT p.table_name) as custom_permissions_count
FROM pyarchinit_users u
LEFT JOIN pyarchinit_roles r ON u.role = r.role_name
LEFT JOIN pyarchinit_permissions p ON u.id = p.user_id
WHERE u.is_active = TRUE
GROUP BY u.id, u.username, u.full_name, u.email, u.role, r.description, u.last_login, u.is_active;

-- Vista permessi per utente
CREATE OR REPLACE VIEW user_permissions_view AS
SELECT
    u.username,
    u.full_name,
    u.role,
    COALESCE(p.table_name, t.tablename) as table_name,
    COALESCE(p.can_insert, r.default_can_insert) as can_insert,
    COALESCE(p.can_update, r.default_can_update) as can_update,
    COALESCE(p.can_delete, r.default_can_delete) as can_delete,
    COALESCE(p.can_view, r.default_can_view) as can_view,
    CASE
        WHEN p.id IS NOT NULL THEN 'Personalizzato'
        ELSE 'Default ruolo'
    END as permission_type
FROM pyarchinit_users u
JOIN pyarchinit_roles r ON u.role = r.role_name
CROSS JOIN (
    SELECT tablename FROM pg_tables
    WHERE schemaname = 'public'
    AND tablename LIKE '%_table%'
) t
LEFT JOIN pyarchinit_permissions p ON u.id = p.user_id AND p.table_name = t.tablename
WHERE u.is_active = TRUE
ORDER BY u.username, t.tablename;

-- 10. FUNZIONI PER ADMIN DASHBOARD

-- Statistiche accessi
CREATE OR REPLACE FUNCTION get_access_statistics(p_days INTEGER DEFAULT 7)
RETURNS TABLE(
    stat_date DATE,
    total_logins INTEGER,
    unique_users INTEGER,
    failed_attempts INTEGER,
    operations_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        DATE(timestamp) as stat_date,
        COUNT(CASE WHEN action = 'login' AND success = TRUE THEN 1 END)::INTEGER as total_logins,
        COUNT(DISTINCT CASE WHEN success = TRUE THEN username END)::INTEGER as unique_users,
        COUNT(CASE WHEN success = FALSE THEN 1 END)::INTEGER as failed_attempts,
        COUNT(CASE WHEN operation IS NOT NULL THEN 1 END)::INTEGER as operations_count
    FROM pyarchinit_access_log
    WHERE timestamp > CURRENT_DATE - p_days
    GROUP BY DATE(timestamp)
    ORDER BY stat_date DESC;
END;
$$ LANGUAGE plpgsql;

-- Report permessi utente
CREATE OR REPLACE FUNCTION get_user_permissions_report(p_username VARCHAR)
RETURNS TABLE(
    table_name VARCHAR,
    can_insert BOOLEAN,
    can_update BOOLEAN,
    can_delete BOOLEAN,
    can_view BOOLEAN,
    is_custom BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COALESCE(p.table_name, t.tablename)::VARCHAR,
        COALESCE(p.can_insert, r.default_can_insert),
        COALESCE(p.can_update, r.default_can_update),
        COALESCE(p.can_delete, r.default_can_delete),
        COALESCE(p.can_view, r.default_can_view),
        (p.id IS NOT NULL) as is_custom
    FROM pyarchinit_users u
    JOIN pyarchinit_roles r ON u.role = r.role_name
    CROSS JOIN (
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
        AND tablename LIKE '%_table%'
    ) t
    LEFT JOIN pyarchinit_permissions p ON u.id = p.user_id AND p.table_name = t.tablename
    WHERE u.username = p_username
    ORDER BY t.tablename;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE '✅ SISTEMA GESTIONE UTENTI INSTALLATO';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Tabelle create:';
    RAISE NOTICE '  - pyarchinit_users: utenti applicazione';
    RAISE NOTICE '  - pyarchinit_permissions: permessi per tabella';
    RAISE NOTICE '  - pyarchinit_roles: ruoli predefiniti';
    RAISE NOTICE '  - pyarchinit_access_log: log accessi';
    RAISE NOTICE '';
    RAISE NOTICE 'Ruoli disponibili:';
    RAISE NOTICE '  - admin: accesso completo';
    RAISE NOTICE '  - responsabile: può modificare tutto';
    RAISE NOTICE '  - archeologo: inserisce e modifica';
    RAISE NOTICE '  - studente: solo inserimento';
    RAISE NOTICE '  - guest: solo lettura';
    RAISE NOTICE '';
    RAISE NOTICE '⚠️ IMPORTANTE: Cambiare password admin di default!';
    RAISE NOTICE '=====================================================';
END $$;