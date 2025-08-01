-- Script per inserire i valori del thesaurus TMA
-- Compatibile con SQLite e PostgreSQL

-- 10.1 - Denominazione collocazione (ldcn)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
VALUES 
('tma_materiali_archeologici', 'MAG01', 'Magazzino 1', '10.1', 'it'),
('tma_materiali_archeologici', 'MAG02', 'Magazzino 2', '10.1', 'it'),
('tma_materiali_archeologici', 'DEP01', 'Deposito 1', '10.1', 'it'),
('tma_materiali_archeologici', 'LAB01', 'Laboratorio 1', '10.1', 'it');

-- 10.2 - Saggio
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
VALUES 
('tma_materiali_archeologici', 'SAG1', 'Saggio 1', '10.2', 'it'),
('tma_materiali_archeologici', 'SAG2', 'Saggio 2', '10.2', 'it'),
('tma_materiali_archeologici', 'SAG3', 'Saggio 3', '10.2', 'it'),
('tma_materiali_archeologici', 'SAGA', 'Saggio A', '10.2', 'it'),
('tma_materiali_archeologici', 'SAGB', 'Saggio B', '10.2', 'it');

-- 10.3 - Vano/Locus
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
VALUES 
('tma_materiali_archeologici', 'V1', 'Vano 1', '10.3', 'it'),
('tma_materiali_archeologici', 'V2', 'Vano 2', '10.3', 'it'),
('tma_materiali_archeologici', 'V3', 'Vano 3', '10.3', 'it'),
('tma_materiali_archeologici', 'L1', 'Locus 1', '10.3', 'it'),
('tma_materiali_archeologici', 'L2', 'Locus 2', '10.3', 'it'),
('tma_materiali_archeologici', 'AMB1', 'Ambiente 1', '10.3', 'it'),
('tma_materiali_archeologici', 'AMB2', 'Ambiente 2', '10.3', 'it');

-- 10.4 - Nome scavo
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
VALUES 
('tma_materiali_archeologici', 'SCA01', 'Scavo archeologico 2024', '10.4', 'it'),
('tma_materiali_archeologici', 'SCA02', 'Scavo di emergenza', '10.4', 'it'),
('tma_materiali_archeologici', 'RIC01', 'Ricognizione superficiale', '10.4', 'it'),
('tma_materiali_archeologici', 'PREV01', 'Scavo preventivo', '10.4', 'it');

-- 10.7 - Area
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
VALUES 
('tma_materiali_archeologici', 'A', 'Area A', '10.7', 'it'),
('tma_materiali_archeologici', 'B', 'Area B', '10.7', 'it'),
('tma_materiali_archeologici', 'C', 'Area C', '10.7', 'it'),
('tma_materiali_archeologici', 'D', 'Area D', '10.7', 'it'),
('tma_materiali_archeologici', '1000', 'Area 1000', '10.7', 'it'),
('tma_materiali_archeologici', '2000', 'Area 2000', '10.7', 'it'),
('tma_materiali_archeologici', '3000', 'Area 3000', '10.7', 'it');

-- 10.10 - Tipologia collocazione (ldct)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
VALUES 
('tma_materiali_archeologici', 'MAG', 'Magazzino', '10.10', 'it'),
('tma_materiali_archeologici', 'DEP', 'Deposito', '10.10', 'it'),
('tma_materiali_archeologici', 'LAB', 'Laboratorio', '10.10', 'it'),
('tma_materiali_archeologici', 'MUS', 'Museo', '10.10', 'it'),
('tma_materiali_archeologici', 'ARCH', 'Archivio', '10.10', 'it');

-- 10.11 - Tipo acquisizione (aint)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
VALUES 
('tma_materiali_archeologici', 'SCA', 'Scavo', '10.11', 'it'),
('tma_materiali_archeologici', 'RIC', 'Ricognizione', '10.11', 'it'),
('tma_materiali_archeologici', 'REC', 'Recupero', '10.11', 'it'),
('tma_materiali_archeologici', 'RIN', 'Rinvenimento fortuito', '10.11', 'it'),
('tma_materiali_archeologici', 'DON', 'Donazione', '10.11', 'it'),
('tma_materiali_archeologici', 'ACQ', 'Acquisto', '10.11', 'it');

-- 10.12 - Tipo fotografia (ftap)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
VALUES 
('tma_materiali_archeologici', 'GEN', 'Generale', '10.12', 'it'),
('tma_materiali_archeologici', 'DET', 'Dettaglio', '10.12', 'it'),
('tma_materiali_archeologici', 'MAC', 'Macro', '10.12', 'it'),
('tma_materiali_archeologici', 'MIC', 'Microscopica', '10.12', 'it'),
('tma_materiali_archeologici', 'RAD', 'Radiografia', '10.12', 'it'),
('tma_materiali_archeologici', 'UV', 'Ultravioletto', '10.12', 'it');

-- 10.13 - Tipo disegno (drat)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
VALUES 
('tma_materiali_archeologici', 'RIL', 'Rilievo', '10.13', 'it'),
('tma_materiali_archeologici', 'RIC', 'Ricostruzione', '10.13', 'it'),
('tma_materiali_archeologici', 'SEZ', 'Sezione', '10.13', 'it'),
('tma_materiali_archeologici', 'PRO', 'Profilo', '10.13', 'it'),
('tma_materiali_archeologici', 'DEC', 'Decorazione', '10.13', 'it'),
('tma_materiali_archeologici', 'SCH', 'Schema', '10.13', 'it');

-- 10.15 - Fascia cronologica (dtzg)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
VALUES 
('tma_materiali_archeologici', 'PREI', 'Preistoria', '10.15', 'it'),
('tma_materiali_archeologici', 'PROT', 'Protostoria', '10.15', 'it'),
('tma_materiali_archeologici', 'ARC', 'Età arcaica', '10.15', 'it'),
('tma_materiali_archeologici', 'CLA', 'Età classica', '10.15', 'it'),
('tma_materiali_archeologici', 'ELL', 'Età ellenistica', '10.15', 'it'),
('tma_materiali_archeologici', 'ROM', 'Età romana', '10.15', 'it'),
('tma_materiali_archeologici', 'TARD', 'Tardoantico', '10.15', 'it'),
('tma_materiali_archeologici', 'MED', 'Medioevo', '10.15', 'it'),
('tma_materiali_archeologici', 'RIN', 'Rinascimento', '10.15', 'it'),
('tma_materiali_archeologici', 'MOD', 'Età moderna', '10.15', 'it'),
('tma_materiali_archeologici', 'CONT', 'Età contemporanea', '10.15', 'it');

-- 10.18 - Località
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
VALUES 
('tma_materiali_archeologici', 'LOC01', 'Località 1', '10.18', 'it'),
('tma_materiali_archeologici', 'LOC02', 'Località 2', '10.18', 'it'),
('tma_materiali_archeologici', 'LOC03', 'Località 3', '10.18', 'it'),
('tma_materiali_archeologici', 'CENTR', 'Centro storico', '10.18', 'it'),
('tma_materiali_archeologici', 'PERIF', 'Periferia', '10.18', 'it');

-- 10.19 - Settore
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
VALUES 
('tma_materiali_archeologici', 'S1', 'Settore 1', '10.19', 'it'),
('tma_materiali_archeologici', 'S2', 'Settore 2', '10.19', 'it'),
('tma_materiali_archeologici', 'S3', 'Settore 3', '10.19', 'it'),
('tma_materiali_archeologici', 'S4', 'Settore 4', '10.19', 'it'),
('tma_materiali_archeologici', 'SA', 'Settore A', '10.19', 'it'),
('tma_materiali_archeologici', 'SB', 'Settore B', '10.19', 'it'),
('tma_materiali_archeologici', 'SC', 'Settore C', '10.19', 'it'),
('tma_materiali_archeologici', 'SD', 'Settore D', '10.19', 'it'),
('tma_materiali_archeologici', 'NE', 'Nord-Est', '10.19', 'it'),
('tma_materiali_archeologici', 'NO', 'Nord-Ovest', '10.19', 'it'),
('tma_materiali_archeologici', 'SE', 'Sud-Est', '10.19', 'it'),
('tma_materiali_archeologici', 'SO', 'Sud-Ovest', '10.19', 'it');

-- Note: Questi sono valori di esempio. Puoi modificarli o aggiungerne altri secondo le tue esigenze.
-- Per eseguire questo script:
-- SQLite: sqlite3 pyarchinit_db.sqlite < insert_tma_thesaurus.sql
-- PostgreSQL: psql -U postgres -d pyarchinit -f insert_tma_thesaurus.sql