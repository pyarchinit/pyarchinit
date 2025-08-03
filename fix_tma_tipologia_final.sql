-- Final fix for TMA tipologia codes
-- Clean up and reorganize according to the correct schema

-- First, remove all duplicate entries
DELETE FROM pyarchinit_thesaurus_sigle
WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM pyarchinit_thesaurus_sigle
    WHERE nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici')
    GROUP BY nome_tabella, sigla, tipologia_sigla
);

-- Remove entries that shouldn't be in certain categories

-- Remove Vano/Locus/Ambiente from 10.3 (should only be Località)
DELETE FROM pyarchinit_thesaurus_sigle 
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND tipologia_sigla = '10.3'
AND sigla NOT LIKE 'LOC%' AND sigla_estesa NOT LIKE '%Località%';

-- Move actual Località entries to 10.3
UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.3'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND (sigla LIKE 'LOC%' OR sigla_estesa LIKE '%Località%' OR sigla IN ('Centro storico', 'Periferia'));

-- Remove non-Material entries from 10.4
DELETE FROM pyarchinit_thesaurus_sigle 
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND tipologia_sigla = '10.4'
AND (sigla LIKE 'SCA%' OR sigla LIKE 'RIC%' OR sigla LIKE 'PREV%' OR sigla_estesa LIKE '%Scavo%' OR sigla_estesa LIKE '%Ricognizione%');

-- Ensure proper Material entries in 10.4
UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.4'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND sigla IN ('CER', 'MET', 'VET', 'OSS', 'PIE', 'LEG') 
AND sigla_estesa IN ('Ceramica', 'Metallo', 'Vetro', 'Osso', 'Pietra', 'Legno');

-- Remove Material entries from 10.7 (Area)
DELETE FROM pyarchinit_thesaurus_sigle 
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND tipologia_sigla = '10.7'
AND sigla IN ('CER', 'MET', 'VET');

-- Fix Type photo entries (should be 10.11)
UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.11'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND sigla IN ('GEN', 'DET', 'MAC', 'MIC', 'RAD', 'UV');

-- Fix Type drawing entries (should be 10.12)
UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.12'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND sigla IN ('RIL', 'RIC', 'SEZ', 'PRO', 'DEC', 'SCH')
AND sigla_estesa IN ('Rilievo', 'Ricostruzione', 'Sezione', 'Profilo', 'Decorazione', 'Schema');

-- Fix Acquisition type entries (should be 10.14)
UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.14'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND sigla IN ('SCA', 'RIC', 'REC', 'RIN', 'DON', 'ACQ')
AND sigla_estesa IN ('Scavo', 'Ricognizione', 'Recupero', 'Rinvenimento fortuito', 'Donazione', 'Acquisto');

-- Move Scavo entries from 10.4 to 10.14
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
SELECT nome_tabella, 'SCA01', 'Scavo archeologico 2024', descrizione, '10.14', lingua
FROM pyarchinit_thesaurus_sigle
WHERE nome_tabella = 'tma_materiali_archeologici' 
AND sigla = 'SCA01' 
AND tipologia_sigla = '10.4'
ON CONFLICT DO NOTHING;

-- Fix Settore entries (10.15) - remove cronologia entries
DELETE FROM pyarchinit_thesaurus_sigle 
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND tipologia_sigla = '10.15'
AND (sigla LIKE '%Età%' OR sigla IN ('PREI', 'PROT', 'ARC', 'CLA', 'ELL', 'ROM', 'TARD', 'MED', 'RIN', 'MOD', 'CONT'));

-- Keep only Settore entries in 10.15
UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.15'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND (sigla LIKE 'S%' OR sigla IN ('NE', 'NO', 'SE', 'SO'))
AND (sigla_estesa LIKE '%Settore%' OR sigla_estesa IN ('Nord-Est', 'Nord-Ovest', 'Sud-Est', 'Sud-Ovest'));

-- Move Cronologia entries to 10.16
UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.16'
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND (sigla IN ('PREI', 'PROT', 'ARC', 'CLA', 'ELL', 'ROM', 'TARD', 'MED', 'RIN', 'MOD', 'CONT') 
     OR sigla_estesa LIKE '%Età%' 
     OR sigla_estesa IN ('Preistoria', 'Protostoria', 'Medioevo', 'Rinascimento', 'Tardoantico'));

-- Remove codes beyond 10.16
DELETE FROM pyarchinit_thesaurus_sigle 
WHERE (nome_tabella = 'tma_materiali_archeologici' OR nome_tabella = 'TMA materiali archeologici')
AND CAST(SUBSTR(tipologia_sigla, 4) AS INTEGER) > 16;

-- Final verification
SELECT tipologia_sigla, COUNT(*) as count, GROUP_CONCAT(sigla || ' (' || sigla_estesa || ')', ', ') as entries
FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici')
GROUP BY tipologia_sigla
ORDER BY CAST(SUBSTR(tipologia_sigla, 4) AS INTEGER);