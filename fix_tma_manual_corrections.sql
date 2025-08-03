-- Manual corrections for remaining issues

-- Fix 10.14 - RIN should be in 10.14, not 10.16
UPDATE pyarchinit_thesaurus_sigle 
SET tipologia_sigla = '10.14'
WHERE nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici')
AND sigla = 'RIN' AND sigla_estesa = 'Rinvenimento fortuito';

-- Add missing cronologia entries to 10.16
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES 
('tma_materiali_archeologici', 'PREI', 'Preistoria', 'Periodo preistorico', '10.16', 'it'),
('tma_materiali_archeologici', 'PROT', 'Protostoria', 'Periodo protostorico', '10.16', 'it'),
('tma_materiali_archeologici', 'ARC', 'Età arcaica', 'Periodo arcaico', '10.16', 'it'),
('tma_materiali_archeologici', 'CLA', 'Età classica', 'Periodo classico', '10.16', 'it'),
('tma_materiali_archeologici', 'ELL', 'Età ellenistica', 'Periodo ellenistico', '10.16', 'it'),
('tma_materiali_archeologici', 'ROM', 'Età romana', 'Periodo romano', '10.16', 'it'),
('tma_materiali_archeologici', 'TARD', 'Tardoantico', 'Periodo tardoantico', '10.16', 'it'),
('tma_materiali_archeologici', 'MED', 'Medioevo', 'Periodo medievale', '10.16', 'it'),
('tma_materiali_archeologici', 'RINAS', 'Rinascimento', 'Periodo rinascimentale', '10.16', 'it'),
('tma_materiali_archeologici', 'MOD', 'Età moderna', 'Periodo moderno', '10.16', 'it'),
('tma_materiali_archeologici', 'CONT', 'Età contemporanea', 'Periodo contemporaneo', '10.16', 'it');

-- Add missing entries for 10.13 (Tipo disegno autore)
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES 
('tma_materiali_archeologici', 'AUT1', 'Autore 1', 'Primo autore', '10.13', 'it'),
('tma_materiali_archeologici', 'AUT2', 'Autore 2', 'Secondo autore', '10.13', 'it');

-- Remove duplicates in 10.4
DELETE FROM pyarchinit_thesaurus_sigle
WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM pyarchinit_thesaurus_sigle
    WHERE nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici')
    AND tipologia_sigla = '10.4'
    GROUP BY sigla
);

-- Add more categoria entries for 10.5
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES 
('tma_materiali_archeologici', 'CER_COM', 'Ceramica comune', 'Ceramica di uso comune', '10.5', 'it'),
('tma_materiali_archeologici', 'CER_FIN', 'Ceramica fine', 'Ceramica fine da mensa', '10.5', 'it'),
('tma_materiali_archeologici', 'MON', 'Moneta', 'Moneta', '10.5', 'it');

-- Add more classe entries for 10.6
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES 
('tma_materiali_archeologici', 'SIG_IT', 'Sigillata italica', 'Terra sigillata italica', '10.6', 'it'),
('tma_materiali_archeologici', 'SIG_AF', 'Sigillata africana', 'Terra sigillata africana', '10.6', 'it'),
('tma_materiali_archeologici', 'VN', 'Vernice nera', 'Ceramica a vernice nera', '10.6', 'it');

-- Add entries for 10.8 (Precisazione tipologica)
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES 
('tma_materiali_archeologici', 'HAYES_23', 'Hayes 23', 'Forma Hayes 23', '10.8', 'it'),
('tma_materiali_archeologici', 'DRAG_18', 'Dragendorff 18', 'Forma Dragendorff 18', '10.8', 'it');

-- Add entries for 10.9 (Definizione)
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES 
('tma_materiali_archeologici', 'PIATTO', 'Piatto', 'Piatto da mensa', '10.9', 'it'),
('tma_materiali_archeologici', 'COPPA', 'Coppa', 'Coppa', '10.9', 'it'),
('tma_materiali_archeologici', 'OLLA', 'Olla', 'Olla da cucina', '10.9', 'it');

-- Final check
SELECT tipologia_sigla, COUNT(*) as count, 
       CASE tipologia_sigla
           WHEN '10.1' THEN 'Denominazione collocazione'
           WHEN '10.2' THEN 'Saggio'
           WHEN '10.3' THEN 'Località'
           WHEN '10.4' THEN 'Materiale'
           WHEN '10.5' THEN 'Categoria'
           WHEN '10.6' THEN 'Classe'
           WHEN '10.7' THEN 'Area'
           WHEN '10.8' THEN 'Precisazione tipologica'
           WHEN '10.9' THEN 'Definizione'
           WHEN '10.10' THEN 'Tipo collocazione'
           WHEN '10.11' THEN 'Tipo foto'
           WHEN '10.12' THEN 'Tipo disegno'
           WHEN '10.13' THEN 'Tipo disegno autore'
           WHEN '10.14' THEN 'Tipologia acquisizione'
           WHEN '10.15' THEN 'Settore'
           WHEN '10.16' THEN 'Cronologia'
       END as descrizione
FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella IN ('tma_materiali_archeologici', 'TMA materiali archeologici')
GROUP BY tipologia_sigla
ORDER BY CAST(SUBSTR(tipologia_sigla, 4) AS INTEGER);