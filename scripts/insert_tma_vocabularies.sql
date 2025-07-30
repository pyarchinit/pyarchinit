-- SQL script to insert TMA vocabularies into pyarchinit_thesaurus_sigle table
-- Based on TMA_vocabolari.xlsx from desktop

-- Create thesaurus table if it doesn't exist
CREATE TABLE IF NOT EXISTS pyarchinit_thesaurus_sigle (
    id_thesaurus_sigle INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_tabella TEXT,
    sigla TEXT,
    sigla_estesa TEXT,
    descrizione TEXT,
    tipologia_sigla TEXT,
    lingua TEXT,
    UNIQUE(id_thesaurus_sigle)
);

-- Delete existing TMA vocabulary entries to avoid duplicates
DELETE FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella = 'tma_materiali_archeologici' 
   AND tipologia_sigla IN ('ldct', 'aint', 'dtzg', 'ftap', 'drat', 'stcc');

DELETE FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella = 'tma_materiali_ripetibili' 
   AND tipologia_sigla IN ('10.4', '10.5', '10.6', '10.8', '10.9');

-- Insert TMA vocabularies for materials table fields
-- Based on TMA_vocabolari.xlsx and using the proper tipologia_sigla codes from TMA.py
-- 10.4 = Materiale, 10.5 = Categoria, 10.6 = Classe, 10.8 = Prec. tipologica, 10.9 = Definizione

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
('tma_materiali_ripetibili', 'VF', 'vetro da finestra', 'Vetro piano', '10.5', 'IT'),
('tma_materiali_ripetibili', 'VM', 'vetro da mensa', 'Vasellame vitreo', '10.5', 'IT'),
('tma_materiali_ripetibili', 'VD', 'vetro decorativo', 'Oggetti ornamentali', '10.5', 'IT'),
-- Metallo categories
('tma_materiali_ripetibili', 'MON', 'monete', 'Numerario', '10.5', 'IT'),
('tma_materiali_ripetibili', 'ORN', 'oggetti di ornamento', 'Ornamenti personali', '10.5', 'IT'),
('tma_materiali_ripetibili', 'UTN', 'utensili', 'Strumenti da lavoro', '10.5', 'IT'),
('tma_materiali_ripetibili', 'ARM', 'armi', 'Armamento', '10.5', 'IT'),
-- Osso categories
('tma_materiali_ripetibili', 'OL', 'oggetti lavorati', 'Manufatti in osso', '10.5', 'IT'),
('tma_materiali_ripetibili', 'FAU', 'resti faunistici', 'Fauna', '10.5', 'IT'),
('tma_materiali_ripetibili', 'STR', 'strumenti', 'Strumenti in osso', '10.5', 'IT');

-- CLASSE (Column 2 in materials table) - tipologia_sigla 10.6
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
-- Ceramica fina classes
('tma_materiali_ripetibili', 'TSI', 'terra sigillata italica', 'Produzione italica', '10.6', 'IT'),
('tma_materiali_ripetibili', 'TSA', 'terra sigillata africana', 'Produzione africana', '10.6', 'IT'),
('tma_materiali_ripetibili', 'TSG', 'terra sigillata gallica', 'Produzione gallica', '10.6', 'IT'),
('tma_materiali_ripetibili', 'VN', 'vernice nera', 'Ceramica a vernice nera', '10.6', 'IT'),
('tma_materiali_ripetibili', 'PS', 'pareti sottili', 'Ceramica a pareti sottili', '10.6', 'IT'),
-- Ceramica comune classes
('tma_materiali_ripetibili', 'ACR', 'acroma', 'Ceramica acroma', '10.6', 'IT'),
('tma_materiali_ripetibili', 'DIP', 'dipinta', 'Ceramica dipinta', '10.6', 'IT'),
('tma_materiali_ripetibili', 'VER', 'verniciata', 'Ceramica verniciata', '10.6', 'IT'),
-- Anfore classes
('tma_materiali_ripetibili', 'AFI', 'anfora italica', 'Produzione italica', '10.6', 'IT'),
('tma_materiali_ripetibili', 'AFA', 'anfora africana', 'Produzione africana', '10.6', 'IT'),
('tma_materiali_ripetibili', 'AFS', 'anfora spagnola', 'Produzione iberica', '10.6', 'IT'),
('tma_materiali_ripetibili', 'AFO', 'anfora orientale', 'Produzione orientale', '10.6', 'IT');

-- DEFINIZIONE (Column 4 in materials table) - tipologia_sigla 10.9
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
-- Forme ceramiche
('tma_materiali_ripetibili', 'PIA', 'piatto', 'Forma aperta', '10.9', 'IT'),
('tma_materiali_ripetibili', 'CIO', 'ciotola', 'Forma aperta', '10.9', 'IT'),
('tma_materiali_ripetibili', 'COP', 'coppa', 'Forma aperta', '10.9', 'IT'),
('tma_materiali_ripetibili', 'BRO', 'brocca', 'Forma chiusa', '10.9', 'IT'),
('tma_materiali_ripetibili', 'OLL', 'olla', 'Forma chiusa', '10.9', 'IT'),
('tma_materiali_ripetibili', 'PEN', 'pentola', 'Forma da fuoco', '10.9', 'IT'),
('tma_materiali_ripetibili', 'TEG', 'tegola', 'Laterizio', '10.9', 'IT'),
('tma_materiali_ripetibili', 'MAT', 'mattone', 'Laterizio', '10.9', 'IT'),
-- Oggetti metallici
('tma_materiali_ripetibili', 'FIB', 'fibula', 'Ornamento', '10.9', 'IT'),
('tma_materiali_ripetibili', 'ANE', 'anello', 'Ornamento', '10.9', 'IT'),
('tma_materiali_ripetibili', 'BRA', 'bracciale', 'Ornamento', '10.9', 'IT'),
('tma_materiali_ripetibili', 'CHI', 'chiodo', 'Elemento strutturale', '10.9', 'IT'),
('tma_materiali_ripetibili', 'LAM', 'lama', 'Utensile', '10.9', 'IT'),
-- Forme vitree
('tma_materiali_ripetibili', 'BOT', 'bottiglia', 'Contenitore', '10.9', 'IT'),
('tma_materiali_ripetibili', 'BIC', 'bicchiere', 'Forma potoria', '10.9', 'IT'),
('tma_materiali_ripetibili', 'PER', 'perla', 'Ornamento', '10.9', 'IT'),
-- Oggetti in osso
('tma_materiali_ripetibili', 'AGO', 'ago', 'Strumento da cucito', '10.9', 'IT'),
('tma_materiali_ripetibili', 'SPI', 'spillone', 'Ornamento', '10.9', 'IT'),
('tma_materiali_ripetibili', 'PET', 'pettine', 'Oggetto da toeletta', '10.9', 'IT');

-- PRECISAZIONE TIPOLOGICA (Column 3 in materials table) - tipologia_sigla 10.8
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
-- Tipologie ceramiche
('tma_materiali_ripetibili', 'DR1', 'Dressel 1', 'Anfora vinaria', '10.8', 'IT'),
('tma_materiali_ripetibili', 'DR2', 'Dressel 2-4', 'Anfora vinaria', '10.8', 'IT'),
('tma_materiali_ripetibili', 'AFR', 'Africana', 'Anfora africana', '10.8', 'IT'),
('tma_materiali_ripetibili', 'HAY', 'Hayes', 'Forma Hayes', '10.8', 'IT'),
('tma_materiali_ripetibili', 'LAM', 'Lamboglia', 'Forma Lamboglia', '10.8', 'IT'),
-- Tecniche di lavorazione vetro
('tma_materiali_ripetibili', 'SOF', 'vetro soffiato', 'Tecnica a soffio', '10.8', 'IT'),
('tma_materiali_ripetibili', 'PRE', 'vetro pressato', 'Tecnica a stampo', '10.8', 'IT'),
('tma_materiali_ripetibili', 'MOS', 'vetro mosaico', 'Tecnica a mosaico', '10.8', 'IT'),
-- Leghe metalliche
('tma_materiali_ripetibili', 'BRZ', 'bronzo', 'Lega di rame e stagno', '10.8', 'IT'),
('tma_materiali_ripetibili', 'FER', 'ferro', 'Ferro battuto o fuso', '10.8', 'IT'),
('tma_materiali_ripetibili', 'ARG', 'argento', 'Argento puro o lega', '10.8', 'IT'),
('tma_materiali_ripetibili', 'AUR', 'oro', 'Oro puro o lega', '10.8', 'IT'),
('tma_materiali_ripetibili', 'PIO', 'piombo', 'Piombo puro', '10.8', 'IT'),
('tma_materiali_ripetibili', 'RAM', 'rame', 'Rame puro', '10.8', 'IT');

-- Add location type vocabularies - ldct field
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_materiali_ripetibili', 'MAG', 'magazzino', 'Magazzino archeologico', 'ldct', 'IT'),
('tma_materiali_ripetibili', 'DEP', 'deposito', 'Deposito temporaneo', 'ldct', 'IT'),
('tma_materiali_ripetibili', 'MUS', 'museo', 'Museo archeologico', 'ldct', 'IT'),
('tma_materiali_ripetibili', 'LAB', 'laboratorio', 'Laboratorio di restauro', 'ldct', 'IT');

-- Add acquisition type vocabularies - aint field
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_materiali_ripetibili', 'SCA', 'scavo', 'Scavo archeologico', 'aint', 'IT'),
('tma_materiali_ripetibili', 'RIC', 'ricognizione', 'Ricognizione di superficie', 'aint', 'IT'),
('tma_materiali_ripetibili', 'FOR', 'rinvenimento fortuito', 'Rinvenimento casuale', 'aint', 'IT'),
('tma_materiali_ripetibili', 'DON', 'donazione', 'Donazione privata', 'aint', 'IT'),
('tma_materiali_ripetibili', 'ACQ', 'acquisto', 'Acquisto legale', 'aint', 'IT');

-- Add chronological range vocabularies - dtzg field
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_materiali_ripetibili', 'BR', 'età del bronzo', 'II millennio a.C.', 'dtzg', 'IT'),
('tma_materiali_ripetibili', 'FE', 'età del ferro', 'I millennio a.C.', 'dtzg', 'IT'),
('tma_materiali_ripetibili', 'ROM', 'età romana', 'III sec. a.C. - V sec. d.C.', 'dtzg', 'IT'),
('tma_materiali_ripetibili', 'IMP', 'età imperiale', 'I - III sec. d.C.', 'dtzg', 'IT'),
('tma_materiali_ripetibili', 'TAR', 'età tardoantica', 'IV - VII sec. d.C.', 'dtzg', 'IT'),
('tma_materiali_ripetibili', 'MED', 'età medievale', 'VII - XV sec. d.C.', 'dtzg', 'IT'),
('tma_materiali_ripetibili', 'MOD', 'età moderna', 'XVI - XVIII sec. d.C.', 'dtzg', 'IT');

-- Insert vocabularies for tma_materiali_ripetibili table (materials table)
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
('tma_materiali_ripetibili', 'VF', 'vetro da finestra', 'Vetro piano', '10.5', 'IT'),
('tma_materiali_ripetibili', 'VM', 'vetro da mensa', 'Vasellame vitreo', '10.5', 'IT'),
('tma_materiali_ripetibili', 'VD', 'vetro decorativo', 'Oggetti ornamentali', '10.5', 'IT'),
-- Metallo categories
('tma_materiali_ripetibili', 'MON', 'monete', 'Numerario', '10.5', 'IT'),
('tma_materiali_ripetibili', 'ORN', 'oggetti di ornamento', 'Ornamenti personali', '10.5', 'IT'),
('tma_materiali_ripetibili', 'UTN', 'utensili', 'Strumenti da lavoro', '10.5', 'IT'),
('tma_materiali_ripetibili', 'ARM', 'armi', 'Armamento', '10.5', 'IT'),
-- Osso categories
('tma_materiali_ripetibili', 'OL', 'oggetti lavorati', 'Manufatti in osso', '10.5', 'IT'),
('tma_materiali_ripetibili', 'FAU', 'resti faunistici', 'Fauna', '10.5', 'IT'),
('tma_materiali_ripetibili', 'STR', 'strumenti', 'Strumenti in osso', '10.5', 'IT');

-- CLASSE (Column 2 in materials table) - tipologia_sigla 10.6
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
-- Ceramica fina classes
('tma_materiali_ripetibili', 'TSI', 'terra sigillata italica', 'Produzione italica', '10.6', 'IT'),
('tma_materiali_ripetibili', 'TSA', 'terra sigillata africana', 'Produzione africana', '10.6', 'IT'),
('tma_materiali_ripetibili', 'TSG', 'terra sigillata gallica', 'Produzione gallica', '10.6', 'IT'),
('tma_materiali_ripetibili', 'VN', 'vernice nera', 'Ceramica a vernice nera', '10.6', 'IT'),
('tma_materiali_ripetibili', 'PS', 'pareti sottili', 'Ceramica a pareti sottili', '10.6', 'IT'),
-- Ceramica comune classes
('tma_materiali_ripetibili', 'ACR', 'acroma', 'Ceramica acroma', '10.6', 'IT'),
('tma_materiali_ripetibili', 'DIP', 'dipinta', 'Ceramica dipinta', '10.6', 'IT'),
('tma_materiali_ripetibili', 'VER', 'verniciata', 'Ceramica verniciata', '10.6', 'IT'),
-- Anfore classes
('tma_materiali_ripetibili', 'AFI', 'anfora italica', 'Produzione italica', '10.6', 'IT'),
('tma_materiali_ripetibili', 'AFA', 'anfora africana', 'Produzione africana', '10.6', 'IT'),
('tma_materiali_ripetibili', 'AFS', 'anfora spagnola', 'Produzione iberica', '10.6', 'IT'),
('tma_materiali_ripetibili', 'AFO', 'anfora orientale', 'Produzione orientale', '10.6', 'IT');

-- PRECISAZIONE TIPOLOGICA (Column 3 in materials table) - tipologia_sigla 10.8
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
-- Tipologie ceramiche
('tma_materiali_ripetibili', 'DR1', 'Dressel 1', 'Anfora vinaria', '10.8', 'IT'),
('tma_materiali_ripetibili', 'DR2', 'Dressel 2-4', 'Anfora vinaria', '10.8', 'IT'),
('tma_materiali_ripetibili', 'AFR', 'Africana', 'Anfora africana', '10.8', 'IT'),
('tma_materiali_ripetibili', 'HAY', 'Hayes', 'Forma Hayes', '10.8', 'IT'),
('tma_materiali_ripetibili', 'LAM', 'Lamboglia', 'Forma Lamboglia', '10.8', 'IT'),
-- Tecniche di lavorazione vetro
('tma_materiali_ripetibili', 'SOF', 'vetro soffiato', 'Tecnica a soffio', '10.8', 'IT'),
('tma_materiali_ripetibili', 'PRE', 'vetro pressato', 'Tecnica a stampo', '10.8', 'IT'),
('tma_materiali_ripetibili', 'MOS', 'vetro mosaico', 'Tecnica a mosaico', '10.8', 'IT'),
-- Leghe metalliche
('tma_materiali_ripetibili', 'BRZ', 'bronzo', 'Lega di rame e stagno', '10.8', 'IT'),
('tma_materiali_ripetibili', 'FER', 'ferro', 'Ferro battuto o fuso', '10.8', 'IT'),
('tma_materiali_ripetibili', 'ARG', 'argento', 'Argento puro o lega', '10.8', 'IT'),
('tma_materiali_ripetibili', 'AUR', 'oro', 'Oro puro o lega', '10.8', 'IT'),
('tma_materiali_ripetibili', 'PIO', 'piombo', 'Piombo puro', '10.8', 'IT'),
('tma_materiali_ripetibili', 'RAM', 'rame', 'Rame puro', '10.8', 'IT');

-- DEFINIZIONE (Column 4 in materials table) - tipologia_sigla 10.9
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
-- Forme ceramiche
('tma_materiali_ripetibili', 'PIA', 'piatto', 'Forma aperta', '10.9', 'IT'),
('tma_materiali_ripetibili', 'CIO', 'ciotola', 'Forma aperta', '10.9', 'IT'),
('tma_materiali_ripetibili', 'COP', 'coppa', 'Forma aperta', '10.9', 'IT'),
('tma_materiali_ripetibili', 'BRO', 'brocca', 'Forma chiusa', '10.9', 'IT'),
('tma_materiali_ripetibili', 'OLL', 'olla', 'Forma chiusa', '10.9', 'IT'),
('tma_materiali_ripetibili', 'PEN', 'pentola', 'Forma da fuoco', '10.9', 'IT'),
('tma_materiali_ripetibili', 'TEG', 'tegola', 'Laterizio', '10.9', 'IT'),
('tma_materiali_ripetibili', 'MAT', 'mattone', 'Laterizio', '10.9', 'IT'),
-- Oggetti metallici
('tma_materiali_ripetibili', 'FIB', 'fibula', 'Ornamento', '10.9', 'IT'),
('tma_materiali_ripetibili', 'ANE', 'anello', 'Ornamento', '10.9', 'IT'),
('tma_materiali_ripetibili', 'BRA', 'bracciale', 'Ornamento', '10.9', 'IT'),
('tma_materiali_ripetibili', 'CHI', 'chiodo', 'Elemento strutturale', '10.9', 'IT'),
('tma_materiali_ripetibili', 'LAM', 'lama', 'Utensile', '10.9', 'IT'),
-- Forme vitree
('tma_materiali_ripetibili', 'BOT', 'bottiglia', 'Contenitore', '10.9', 'IT'),
('tma_materiali_ripetibili', 'BIC', 'bicchiere', 'Forma potoria', '10.9', 'IT'),
('tma_materiali_ripetibili', 'PER', 'perla', 'Ornamento', '10.9', 'IT'),
-- Oggetti in osso
('tma_materiali_ripetibili', 'AGO', 'ago', 'Strumento da cucito', '10.9', 'IT'),
('tma_materiali_ripetibili', 'SPI', 'spillone', 'Ornamento', '10.9', 'IT'),
('tma_materiali_ripetibili', 'PET', 'pettine', 'Oggetto da toeletta', '10.9', 'IT');

-- Documentation photo type vocabularies - ftap field
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_materiali_ripetibili', 'DIG', 'digitale', 'Fotografia digitale', 'ftap', 'IT'),
('tma_materiali_ripetibili', 'ANA', 'analogica', 'Fotografia analogica', 'ftap', 'IT'),
('tma_materiali_ripetibili', 'BN', 'b/n', 'Bianco e nero', 'ftap', 'IT'),
('tma_materiali_ripetibili', 'COL', 'colore', 'A colori', 'ftap', 'IT');

-- Documentation drawing type vocabularies - drat field
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_materiali_ripetibili', 'RIL', 'rilievo', 'Rilievo archeologico', 'drat', 'IT'),
('tma_materiali_ripetibili', 'SCH', 'schizzo', 'Schizzo a mano', 'drat', 'IT'),
('tma_materiali_ripetibili', 'PLA', 'pianta', 'Pianta planimetrica', 'drat', 'IT'),
('tma_materiali_ripetibili', 'SEZ', 'sezione', 'Sezione stratigrafica', 'drat', 'IT'),
('tma_materiali_ripetibili', 'PRO', 'prospetto', 'Prospetto architettonico', 'drat', 'IT');

-- Conservation status vocabularies - stcc field
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_materiali_ripetibili', 'BUO', 'buono', 'Stato di conservazione buono', 'stcc', 'IT'),
('tma_materiali_ripetibili', 'DIS', 'discreto', 'Stato di conservazione discreto', 'stcc', 'IT'),
('tma_materiali_ripetibili', 'CAT', 'cattivo', 'Stato di conservazione cattivo', 'stcc', 'IT'),
('tma_materiali_ripetibili', 'PES', 'pessimo', 'Stato di conservazione pessimo', 'stcc', 'IT'),
('tma_materiali_ripetibili', 'FRA', 'frammentario', 'Stato frammentario', 'stcc', 'IT');

-- Acquisition type vocabularies - aint field (ICCD) for main TMA table
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_materiali_archeologici', 'ICCD', 'ICCD', 'Istituto Centrale per il Catalogo e la Documentazione', 'aint', 'IT'),
('tma_materiali_archeologici', 'SCA', 'scavo', 'Scavo archeologico', 'aint', 'IT'),
('tma_materiali_archeologici', 'RIC', 'ricognizione', 'Ricognizione di superficie', 'aint', 'IT'),
('tma_materiali_archeologici', 'RIN', 'rinvenimento', 'Rinvenimento fortuito', 'aint', 'IT');

-- Location type vocabularies - ldct field for main TMA table
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('tma_materiali_archeologici', 'DEP', 'deposito', 'Deposito archeologico', 'ldct', 'IT'),
('tma_materiali_archeologici', 'MAG', 'magazzino', 'Magazzino', 'ldct', 'IT'),
('tma_materiali_archeologici', 'LAB', 'laboratorio', 'Laboratorio', 'ldct', 'IT'),
('tma_materiali_archeologici', 'MUS', 'museo', 'Museo', 'ldct', 'IT');

-- Query to verify the insertion
SELECT COUNT(*) as total_tma_vocabularies 
FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella IN ('tma_materiali_ripetibili', 'tma_materiali_ripetibili');