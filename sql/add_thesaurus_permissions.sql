-- Add permissions for pyarchinit_thesaurus_sigle table
-- Run this script as postgres superuser

-- Grant to admin role (full access)
GRANT ALL PRIVILEGES ON pyarchinit_thesaurus_sigle TO admin;
GRANT USAGE, SELECT ON SEQUENCE pyarchinit_thesaurus_sigle_id_seq TO admin;

-- Grant to editor1/responsabile role (view, insert, update)
GRANT SELECT, INSERT, UPDATE ON pyarchinit_thesaurus_sigle TO editor1;
GRANT USAGE, SELECT ON SEQUENCE pyarchinit_thesaurus_sigle_id_seq TO editor1;

-- Grant to st1/studente role (view, insert)
GRANT SELECT, INSERT ON pyarchinit_thesaurus_sigle TO st1;
GRANT USAGE, SELECT ON SEQUENCE pyarchinit_thesaurus_sigle_id_seq TO st1;

-- Grant to guest role (view only)
GRANT SELECT ON pyarchinit_thesaurus_sigle TO guest;

-- Also add default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO guest;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT ON TABLES TO st1;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO editor1;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO admin;

-- Message
DO $$
BEGIN
    RAISE NOTICE 'Permissions for pyarchinit_thesaurus_sigle have been updated';
END $$;
