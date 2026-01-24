-- Populate thesaurus for Fauna form in English
-- Two terms per code for testing purposes
-- Run this SQL in your PyArchInit database (SQLite or PostgreSQL)

-- 13.1 - Context
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'CTX1', 'Primary deposit', '', '13.1', 'en');
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'CTX2', 'Secondary deposit', '', '13.1', 'en');

-- 13.2 - Methodology
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'MTH1', 'Manual collection', '', '13.2', 'en');
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'MTH2', 'Sieving', '', '13.2', 'en');

-- 13.3 - Accumulation type
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'ACC1', 'Natural accumulation', '', '13.3', 'en');
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'ACC2', 'Anthropic accumulation', '', '13.3', 'en');

-- 13.4 - Deposition
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'DEP1', 'Primary deposition', '', '13.4', 'en');
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'DEP2', 'Secondary deposition', '', '13.4', 'en');

-- 13.5 - Fragmentation
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'FRG1', 'Complete', '', '13.5', 'en');
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'FRG2', 'Fragmented', '', '13.5', 'en');

-- 13.6 - Conservation
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'CON1', 'Good', '', '13.6', 'en');
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'CON2', 'Poor', '', '13.6', 'en');

-- 13.7 - Reliability
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'REL1', 'High reliability', '', '13.7', 'en');
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'REL2', 'Low reliability', '', '13.7', 'en');

-- 13.8 - Combustion
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'CMB1', 'Present', '', '13.8', 'en');
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'CMB2', 'Absent', '', '13.8', 'en');

-- 13.9 - Combustion type
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'TCM1', 'Carbonized', '', '13.9', 'en');
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'TCM2', 'Calcined', '', '13.9', 'en');

-- 13.10 - Anatomical connection
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'ANC1', 'In connection', '', '13.10', 'en');
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'ANC2', 'Disarticulated', '', '13.10', 'en');

-- 13.11 - Species (for tableWidget)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'BT', 'Bos taurus', '', '13.11', 'en');
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'OA', 'Ovis aries', '', '13.11', 'en');

-- 13.12 - PSI (for tableWidget)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'PSI1', 'Adult', '', '13.12', 'en');
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'PSI2', 'Juvenile', '', '13.12', 'en');

-- 13.13 - Anatomical element (for tableWidget)
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'FEM', 'Femur', '', '13.13', 'en');
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'HUM', 'Humerus', '', '13.13', 'en');

-- Verify insertion
SELECT tipologia_sigla, sigla, sigla_estesa FROM pyarchinit_thesaurus_sigle
WHERE lingua = 'en' AND tipologia_sigla LIKE '13.%'
ORDER BY tipologia_sigla, sigla;
