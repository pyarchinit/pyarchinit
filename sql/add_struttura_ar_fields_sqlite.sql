-- =====================================================
-- AGGIUNTA CAMPI SCHEDA STRUTTURA AR (SQLite)
-- Nuovi campi per Architettura Rupestre
-- =====================================================

-- Campi generali
ALTER TABLE struttura_table ADD COLUMN data_compilazione TEXT;
ALTER TABLE struttura_table ADD COLUMN nome_compilatore TEXT;

-- Stato conservazione (campo ripetibile JSON: [[stato, grado, fattori_agenti], ...])
ALTER TABLE struttura_table ADD COLUMN stato_conservazione TEXT;

-- Dati generali architettura
ALTER TABLE struttura_table ADD COLUMN quota REAL;
ALTER TABLE struttura_table ADD COLUMN relazione_topografica TEXT;
ALTER TABLE struttura_table ADD COLUMN prospetto_ingresso TEXT;
ALTER TABLE struttura_table ADD COLUMN orientamento_ingresso TEXT;
ALTER TABLE struttura_table ADD COLUMN articolazione TEXT;
ALTER TABLE struttura_table ADD COLUMN n_ambienti INTEGER;
ALTER TABLE struttura_table ADD COLUMN orientamento_ambienti TEXT;
ALTER TABLE struttura_table ADD COLUMN sviluppo_planimetrico TEXT;
ALTER TABLE struttura_table ADD COLUMN elementi_costitutivi TEXT;
ALTER TABLE struttura_table ADD COLUMN motivo_decorativo TEXT;

-- Dati archeologici
ALTER TABLE struttura_table ADD COLUMN potenzialita_archeologica TEXT;
ALTER TABLE struttura_table ADD COLUMN manufatti TEXT;
ALTER TABLE struttura_table ADD COLUMN elementi_datanti TEXT;
ALTER TABLE struttura_table ADD COLUMN fasi_funzionali TEXT;
