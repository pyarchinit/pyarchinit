-- Crea tabella ruoli e popola con ruoli predefiniti
CREATE TABLE IF NOT EXISTS pyarchinit_roles (
    role_name VARCHAR(50) PRIMARY KEY,
    description TEXT,
    default_can_view BOOLEAN DEFAULT TRUE,
    default_can_insert BOOLEAN DEFAULT FALSE,
    default_can_update BOOLEAN DEFAULT FALSE,
    default_can_delete BOOLEAN DEFAULT FALSE,
    is_system_role BOOLEAN DEFAULT TRUE
);

-- Inserisci ruoli predefiniti se non esistono
INSERT INTO pyarchinit_roles (role_name, description, default_can_view, default_can_insert, default_can_update, default_can_delete, is_system_role)
VALUES
    ('admin', 'Amministratore completo del sistema', TRUE, TRUE, TRUE, TRUE, TRUE),
    ('responsabile', 'Responsabile di scavo', TRUE, TRUE, TRUE, FALSE, TRUE),
    ('archeologo', 'Archeologo/Operatore', TRUE, TRUE, FALSE, FALSE, TRUE),
    ('studente', 'Studente/Tirocinante', TRUE, FALSE, FALSE, FALSE, TRUE),
    ('guest', 'Ospite solo lettura', TRUE, FALSE, FALSE, FALSE, TRUE)
ON CONFLICT (role_name) DO NOTHING;

-- Report
DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count FROM pyarchinit_roles;
    RAISE NOTICE 'Ruoli nel sistema: %', v_count;
END $$;