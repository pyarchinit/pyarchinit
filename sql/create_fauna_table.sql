-- Schema per la tabella fauna_table
-- Questa tabella si integra con us_table di pyarchinit per i dati faunistici

CREATE TABLE IF NOT EXISTS "fauna_table" (
    -- Chiave primaria
    id_fauna INTEGER PRIMARY KEY AUTOINCREMENT,

    -- DATI IDENTIFICATIVI (ID 1-6: join con us_table)
    -- Foreign key verso us_table
    id_us INTEGER,
    sito TEXT,              -- ID 1: SITO
    area TEXT,              -- ID 3: AREA
    saggio TEXT,            -- ID 4: SAGGIO
    us TEXT,                -- ID 5: US
    datazione_us TEXT,      -- ID 6: DATAZIONE US

    -- DATI DEPOSIZIONALI
    responsabile_scheda TEXT DEFAULT '',                    -- ID 7: RESPONSABILE DELLA SCHEDA
    data_compilazione DATE,                                 -- ID 8: DATA DI COMPILAZIONE
    documentazione_fotografica TEXT DEFAULT '',             -- ID 9: DOCUMENTAZIONE FOTOGRAFICA
    metodologia_recupero TEXT DEFAULT '',                   -- ID 10: METODOLOGIA DI RECUPERO (A MANO/SETACCIO/FLOTTAZIONE)
    contesto TEXT DEFAULT '',                               -- ID 11: CONTESTO (FUNERARIO/ABITATIVO/PRODUTTIVO/IPOGEO/CULTUALE/ALTRO)
    descrizione_contesto TEXT DEFAULT '',                   -- ID 12: DESCRIZIONE DEL CONTESTO DI RINVENIMENTO

    -- DATI ARCHEOZOOLOGICI
    resti_connessione_anatomica TEXT DEFAULT '',            -- ID 13: RESTI IN CONNESSIONE ANATOMICA (SI/NO/PARZIALE)
    tipologia_accumulo TEXT DEFAULT '',                     -- ID 14: TIPOLOGIA DI ACCUMULO
    deposizione TEXT DEFAULT '',                            -- ID 15: DEPOSIZIONE (PRIMARIA/SECONDARIA/RIMANEGGIATA)
    numero_stimato_resti TEXT DEFAULT '',                   -- ID 16: NUMERO STIMATO RESTI OSTEOLOGICI
    numero_minimo_individui INTEGER DEFAULT 0,              -- ID 17: NUMERO MINIMO DI INDIVIDUI (NMI)
    specie TEXT DEFAULT '',                                 -- ID 18: SPECIE (backward compatible, prima specie)
    parti_scheletriche TEXT DEFAULT '',                     -- ID 19: PARTI SCHELETRICHE PRESENTI (backward compatible)
    specie_psi TEXT DEFAULT '',                             -- ID 18b: SPECIE e PSI multiple (JSON array: [[specie, psi], ...])
    misure_ossa TEXT DEFAULT '',                            -- ID 20: MISURE DI OSSA (JSON array: [[elemento, specie, GL, GB, Bp, Bd], ...])

    -- DATI TAFONOMICI
    stato_frammentazione TEXT DEFAULT '',                   -- ID 21: STATO DI FRAMMENTAZIONE (SI/NO/PARZIALE)
    tracce_combustione TEXT DEFAULT '',                     -- ID 22: TRACCE DI COMBUSTIONE (SI/NO/SCARSE/DIFFUSE)
    combustione_altri_materiali_us BOOLEAN DEFAULT 0,       -- ID 23: COMBUSTIONE SU ALTRI MATERIALI DELLA US
    tipo_combustione TEXT DEFAULT '',                       -- ID 24: TIPO DI COMBUSTIONE (ACCIDENTALE/INTENZIONALE/NATURALE/ANTROPICA)
    segni_tafonomici_evidenti TEXT DEFAULT '',              -- ID 25: SEGNI TAFONOMICI EVIDENTI (SI/NO/SCARSI/DIFFUSI)
    caratterizzazione_segni_tafonomici TEXT DEFAULT '',     -- ID 26: CARATTERIZZAZIONE SEGNI TAFONOMICI (ANTROPICA/NATURALE)
    stato_conservazione TEXT DEFAULT '',                    -- ID 27: STATO DI CONSERVAZIONE (0/1/2/3/4/5)
    alterazioni_morfologiche TEXT DEFAULT '',               -- ID 28: ALTERAZIONI MORFOLOGICHE O PATOLOGICHE

    -- DATI CONTESTUALI
    note_terreno_giacitura TEXT DEFAULT '',                 -- ID 29: NOTE SUL TERRENO DI GIACITURA
    campionature_effettuate TEXT DEFAULT '',                -- ID 30: CAMPIONATURE EFFETTUATE
    affidabilita_stratigrafica TEXT DEFAULT '',             -- ID 31: AFFIDABILITÀ STRATIGRAFICA
    classi_reperti_associazione TEXT DEFAULT '',            -- ID 32: CLASSI DI REPERTI IN ASSOCIAZIONE
    osservazioni TEXT DEFAULT '',                           -- ID 33: OSSERVAZIONI
    interpretazione TEXT DEFAULT '',                        -- ID 34: INTERPRETAZIONE

    -- Foreign key constraint
    FOREIGN KEY (id_us) REFERENCES us_table(id_us) ON DELETE CASCADE
);

-- Indici per migliorare le performance delle query
CREATE INDEX IF NOT EXISTS idx_fauna_id_us ON fauna_table(id_us);
CREATE INDEX IF NOT EXISTS idx_fauna_sito ON fauna_table(sito);
CREATE INDEX IF NOT EXISTS idx_fauna_area ON fauna_table(area);
CREATE INDEX IF NOT EXISTS idx_fauna_us ON fauna_table(us);
CREATE INDEX IF NOT EXISTS idx_fauna_specie ON fauna_table(specie);
CREATE INDEX IF NOT EXISTS idx_fauna_contesto ON fauna_table(contesto);