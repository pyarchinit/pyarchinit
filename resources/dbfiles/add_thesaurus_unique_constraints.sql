-- Add UNIQUE constraints to pyarchinit_thesaurus_sigle table
-- This prevents duplicates during import/export operations

-- First, add lingua column if it doesn't exist (for older databases)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                   AND table_name = 'pyarchinit_thesaurus_sigle'
                   AND column_name = 'lingua') THEN
        ALTER TABLE public.pyarchinit_thesaurus_sigle
        ADD COLUMN lingua character varying(10) DEFAULT 'it';
    END IF;
END $$;

-- Add n_tipologia and n_sigla columns if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                   AND table_name = 'pyarchinit_thesaurus_sigle'
                   AND column_name = 'n_tipologia') THEN
        ALTER TABLE public.pyarchinit_thesaurus_sigle
        ADD COLUMN n_tipologia integer;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                   AND table_name = 'pyarchinit_thesaurus_sigle'
                   AND column_name = 'n_sigla') THEN
        ALTER TABLE public.pyarchinit_thesaurus_sigle
        ADD COLUMN n_sigla integer;
    END IF;
END $$;

-- Drop existing constraint if it exists (to allow re-running this script)
ALTER TABLE public.pyarchinit_thesaurus_sigle
DROP CONSTRAINT IF EXISTS thesaurus_unique_key;

ALTER TABLE public.pyarchinit_thesaurus_sigle
DROP CONSTRAINT IF EXISTS thesaurus_unique_sigla_estesa;

ALTER TABLE public.pyarchinit_thesaurus_sigle
DROP CONSTRAINT IF EXISTS thesaurus_unique_sigla;

-- Add UNIQUE constraint for the main key (lingua, nome_tabella, tipologia_sigla, sigla_estesa)
-- This is the most important one - prevents duplicate entries
ALTER TABLE public.pyarchinit_thesaurus_sigle
ADD CONSTRAINT thesaurus_unique_key
UNIQUE (lingua, nome_tabella, tipologia_sigla, sigla_estesa);

-- Add UNIQUE constraint for sigla within same context
-- This prevents same abbreviation being used twice in same table/type/language
ALTER TABLE public.pyarchinit_thesaurus_sigle
ADD CONSTRAINT thesaurus_unique_sigla
UNIQUE (lingua, nome_tabella, tipologia_sigla, sigla);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_thesaurus_lingua
ON public.pyarchinit_thesaurus_sigle(lingua);

CREATE INDEX IF NOT EXISTS idx_thesaurus_nome_tabella
ON public.pyarchinit_thesaurus_sigle(nome_tabella);

CREATE INDEX IF NOT EXISTS idx_thesaurus_tipologia_sigla
ON public.pyarchinit_thesaurus_sigle(tipologia_sigla);

CREATE INDEX IF NOT EXISTS idx_thesaurus_composite
ON public.pyarchinit_thesaurus_sigle(lingua, nome_tabella, tipologia_sigla);

-- Add comment to table explaining the constraints
COMMENT ON TABLE public.pyarchinit_thesaurus_sigle IS
'Thesaurus table with unique constraints on (lingua, nome_tabella, tipologia_sigla, sigla_estesa) to prevent duplicates during import';

-- SQLite version (save this as add_thesaurus_unique_constraints_sqlite.sql)
-- For SQLite we need to recreate the table with constraints

/*
-- For SQLite:
CREATE TABLE IF NOT EXISTS pyarchinit_thesaurus_sigle_new (
    id_thesaurus_sigle INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_tabella TEXT,
    sigla TEXT,
    sigla_estesa TEXT,
    descrizione TEXT,
    tipologia_sigla TEXT,
    lingua TEXT DEFAULT 'it',
    n_tipologia INTEGER,
    n_sigla INTEGER,
    UNIQUE(lingua, nome_tabella, tipologia_sigla, sigla_estesa),
    UNIQUE(lingua, nome_tabella, tipologia_sigla, sigla)
);

-- Copy data from old table
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle_new
SELECT * FROM pyarchinit_thesaurus_sigle;

-- Drop old table and rename new one
DROP TABLE pyarchinit_thesaurus_sigle;
ALTER TABLE pyarchinit_thesaurus_sigle_new RENAME TO pyarchinit_thesaurus_sigle;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_thesaurus_lingua
ON pyarchinit_thesaurus_sigle(lingua);

CREATE INDEX IF NOT EXISTS idx_thesaurus_nome_tabella
ON pyarchinit_thesaurus_sigle(nome_tabella);

CREATE INDEX IF NOT EXISTS idx_thesaurus_tipologia_sigla
ON pyarchinit_thesaurus_sigle(tipologia_sigla);

CREATE INDEX IF NOT EXISTS idx_thesaurus_composite
ON pyarchinit_thesaurus_sigle(lingua, nome_tabella, tipologia_sigla);
*/