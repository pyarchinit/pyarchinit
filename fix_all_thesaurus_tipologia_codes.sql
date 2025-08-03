-- Fix all wrong tipologia_sigla codes in the thesaurus table
-- Based on the correct schema provided by the user

-- First, let's see what we have with wrong codes
SELECT 'Current wrong codes:' as info;
SELECT tipologia_sigla, COUNT(*) as count, MIN(sigla_estesa) as example
FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici')
AND tipologia_sigla IN ('10.18', '10.19')
GROUP BY tipologia_sigla;

-- Fix località: 10.18 → 10.3
UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.3'
WHERE nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici')
AND tipologia_sigla = '10.18';

SELECT 'Fixed località from 10.18 to 10.3' as status;

-- Fix settore: 10.19 → 10.15
UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.15'
WHERE nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici')
AND tipologia_sigla = '10.19';

SELECT 'Fixed settore from 10.19 to 10.15' as status;

-- Also fix for tma_materiali_ripetibili table if exists
UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.3'
WHERE nome_tabella = 'tma_materiali_ripetibili'
AND tipologia_sigla = '10.18';

UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.15'
WHERE nome_tabella = 'tma_materiali_ripetibili'
AND tipologia_sigla = '10.19';

-- Verify the correct schema is now in place
SELECT 'Final verification:' as info;
SELECT tipologia_sigla, 
       CASE tipologia_sigla
           WHEN '10.1' THEN 'Denominazione collocazione (ldcn)'
           WHEN '10.2' THEN 'Saggio'
           WHEN '10.3' THEN 'Località'
           WHEN '10.4' THEN 'Materiale'
           WHEN '10.5' THEN 'Categoria'
           WHEN '10.6' THEN 'Classe'
           WHEN '10.7' THEN 'Area'
           WHEN '10.8' THEN 'Precisazione tipologica'
           WHEN '10.9' THEN 'Definizione'
           WHEN '10.10' THEN 'Tipologia collocazione (ldct)'
           WHEN '10.11' THEN 'Tipo foto (ftap)'
           WHEN '10.12' THEN 'Tipo disegno (drat)'
           WHEN '10.13' THEN 'Tipo disegno autore (drau)'
           WHEN '10.14' THEN 'Tipologia acquisizione (aint)'
           WHEN '10.15' THEN 'Settore'
           WHEN '10.16' THEN 'Cronologia (dtzg)'
           ELSE 'UNKNOWN - SHOULD NOT EXIST!'
       END as field_type,
       COUNT(*) as count
FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici')
GROUP BY tipologia_sigla
ORDER BY CAST(SUBSTR(tipologia_sigla, 4) AS INTEGER);

-- Check if any 10.17, 10.18, 10.19 still exist (they shouldn't)
SELECT 'Checking for invalid codes that should not exist:' as info;
SELECT tipologia_sigla, COUNT(*) as count
FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici', 'tma_materiali_ripetibili')
AND CAST(SUBSTR(tipologia_sigla, 4) AS INTEGER) > 16
GROUP BY tipologia_sigla;

-- Check hierarchy relationships for località → area → settore
SELECT 'Checking hierarchy (should show località->area and area->settore):' as info;
SELECT 
    child.tipologia_sigla as child_type,
    parent.tipologia_sigla as parent_type,
    COUNT(*) as relationships
FROM pyarchinit_thesaurus_sigle child
LEFT JOIN pyarchinit_thesaurus_sigle parent ON child.id_parent = parent.id_thesaurus_sigle
WHERE child.nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici')
AND child.id_parent IS NOT NULL
GROUP BY child.tipologia_sigla, parent.tipologia_sigla;