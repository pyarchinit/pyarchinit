-- Script per aggiungere le colonne mancanti n_tipologia e n_sigla
-- alla tabella pyarchinit_thesaurus_sigle in PostgreSQL

-- Aggiungi colonna n_tipologia se non esiste
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                   AND table_name = 'pyarchinit_thesaurus_sigle'
                   AND column_name = 'n_tipologia') THEN
        ALTER TABLE public.pyarchinit_thesaurus_sigle
        ADD COLUMN n_tipologia integer;

        RAISE NOTICE 'Colonna n_tipologia aggiunta con successo';
    ELSE
        RAISE NOTICE 'Colonna n_tipologia già esistente';
    END IF;
END $$;

-- Aggiungi colonna n_sigla se non esiste
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                   AND table_name = 'pyarchinit_thesaurus_sigle'
                   AND column_name = 'n_sigla') THEN
        ALTER TABLE public.pyarchinit_thesaurus_sigle
        ADD COLUMN n_sigla integer;

        RAISE NOTICE 'Colonna n_sigla aggiunta con successo';
    ELSE
        RAISE NOTICE 'Colonna n_sigla già esistente';
    END IF;
END $$;

-- Verifica che le colonne siano state aggiunte
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'pyarchinit_thesaurus_sigle'
AND column_name IN ('n_tipologia', 'n_sigla');