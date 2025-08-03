-- Script to fix TMA tipologia_sigla codes - Version 2
-- This script uses more specific matching to avoid wrong assignments

-- First, let's check what we have
SELECT nome_tabella, tipologia_sigla, sigla, sigla_estesa
FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici')
ORDER BY nome_tabella, tipologia_sigla;

-- Fix wrong assignments based on sigla values

-- 10.3 should be for Località (not Vano/Locus/Ambiente)
UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.3'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND sigla IN ('Località 1', 'Località 2', 'Località 3', 'Centro storico', 'Periferia');

-- Vano/Locus/Ambiente should not be 10.3 - remove them or assign to appropriate code
DELETE FROM pyarchinit_thesaurus_sigle 
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND tipologia_sigla = '10.3'
AND sigla IN ('Vano 1', 'Vano 2', 'Vano 3', 'Locus 1', 'Locus 2', 'Ambiente 1', 'Ambiente 2');

-- 10.4 should be for Materiale (not for Scavo/Ricognizione)
UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.14'  -- Move to Tipologia acquisizione
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND tipologia_sigla = '10.4'
AND sigla LIKE '%Scavo%' OR sigla LIKE '%Ricognizione%';

-- Add proper Materiale entries if missing
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'tma_materiali_archeologici', 'CER', 'Ceramica', 'Materiale ceramico', '10.4', 'it'
WHERE NOT EXISTS (
    SELECT 1 FROM pyarchinit_thesaurus_sigle 
    WHERE nome_tabella = 'tma_materiali_archeologici' 
    AND tipologia_sigla = '10.4' 
    AND sigla = 'CER'
);

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'tma_materiali_archeologici', 'MET', 'Metallo', 'Materiale metallico', '10.4', 'it'
WHERE NOT EXISTS (
    SELECT 1 FROM pyarchinit_thesaurus_sigle 
    WHERE nome_tabella = 'tma_materiali_archeologici' 
    AND tipologia_sigla = '10.4' 
    AND sigla = 'MET'
);

INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'tma_materiali_archeologici', 'VET', 'Vetro', 'Materiale vitreo', '10.4', 'it'
WHERE NOT EXISTS (
    SELECT 1 FROM pyarchinit_thesaurus_sigle 
    WHERE nome_tabella = 'tma_materiali_archeologici' 
    AND tipologia_sigla = '10.4' 
    AND sigla = 'VET'
);

-- 10.5 should be for Categoria
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT 'tma_materiali_archeologici', 'ANF', 'Anfora', 'Contenitore da trasporto', '10.5', 'it'
WHERE NOT EXISTS (
    SELECT 1 FROM pyarchinit_thesaurus_sigle 
    WHERE nome_tabella = 'tma_materiali_archeologici' 
    AND tipologia_sigla = '10.5' 
    AND sigla = 'ANF'
);

-- 10.7 should be for Area (not Ceramica/Metallo/Vetro)
DELETE FROM pyarchinit_thesaurus_sigle 
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND tipologia_sigla = '10.7'
AND sigla IN ('Ceramica', 'Metallo', 'Vetro');

-- 10.11 should be for Tipo foto (not Tipologia acquisizione)
UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.11'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND sigla IN ('Dettaglio', 'Generale', 'Macro', 'Microscopica', 'Radiografia', 'Ultravioletto');

-- 10.12 should be for Tipo disegno
UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.12'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND sigla IN ('Decorazione', 'Profilo', 'Ricostruzione', 'Rilievo', 'Schema', 'Sezione');

-- 10.14 should be for Tipologia acquisizione
UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.14'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND sigla IN ('Acquisto', 'Donazione', 'Recupero', 'Ricognizione', 'Rinvenimento fortuito', 'Scavo');

-- 10.15 should be for Settore
UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.15'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND (sigla LIKE 'Settore%' OR sigla IN ('Nord-Est', 'Nord-Ovest', 'Sud-Est', 'Sud-Ovest'));

-- 10.16 should be for Cronologia (not Età/Periodo)
UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.16'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND (sigla LIKE 'Età%' OR sigla IN ('Medioevo', 'Preistoria', 'Protostoria', 'Rinascimento', 'Tardoantico'));

-- Remove wrong entries with codes 10.18 and 10.19
DELETE FROM pyarchinit_thesaurus_sigle 
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND tipologia_sigla IN ('10.18', '10.19');

-- Final check
SELECT nome_tabella, tipologia_sigla, sigla, sigla_estesa
FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici')
ORDER BY nome_tabella, CAST(SUBSTR(tipologia_sigla, 4) AS INTEGER);