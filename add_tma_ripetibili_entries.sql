-- Add entries for tma_materiali_ripetibili table

-- First check what exists
SELECT nome_tabella, tipologia_sigla, COUNT(*) as count
FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella IN ('tma_materiali_ripetibili', 'TMA materiali ripetibili')
GROUP BY nome_tabella, tipologia_sigla;

-- Add entries for tma_materiali_ripetibili
-- 10.4 Materiale (same as tma_materiali_archeologici)
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'tma_materiali_ripetibili', sigla, sigla_estesa, descrizione, tipologia_sigla, lingua
FROM pyarchinit_thesaurus_sigle
WHERE nome_tabella = 'tma_materiali_archeologici' AND tipologia_sigla = '10.4';

-- 10.5 Categoria (same as tma_materiali_archeologici)
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'tma_materiali_ripetibili', sigla, sigla_estesa, descrizione, tipologia_sigla, lingua
FROM pyarchinit_thesaurus_sigle
WHERE nome_tabella = 'tma_materiali_archeologici' AND tipologia_sigla = '10.5';

-- 10.6 Classe (same as tma_materiali_archeologici)
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'tma_materiali_ripetibili', sigla, sigla_estesa, descrizione, tipologia_sigla, lingua
FROM pyarchinit_thesaurus_sigle
WHERE nome_tabella = 'tma_materiali_archeologici' AND tipologia_sigla = '10.6';

-- 10.8 Precisazione tipologica (same as tma_materiali_archeologici)
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'tma_materiali_ripetibili', sigla, sigla_estesa, descrizione, tipologia_sigla, lingua
FROM pyarchinit_thesaurus_sigle
WHERE nome_tabella = 'tma_materiali_archeologici' AND tipologia_sigla = '10.8';

-- 10.9 Definizione (same as tma_materiali_archeologici)
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'tma_materiali_ripetibili', sigla, sigla_estesa, descrizione, tipologia_sigla, lingua
FROM pyarchinit_thesaurus_sigle
WHERE nome_tabella = 'tma_materiali_archeologici' AND tipologia_sigla = '10.9';

-- 10.16 Cronologia (same as tma_materiali_archeologici)
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'tma_materiali_ripetibili', sigla, sigla_estesa, descrizione, tipologia_sigla, lingua
FROM pyarchinit_thesaurus_sigle
WHERE nome_tabella = 'tma_materiali_archeologici' AND tipologia_sigla = '10.16';

-- Final verification for both tables
SELECT nome_tabella, tipologia_sigla, COUNT(*) as count
FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici', 'tma_materiali_ripetibili', 'TMA materiali ripetibili')
GROUP BY nome_tabella, tipologia_sigla
ORDER BY nome_tabella, CAST(SUBSTR(tipologia_sigla, 4) AS INTEGER);