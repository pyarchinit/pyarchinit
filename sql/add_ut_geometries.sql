-- =====================================================
-- UT Geometry Tables and Spatial Views
-- For PostgreSQL/PostGIS
-- =====================================================

-- =====================================================
-- UT Point Geometries
-- =====================================================

CREATE SEQUENCE IF NOT EXISTS public.pyarchinit_ut_point_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE TABLE IF NOT EXISTS public.pyarchinit_ut_point (
    gid BIGINT DEFAULT nextval('public.pyarchinit_ut_point_gid_seq'::regclass) NOT NULL,
    sito TEXT,
    nr_ut INTEGER,
    def_ut TEXT,
    quota DOUBLE PRECISION,
    the_geom geometry(Point, -1),
    data_rilevamento VARCHAR(100),
    responsabile VARCHAR(255),
    note TEXT,
    CONSTRAINT pyarchinit_ut_point_pkey PRIMARY KEY (gid)
);

CREATE INDEX IF NOT EXISTS idx_pyarchinit_ut_point_geom ON public.pyarchinit_ut_point USING gist(the_geom);
CREATE INDEX IF NOT EXISTS idx_pyarchinit_ut_point_sito ON public.pyarchinit_ut_point(sito);
CREATE INDEX IF NOT EXISTS idx_pyarchinit_ut_point_nr_ut ON public.pyarchinit_ut_point(nr_ut);

-- =====================================================
-- UT Line Geometries
-- =====================================================

CREATE SEQUENCE IF NOT EXISTS public.pyarchinit_ut_line_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE TABLE IF NOT EXISTS public.pyarchinit_ut_line (
    gid BIGINT DEFAULT nextval('public.pyarchinit_ut_line_gid_seq'::regclass) NOT NULL,
    sito TEXT,
    nr_ut INTEGER,
    def_ut TEXT,
    tipo_linea VARCHAR(100),
    lunghezza DOUBLE PRECISION,
    the_geom geometry(LineString, -1),
    data_rilevamento VARCHAR(100),
    responsabile VARCHAR(255),
    note TEXT,
    CONSTRAINT pyarchinit_ut_line_pkey PRIMARY KEY (gid)
);

CREATE INDEX IF NOT EXISTS idx_pyarchinit_ut_line_geom ON public.pyarchinit_ut_line USING gist(the_geom);
CREATE INDEX IF NOT EXISTS idx_pyarchinit_ut_line_sito ON public.pyarchinit_ut_line(sito);
CREATE INDEX IF NOT EXISTS idx_pyarchinit_ut_line_nr_ut ON public.pyarchinit_ut_line(nr_ut);

-- =====================================================
-- UT Polygon Geometries
-- =====================================================

CREATE SEQUENCE IF NOT EXISTS public.pyarchinit_ut_polygon_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE TABLE IF NOT EXISTS public.pyarchinit_ut_polygon (
    gid BIGINT DEFAULT nextval('public.pyarchinit_ut_polygon_gid_seq'::regclass) NOT NULL,
    sito TEXT,
    nr_ut INTEGER,
    def_ut TEXT,
    area_mq DOUBLE PRECISION,
    perimetro DOUBLE PRECISION,
    the_geom geometry(Polygon, -1),
    data_rilevamento VARCHAR(100),
    responsabile VARCHAR(255),
    note TEXT,
    CONSTRAINT pyarchinit_ut_polygon_pkey PRIMARY KEY (gid)
);

CREATE INDEX IF NOT EXISTS idx_pyarchinit_ut_polygon_geom ON public.pyarchinit_ut_polygon USING gist(the_geom);
CREATE INDEX IF NOT EXISTS idx_pyarchinit_ut_polygon_sito ON public.pyarchinit_ut_polygon(sito);
CREATE INDEX IF NOT EXISTS idx_pyarchinit_ut_polygon_nr_ut ON public.pyarchinit_ut_polygon(nr_ut);

-- =====================================================
-- UT Spatial View - Points joined with ut_table
-- =====================================================

DROP VIEW IF EXISTS public.pyarchinit_ut_point_view;

CREATE OR REPLACE VIEW public.pyarchinit_ut_point_view AS
SELECT
    p.gid,
    p.the_geom,
    p.sito,
    p.nr_ut,
    p.def_ut,
    p.quota,
    p.data_rilevamento,
    p.responsabile AS rilevatore,
    p.note AS note_geometria,
    u.id_ut,
    u.progetto,
    u.ut_letterale,
    u.descrizione_ut,
    u.interpretazione_ut,
    u.nazione,
    u.regione,
    u.provincia,
    u.comune,
    u.frazione,
    u.localita,
    u.indirizzo,
    u.nr_civico,
    u.carta_topo_igm,
    u.carta_ctr,
    u.coord_geografiche,
    u.coord_piane,
    u.andamento_terreno_pendenza,
    u.utilizzo_suolo_vegetazione,
    u.descrizione_empirica_suolo,
    u.descrizione_luogo,
    u.metodo_rilievo_e_ricognizione,
    u.geometria,
    u.bibliografia,
    u.data AS data_schedatura,
    u.ora_meteo,
    u.responsabile AS responsabile_scheda,
    u.dimensioni_ut,
    u.rep_per_mq,
    u.rep_datanti,
    u."periodo_I",
    u."datazione_I",
    u."interpretazione_I",
    u."periodo_II",
    u."datazione_II",
    u."interpretazione_II",
    u.documentazione,
    u.enti_tutela_vincoli,
    u.indagini_preliminari,
    u.visibility_percent,
    u.vegetation_coverage,
    u.gps_method,
    u.coordinate_precision,
    u.survey_type,
    u.surface_condition,
    u.accessibility,
    u.photo_documentation,
    u.weather_conditions,
    u.team_members,
    u.foglio_catastale
FROM
    public.pyarchinit_ut_point p
LEFT JOIN
    public.ut_table u ON p.sito = u.progetto AND p.nr_ut = u.nr_ut;

-- =====================================================
-- UT Spatial View - Lines joined with ut_table
-- =====================================================

DROP VIEW IF EXISTS public.pyarchinit_ut_line_view;

CREATE OR REPLACE VIEW public.pyarchinit_ut_line_view AS
SELECT
    l.gid,
    l.the_geom,
    l.sito,
    l.nr_ut,
    l.def_ut,
    l.tipo_linea,
    l.lunghezza,
    l.data_rilevamento,
    l.responsabile AS rilevatore,
    l.note AS note_geometria,
    u.id_ut,
    u.progetto,
    u.ut_letterale,
    u.descrizione_ut,
    u.interpretazione_ut,
    u.nazione,
    u.regione,
    u.provincia,
    u.comune,
    u.localita,
    u.metodo_rilievo_e_ricognizione,
    u.data AS data_schedatura,
    u.responsabile AS responsabile_scheda,
    u.survey_type,
    u.visibility_percent,
    u.weather_conditions,
    u.team_members
FROM
    public.pyarchinit_ut_line l
LEFT JOIN
    public.ut_table u ON l.sito = u.progetto AND l.nr_ut = u.nr_ut;

-- =====================================================
-- UT Spatial View - Polygons joined with ut_table
-- =====================================================

DROP VIEW IF EXISTS public.pyarchinit_ut_polygon_view;

CREATE OR REPLACE VIEW public.pyarchinit_ut_polygon_view AS
SELECT
    p.gid,
    p.the_geom,
    p.sito,
    p.nr_ut,
    p.def_ut,
    p.area_mq,
    p.perimetro,
    p.data_rilevamento,
    p.responsabile AS rilevatore,
    p.note AS note_geometria,
    u.id_ut,
    u.progetto,
    u.ut_letterale,
    u.descrizione_ut,
    u.interpretazione_ut,
    u.nazione,
    u.regione,
    u.provincia,
    u.comune,
    u.frazione,
    u.localita,
    u.indirizzo,
    u.carta_topo_igm,
    u.carta_ctr,
    u.coord_geografiche,
    u.coord_piane,
    u.andamento_terreno_pendenza,
    u.utilizzo_suolo_vegetazione,
    u.descrizione_empirica_suolo,
    u.descrizione_luogo,
    u.metodo_rilievo_e_ricognizione,
    u.geometria,
    u.bibliografia,
    u.data AS data_schedatura,
    u.ora_meteo,
    u.responsabile AS responsabile_scheda,
    u.dimensioni_ut,
    u.rep_per_mq,
    u.rep_datanti,
    u."periodo_I",
    u."datazione_I",
    u."interpretazione_I",
    u."periodo_II",
    u."datazione_II",
    u."interpretazione_II",
    u.documentazione,
    u.enti_tutela_vincoli,
    u.indagini_preliminari,
    u.visibility_percent,
    u.vegetation_coverage,
    u.gps_method,
    u.coordinate_precision,
    u.survey_type,
    u.surface_condition,
    u.accessibility,
    u.photo_documentation,
    u.weather_conditions,
    u.team_members,
    u.foglio_catastale
FROM
    public.pyarchinit_ut_polygon p
LEFT JOIN
    public.ut_table u ON p.sito = u.progetto AND p.nr_ut = u.nr_ut;

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON public.pyarchinit_ut_point TO PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.pyarchinit_ut_line TO PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.pyarchinit_ut_polygon TO PUBLIC;
GRANT SELECT ON public.pyarchinit_ut_point_view TO PUBLIC;
GRANT SELECT ON public.pyarchinit_ut_line_view TO PUBLIC;
GRANT SELECT ON public.pyarchinit_ut_polygon_view TO PUBLIC;
GRANT USAGE, SELECT ON SEQUENCE public.pyarchinit_ut_point_gid_seq TO PUBLIC;
GRANT USAGE, SELECT ON SEQUENCE public.pyarchinit_ut_line_gid_seq TO PUBLIC;
GRANT USAGE, SELECT ON SEQUENCE public.pyarchinit_ut_polygon_gid_seq TO PUBLIC;
