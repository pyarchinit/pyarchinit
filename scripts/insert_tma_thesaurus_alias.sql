-- SQL script to insert TMA thesaurus with correct alias table names
-- This script uses the alias names instead of real database table names

-- First, clean up any existing entries
DELETE FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella IN ('tma_table', 'tma_materiali_table');

-- Materials table fields (tma_materiali_table alias)
-- MATERIALE (Column 0) - tipologia_sigla 10.4
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_materiali_table', 'CER', 'ceramica', 'Materiale ceramico', '10.4', 'IT'),
('tma_materiali_table', 'VET', 'vetro', 'Materiale vitreo', '10.4', 'IT'),
('tma_materiali_table', 'MET', 'metallo', 'argento, bronzo, oro, piombo, rame', '10.4', 'IT'),
('tma_materiali_table', 'FIT', 'materiale fittile', 'argilla', '10.4', 'IT'),
('tma_materiali_table', 'LIT', 'materiale litico', 'oggetti in pietra', '10.4', 'IT'),
('tma_materiali_table', 'IND', 'industria litica', 'scheggiata, pesante', '10.4', 'IT'),
('tma_materiali_table', 'OSS', 'osso', 'Materiale osseo', '10.4', 'IT'),
('tma_materiali_table', 'AVO', 'avorio', 'Materiale eburneo', '10.4', 'IT'),
('tma_materiali_table', 'ROS', 'resti osteologici', 'Resti ossei', '10.4', 'IT'),
('tma_materiali_table', 'LEG', 'legno', 'Materiale ligneo', '10.4', 'IT'),
('tma_materiali_table', 'ORG', 'materiale organico', 'carbone, resti animali', '10.4', 'IT'),
('tma_materiali_table', 'TER', 'campioni di terra', 'Campioni di sedimento', '10.4', 'IT'),
('tma_materiali_table', 'ALT', 'altri materiali', 'pasta vitrea, cristallo di rocca, ocra', '10.4', 'IT');

-- CATEGORIA (Column 1) - tipologia_sigla 10.5
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_materiali_table', 'CC', 'ceramica comune', 'Ceramica di uso comune', '10.5', 'IT'),
('tma_materiali_table', 'CF', 'ceramica fine', 'Ceramica da mensa fine', '10.5', 'IT'),
('tma_materiali_table', 'CK', 'ceramica da cucina', 'Ceramica da fuoco', '10.5', 'IT'),
('tma_materiali_table', 'CM', 'ceramica da mensa', 'Ceramica da tavola', '10.5', 'IT'),
('tma_materiali_table', 'ANF', 'anfore', 'Contenitori da trasporto', '10.5', 'IT'),
('tma_materiali_table', 'LUC', 'lucerne', 'Illuminazione', '10.5', 'IT'),
('tma_materiali_table', 'VF', 'vetro finestra', 'Vetro piano da finestra', '10.5', 'IT'),
('tma_materiali_table', 'VC', 'vetro contenitore', 'Contenitori in vetro', '10.5', 'IT'),
('tma_materiali_table', 'VO', 'vetro ornamento', 'Oggetti ornamentali', '10.5', 'IT'),
('tma_materiali_table', 'BR', 'bronzo', 'Oggetti in bronzo', '10.5', 'IT'),
('tma_materiali_table', 'FE', 'ferro', 'Oggetti in ferro', '10.5', 'IT'),
('tma_materiali_table', 'PB', 'piombo', 'Oggetti in piombo', '10.5', 'IT'),
('tma_materiali_table', 'AG', 'argento', 'Oggetti in argento', '10.5', 'IT'),
('tma_materiali_table', 'AU', 'oro', 'Oggetti in oro', '10.5', 'IT'),
('tma_materiali_table', 'LAT', 'laterizi', 'Mattoni e tegole', '10.5', 'IT'),
('tma_materiali_table', 'INT', 'intonaco', 'Intonaco dipinto', '10.5', 'IT'),
('tma_materiali_table', 'MOS', 'mosaico', 'Tessere musive', '10.5', 'IT');

-- CLASSE (Column 2) - tipologia_sigla 10.6
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_materiali_table', 'TS', 'terra sigillata', 'Terra sigillata', '10.6', 'IT'),
('tma_materiali_table', 'TSI', 'terra sigillata italica', 'Produzione italica', '10.6', 'IT'),
('tma_materiali_table', 'TSA', 'terra sigillata africana', 'Produzione africana', '10.6', 'IT'),
('tma_materiali_table', 'TSG', 'terra sigillata gallica', 'Produzione gallica', '10.6', 'IT'),
('tma_materiali_table', 'PF', 'pareti fini', 'Ceramica a pareti sottili', '10.6', 'IT'),
('tma_materiali_table', 'VN', 'vernice nera', 'Ceramica a vernice nera', '10.6', 'IT'),
('tma_materiali_table', 'MED', 'maiolica', 'Ceramica medievale', '10.6', 'IT'),
('tma_materiali_table', 'VS', 'vetro soffiato', 'Tecnica a soffio', '10.6', 'IT'),
('tma_materiali_table', 'VF', 'vetro fuso', 'Tecnica a fusione', '10.6', 'IT'),
('tma_materiali_table', 'MON', 'moneta', 'Numismatica', '10.6', 'IT'),
('tma_materiali_table', 'STR', 'strumento', 'Strumenti e utensili', '10.6', 'IT'),
('tma_materiali_table', 'ORN', 'ornamento', 'Oggetti di ornamento', '10.6', 'IT');

-- PREC. TIPOLOGICA (Column 3) - tipologia_sigla 10.8
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_materiali_table', 'PIA', 'piatto', 'Forma aperta', '10.8', 'IT'),
('tma_materiali_table', 'COP', 'coppa', 'Forma aperta', '10.8', 'IT'),
('tma_materiali_table', 'BIC', 'bicchiere', 'Forma potoria', '10.8', 'IT'),
('tma_materiali_table', 'BOC', 'boccale', 'Forma potoria', '10.8', 'IT'),
('tma_materiali_table', 'OLL', 'olla', 'Forma chiusa', '10.8', 'IT'),
('tma_materiali_table', 'PEN', 'pentola', 'Forma da cucina', '10.8', 'IT'),
('tma_materiali_table', 'ANF', 'anfora', 'Contenitore da trasporto', '10.8', 'IT'),
('tma_materiali_table', 'FIB', 'fibula', 'Elemento di abbigliamento', '10.8', 'IT'),
('tma_materiali_table', 'ANE', 'anello', 'Ornamento personale', '10.8', 'IT'),
('tma_materiali_table', 'CHI', 'chiodo', 'Elemento strutturale', '10.8', 'IT');

-- DEFINIZIONE (Column 4) - tipologia_sigla 10.9
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_materiali_table', 'ORL', 'orlo', 'Frammento di orlo', '10.9', 'IT'),
('tma_materiali_table', 'FND', 'fondo', 'Frammento di fondo', '10.9', 'IT'),
('tma_materiali_table', 'ANS', 'ansa', 'Frammento di ansa', '10.9', 'IT'),
('tma_materiali_table', 'PAR', 'parete', 'Frammento di parete', '10.9', 'IT'),
('tma_materiali_table', 'INT', 'integro', 'Oggetto integro', '10.9', 'IT'),
('tma_materiali_table', 'RIC', 'ricomposto', 'Oggetto ricomposto', '10.9', 'IT'),
('tma_materiali_table', 'LAM', 'lama', 'Utensile', '10.9', 'IT'),
('tma_materiali_table', 'BOT', 'bottiglia', 'Contenitore', '10.9', 'IT'),
('tma_materiali_table', 'PER', 'perla', 'Ornamento', '10.9', 'IT'),
('tma_materiali_table', 'AGO', 'ago', 'Strumento da cucito', '10.9', 'IT'),
('tma_materiali_table', 'SPI', 'spillone', 'Ornamento', '10.9', 'IT'),
('tma_materiali_table', 'PET', 'pettine', 'Oggetto da toeletta', '10.9', 'IT');

-- Main TMA table fields (tma_table alias)
-- Location type (ldct) - tipologia_sigla 10.10
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_table', 'DEP', 'deposito', 'Deposito archeologico', '10.10', 'IT'),
('tma_table', 'MAG', 'magazzino', 'Magazzino', '10.10', 'IT'),
('tma_table', 'LAB', 'laboratorio', 'Laboratorio', '10.10', 'IT'),
('tma_table', 'MUS', 'museo', 'Museo', '10.10', 'IT');

-- Acquisition type (aint) - tipologia_sigla 10.11
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_table', 'ICD', 'ICCD', 'Istituto Centrale per il Catalogo e la Documentazione', '10.11', 'IT'),
('tma_table', 'SCA', 'scavo', 'Scavo archeologico', '10.11', 'IT'),
('tma_table', 'RIC', 'ricognizione', 'Ricognizione di superficie', '10.11', 'IT'),
('tma_table', 'RIN', 'rinvenimento', 'Rinvenimento fortuito', '10.11', 'IT');

-- Photo type (ftap) - tipologia_sigla 10.12
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_table', 'DIG', 'digitale', 'Fotografia digitale', '10.12', 'IT'),
('tma_table', 'ANA', 'analogica', 'Fotografia analogica', '10.12', 'IT'),
('tma_table', 'BN', 'b/n', 'Bianco e nero', '10.12', 'IT'),
('tma_table', 'COL', 'colore', 'A colori', '10.12', 'IT');

-- Drawing type (drat) - tipologia_sigla 10.13
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_table', 'RIL', 'rilievo', 'Rilievo archeologico', '10.13', 'IT'),
('tma_table', 'SCH', 'schizzo', 'Schizzo a mano', '10.13', 'IT'),
('tma_table', 'PLA', 'pianta', 'Pianta planimetrica', '10.13', 'IT'),
('tma_table', 'SEZ', 'sezione', 'Sezione stratigrafica', '10.13', 'IT'),
('tma_table', 'PRO', 'prospetto', 'Prospetto architettonico', '10.13', 'IT');

-- Conservation status (stcc) - tipologia_sigla 10.14
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_table', 'BUO', 'buono', 'Stato di conservazione buono', '10.14', 'IT'),
('tma_table', 'DIS', 'discreto', 'Stato di conservazione discreto', '10.14', 'IT'),
('tma_table', 'CAT', 'cattivo', 'Stato di conservazione cattivo', '10.14', 'IT'),
('tma_table', 'PES', 'pessimo', 'Stato di conservazione pessimo', '10.14', 'IT'),
('tma_table', 'FRA', 'frammentario', 'Stato frammentario', '10.14', 'IT');

-- Material type (ogtm) for main TMA table - tipologia_sigla 10.15
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_table', 'CER', 'ceramica', 'Materiale ceramico', '10.15', 'IT'),
('tma_table', 'VET', 'vetro', 'Materiale vitreo', '10.15', 'IT'),
('tma_table', 'MET', 'metallo', 'Materiali metallici', '10.15', 'IT'),
('tma_table', 'ORG', 'organico', 'Materiali organici', '10.15', 'IT'),
('tma_table', 'LIT', 'litico', 'Materiali litici', '10.15', 'IT'),
('tma_table', 'MIS', 'misto', 'Materiali misti', '10.15', 'IT');

-- Add TMA tables to configuration manager thesaurus
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('pyarchinit_nome_tabelle', '27', 'tma_table', 'Tabella Materiali Archeologici', 'n', 'IT'),
('pyarchinit_nome_tabelle', '28', 'tma_materiali_table', 'Tabella Materiali Ripetibili TMA', 'n', 'IT');

-- Verify the insertion
SELECT COUNT(*) as total, nome_tabella, tipologia_sigla
FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella IN ('tma_table', 'tma_materiali_table')
GROUP BY nome_tabella, tipologia_sigla
ORDER BY nome_tabella, tipologia_sigla;