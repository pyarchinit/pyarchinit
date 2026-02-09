-- Sync tipologia values from TMA to inventario_materiali
-- This copies the TMA precisazione tipologica (10.12) values to inventario tipologia (3.12)

-- First, let's copy Italian values from TMA to inventario_materiali
INSERT INTO pyarchinit_thesaurus_sigle (lingua, nome_tabella, tipologia_sigla, sigla_estesa, sigla, n_tipologia, n_sigla)
SELECT
    'it',
    'inventario_materiali_table',
    '3.12',
    sigla_estesa,
    sigla,
    3,
    12
FROM pyarchinit_thesaurus_sigle
WHERE nome_tabella = 'TMA materiali archeologici'
AND tipologia_sigla = '10.12'
AND lingua = 'it'
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla_estesa) DO NOTHING;

-- Copy English values
INSERT INTO pyarchinit_thesaurus_sigle (lingua, nome_tabella, tipologia_sigla, sigla_estesa, sigla, n_tipologia, n_sigla)
SELECT
    'en',
    'inventario_materiali_table',
    '3.12',
    sigla_estesa,
    sigla,
    3,
    12
FROM pyarchinit_thesaurus_sigle
WHERE nome_tabella = 'TMA materiali archeologici'
AND tipologia_sigla = '10.12'
AND lingua = 'en'
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla_estesa) DO NOTHING;

-- Copy German values
INSERT INTO pyarchinit_thesaurus_sigle (lingua, nome_tabella, tipologia_sigla, sigla_estesa, sigla, n_tipologia, n_sigla)
SELECT
    'de',
    'inventario_materiali_table',
    '3.12',
    sigla_estesa,
    sigla,
    3,
    12
FROM pyarchinit_thesaurus_sigle
WHERE nome_tabella = 'TMA materiali archeologici'
AND tipologia_sigla = '10.12'
AND lingua = 'de'
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla_estesa) DO NOTHING;

-- If there are no values in 10.12, try copying from 10.8 or 10.9 (alternative codes for macp)
INSERT INTO pyarchinit_thesaurus_sigle (lingua, nome_tabella, tipologia_sigla, sigla_estesa, sigla, n_tipologia, n_sigla)
SELECT
    lingua,
    'inventario_materiali_table',
    '3.12',
    sigla_estesa,
    sigla,
    3,
    12
FROM pyarchinit_thesaurus_sigle
WHERE nome_tabella IN ('TMA materiali archeologici', 'tma_materiali_ripetibili')
AND tipologia_sigla IN ('10.8', '10.9')
AND sigla_estesa LIKE '%tipo%' OR sigla_estesa LIKE '%prec%'
ON CONFLICT (lingua, nome_tabella, tipologia_sigla, sigla_estesa) DO NOTHING;