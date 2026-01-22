-- =====================================================
-- AGGIUNTA CAMPI SCHEDA STRUTTURA AR (PostgreSQL)
-- Nuovi campi per Architettura Rupestre
-- =====================================================

-- Campi generali
ALTER TABLE struttura_table
ADD COLUMN IF NOT EXISTS data_compilazione TEXT,
ADD COLUMN IF NOT EXISTS nome_compilatore TEXT;

-- Stato conservazione (campo ripetibile JSON: [[stato, grado, fattori_agenti], ...])
ALTER TABLE struttura_table
ADD COLUMN IF NOT EXISTS stato_conservazione TEXT;

-- Dati generali architettura
ALTER TABLE struttura_table
ADD COLUMN IF NOT EXISTS quota FLOAT,
ADD COLUMN IF NOT EXISTS relazione_topografica TEXT,
ADD COLUMN IF NOT EXISTS prospetto_ingresso TEXT,  -- JSON: [[prospetto], ...]
ADD COLUMN IF NOT EXISTS orientamento_ingresso TEXT,
ADD COLUMN IF NOT EXISTS articolazione TEXT,
ADD COLUMN IF NOT EXISTS n_ambienti INTEGER,
ADD COLUMN IF NOT EXISTS orientamento_ambienti TEXT,  -- JSON: [[orientamento], ...]
ADD COLUMN IF NOT EXISTS sviluppo_planimetrico TEXT,
ADD COLUMN IF NOT EXISTS elementi_costitutivi TEXT,  -- JSON: [[elemento], ...]
ADD COLUMN IF NOT EXISTS motivo_decorativo TEXT;

-- Dati archeologici
ALTER TABLE struttura_table
ADD COLUMN IF NOT EXISTS potenzialita_archeologica TEXT,
ADD COLUMN IF NOT EXISTS manufatti TEXT,  -- JSON: [[manufatto], ...]
ADD COLUMN IF NOT EXISTS elementi_datanti TEXT,
ADD COLUMN IF NOT EXISTS fasi_funzionali TEXT;  -- JSON: [[ambiente, periodizzazione, definizione], ...]

-- Commenti per documentazione
COMMENT ON COLUMN struttura_table.data_compilazione IS 'Data di compilazione della scheda';
COMMENT ON COLUMN struttura_table.nome_compilatore IS 'Nome del compilatore della scheda';
COMMENT ON COLUMN struttura_table.stato_conservazione IS 'Stato di conservazione (JSON: [[stato, grado, fattori_agenti], ...])';
COMMENT ON COLUMN struttura_table.quota IS 'Quota della struttura in metri';
COMMENT ON COLUMN struttura_table.relazione_topografica IS 'Relazione topografica della struttura';
COMMENT ON COLUMN struttura_table.prospetto_ingresso IS 'Prospetto ingresso (JSON: [[prospetto], ...])';
COMMENT ON COLUMN struttura_table.orientamento_ingresso IS 'Orientamento ingresso (N, NE, E, SE, S, SO, O, NO)';
COMMENT ON COLUMN struttura_table.articolazione IS 'Articolazione (Ambiente unico/Ambiente composito)';
COMMENT ON COLUMN struttura_table.n_ambienti IS 'Numero di ambienti';
COMMENT ON COLUMN struttura_table.orientamento_ambienti IS 'Orientamento ambienti (JSON: [[orientamento], ...])';
COMMENT ON COLUMN struttura_table.sviluppo_planimetrico IS 'Sviluppo planimetrico della struttura';
COMMENT ON COLUMN struttura_table.elementi_costitutivi IS 'Elementi costitutivi (JSON: [[elemento], ...])';
COMMENT ON COLUMN struttura_table.motivo_decorativo IS 'Motivo decorativo presente';
COMMENT ON COLUMN struttura_table.potenzialita_archeologica IS 'Potenzialità archeologica (Nulla/Bassa/Media/Alta)';
COMMENT ON COLUMN struttura_table.manufatti IS 'Manufatti rinvenuti (JSON: [[manufatto], ...])';
COMMENT ON COLUMN struttura_table.elementi_datanti IS 'Elementi datanti';
COMMENT ON COLUMN struttura_table.fasi_funzionali IS 'Fasi funzionali (JSON: [[ambiente, periodizzazione, definizione], ...])';

DO $$
BEGIN
    RAISE NOTICE '✅ Campi scheda struttura AR aggiunti con successo a struttura_table';
END $$;
