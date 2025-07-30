-- Script to clean and fix TMA thesaurus entries

-- First, delete ALL existing TMA thesaurus entries
DELETE FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella IN ('tma_materiali_archeologici', 'tma_materiali_ripetibili');

-- Now insert with correct tipologia_sigla codes
-- Materials table fields use 10.4-10.9 as already defined
-- Main TMA table fields need numeric codes too

-- MATERIALE (Column 0 in materials table) - tipologia_sigla 10.4
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_materiali_ripetibili', 'CER', 'ceramica', 'Materiale ceramico', '10.4', 'IT'),
('tma_materiali_ripetibili', 'VET', 'vetro', 'Materiale vitreo', '10.4', 'IT'),
('tma_materiali_ripetibili', 'MET', 'metallo', 'argento, bronzo, oro, piombo, rame', '10.4', 'IT'),
('tma_materiali_ripetibili', 'FIT', 'materiale fittile', 'argilla', '10.4', 'IT'),
('tma_materiali_ripetibili', 'LIT', 'materiale litico', 'oggetti in pietra', '10.4', 'IT'),
('tma_materiali_ripetibili', 'IND', 'industria litica', 'scheggiata, pesante', '10.4', 'IT'),
('tma_materiali_ripetibili', 'OSS', 'osso', 'Materiale osseo', '10.4', 'IT'),
('tma_materiali_ripetibili', 'AVO', 'avorio', 'Materiale eburneo', '10.4', 'IT'),
('tma_materiali_ripetibili', 'ROS', 'resti osteologici', 'Resti ossei', '10.4', 'IT'),
('tma_materiali_ripetibili', 'LEG', 'legno', 'Materiale ligneo', '10.4', 'IT'),
('tma_materiali_ripetibili', 'ORG', 'materiale organico', 'carbone, resti animali', '10.4', 'IT'),
('tma_materiali_ripetibili', 'TER', 'campioni di terra', 'Campioni di sedimento', '10.4', 'IT'),
('tma_materiali_ripetibili', 'ALT', 'altri materiali', 'pasta vitrea, cristallo di rocca, ocra', '10.4', 'IT');

-- CATEGORIA (Column 1 in materials table) - tipologia_sigla 10.5
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
-- Ceramica categories
('tma_materiali_ripetibili', 'CC', 'ceramica comune', 'Ceramica di uso comune', '10.5', 'IT'),
('tma_materiali_ripetibili', 'CF', 'ceramica fine', 'Ceramica da mensa fine', '10.5', 'IT'),
('tma_materiali_ripetibili', 'CK', 'ceramica da cucina', 'Ceramica da fuoco', '10.5', 'IT'),
('tma_materiali_ripetibili', 'CM', 'ceramica da mensa', 'Ceramica da tavola', '10.5', 'IT'),
('tma_materiali_ripetibili', 'ANF', 'anfore', 'Contenitori da trasporto', '10.5', 'IT'),
('tma_materiali_ripetibili', 'LUC', 'lucerne', 'Illuminazione', '10.5', 'IT'),
-- Vetro categories
('tma_materiali_ripetibili', 'VF', 'vetro finestra', 'Vetro piano da finestra', '10.5', 'IT'),
('tma_materiali_ripetibili', 'VC', 'vetro contenitore', 'Contenitori in vetro', '10.5', 'IT'),
('tma_materiali_ripetibili', 'VO', 'vetro ornamento', 'Oggetti ornamentali', '10.5', 'IT'),
-- Metallo categories
('tma_materiali_ripetibili', 'BR', 'bronzo', 'Oggetti in bronzo', '10.5', 'IT'),
('tma_materiali_ripetibili', 'FE', 'ferro', 'Oggetti in ferro', '10.5', 'IT'),
('tma_materiali_ripetibili', 'PB', 'piombo', 'Oggetti in piombo', '10.5', 'IT'),
('tma_materiali_ripetibili', 'AG', 'argento', 'Oggetti in argento', '10.5', 'IT'),
('tma_materiali_ripetibili', 'AU', 'oro', 'Oggetti in oro', '10.5', 'IT'),
-- Altri materiali
('tma_materiali_ripetibili', 'LAT', 'laterizi', 'Mattoni e tegole', '10.5', 'IT'),
('tma_materiali_ripetibili', 'INT', 'intonaco', 'Intonaco dipinto', '10.5', 'IT'),
('tma_materiali_ripetibili', 'MOS', 'mosaico', 'Tessere musive', '10.5', 'IT');

-- CLASSE (Column 2 in materials table) - tipologia_sigla 10.6
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
-- Classi ceramiche
('tma_materiali_ripetibili', 'TS', 'terra sigillata', 'Terra sigillata', '10.6', 'IT'),
('tma_materiali_ripetibili', 'TSI', 'terra sigillata italica', 'Produzione italica', '10.6', 'IT'),
('tma_materiali_ripetibili', 'TSA', 'terra sigillata africana', 'Produzione africana', '10.6', 'IT'),
('tma_materiali_ripetibili', 'TSG', 'terra sigillata gallica', 'Produzione gallica', '10.6', 'IT'),
('tma_materiali_ripetibili', 'PF', 'pareti fini', 'Ceramica a pareti sottili', '10.6', 'IT'),
('tma_materiali_ripetibili', 'VN', 'vernice nera', 'Ceramica a vernice nera', '10.6', 'IT'),
('tma_materiali_ripetibili', 'MED', 'maiolica', 'Ceramica medievale', '10.6', 'IT'),
-- Classi vetro
('tma_materiali_ripetibili', 'VS', 'vetro soffiato', 'Tecnica a soffio', '10.6', 'IT'),
('tma_materiali_ripetibili', 'VF', 'vetro fuso', 'Tecnica a fusione', '10.6', 'IT'),
-- Classi metallo
('tma_materiali_ripetibili', 'MON', 'moneta', 'Numismatica', '10.6', 'IT'),
('tma_materiali_ripetibili', 'STR', 'strumento', 'Strumenti e utensili', '10.6', 'IT'),
('tma_materiali_ripetibili', 'ORN', 'ornamento', 'Oggetti di ornamento', '10.6', 'IT');

-- PREC. TIPOLOGICA (Column 3 in materials table) - tipologia_sigla 10.8
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
-- Forme ceramiche
('tma_materiali_ripetibili', 'PIA', 'piatto', 'Forma aperta', '10.8', 'IT'),
('tma_materiali_ripetibili', 'COP', 'coppa', 'Forma aperta', '10.8', 'IT'),
('tma_materiali_ripetibili', 'BIC', 'bicchiere', 'Forma potoria', '10.8', 'IT'),
('tma_materiali_ripetibili', 'BOC', 'boccale', 'Forma potoria', '10.8', 'IT'),
('tma_materiali_ripetibili', 'OLL', 'olla', 'Forma chiusa', '10.8', 'IT'),
('tma_materiali_ripetibili', 'PEN', 'pentola', 'Forma da cucina', '10.8', 'IT'),
('tma_materiali_ripetibili', 'ANF', 'anfora', 'Contenitore da trasporto', '10.8', 'IT'),
-- Forme metalliche
('tma_materiali_ripetibili', 'FIB', 'fibula', 'Elemento di abbigliamento', '10.8', 'IT'),
('tma_materiali_ripetibili', 'ANE', 'anello', 'Ornamento personale', '10.8', 'IT'),
('tma_materiali_ripetibili', 'CHI', 'chiodo', 'Elemento strutturale', '10.8', 'IT');

-- DEFINIZIONE (Column 4 in materials table) - tipologia_sigla 10.9
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
-- Definizioni ceramiche
('tma_materiali_ripetibili', 'ORL', 'orlo', 'Frammento di orlo', '10.9', 'IT'),
('tma_materiali_ripetibili', 'FND', 'fondo', 'Frammento di fondo', '10.9', 'IT'),
('tma_materiali_ripetibili', 'ANS', 'ansa', 'Frammento di ansa', '10.9', 'IT'),
('tma_materiali_ripetibili', 'PAR', 'parete', 'Frammento di parete', '10.9', 'IT'),
('tma_materiali_ripetibili', 'INT', 'integro', 'Oggetto integro', '10.9', 'IT'),
('tma_materiali_ripetibili', 'RIC', 'ricomposto', 'Oggetto ricomposto', '10.9', 'IT'),
-- Definizioni metallo
('tma_materiali_ripetibili', 'LAM', 'lama', 'Utensile', '10.9', 'IT'),
-- Forme vitree
('tma_materiali_ripetibili', 'BOT', 'bottiglia', 'Contenitore', '10.9', 'IT'),
('tma_materiali_ripetibili', 'PER', 'perla', 'Ornamento', '10.9', 'IT'),
-- Oggetti in osso
('tma_materiali_ripetibili', 'AGO', 'ago', 'Strumento da cucito', '10.9', 'IT'),
('tma_materiali_ripetibili', 'SPI', 'spillone', 'Ornamento', '10.9', 'IT'),
('tma_materiali_ripetibili', 'PET', 'pettine', 'Oggetto da toeletta', '10.9', 'IT');

-- Main TMA table fields with numeric codes
-- Location type - ldct field - tipologia_sigla 10.10
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_materiali_archeologici', 'DEP', 'deposito', 'Deposito archeologico', '10.10', 'IT'),
('tma_materiali_archeologici', 'MAG', 'magazzino', 'Magazzino', '10.10', 'IT'),
('tma_materiali_archeologici', 'LAB', 'laboratorio', 'Laboratorio', '10.10', 'IT'),
('tma_materiali_archeologici', 'MUS', 'museo', 'Museo', '10.10', 'IT');

-- Acquisition type - aint field - tipologia_sigla 10.11
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_materiali_archeologici', 'ICD', 'ICCD', 'Istituto Centrale per il Catalogo e la Documentazione', '10.11', 'IT'),
('tma_materiali_archeologici', 'SCA', 'scavo', 'Scavo archeologico', '10.11', 'IT'),
('tma_materiali_archeologici', 'RIC', 'ricognizione', 'Ricognizione di superficie', '10.11', 'IT'),
('tma_materiali_archeologici', 'RIN', 'rinvenimento', 'Rinvenimento fortuito', '10.11', 'IT');

-- Photo type - ftap field - tipologia_sigla 10.12
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_materiali_archeologici', 'DIG', 'digitale', 'Fotografia digitale', '10.12', 'IT'),
('tma_materiali_archeologici', 'ANA', 'analogica', 'Fotografia analogica', '10.12', 'IT'),
('tma_materiali_archeologici', 'BN', 'b/n', 'Bianco e nero', '10.12', 'IT'),
('tma_materiali_archeologici', 'COL', 'colore', 'A colori', '10.12', 'IT');

-- Drawing type - drat field - tipologia_sigla 10.13
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_materiali_archeologici', 'RIL', 'rilievo', 'Rilievo archeologico', '10.13', 'IT'),
('tma_materiali_archeologici', 'SCH', 'schizzo', 'Schizzo a mano', '10.13', 'IT'),
('tma_materiali_archeologici', 'PLA', 'pianta', 'Pianta planimetrica', '10.13', 'IT'),
('tma_materiali_archeologici', 'SEZ', 'sezione', 'Sezione stratigrafica', '10.13', 'IT'),
('tma_materiali_archeologici', 'PRO', 'prospetto', 'Prospetto architettonico', '10.13', 'IT');

-- Conservation status - stcc field - tipologia_sigla 10.14
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_materiali_archeologici', 'BUO', 'buono', 'Stato di conservazione buono', '10.14', 'IT'),
('tma_materiali_archeologici', 'DIS', 'discreto', 'Stato di conservazione discreto', '10.14', 'IT'),
('tma_materiali_archeologici', 'CAT', 'cattivo', 'Stato di conservazione cattivo', '10.14', 'IT'),
('tma_materiali_archeologici', 'PES', 'pessimo', 'Stato di conservazione pessimo', '10.14', 'IT'),
('tma_materiali_archeologici', 'FRA', 'frammentario', 'Stato frammentario', '10.14', 'IT');

-- Verify the updates
SELECT COUNT(*) as total_tma_vocabularies, tipologia_sigla, nome_tabella
FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella IN ('tma_materiali_archeologici', 'tma_materiali_ripetibili')
GROUP BY tipologia_sigla, nome_tabella
ORDER BY tipologia_sigla;