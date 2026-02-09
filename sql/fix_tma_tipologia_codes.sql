-- Script to fix TMA tipologia_sigla codes in pyarchinit_thesaurus_sigle table
-- According to the correct schema

-- Backup the table first (if needed)
-- CREATE TABLE pyarchinit_thesaurus_sigle_backup AS SELECT * FROM pyarchinit_thesaurus_sigle;

-- Update tipologia_sigla codes for 'tma_materiali_archeologici' and 'tma_materiali_ripetibili'

-- First, let's see what we have
SELECT nome_tabella, tipologia_sigla, sigla_estesa, COUNT(*) as count
FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici', 'tma_materiali_ripetibili', 'TMA materiali ripetibili')
GROUP BY nome_tabella, tipologia_sigla, sigla_estesa
ORDER BY nome_tabella, tipologia_sigla;

-- Update the tipologia_sigla based on sigla_estesa
-- For tma_materiali_archeologici

UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.1'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND LOWER(sigla_estesa) LIKE '%denominazione collocazione%';

UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.2'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND LOWER(sigla_estesa) LIKE '%saggio%';

UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.3'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND (LOWER(sigla_estesa) LIKE '%località%' OR LOWER(sigla_estesa) LIKE '%localita%');

UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.4'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici' OR 
       nome_tabella = 'tma_materiali_ripetibili' OR nome_tabella = 'TMA materiali ripetibili')
AND LOWER(sigla_estesa) LIKE '%materiale%' AND LOWER(sigla_estesa) NOT LIKE '%categoria%';

UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.5'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici' OR 
       nome_tabella = 'tma_materiali_ripetibili' OR nome_tabella = 'TMA materiali ripetibili')
AND LOWER(sigla_estesa) LIKE '%categoria%';

UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.6'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici' OR 
       nome_tabella = 'tma_materiali_ripetibili' OR nome_tabella = 'TMA materiali ripetibili')
AND LOWER(sigla_estesa) LIKE '%classe%';

UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.7'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND LOWER(sigla_estesa) LIKE '%area%';

UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.8'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici' OR 
       nome_tabella = 'tma_materiali_ripetibili' OR nome_tabella = 'TMA materiali ripetibili')
AND (LOWER(sigla_estesa) LIKE '%precisazione tipologica%' OR LOWER(sigla_estesa) LIKE '%prec%tipologica%');

UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.9'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici' OR 
       nome_tabella = 'tma_materiali_ripetibili' OR nome_tabella = 'TMA materiali ripetibili')
AND LOWER(sigla_estesa) LIKE '%definizione%';

UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.10'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND LOWER(sigla_estesa) LIKE '%tipo collocazione%';

UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.11'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND LOWER(sigla_estesa) LIKE '%tipo foto%';

UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.12'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND LOWER(sigla_estesa) LIKE '%tipo disegno%' AND LOWER(sigla_estesa) NOT LIKE '%autore%';

UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.13'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND (LOWER(sigla_estesa) LIKE '%tipo disegno autore%' OR LOWER(sigla_estesa) LIKE '%disegno%autore%');

UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.14'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND LOWER(sigla_estesa) LIKE '%tipologia acquisizione%';

UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.15'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND LOWER(sigla_estesa) LIKE '%settore%';

UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.16'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici' OR 
       nome_tabella = 'tma_materiali_ripetibili' OR nome_tabella = 'TMA materiali ripetibili')
AND LOWER(sigla_estesa) LIKE '%cronologia%';

-- Verify the updates
SELECT nome_tabella, tipologia_sigla, sigla_estesa, COUNT(*) as count
FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici', 'tma_materiali_ripetibili', 'TMA materiali ripetibili')
GROUP BY nome_tabella, tipologia_sigla, sigla_estesa
ORDER BY nome_tabella, CAST(SUBSTR(tipologia_sigla, 4) AS INTEGER);