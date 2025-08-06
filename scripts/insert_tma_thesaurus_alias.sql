-- SQL script to insert TMA thesaurus with correct alias table names
-- This script uses friendly names for UI display while maintaining backward compatibility

-- First, clean up any existing entries
DELETE FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella IN ('tma_table', 'tma_materiali_table', 'TMA materiali archeologici', 'TMA materiali ripetibili', 'TMA Materiali Ripetibili', 'tma_materiali_archeologici', 'tma_materiali_ripetibili');

-- Materials table fields (TMA materiali ripetibili)
-- MATERIALE (Column 0) - tipologia_sigla 10.4
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('TMA Materiali Ripetibili', 'CER', 'ceramica', 'Materiale ceramico', '10.4', 'IT'),
('TMA Materiali Ripetibili', 'VET', 'vetro', 'Materiale vitreo', '10.4', 'IT'),
('TMA Materiali Ripetibili', 'MET', 'metallo', 'argento, bronzo, oro, piombo, rame', '10.4', 'IT'),
('TMA Materiali Ripetibili', 'FIT', 'materiale fittile', 'argilla', '10.4', 'IT'),
('TMA Materiali Ripetibili', 'LIT', 'materiale litico', 'oggetti in pietra', '10.4', 'IT'),
('TMA Materiali Ripetibili', 'IND', 'industria litica', 'scheggiata, pesante', '10.4', 'IT'),
('TMA Materiali Ripetibili', 'OSS', 'osso', 'Materiale osseo', '10.4', 'IT'),
('TMA Materiali Ripetibili', 'AVO', 'avorio', 'Materiale eburneo', '10.4', 'IT'),
('TMA Materiali Ripetibili', 'ROS', 'resti osteologici', 'Resti ossei', '10.4', 'IT'),
('TMA Materiali Ripetibili', 'LEG', 'legno', 'Materiale ligneo', '10.4', 'IT'),
('TMA Materiali Ripetibili', 'ORG', 'materiale organico', 'carbone, resti animali', '10.4', 'IT'),
('TMA Materiali Ripetibili', 'TER', 'campioni di terra', 'Campioni di sedimento', '10.4', 'IT'),
('TMA Materiali Ripetibili', 'ALT', 'altri materiali', 'pasta vitrea, cristallo di rocca, ocra', '10.4', 'IT');

-- CATEGORIA (Column 1) - tipologia_sigla 10.5
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('TMA Materiali Ripetibili', 'CC', 'ceramica comune', 'Ceramica di uso comune', '10.5', 'IT'),
('TMA Materiali Ripetibili', 'CF', 'ceramica fine', 'Ceramica da mensa fine', '10.5', 'IT'),
('TMA Materiali Ripetibili', 'CK', 'ceramica da cucina', 'Ceramica da fuoco', '10.5', 'IT'),
('TMA Materiali Ripetibili', 'CM', 'ceramica da mensa', 'Ceramica da tavola', '10.5', 'IT'),
('TMA Materiali Ripetibili', 'ANF', 'anfore', 'Contenitori da trasporto', '10.5', 'IT'),
('TMA Materiali Ripetibili', 'LUC', 'lucerne', 'Illuminazione', '10.5', 'IT'),
('TMA Materiali Ripetibili', 'VF', 'vetro finestra', 'Vetro piano da finestra', '10.5', 'IT'),
('TMA Materiali Ripetibili', 'VC', 'vetro contenitore', 'Contenitori in vetro', '10.5', 'IT'),
('TMA Materiali Ripetibili', 'VO', 'vetro ornamento', 'Oggetti ornamentali', '10.5', 'IT'),
('TMA Materiali Ripetibili', 'BR', 'bronzo', 'Oggetti in bronzo', '10.5', 'IT'),
('TMA Materiali Ripetibili', 'FE', 'ferro', 'Oggetti in ferro', '10.5', 'IT'),
('TMA Materiali Ripetibili', 'PB', 'piombo', 'Oggetti in piombo', '10.5', 'IT'),
('TMA Materiali Ripetibili', 'AG', 'argento', 'Oggetti in argento', '10.5', 'IT'),
('TMA Materiali Ripetibili', 'AU', 'oro', 'Oggetti in oro', '10.5', 'IT'),
('TMA Materiali Ripetibili', 'LAT', 'laterizi', 'Mattoni e tegole', '10.5', 'IT'),
('TMA Materiali Ripetibili', 'INT', 'intonaco', 'Intonaco dipinto', '10.5', 'IT'),
('TMA Materiali Ripetibili', 'MOS', 'mosaico', 'Tessere musive', '10.5', 'IT');

-- CLASSE (Column 2) - tipologia_sigla 10.6
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('TMA Materiali Ripetibili', 'TS', 'terra sigillata', 'Terra sigillata', '10.6', 'IT'),
('TMA Materiali Ripetibili', 'TSI', 'terra sigillata italica', 'Produzione italica', '10.6', 'IT'),
('TMA Materiali Ripetibili', 'TSA', 'terra sigillata africana', 'Produzione africana', '10.6', 'IT'),
('TMA Materiali Ripetibili', 'TSG', 'terra sigillata gallica', 'Produzione gallica', '10.6', 'IT'),
('TMA Materiali Ripetibili', 'PF', 'pareti fini', 'Ceramica a pareti sottili', '10.6', 'IT'),
('TMA Materiali Ripetibili', 'VN', 'vernice nera', 'Ceramica a vernice nera', '10.6', 'IT'),
('TMA Materiali Ripetibili', 'MED', 'maiolica', 'Ceramica medievale', '10.6', 'IT'),
('TMA Materiali Ripetibili', 'VS', 'vetro soffiato', 'Tecnica a soffio', '10.6', 'IT'),
('TMA Materiali Ripetibili', 'VF', 'vetro fuso', 'Tecnica a fusione', '10.6', 'IT'),
('TMA Materiali Ripetibili', 'MON', 'moneta', 'Numismatica', '10.6', 'IT'),
('TMA Materiali Ripetibili', 'STR', 'strumento', 'Strumenti e utensili', '10.6', 'IT'),
('TMA Materiali Ripetibili', 'ORN', 'ornamento', 'Oggetti di ornamento', '10.6', 'IT');

-- PREC. TIPOLOGICA (Column 3) - tipologia_sigla 10.8
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('TMA Materiali Ripetibili', 'PIA', 'piatto', 'Forma aperta', '10.8', 'IT'),
('TMA Materiali Ripetibili', 'COP', 'coppa', 'Forma aperta', '10.8', 'IT'),
('TMA Materiali Ripetibili', 'BIC', 'bicchiere', 'Forma potoria', '10.8', 'IT'),
('TMA Materiali Ripetibili', 'BOC', 'boccale', 'Forma potoria', '10.8', 'IT'),
('TMA Materiali Ripetibili', 'OLL', 'olla', 'Forma chiusa', '10.8', 'IT'),
('TMA Materiali Ripetibili', 'PEN', 'pentola', 'Forma da cucina', '10.8', 'IT'),
('TMA Materiali Ripetibili', 'ANF', 'anfora', 'Contenitore da trasporto', '10.8', 'IT'),
('TMA Materiali Ripetibili', 'FIB', 'fibula', 'Elemento di abbigliamento', '10.8', 'IT'),
('TMA Materiali Ripetibili', 'ANE', 'anello', 'Ornamento personale', '10.8', 'IT'),
('TMA Materiali Ripetibili', 'CHI', 'chiodo', 'Elemento strutturale', '10.8', 'IT');

-- DEFINIZIONE (Column 4) - tipologia_sigla 10.9
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('TMA Materiali Ripetibili', 'ORL', 'orlo', 'Frammento di orlo', '10.9', 'IT'),
('TMA Materiali Ripetibili', 'FND', 'fondo', 'Frammento di fondo', '10.9', 'IT'),
('TMA Materiali Ripetibili', 'ANS', 'ansa', 'Frammento di ansa', '10.9', 'IT'),
('TMA Materiali Ripetibili', 'PAR', 'parete', 'Frammento di parete', '10.9', 'IT'),
('TMA Materiali Ripetibili', 'INT', 'integro', 'Oggetto integro', '10.9', 'IT'),
('TMA Materiali Ripetibili', 'RIC', 'ricomposto', 'Oggetto ricomposto', '10.9', 'IT'),
('TMA Materiali Ripetibili', 'LAM', 'lama', 'Utensile', '10.9', 'IT'),
('TMA Materiali Ripetibili', 'BOT', 'bottiglia', 'Contenitore', '10.9', 'IT'),
('TMA Materiali Ripetibili', 'PER', 'perla', 'Ornamento', '10.9', 'IT'),
('TMA Materiali Ripetibili', 'AGO', 'ago', 'Strumento da cucito', '10.9', 'IT'),
('TMA Materiali Ripetibili', 'SPI', 'spillone', 'Ornamento', '10.9', 'IT'),
('TMA Materiali Ripetibili', 'PET', 'pettine', 'Oggetto da toeletta', '10.9', 'IT');

-- Main TMA table fields (tma_table alias)
-- Location type (ldct) - tipologia_sigla 10.10
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('TMA materiali archeologici', 'DEP', 'deposito', 'Deposito archeologico', '10.10', 'IT'),
('TMA materiali archeologici', 'MAG', 'magazzino', 'Magazzino', '10.10', 'IT'),
('TMA materiali archeologici', 'LAB', 'laboratorio', 'Laboratorio', '10.10', 'IT'),
('TMA materiali archeologici', 'MUS', 'museo', 'Museo', '10.10', 'IT');

-- Acquisition type (aint) - tipologia_sigla 10.11
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('TMA materiali archeologici', 'ICD', 'ICCD', 'Istituto Centrale per il Catalogo e la Documentazione', '10.11', 'IT'),
('TMA materiali archeologici', 'SCA', 'scavo', 'Scavo archeologico', '10.11', 'IT'),
('TMA materiali archeologici', 'RIC', 'ricognizione', 'Ricognizione di superficie', '10.11', 'IT'),
('TMA materiali archeologici', 'RIN', 'rinvenimento', 'Rinvenimento fortuito', '10.11', 'IT');

-- Photo type (ftap) - tipologia_sigla 10.12
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('TMA materiali archeologici', 'DIG', 'digitale', 'Fotografia digitale', '10.12', 'IT'),
('TMA materiali archeologici', 'ANA', 'analogica', 'Fotografia analogica', '10.12', 'IT'),
('TMA materiali archeologici', 'BN', 'b/n', 'Bianco e nero', '10.12', 'IT'),
('TMA materiali archeologici', 'COL', 'colore', 'A colori', '10.12', 'IT');

-- Drawing type (drat) - tipologia_sigla 10.13
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('TMA materiali archeologici', 'RIL', 'rilievo', 'Rilievo archeologico', '10.13', 'IT'),
('TMA materiali archeologici', 'SCH', 'schizzo', 'Schizzo a mano', '10.13', 'IT'),
('TMA materiali archeologici', 'PLA', 'pianta', 'Pianta planimetrica', '10.13', 'IT'),
('TMA materiali archeologici', 'SEZ', 'sezione', 'Sezione stratigrafica', '10.13', 'IT'),
('TMA materiali archeologici', 'PRO', 'prospetto', 'Prospetto architettonico', '10.13', 'IT');

-- Conservation status (stcc) - tipologia_sigla 10.14
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('TMA materiali archeologici', 'BUO', 'buono', 'Stato di conservazione buono', '10.14', 'IT'),
('TMA materiali archeologici', 'DIS', 'discreto', 'Stato di conservazione discreto', '10.14', 'IT'),
('TMA materiali archeologici', 'CAT', 'cattivo', 'Stato di conservazione cattivo', '10.14', 'IT'),
('TMA materiali archeologici', 'PES', 'pessimo', 'Stato di conservazione pessimo', '10.14', 'IT'),
('TMA materiali archeologici', 'FRA', 'frammentario', 'Stato frammentario', '10.14', 'IT');

-- Material type (ogtm) for main TMA table - tipologia_sigla 10.15
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('TMA materiali archeologici', 'CER', 'ceramica', 'Materiale ceramico', '10.15', 'IT'),
('TMA materiali archeologici', 'VET', 'vetro', 'Materiale vitreo', '10.15', 'IT'),
('TMA materiali archeologici', 'MET', 'metallo', 'Materiali metallici', '10.15', 'IT'),
('TMA materiali archeologici', 'ORG', 'organico', 'Materiali organici', '10.15', 'IT'),
('TMA materiali archeologici', 'LIT', 'litico', 'Materiali litici', '10.15', 'IT'),
('TMA materiali archeologici', 'MIS', 'misto', 'Materiali misti', '10.15', 'IT');

-- Add TMA tables to configuration manager thesaurus
INSERT INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua) VALUES
('pyarchinit_nome_tabelle', '27', 'TMA materiali archeologici', 'Tabella Materiali Archeologici', 'n', 'IT'),
('pyarchinit_nome_tabelle', '28', 'TMA Materiali Ripetibili', 'Tabella Materiali Ripetibili TMA', 'n', 'IT');

-- Verify the insertion
SELECT COUNT(*) as total, nome_tabella, tipologia_sigla
FROM pyarchinit_thesaurus_sigle 
WHERE nome_tabella IN ('TMA materiali archeologici', 'TMA Materiali Ripetibili')
GROUP BY nome_tabella, tipologia_sigla
ORDER BY nome_tabella, tipologia_sigla;