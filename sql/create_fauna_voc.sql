-- Tabella vocabolario controllato per fauna_table
-- Gestisce le liste controllate per i vari campi

CREATE TABLE IF NOT EXISTS "fauna_voc" (
    id_voc INTEGER PRIMARY KEY AUTOINCREMENT,
    campo TEXT NOT NULL,              -- Nome del campo a cui si riferisce
    valore TEXT NOT NULL,             -- Valore della lista controllata
    descrizione TEXT DEFAULT '',      -- Descrizione opzionale del valore
    ordinamento INTEGER DEFAULT 0,    -- Ordine di visualizzazione
    attivo BOOLEAN DEFAULT 1,         -- Se il valore è attivo/utilizzabile
    UNIQUE(campo, valore)
);

-- Popolare il vocabolario con i valori standard

-- ID 10: METODOLOGIA DI RECUPERO
INSERT OR IGNORE INTO fauna_voc (campo, valore, ordinamento) VALUES
    ('metodologia_recupero', 'A MANO', 1),
    ('metodologia_recupero', 'SETACCIO', 2),
    ('metodologia_recupero', 'FLOTTAZIONE', 3);

-- ID 11: CONTESTO
INSERT OR IGNORE INTO fauna_voc (campo, valore, ordinamento) VALUES
    ('contesto', 'FUNERARIO', 1),
    ('contesto', 'ABITATIVO', 2),
    ('contesto', 'PRODUTTIVO', 3),
    ('contesto', 'IPOGEO', 4),
    ('contesto', 'CULTUALE', 5),
    ('contesto', 'ALTRO', 6);

-- ID 13: RESTI IN CONNESSIONE ANATOMICA
INSERT OR IGNORE INTO fauna_voc (campo, valore, ordinamento) VALUES
    ('resti_connessione_anatomica', 'SI', 1),
    ('resti_connessione_anatomica', 'NO', 2),
    ('resti_connessione_anatomica', 'PARZIALE', 3);

-- ID 14: TIPOLOGIA DI ACCUMULO
INSERT OR IGNORE INTO fauna_voc (campo, valore, ordinamento) VALUES
    ('tipologia_accumulo', 'CONCENTRAZIONE LOCALIZZATA', 1),
    ('tipologia_accumulo', 'RESTI SELEZIONATI', 2),
    ('tipologia_accumulo', 'RESTI SPORADICI', 3),
    ('tipologia_accumulo', 'NATURALE', 4),
    ('tipologia_accumulo', 'ANTROPICO', 5);

-- ID 15: DEPOSIZIONE
INSERT OR IGNORE INTO fauna_voc (campo, valore, ordinamento) VALUES
    ('deposizione', 'DEPOSIZIONE PRIMARIA', 1),
    ('deposizione', 'DEPOSIZIONE SECONDARIA', 2),
    ('deposizione', 'RIMANEGGIATA', 3);

-- ID 16: NUMERO STIMATO RESTI OSTEOLOGICI
INSERT OR IGNORE INTO fauna_voc (campo, valore, ordinamento) VALUES
    ('numero_stimato_resti', 'Pochi (1-10)', 1),
    ('numero_stimato_resti', 'Discreti (10-30)', 2),
    ('numero_stimato_resti', 'Numerosi (30-100)', 3),
    ('numero_stimato_resti', 'Abbondanti (>100)', 4);

-- ID 18: SPECIE (esempi comuni - da integrare con database completo)
INSERT OR IGNORE INTO fauna_voc (campo, valore, ordinamento) VALUES
    ('specie', 'Bos taurus', 1),
    ('specie', 'Sus scrofa domesticus', 2),
    ('specie', 'Ovis aries', 3),
    ('specie', 'Capra hircus', 4),
    ('specie', 'Equus caballus', 5),
    ('specie', 'Equus asinus', 6),
    ('specie', 'Canis familiaris', 7),
    ('specie', 'Felis catus', 8),
    ('specie', 'Gallus gallus', 9),
    ('specie', 'Cervus elaphus', 10),
    ('specie', 'Sus scrofa', 11),
    ('specie', 'Capreolus capreolus', 12),
    ('specie', 'Lepus europaeus', 13),
    ('specie', 'Oryctolagus cuniculus', 14),
    ('specie', 'Indeterminata', 99);

-- ID 19: PARTI SCHELETRICHE PRESENTI
INSERT OR IGNORE INTO fauna_voc (campo, valore, ordinamento) VALUES
    ('parti_scheletriche', 'Cranio', 1),
    ('parti_scheletriche', 'Mandibola', 2),
    ('parti_scheletriche', 'Vertebre cervicali', 3),
    ('parti_scheletriche', 'Vertebre toraciche', 4),
    ('parti_scheletriche', 'Vertebre lombari', 5),
    ('parti_scheletriche', 'Sacro', 6),
    ('parti_scheletriche', 'Coste', 7),
    ('parti_scheletriche', 'Scapola', 8),
    ('parti_scheletriche', 'Omero', 9),
    ('parti_scheletriche', 'Radio', 10),
    ('parti_scheletriche', 'Ulna', 11),
    ('parti_scheletriche', 'Carpo', 12),
    ('parti_scheletriche', 'Metacarpo', 13),
    ('parti_scheletriche', 'Pelvi', 14),
    ('parti_scheletriche', 'Femore', 15),
    ('parti_scheletriche', 'Tibia', 16),
    ('parti_scheletriche', 'Fibula', 17),
    ('parti_scheletriche', 'Tarso', 18),
    ('parti_scheletriche', 'Metatarso', 19),
    ('parti_scheletriche', 'Falangi', 20),
    ('parti_scheletriche', 'Metapodio', 21);

-- ELEMENTO ANATOMICO (per tabella misure - elementi misurabili)
INSERT OR IGNORE INTO fauna_voc (campo, valore, ordinamento) VALUES
    ('elemento_anatomico', 'Astragalo', 1),
    ('elemento_anatomico', 'Calcagno', 2),
    ('elemento_anatomico', 'Falange I', 3),
    ('elemento_anatomico', 'Falange II', 4),
    ('elemento_anatomico', 'Falange III', 5),
    ('elemento_anatomico', 'Femore', 6),
    ('elemento_anatomico', 'Metacarpo', 7),
    ('elemento_anatomico', 'Metatarso', 8),
    ('elemento_anatomico', 'Omero', 9),
    ('elemento_anatomico', 'Radio', 10),
    ('elemento_anatomico', 'Scapola', 11),
    ('elemento_anatomico', 'Tibia', 12),
    ('elemento_anatomico', 'Ulna', 13),
    ('elemento_anatomico', 'Atlante', 14),
    ('elemento_anatomico', 'Epistrofeo', 15),
    ('elemento_anatomico', 'Pelvi', 16),
    ('elemento_anatomico', 'Mandibola', 17),
    ('elemento_anatomico', 'Altro', 99);

-- ID 21: STATO DI FRAMMENTAZIONE
INSERT OR IGNORE INTO fauna_voc (campo, valore, ordinamento) VALUES
    ('stato_frammentazione', 'SI', 1),
    ('stato_frammentazione', 'NO', 2),
    ('stato_frammentazione', 'PARZIALE', 3);

-- ID 22: TRACCE DI COMBUSTIONE
INSERT OR IGNORE INTO fauna_voc (campo, valore, ordinamento) VALUES
    ('tracce_combustione', 'SI', 1),
    ('tracce_combustione', 'NO', 2),
    ('tracce_combustione', 'SCARSE', 3),
    ('tracce_combustione', 'DIFFUSE', 4);

-- ID 24: TIPO DI COMBUSTIONE
INSERT OR IGNORE INTO fauna_voc (campo, valore, ordinamento) VALUES
    ('tipo_combustione', 'ACCIDENTALE', 1),
    ('tipo_combustione', 'INTENZIONALE', 2),
    ('tipo_combustione', 'NATURALE', 3),
    ('tipo_combustione', 'ANTROPICA', 4);

-- ID 25: SEGNI TAFONOMICI EVIDENTI
INSERT OR IGNORE INTO fauna_voc (campo, valore, ordinamento) VALUES
    ('segni_tafonomici_evidenti', 'SI', 1),
    ('segni_tafonomici_evidenti', 'NO', 2),
    ('segni_tafonomici_evidenti', 'SCARSI', 3),
    ('segni_tafonomici_evidenti', 'DIFFUSI', 4);

-- ID 26: CARATTERIZZAZIONE SEGNI TAFONOMICI
INSERT OR IGNORE INTO fauna_voc (campo, valore, ordinamento) VALUES
    ('caratterizzazione_segni_tafonomici', 'ANTROPICA', 1),
    ('caratterizzazione_segni_tafonomici', 'NATURALE', 2);

-- ID 27: STATO DI CONSERVAZIONE
INSERT OR IGNORE INTO fauna_voc (campo, valore, descrizione, ordinamento) VALUES
    ('stato_conservazione', '0', 'Pessimo', 0),
    ('stato_conservazione', '1', 'Molto cattivo', 1),
    ('stato_conservazione', '2', 'Cattivo', 2),
    ('stato_conservazione', '3', 'Discreto', 3),
    ('stato_conservazione', '4', 'Buono', 4),
    ('stato_conservazione', '5', 'Ottimo', 5);

-- Indici per migliorare le performance
CREATE INDEX IF NOT EXISTS idx_fauna_voc_campo ON fauna_voc(campo);
CREATE INDEX IF NOT EXISTS idx_fauna_voc_attivo ON fauna_voc(attivo);