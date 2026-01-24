-- =====================================================
-- AGGIORNAMENTO SCHEMA PYARCHINIT
-- Aggiunge quota e sistema di concorrenza
-- =====================================================

-- 0. CREAZIONE FAUNA_TABLE SE NON ESISTE
-- =====================================================
CREATE TABLE IF NOT EXISTS "fauna_table" (
    id_fauna BIGSERIAL PRIMARY KEY,
    id_us BIGINT,
    sito TEXT,
    area TEXT,
    saggio TEXT,
    us TEXT,
    datazione_us TEXT,
    responsabile_scheda TEXT DEFAULT '',
    data_compilazione DATE,
    documentazione_fotografica TEXT DEFAULT '',
    metodologia_recupero TEXT DEFAULT '',
    contesto TEXT DEFAULT '',
    descrizione_contesto TEXT DEFAULT '',
    resti_connessione_anatomica TEXT DEFAULT '',
    tipologia_accumulo TEXT DEFAULT '',
    deposizione TEXT DEFAULT '',
    numero_stimato_resti TEXT DEFAULT '',
    numero_minimo_individui INTEGER DEFAULT 0,
    specie TEXT DEFAULT '',
    parti_scheletriche TEXT DEFAULT '',
    specie_psi TEXT DEFAULT '',
    misure_ossa TEXT DEFAULT '',
    stato_frammentazione TEXT DEFAULT '',
    tracce_combustione TEXT DEFAULT '',
    combustione_altri_materiali_us BOOLEAN DEFAULT FALSE,
    tipo_combustione TEXT DEFAULT '',
    segni_tafonomici_evidenti TEXT DEFAULT '',
    caratterizzazione_segni_tafonomici TEXT DEFAULT '',
    stato_conservazione TEXT DEFAULT '',
    alterazioni_morfologiche TEXT DEFAULT '',
    note_terreno_giacitura TEXT DEFAULT '',
    campionature_effettuate TEXT DEFAULT '',
    affidabilita_stratigrafica TEXT DEFAULT '',
    classi_reperti_associazione TEXT DEFAULT '',
    osservazioni TEXT DEFAULT '',
    interpretazione TEXT DEFAULT '',
    CONSTRAINT ID_fauna_unico UNIQUE (sito, area, us, id_fauna)
);

CREATE INDEX IF NOT EXISTS idx_fauna_id_us ON fauna_table(id_us);
CREATE INDEX IF NOT EXISTS idx_fauna_sito ON fauna_table(sito);
CREATE INDEX IF NOT EXISTS idx_fauna_area ON fauna_table(area);
CREATE INDEX IF NOT EXISTS idx_fauna_us ON fauna_table(us);
CREATE INDEX IF NOT EXISTS idx_fauna_specie ON fauna_table(specie);
CREATE INDEX IF NOT EXISTS idx_fauna_contesto ON fauna_table(contesto);

-- 1. CAMPO QUOTA PER INVENTARIO MATERIALI
-- =====================================================
ALTER TABLE inventario_materiali_table
ADD COLUMN IF NOT EXISTS quota_usm FLOAT,
ADD COLUMN IF NOT EXISTS unita_misura_quota VARCHAR(20) DEFAULT 'm s.l.m.';

COMMENT ON COLUMN inventario_materiali_table.quota_usm IS 'Quota US/USM (può essere negativa)';
COMMENT ON COLUMN inventario_materiali_table.unita_misura_quota IS 'Unità di misura quota (es: m s.l.m., m, cm)';

-- 1b. CAMPI PHOTO_ID E DRAWING_ID PER INVENTARIO MATERIALI
-- =====================================================
ALTER TABLE inventario_materiali_table
ADD COLUMN IF NOT EXISTS photo_id TEXT,
ADD COLUMN IF NOT EXISTS drawing_id TEXT;

COMMENT ON COLUMN inventario_materiali_table.photo_id IS 'Nomi delle foto associate (auto-popolato, immagini che NON iniziano con D_)';
COMMENT ON COLUMN inventario_materiali_table.drawing_id IS 'Nomi dei disegni associati (auto-popolato, immagini che iniziano con D_)';

-- 2. CAMPI CONCORRENZA PER TUTTE LE TABELLE
-- =====================================================

-- Funzione helper per aggiungere campi concorrenza
CREATE OR REPLACE FUNCTION add_concurrency_columns(table_name text)
RETURNS void AS $$
BEGIN
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS last_modified_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP', table_name);
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS last_modified_by VARCHAR(100)', table_name);
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS version_number INTEGER DEFAULT 1', table_name);
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS editing_by VARCHAR(100)', table_name);
    EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS editing_since TIMESTAMP', table_name);
    RAISE NOTICE 'Colonne concorrenza aggiunte a %', table_name;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Errore aggiungendo colonne a %: %', table_name, SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- Applica a tutte le tabelle principali
SELECT add_concurrency_columns('us_table');
SELECT add_concurrency_columns('tma_materiali_archeologici');
SELECT add_concurrency_columns('inventario_materiali_table');
SELECT add_concurrency_columns('site_table');
SELECT add_concurrency_columns('struttura_table');
SELECT add_concurrency_columns('periodizzazione_table');
SELECT add_concurrency_columns('tomba_table');
SELECT add_concurrency_columns('individui_table');
SELECT add_concurrency_columns('campioni_table');
SELECT add_concurrency_columns('documentazione_table');
SELECT add_concurrency_columns('detsesso_table');
SELECT add_concurrency_columns('deteta_table');
SELECT add_concurrency_columns('archeozoology_table');
SELECT add_concurrency_columns('pottery_table');
SELECT add_concurrency_columns('fauna_table');
SELECT add_concurrency_columns('ut_table');

-- 2b. UT_TABLE NUOVI CAMPI SURVEY (v4.9.21+)
-- =====================================================
ALTER TABLE ut_table ADD COLUMN IF NOT EXISTS visibility_percent INTEGER;
ALTER TABLE ut_table ADD COLUMN IF NOT EXISTS vegetation_coverage VARCHAR(255);
ALTER TABLE ut_table ADD COLUMN IF NOT EXISTS gps_method VARCHAR(100);
ALTER TABLE ut_table ADD COLUMN IF NOT EXISTS coordinate_precision FLOAT;
ALTER TABLE ut_table ADD COLUMN IF NOT EXISTS survey_type VARCHAR(100);
ALTER TABLE ut_table ADD COLUMN IF NOT EXISTS surface_condition VARCHAR(255);
ALTER TABLE ut_table ADD COLUMN IF NOT EXISTS accessibility VARCHAR(255);
ALTER TABLE ut_table ADD COLUMN IF NOT EXISTS photo_documentation INTEGER;
ALTER TABLE ut_table ADD COLUMN IF NOT EXISTS weather_conditions VARCHAR(255);
ALTER TABLE ut_table ADD COLUMN IF NOT EXISTS team_members TEXT;
ALTER TABLE ut_table ADD COLUMN IF NOT EXISTS foglio_catastale VARCHAR(100);
-- Analysis fields (v4.9.70+)
ALTER TABLE ut_table ADD COLUMN IF NOT EXISTS potential_score NUMERIC(5,2);
ALTER TABLE ut_table ADD COLUMN IF NOT EXISTS risk_score NUMERIC(5,2);
ALTER TABLE ut_table ADD COLUMN IF NOT EXISTS potential_factors TEXT;
ALTER TABLE ut_table ADD COLUMN IF NOT EXISTS risk_factors TEXT;
ALTER TABLE ut_table ADD COLUMN IF NOT EXISTS analysis_date VARCHAR(100);
ALTER TABLE ut_table ADD COLUMN IF NOT EXISTS analysis_method VARCHAR(100);

COMMENT ON COLUMN ut_table.visibility_percent IS 'Percentuale visibilita superficie (0-100)';
COMMENT ON COLUMN ut_table.vegetation_coverage IS 'Copertura vegetazione';
COMMENT ON COLUMN ut_table.gps_method IS 'Metodo GPS utilizzato';
COMMENT ON COLUMN ut_table.coordinate_precision IS 'Precisione coordinate';
COMMENT ON COLUMN ut_table.survey_type IS 'Tipo di ricognizione';
COMMENT ON COLUMN ut_table.surface_condition IS 'Condizione superficie';
COMMENT ON COLUMN ut_table.accessibility IS 'Accessibilita';
COMMENT ON COLUMN ut_table.photo_documentation IS 'Documentazione fotografica';
COMMENT ON COLUMN ut_table.weather_conditions IS 'Condizioni meteo';
COMMENT ON COLUMN ut_table.team_members IS 'Membri del team';
COMMENT ON COLUMN ut_table.foglio_catastale IS 'Foglio catastale';

-- 3. SISTEMA GESTIONE UTENTI
-- =====================================================

-- Tabella utenti
CREATE TABLE IF NOT EXISTS pyarchinit_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'archeologo',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    last_login TIMESTAMP,
    last_ip VARCHAR(50),
    notes TEXT
);

-- Tabella permessi
CREATE TABLE IF NOT EXISTS pyarchinit_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES pyarchinit_users(id) ON DELETE CASCADE,
    table_name VARCHAR(100) NOT NULL,
    can_insert BOOLEAN DEFAULT FALSE,
    can_update BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    can_view BOOLEAN DEFAULT TRUE,
    site_filter VARCHAR(100),
    area_filter VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    UNIQUE(user_id, table_name)
);

-- Tabella ruoli
CREATE TABLE IF NOT EXISTS pyarchinit_roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    default_can_insert BOOLEAN DEFAULT FALSE,
    default_can_update BOOLEAN DEFAULT FALSE,
    default_can_delete BOOLEAN DEFAULT FALSE,
    default_can_view BOOLEAN DEFAULT TRUE,
    is_system_role BOOLEAN DEFAULT FALSE
);

-- Tabella log accessi
CREATE TABLE IF NOT EXISTS pyarchinit_access_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES pyarchinit_users(id),
    username VARCHAR(50),
    action VARCHAR(50),
    table_accessed VARCHAR(100),
    operation VARCHAR(20),
    record_id INTEGER,
    ip_address VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN,
    error_message TEXT
);

-- Inserisci ruoli predefiniti
INSERT INTO pyarchinit_roles (role_name, description, default_can_insert, default_can_update, default_can_delete, default_can_view, is_system_role) VALUES
('admin', 'Amministratore - Accesso completo', TRUE, TRUE, TRUE, TRUE, TRUE),
('responsabile', 'Responsabile scavo - Può modificare tutto', TRUE, TRUE, TRUE, TRUE, FALSE),
('archeologo', 'Archeologo - Può inserire e modificare', TRUE, TRUE, FALSE, TRUE, FALSE),
('studente', 'Studente - Solo inserimento', TRUE, FALSE, FALSE, TRUE, FALSE),
('guest', 'Ospite - Solo visualizzazione', FALSE, FALSE, FALSE, TRUE, FALSE)
ON CONFLICT (role_name) DO NOTHING;

-- 4. AUDIT LOG
-- =====================================================

CREATE TABLE IF NOT EXISTS pyarchinit_audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER,
    operation VARCHAR(20) NOT NULL,
    user_name VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    old_data JSONB,
    new_data JSONB,
    changes JSONB
);

CREATE INDEX IF NOT EXISTS idx_audit_table_record ON pyarchinit_audit_log(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON pyarchinit_audit_log(timestamp);

-- 5. FUNZIONI GESTIONE CONCORRENZA
-- =====================================================

-- Check version conflict
CREATE OR REPLACE FUNCTION check_version_conflict(
    p_table_name VARCHAR,
    p_record_id INTEGER,
    p_expected_version INTEGER
)
RETURNS TABLE(
    has_conflict BOOLEAN,
    current_version INTEGER,
    last_modified_by VARCHAR,
    last_modified_timestamp TIMESTAMP
) AS $$
DECLARE
    v_query TEXT;
    v_result RECORD;
BEGIN
    v_query := format('
        SELECT version_number, last_modified_by, last_modified_timestamp
        FROM %I
        WHERE id = $1',
        p_table_name
    );

    EXECUTE v_query INTO v_result USING p_record_id;

    RETURN QUERY
    SELECT
        v_result.version_number != p_expected_version,
        v_result.version_number,
        v_result.last_modified_by,
        v_result.last_modified_timestamp;
END;
$$ LANGUAGE plpgsql;

-- Clean stale locks
CREATE OR REPLACE FUNCTION clean_stale_locks()
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER := 0;
    v_table_name TEXT;
    v_temp_count INTEGER;
BEGIN
    FOR v_table_name IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        AND tablename LIKE '%_table%'
    LOOP
        EXECUTE format('
            UPDATE %I
            SET editing_by = NULL, editing_since = NULL
            WHERE editing_since < CURRENT_TIMESTAMP - INTERVAL ''30 minutes''
            AND editing_by IS NOT NULL',
            v_table_name
        );

        GET DIAGNOSTICS v_temp_count = ROW_COUNT;
        v_count := v_count + v_temp_count;
    END LOOP;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- 6. VISTE AGGIORNATE
-- =====================================================

-- Vista reperti con quota
DROP VIEW IF EXISTS pyarchinit_reperti_view CASCADE;

CREATE OR REPLACE VIEW pyarchinit_reperti_view AS
SELECT
    im.id_invmat,
    im.sito,
    im.numero_inventario,
    im.tipo_reperto,
    im.criterio_schedatura,
    im.definizione,
    im.descrizione,
    im.area,
    im.us,
    im.lavato,
    im.nr_cassa,
    im.luogo_conservazione,
    im.stato_conservazione,
    im.datazione_reperto,
    im.elementi_reperto,
    im.misurazioni,
    im.rif_biblio,
    im.tecnologie,
    im.forme_minime,
    im.forme_massime,
    im.totale_frammenti,
    im.corpo_ceramico,
    im.rivestimento,
    im.diametro_orlo,
    im.peso,
    im.tipo,
    im.eve_orlo,
    im.repertato,
    im.diagnostico,
    im.quota_usm,
    im.unita_misura_quota,
    im.last_modified_timestamp,
    im.last_modified_by,
    im.version_number
FROM inventario_materiali_table im;

-- Vista sessioni editing attive (TUTTE LE TABELLE)
CREATE OR REPLACE VIEW active_editing_sessions AS
SELECT 'us_table'::text AS table_name, id_us AS id, COALESCE(us::text, '') AS reference, sito, area, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 AS minutes_editing FROM us_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'pottery_table'::text, id_rep, id_number::text, sito, area, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM pottery_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'inventario_materiali_table'::text, id_invmat, numero_inventario::text, sito, area, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM inventario_materiali_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'tma_materiali_archeologici'::text, id, COALESCE(dscu, ''), sito, area, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM tma_materiali_archeologici WHERE editing_by IS NOT NULL
UNION ALL SELECT 'archeozoology_table'::text, id_archzoo, id_archzoo::text, sito, area, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM archeozoology_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'campioni_table'::text, id_campione, nr_campione::text, sito, area, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM campioni_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'individui_table'::text, id_scheda_ind, nr_individuo::text, sito, area, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM individui_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'tomba_table'::text, id_tomba, nr_scheda_taf::text, sito, area, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM tomba_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'periodizzazione_table'::text, id_perfas, (periodo::text || '.' || fase::text), sito, area, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM periodizzazione_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'struttura_table'::text, id_struttura, sigla_struttura, sito, ''::text, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM struttura_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'documentazione_table'::text, id_documentazione, nome_doc, sito, ''::text, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM documentazione_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'site_table'::text, id_sito, sito, sito, ''::text, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM site_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'inventario_lapidei_table'::text, id_invlap, scheda_numero::text, sito, ''::text, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM inventario_lapidei_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'deteta_table'::text, id_det_eta, id_det_eta::text, sito, ''::text, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM deteta_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'detsesso_table'::text, id_det_sesso, id_det_sesso::text, sito, ''::text, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM detsesso_table WHERE editing_by IS NOT NULL
UNION ALL SELECT 'pyarchinit_thesaurus_sigle'::text, id_thesaurus_sigle, sigla, ''::text, ''::text, editing_by, editing_since, EXTRACT(epoch FROM CURRENT_TIMESTAMP - editing_since) / 60 FROM pyarchinit_thesaurus_sigle WHERE editing_by IS NOT NULL
ORDER BY 7 DESC;

-- 7. VINCOLI UNIQUE PER PREVENIRE DUPLICATI
-- =====================================================

-- TMA
ALTER TABLE tma_materiali_archeologici
DROP CONSTRAINT IF EXISTS tma_unique_key;
ALTER TABLE tma_materiali_archeologici
ADD CONSTRAINT tma_unique_key UNIQUE (dscu, sito, area, saggio);

-- US
ALTER TABLE us_table
DROP CONSTRAINT IF EXISTS us_unique_key;
ALTER TABLE us_table
ADD CONSTRAINT us_unique_key UNIQUE (sito, area, us);

-- Inventario (già esistente ma verifichiamo)
ALTER TABLE inventario_materiali_table
DROP CONSTRAINT IF EXISTS "ID_invmat_unico";
ALTER TABLE inventario_materiali_table
ADD CONSTRAINT "ID_invmat_unico" UNIQUE (sito, numero_inventario);

-- Site
ALTER TABLE site_table
DROP CONSTRAINT IF EXISTS site_unique_key;
ALTER TABLE site_table
ADD CONSTRAINT site_unique_key UNIQUE (sito);

-- Periodizzazione
ALTER TABLE periodizzazione_table
DROP CONSTRAINT IF EXISTS period_unique_key;
ALTER TABLE periodizzazione_table
ADD CONSTRAINT period_unique_key UNIQUE (sito, periodo, fase);

-- Struttura
ALTER TABLE struttura_table
DROP CONSTRAINT IF EXISTS struttura_unique_key;
ALTER TABLE struttura_table
ADD CONSTRAINT struttura_unique_key UNIQUE (sito, sigla_struttura, numero_struttura);

-- Individui
ALTER TABLE individui_table
DROP CONSTRAINT IF EXISTS individui_unique_key;
ALTER TABLE individui_table
ADD CONSTRAINT individui_unique_key UNIQUE (sito, nr_individuo);

-- Campioni
ALTER TABLE campioni_table
DROP CONSTRAINT IF EXISTS campioni_unique_key;
ALTER TABLE campioni_table
ADD CONSTRAINT campioni_unique_key UNIQUE (sito, nr_campione);

-- =====================================================
-- UT Geometry Tables (for Territorial Units)
-- =====================================================

-- UT Point Geometry Table
CREATE SEQUENCE IF NOT EXISTS public.pyarchinit_ut_point_gid_seq
    START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

CREATE TABLE IF NOT EXISTS public.pyarchinit_ut_point (
    gid BIGINT DEFAULT nextval('public.pyarchinit_ut_point_gid_seq'::regclass) NOT NULL,
    sito TEXT,
    nr_ut INTEGER,
    def_ut TEXT,
    quota DOUBLE PRECISION,
    the_geom geometry(Point),
    data_rilevamento VARCHAR(100),
    responsabile VARCHAR(255),
    note TEXT,
    CONSTRAINT pyarchinit_ut_point_pkey PRIMARY KEY (gid)
);

CREATE INDEX IF NOT EXISTS idx_pyarchinit_ut_point_geom ON public.pyarchinit_ut_point USING gist(the_geom);
CREATE INDEX IF NOT EXISTS idx_pyarchinit_ut_point_sito ON public.pyarchinit_ut_point(sito);

-- UT Line Geometry Table
CREATE SEQUENCE IF NOT EXISTS public.pyarchinit_ut_line_gid_seq
    START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

CREATE TABLE IF NOT EXISTS public.pyarchinit_ut_line (
    gid BIGINT DEFAULT nextval('public.pyarchinit_ut_line_gid_seq'::regclass) NOT NULL,
    sito TEXT,
    nr_ut INTEGER,
    def_ut TEXT,
    tipo_linea VARCHAR(100),
    lunghezza DOUBLE PRECISION,
    the_geom geometry(LineString),
    data_rilevamento VARCHAR(100),
    responsabile VARCHAR(255),
    note TEXT,
    CONSTRAINT pyarchinit_ut_line_pkey PRIMARY KEY (gid)
);

CREATE INDEX IF NOT EXISTS idx_pyarchinit_ut_line_geom ON public.pyarchinit_ut_line USING gist(the_geom);
CREATE INDEX IF NOT EXISTS idx_pyarchinit_ut_line_sito ON public.pyarchinit_ut_line(sito);

-- UT Polygon Geometry Table
CREATE SEQUENCE IF NOT EXISTS public.pyarchinit_ut_polygon_gid_seq
    START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

CREATE TABLE IF NOT EXISTS public.pyarchinit_ut_polygon (
    gid BIGINT DEFAULT nextval('public.pyarchinit_ut_polygon_gid_seq'::regclass) NOT NULL,
    sito TEXT,
    nr_ut INTEGER,
    def_ut TEXT,
    area_mq DOUBLE PRECISION,
    perimetro DOUBLE PRECISION,
    the_geom geometry(Polygon),
    data_rilevamento VARCHAR(100),
    responsabile VARCHAR(255),
    note TEXT,
    CONSTRAINT pyarchinit_ut_polygon_pkey PRIMARY KEY (gid)
);

CREATE INDEX IF NOT EXISTS idx_pyarchinit_ut_polygon_geom ON public.pyarchinit_ut_polygon USING gist(the_geom);
CREATE INDEX IF NOT EXISTS idx_pyarchinit_ut_polygon_sito ON public.pyarchinit_ut_polygon(sito);

-- UT Views
CREATE OR REPLACE VIEW public.pyarchinit_ut_point_view AS
SELECT p.gid, p.the_geom, p.sito, p.nr_ut, p.def_ut, p.quota, p.data_rilevamento,
       p.responsabile AS rilevatore, p.note AS note_geometria,
       u.id_ut, u.progetto, u.ut_letterale, u.descrizione_ut, u.interpretazione_ut
FROM public.pyarchinit_ut_point p
LEFT JOIN public.ut_table u ON p.sito = u.progetto AND p.nr_ut = u.nr_ut;

CREATE OR REPLACE VIEW public.pyarchinit_ut_line_view AS
SELECT l.gid, l.the_geom, l.sito, l.nr_ut, l.def_ut, l.tipo_linea, l.lunghezza,
       l.data_rilevamento, l.responsabile AS rilevatore, l.note AS note_geometria,
       u.id_ut, u.progetto, u.ut_letterale, u.descrizione_ut, u.interpretazione_ut
FROM public.pyarchinit_ut_line l
LEFT JOIN public.ut_table u ON l.sito = u.progetto AND l.nr_ut = u.nr_ut;

CREATE OR REPLACE VIEW public.pyarchinit_ut_polygon_view AS
SELECT p.gid, p.the_geom, p.sito, p.nr_ut, p.def_ut, p.area_mq, p.perimetro,
       p.data_rilevamento, p.responsabile AS rilevatore, p.note AS note_geometria,
       u.id_ut, u.progetto, u.ut_letterale, u.descrizione_ut, u.interpretazione_ut
FROM public.pyarchinit_ut_polygon p
LEFT JOIN public.ut_table u ON p.sito = u.progetto AND p.nr_ut = u.nr_ut;

-- Grant permissions for UT tables
GRANT SELECT, INSERT, UPDATE, DELETE ON public.pyarchinit_ut_point TO PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.pyarchinit_ut_line TO PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.pyarchinit_ut_polygon TO PUBLIC;
GRANT SELECT ON public.pyarchinit_ut_point_view TO PUBLIC;
GRANT SELECT ON public.pyarchinit_ut_line_view TO PUBLIC;
GRANT SELECT ON public.pyarchinit_ut_polygon_view TO PUBLIC;
GRANT USAGE, SELECT ON SEQUENCE public.pyarchinit_ut_point_gid_seq TO PUBLIC;
GRANT USAGE, SELECT ON SEQUENCE public.pyarchinit_ut_line_gid_seq TO PUBLIC;
GRANT USAGE, SELECT ON SEQUENCE public.pyarchinit_ut_polygon_gid_seq TO PUBLIC;

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE '✅ SCHEMA PYARCHINIT AGGIORNATO';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Aggiunte:';
    RAISE NOTICE '  1. Campo quota (quota_usm) in inventario_materiali_table';
    RAISE NOTICE '  2. Sistema di concorrenza su tutte le tabelle';
    RAISE NOTICE '  3. Gestione utenti e permessi';
    RAISE NOTICE '  4. Sistema di audit';
    RAISE NOTICE '  5. Vincoli UNIQUE per prevenire duplicati';
    RAISE NOTICE '';
    RAISE NOTICE 'Eseguire SELECT clean_stale_locks() periodicamente';
    RAISE NOTICE '=====================================================';
END $$;