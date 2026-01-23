-- Setup Fauna table and thesaurus for SQLite database
-- Run this script on your SQLite database to enable the Fauna form

-- Create fauna_table if it doesn't exist
CREATE TABLE IF NOT EXISTS fauna_table (
    id_fauna INTEGER PRIMARY KEY AUTOINCREMENT,
    id_us INTEGER,
    sito TEXT,
    area TEXT,
    saggio TEXT,
    us TEXT,
    datazione_us TEXT,
    responsabile_scheda TEXT,
    data_compilazione DATE,
    documentazione_fotografica TEXT,
    metodologia_recupero TEXT,
    contesto TEXT,
    descrizione_contesto TEXT,
    resti_connessione_anatomica TEXT,
    tipologia_accumulo TEXT,
    deposizione TEXT,
    numero_stimato_resti TEXT,
    numero_minimo_individui INTEGER,
    specie TEXT,
    parti_scheletriche TEXT,
    specie_psi TEXT,
    misure_ossa TEXT,
    stato_frammentazione TEXT,
    tracce_combustione TEXT,
    combustione_altri_materiali_us INTEGER,
    tipo_combustione TEXT,
    segni_tafonomici_evidenti TEXT,
    caratterizzazione_segni_tafonomici TEXT,
    stato_conservazione TEXT,
    alterazioni_morfologiche TEXT,
    note_terreno_giacitura TEXT,
    campionature_effettuate TEXT,
    affidabilita_stratigrafica TEXT,
    classi_reperti_associazione TEXT,
    osservazioni TEXT,
    interpretazione TEXT,
    UNIQUE (sito, area, us, id_fauna)
);

-- Add thesaurus entries for fauna_table (Italian)

-- 13.1 - Contesto
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'DOMESTICO', 'Contesto domestico', 'Contesto residenziale/abitativo', '13.1', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'RITUALE', 'Contesto rituale', 'Contesto cerimoniale/rituale', '13.1', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'FUNERARIO', 'Contesto funerario', 'Contesto sepolcrale/funerario', '13.1', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'PRODUTTIVO', 'Contesto produttivo', 'Contesto artigianale/industriale', '13.1', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'RIFIUTI', 'Deposito rifiuti', 'Scarico/deposito di rifiuti', '13.1', 'IT');

-- 13.2 - Metodologia Recupero
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'MANUALE', 'Raccolta manuale', 'Recupero manuale durante lo scavo', '13.2', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'SETACCIO', 'Setacciatura', 'Recupero mediante setacciatura', '13.2', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'FLOTTAZIONE', 'Flottazione', 'Recupero mediante flottazione', '13.2', 'IT');

-- 13.3 - Tipologia Accumulo
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'NATURALE', 'Accumulo naturale', 'Accumulo per cause naturali', '13.3', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'ANTROPICO', 'Accumulo antropico', 'Accumulo per attività umana', '13.3', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'MISTO', 'Accumulo misto', 'Accumulo di origine mista', '13.3', 'IT');

-- 13.4 - Deposizione
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'PRIMARIA', 'Deposizione primaria', 'Deposizione in situ', '13.4', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'SECONDARIA', 'Deposizione secondaria', 'Deposizione dopo spostamento', '13.4', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'RIMANEGGIATA', 'Deposizione rimaneggiata', 'Deposizione disturbata', '13.4', 'IT');

-- 13.5 - Stato Frammentazione
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'INTEGRO', 'Integro', 'Osso completo', '13.5', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'FRAMMENTATO', 'Frammentato', 'Osso frammentato', '13.5', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'PARZIALE', 'Parziale', 'Osso parzialmente conservato', '13.5', 'IT');

-- 13.6 - Stato Conservazione
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'BUONO', 'Buono', 'Buono stato di conservazione', '13.6', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'MEDIOCRE', 'Mediocre', 'Stato di conservazione mediocre', '13.6', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'CATTIVO', 'Cattivo', 'Cattivo stato di conservazione', '13.6', 'IT');

-- 13.7 - Affidabilità Stratigrafica
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'ALTA', 'Alta affidabilità', 'Alta affidabilità stratigrafica', '13.7', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'MEDIA', 'Media affidabilità', 'Media affidabilità stratigrafica', '13.7', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'BASSA', 'Bassa affidabilità', 'Bassa affidabilità stratigrafica', '13.7', 'IT');

-- 13.8 - Tracce Combustione
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'ASSENTI', 'Assenti', 'Nessuna traccia di combustione', '13.8', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'PRESENTI', 'Presenti', 'Tracce di combustione presenti', '13.8', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'DIFFUSE', 'Diffuse', 'Tracce di combustione diffuse', '13.8', 'IT');

-- 13.9 - Tipo Combustione
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'CARBONIZZAZIONE', 'Carbonizzazione', 'Combustione con carbonizzazione', '13.9', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'CALCINAZIONE', 'Calcinazione', 'Combustione con calcinazione', '13.9', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'PARZIALE', 'Parziale', 'Combustione parziale', '13.9', 'IT');

-- 13.10 - Connessione Anatomica
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'SI', 'In connessione', 'Ossa in connessione anatomica', '13.10', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'NO', 'Non in connessione', 'Ossa disarticolate', '13.10', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'PARZIALE', 'Parziale', 'Connessione anatomica parziale', '13.10', 'IT');

-- 13.11 - Specie
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'BOS_TAURUS', 'Bos taurus', 'Bovino domestico', '13.11', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'OVIS_ARIES', 'Ovis aries', 'Pecora domestica', '13.11', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'CAPRA_HIRCUS', 'Capra hircus', 'Capra domestica', '13.11', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'SUS_DOMESTICUS', 'Sus domesticus', 'Maiale domestico', '13.11', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'OVIS_CAPRA', 'Ovis/Capra', 'Ovicaprino indeterminato', '13.11', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'CERVUS_ELAPHUS', 'Cervus elaphus', 'Cervo', '13.11', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'EQUUS_CABALLUS', 'Equus caballus', 'Cavallo', '13.11', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'CANIS_FAMILIARIS', 'Canis familiaris', 'Cane domestico', '13.11', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'INDET', 'Indeterminato', 'Specie indeterminata', '13.11', 'IT');

-- 13.12 - Parti Scheletriche (PSI)
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'CRANIO', 'Cranio', 'Cranio/elementi craniali', '13.12', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'MANDIBOLA', 'Mandibola', 'Mandibola/mascella', '13.12', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'VERTEBRE', 'Vertebre', 'Elementi vertebrali', '13.12', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'COSTE', 'Coste', 'Costole', '13.12', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'SCAPOLA', 'Scapola', 'Scapola', '13.12', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'OMERO', 'Omero', 'Omero', '13.12', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'RADIO', 'Radio', 'Radio', '13.12', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'ULNA', 'Ulna', 'Ulna', '13.12', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'PELVI', 'Pelvi', 'Bacino', '13.12', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'FEMORE', 'Femore', 'Femore', '13.12', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'TIBIA', 'Tibia', 'Tibia', '13.12', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'METAPODIO', 'Metapodio', 'Metacarpo/Metatarso', '13.12', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'FALANGI', 'Falangi', 'Falangi', '13.12', 'IT');

-- 13.13 - Elemento Anatomico
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'HUM', 'Humerus', 'Omero', '13.13', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'RAD', 'Radius', 'Radio', '13.13', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'FEM', 'Femur', 'Femore', '13.13', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'TIB', 'Tibia', 'Tibia', '13.13', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'MTC', 'Metacarpus', 'Metacarpo', '13.13', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'MTT', 'Metatarsus', 'Metatarso', '13.13', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'AST', 'Astragalus', 'Astragalo', '13.13', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'CAL', 'Calcaneus', 'Calcagno', '13.13', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'PHI', 'Phalanx I', 'Prima falange', '13.13', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'PHII', 'Phalanx II', 'Seconda falange', '13.13', 'IT');
INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
VALUES ('fauna_table', 'PHIII', 'Phalanx III', 'Terza falange', '13.13', 'IT');

-- Verify
SELECT 'Fauna table and thesaurus setup complete!' AS status;
SELECT COUNT(*) AS fauna_thesaurus_count FROM pyarchinit_thesaurus_sigle WHERE nome_tabella = 'fauna_table';
