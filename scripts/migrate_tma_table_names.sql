-- Migration script to update TMA table names from database names to friendly names
-- This ensures backward compatibility while using user-friendly names in the UI

-- Update existing entries from tma_table to TMA materiali archeologici
UPDATE pyarchinit_thesaurus_sigle 
SET nome_tabella = 'TMA materiali archeologici'
WHERE nome_tabella = 'tma_table';

-- Update existing entries from tma_materiali_table to TMA Materiali Ripetibili
UPDATE pyarchinit_thesaurus_sigle 
SET nome_tabella = 'TMA Materiali Ripetibili'
WHERE nome_tabella = 'tma_materiali_table';

-- Also update the old incorrect names if they exist
UPDATE pyarchinit_thesaurus_sigle 
SET nome_tabella = 'TMA materiali archeologici'
WHERE nome_tabella = 'tma_materiali_archeologici';

UPDATE pyarchinit_thesaurus_sigle 
SET nome_tabella = 'TMA Materiali Ripetibili'
WHERE nome_tabella = 'tma_materiali_ripetibili';

-- Update lowercase version to correct case
UPDATE pyarchinit_thesaurus_sigle 
SET nome_tabella = 'TMA Materiali Ripetibili'
WHERE nome_tabella = 'TMA materiali ripetibili';

-- Update the pyarchinit_nome_tabelle entries
UPDATE pyarchinit_thesaurus_sigle 
SET sigla_estesa = 'TMA materiali archeologici'
WHERE nome_tabella = 'pyarchinit_nome_tabelle' 
AND sigla = '27';

UPDATE pyarchinit_thesaurus_sigle 
SET sigla_estesa = 'TMA Materiali Ripetibili'
WHERE nome_tabella = 'pyarchinit_nome_tabelle' 
AND sigla = '28';

-- Verify the migration
SELECT 'Updated records for TMA materiali archeologici:' as status, COUNT(*) as count
FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella = 'TMA materiali archeologici'
UNION ALL
SELECT 'Updated records for TMA Materiali Ripetibili:' as status, COUNT(*) as count
FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella = 'TMA Materiali Ripetibili';