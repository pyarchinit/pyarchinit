
-- Script per aggiornare la lunghezza del campo sigla in PostgreSQL
-- Esegui questo script nel tuo database PostgreSQL

-- Aggiorna la lunghezza del campo sigla
ALTER TABLE pyarchinit_thesaurus_sigle 
ALTER COLUMN sigla TYPE VARCHAR(100);

-- Aggiorna anche parent_sigla se esiste
ALTER TABLE pyarchinit_thesaurus_sigle 
ALTER COLUMN parent_sigla TYPE VARCHAR(100);

-- Verifica
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'pyarchinit_thesaurus_sigle'
AND column_name IN ('sigla', 'parent_sigla');
