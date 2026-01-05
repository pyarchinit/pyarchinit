-- =====================================================
-- UT Geometry Tables and Spatial Views
-- For SQLite/SpatiaLite
-- =====================================================

-- =====================================================
-- UT Point Geometries
-- =====================================================

CREATE TABLE IF NOT EXISTS pyarchinit_ut_point (
    gid INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT,
    nr_ut INTEGER,
    def_ut TEXT,
    quota REAL,
    data_rilevamento TEXT,
    responsabile TEXT,
    note TEXT
);

-- Add SpatiaLite geometry column (run only once)
-- SELECT AddGeometryColumn('pyarchinit_ut_point', 'the_geom', -1, 'POINT', 'XY');
-- SELECT CreateSpatialIndex('pyarchinit_ut_point', 'the_geom');

-- =====================================================
-- UT Line Geometries
-- =====================================================

CREATE TABLE IF NOT EXISTS pyarchinit_ut_line (
    gid INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT,
    nr_ut INTEGER,
    def_ut TEXT,
    tipo_linea TEXT,
    lunghezza REAL,
    data_rilevamento TEXT,
    responsabile TEXT,
    note TEXT
);

-- Add SpatiaLite geometry column (run only once)
-- SELECT AddGeometryColumn('pyarchinit_ut_line', 'the_geom', -1, 'LINESTRING', 'XY');
-- SELECT CreateSpatialIndex('pyarchinit_ut_line', 'the_geom');

-- =====================================================
-- UT Polygon Geometries
-- =====================================================

CREATE TABLE IF NOT EXISTS pyarchinit_ut_polygon (
    gid INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT,
    nr_ut INTEGER,
    def_ut TEXT,
    area_mq REAL,
    perimetro REAL,
    data_rilevamento TEXT,
    responsabile TEXT,
    note TEXT
);

-- Add SpatiaLite geometry column (run only once)
-- SELECT AddGeometryColumn('pyarchinit_ut_polygon', 'the_geom', -1, 'POLYGON', 'XY');
-- SELECT CreateSpatialIndex('pyarchinit_ut_polygon', 'the_geom');

-- =====================================================
-- UT Spatial View - Points joined with ut_table
-- =====================================================

DROP VIEW IF EXISTS pyarchinit_ut_point_view;

CREATE VIEW IF NOT EXISTS pyarchinit_ut_point_view AS
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
    u.periodo_I,
    u.datazione_I,
    u.interpretazione_I,
    u.periodo_II,
    u.datazione_II,
    u.interpretazione_II,
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
    pyarchinit_ut_point p
LEFT JOIN
    ut_table u ON p.sito = u.progetto AND p.nr_ut = u.nr_ut;

-- =====================================================
-- UT Spatial View - Lines joined with ut_table
-- =====================================================

DROP VIEW IF EXISTS pyarchinit_ut_line_view;

CREATE VIEW IF NOT EXISTS pyarchinit_ut_line_view AS
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
    pyarchinit_ut_line l
LEFT JOIN
    ut_table u ON l.sito = u.progetto AND l.nr_ut = u.nr_ut;

-- =====================================================
-- UT Spatial View - Polygons joined with ut_table
-- =====================================================

DROP VIEW IF EXISTS pyarchinit_ut_polygon_view;

CREATE VIEW IF NOT EXISTS pyarchinit_ut_polygon_view AS
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
    u.periodo_I,
    u.datazione_I,
    u.interpretazione_I,
    u.periodo_II,
    u.datazione_II,
    u.interpretazione_II,
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
    pyarchinit_ut_polygon p
LEFT JOIN
    ut_table u ON p.sito = u.progetto AND p.nr_ut = u.nr_ut;
