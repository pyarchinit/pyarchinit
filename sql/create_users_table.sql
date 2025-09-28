-- Creazione tabella utenti PyArchInit
CREATE TABLE IF NOT EXISTS pyarchinit_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    full_name VARCHAR(200),
    email VARCHAR(200),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Inserisci utente admin di default (password: admin123)
-- La password dovrebbe essere hashata, ma per ora mettiamo un placeholder
INSERT INTO pyarchinit_users (username, password_hash, role, full_name, email)
VALUES
    ('admin', 'admin123', 'administrator', 'Administrator', 'admin@pyarchinit.org'),
    ('postgres', 'postgres', 'administrator', 'PostgreSQL Admin', 'postgres@pyarchinit.org')
ON CONFLICT (username) DO NOTHING;

-- Crea tabella gruppi/ruoli
CREATE TABLE IF NOT EXISTS pyarchinit_roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions TEXT
);

-- Inserisci ruoli di default
INSERT INTO pyarchinit_roles (role_name, description) VALUES
    ('administrator', 'Full system access'),
    ('responsabile', 'Site manager with full data access'),
    ('archeologo', 'Archaeologist with data entry and edit permissions'),
    ('studente', 'Student with limited edit permissions'),
    ('guest', 'Read-only access')
ON CONFLICT (role_name) DO NOTHING;