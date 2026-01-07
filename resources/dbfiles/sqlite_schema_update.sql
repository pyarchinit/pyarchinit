-- ============================================================
-- PYARCHINIT SQLite Schema Update Script
-- Generated from PostgreSQL schema
-- ============================================================

-- ============================================================
-- PART 1: CREATE MISSING TABLES
-- ============================================================

-- Table: fauna_table
CREATE TABLE IF NOT EXISTS fauna_table (
    id_fauna INTEGER PRIMARY KEY AUTOINCREMENT,
    id_us INTEGER,
    sito TEXT,
    area TEXT,
    saggio TEXT,
    us TEXT,
    datazione_us TEXT,
    responsabile_scheda TEXT,
    data_compilazione TEXT,
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
    interpretazione TEXT
);

-- Table: logins
CREATE TABLE IF NOT EXISTS logins (
    login_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    login_time TEXT
);

-- Table: users
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

-- Table: media_to_us_table
CREATE TABLE IF NOT EXISTS media_to_us_table (
    id_mediaToUs INTEGER PRIMARY KEY AUTOINCREMENT,
    id_us INTEGER,
    sito TEXT,
    area TEXT,
    us INTEGER,
    id_media INTEGER,
    filepath TEXT
);

-- Table: pyarchinit_access_log
CREATE TABLE IF NOT EXISTS pyarchinit_access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    action TEXT,
    table_accessed TEXT,
    operation TEXT,
    record_id INTEGER,
    ip_address TEXT,
    timestamp TEXT,
    success INTEGER,
    error_message TEXT
);

-- Table: pyarchinit_activity_log
CREATE TABLE IF NOT EXISTS pyarchinit_activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    action TEXT,
    table_name TEXT,
    record_id INTEGER,
    timestamp TEXT,
    details TEXT,
    ip_address TEXT,
    session_id TEXT
);

-- Table: pyarchinit_audit_log
CREATE TABLE IF NOT EXISTS pyarchinit_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_id INTEGER,
    operation TEXT NOT NULL,
    user_name TEXT,
    timestamp TEXT,
    old_data TEXT,
    new_data TEXT,
    changes TEXT
);

-- Table: pyarchinit_codici_tipologia
CREATE TABLE IF NOT EXISTS pyarchinit_codici_tipologia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipologia_progetto TEXT,
    tipologia_definizione_tipologia TEXT,
    tipologia_gruppo TEXT,
    tipologia_definizione_gruppo TEXT,
    tipologia_codice TEXT,
    tipologia_sottocodice TEXT,
    tipologia_definizione_codice TEXT,
    tipologia_descrizione TEXT
);

-- Table: pyarchinit_inventario_materiali
CREATE TABLE IF NOT EXISTS pyarchinit_inventario_materiali (
    idim_pk INTEGER PRIMARY KEY,
    sito TEXT,
    area INTEGER,
    us INTEGER,
    nr_cassa INTEGER,
    tipo_materiale TEXT,
    nr_reperto INTEGER,
    lavato_si_no TEXT,
    descrizione_rep TEXT
);

-- Table: pyarchinit_ipotesi_strutture
CREATE TABLE IF NOT EXISTS pyarchinit_ipotesi_strutture (
    gid INTEGER PRIMARY KEY AUTOINCREMENT,
    id INTEGER,
    scavo TEXT,
    ID_strutt TEXT,
    per_iniz INTEGER,
    per_fin INTEGER,
    dataz_ext TEXT,
    fase_iniz INTEGER,
    fase_fin INTEGER,
    descrizion TEXT,
    the_geom TEXT
);

-- Table: pyarchinit_permissions
CREATE TABLE IF NOT EXISTS pyarchinit_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    table_name TEXT NOT NULL,
    can_insert INTEGER,
    can_update INTEGER,
    can_delete INTEGER,
    can_view INTEGER,
    site_filter TEXT,
    area_filter TEXT,
    created_at TEXT,
    created_by TEXT
);

-- Table: pyarchinit_ripartizioni_temporali
CREATE TABLE IF NOT EXISTS pyarchinit_ripartizioni_temporali (
    sito TEXT,
    sigla_periodo TEXT,
    sigla_fase TEXT,
    cronologia_numerica INTEGER,
    cronologia_numerica_finale INTEGER,
    datazione_estesa_stringa TEXT,
    id_periodo INTEGER PRIMARY KEY AUTOINCREMENT,
    descrizione TEXT
);

-- Table: pyarchinit_roles
CREATE TABLE IF NOT EXISTS pyarchinit_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT NOT NULL,
    description TEXT,
    default_can_insert INTEGER,
    default_can_update INTEGER,
    default_can_delete INTEGER,
    default_can_view INTEGER,
    is_system_role INTEGER
);

-- Table: pyarchinit_rou_thesaurus
CREATE TABLE IF NOT EXISTS pyarchinit_rou_thesaurus (
    ID_rou INTEGER PRIMARY KEY AUTOINCREMENT,
    valore_ro TEXT,
    rou_descrizione TEXT
);

-- Table: pyarchinit_sync_lock
CREATE TABLE IF NOT EXISTS pyarchinit_sync_lock (
    id INTEGER PRIMARY KEY,
    locked_by TEXT,
    locked_at TEXT,
    operation TEXT
);

-- Table: pyarchinit_tipologia_sepolture
CREATE TABLE IF NOT EXISTS pyarchinit_tipologia_sepolture (
    gid INTEGER PRIMARY KEY AUTOINCREMENT,
    id_sepoltura TEXT,
    azimut REAL,
    tipologia TEXT,
    the_geom TEXT,
    sito_ts TEXT,
    t_progetto TEXT,
    t_gruppo TEXT,
    t_codice TEXT,
    t_sottocodice TEXT,
    corredo TEXT
);

-- Table: pyarchinit_users
CREATE TABLE IF NOT EXISTS pyarchinit_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    email TEXT,
    role TEXT,
    is_active INTEGER,
    created_at TEXT,
    created_by TEXT,
    last_login TEXT,
    last_ip TEXT,
    notes TEXT
);

-- Table: pyarchinit_ut_line
CREATE TABLE IF NOT EXISTS pyarchinit_ut_line (
    gid INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT,
    nr_ut INTEGER,
    def_ut TEXT,
    tipo_linea TEXT,
    lunghezza REAL,
    the_geom TEXT,
    data_rilevamento TEXT,
    responsabile TEXT,
    note TEXT
);

-- Table: pyarchinit_ut_point
CREATE TABLE IF NOT EXISTS pyarchinit_ut_point (
    gid INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT,
    nr_ut INTEGER,
    def_ut TEXT,
    quota REAL,
    the_geom TEXT,
    data_rilevamento TEXT,
    responsabile TEXT,
    note TEXT
);

-- Table: pyarchinit_ut_polygon
CREATE TABLE IF NOT EXISTS pyarchinit_ut_polygon (
    gid INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT,
    nr_ut INTEGER,
    def_ut TEXT,
    area_mq REAL,
    perimetro REAL,
    the_geom TEXT,
    data_rilevamento TEXT,
    responsabile TEXT,
    note TEXT
);

-- Table: pyuscaratterizzazioni
CREATE TABLE IF NOT EXISTS pyuscaratterizzazioni (
    gid INTEGER PRIMARY KEY AUTOINCREMENT,
    area_c INTEGER,
    scavo_c TEXT,
    us_c INTEGER,
    the_geom TEXT,
    stratigraph_index_car INTEGER,
    tipo_us_c TEXT
);

-- Table: pyuscarlinee
CREATE TABLE IF NOT EXISTS pyuscarlinee (
    gid INTEGER PRIMARY KEY AUTOINCREMENT,
    sito_l TEXT,
    area_l TEXT,
    us_l TEXT,
    tipo_us_l TEXT,
    the_geom TEXT
);

-- Table: tma_materiali_archeologici
CREATE TABLE IF NOT EXISTS tma_materiali_archeologici (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT,
    area TEXT,
    localita TEXT,
    settore TEXT,
    inventario TEXT,
    ogtm TEXT,
    ldct TEXT,
    ldcn TEXT,
    vecchia_collocazione TEXT,
    cassetta TEXT,
    scan TEXT,
    saggio TEXT,
    vano_locus TEXT,
    dscd TEXT,
    dscu TEXT,
    rcgd TEXT,
    rcgz TEXT,
    aint TEXT,
    aind TEXT,
    dtzg TEXT,
    deso TEXT,
    nsc TEXT,
    ftap TEXT,
    ftan TEXT,
    drat TEXT,
    dran TEXT,
    draa TEXT,
    created_at TEXT,
    updated_at TEXT,
    created_by TEXT,
    updated_by TEXT,
    version_number INTEGER,
    editing_by TEXT,
    editing_since TEXT,
    last_modified_by TEXT,
    last_modified_timestamp TEXT,
    audit_trail TEXT
);

-- Table: tma_materiali_ripetibili
CREATE TABLE IF NOT EXISTS tma_materiali_ripetibili (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_tma INTEGER NOT NULL,
    madi TEXT,
    macc TEXT,
    macl TEXT,
    macp TEXT,
    macd TEXT,
    cronologia_mac TEXT,
    macq TEXT,
    peso REAL,
    created_at TEXT,
    updated_at TEXT,
    created_by TEXT,
    updated_by TEXT,
    version_number INTEGER,
    editing_by TEXT,
    editing_since TEXT,
    last_modified_by TEXT,
    last_modified_timestamp TEXT
);


-- ============================================================
-- PART 2: ADD MISSING COLUMNS TO EXISTING TABLES
-- ============================================================

-- Table: site_table
ALTER TABLE site_table ADD COLUMN version_number INTEGER DEFAULT 1;
ALTER TABLE site_table ADD COLUMN editing_by TEXT DEFAULT NULL;
ALTER TABLE site_table ADD COLUMN editing_since TEXT DEFAULT NULL;
ALTER TABLE site_table ADD COLUMN last_modified_by TEXT DEFAULT NULL;
ALTER TABLE site_table ADD COLUMN last_modified_timestamp TEXT DEFAULT NULL;
ALTER TABLE site_table ADD COLUMN audit_trail TEXT DEFAULT NULL;
ALTER TABLE site_table ADD COLUMN toponimo TEXT DEFAULT NULL;
ALTER TABLE site_table ADD COLUMN latitudine TEXT DEFAULT NULL;
ALTER TABLE site_table ADD COLUMN longitudine TEXT DEFAULT NULL;
ALTER TABLE site_table ADD COLUMN geom TEXT DEFAULT NULL;

-- Table: us_table
ALTER TABLE us_table ADD COLUMN version_number INTEGER DEFAULT 1;
ALTER TABLE us_table ADD COLUMN editing_by TEXT DEFAULT NULL;
ALTER TABLE us_table ADD COLUMN editing_since TEXT DEFAULT NULL;
ALTER TABLE us_table ADD COLUMN last_modified_by TEXT DEFAULT NULL;
ALTER TABLE us_table ADD COLUMN last_modified_timestamp TEXT DEFAULT NULL;
ALTER TABLE us_table ADD COLUMN audit_trail TEXT DEFAULT NULL;
ALTER TABLE us_table ADD COLUMN organici TEXT DEFAULT NULL;
ALTER TABLE us_table ADD COLUMN inorganici TEXT DEFAULT NULL;
ALTER TABLE us_table ADD COLUMN quantificazioni TEXT DEFAULT NULL;
ALTER TABLE us_table ADD COLUMN sing_doc TEXT DEFAULT NULL;
ALTER TABLE us_table ADD COLUMN unita_edilizie TEXT DEFAULT NULL;

-- Table: inventario_materiali_table
ALTER TABLE inventario_materiali_table ADD COLUMN version_number INTEGER DEFAULT 1;
ALTER TABLE inventario_materiali_table ADD COLUMN editing_by TEXT DEFAULT NULL;
ALTER TABLE inventario_materiali_table ADD COLUMN editing_since TEXT DEFAULT NULL;
ALTER TABLE inventario_materiali_table ADD COLUMN last_modified_by TEXT DEFAULT NULL;
ALTER TABLE inventario_materiali_table ADD COLUMN last_modified_timestamp TEXT DEFAULT NULL;
ALTER TABLE inventario_materiali_table ADD COLUMN audit_trail TEXT DEFAULT NULL;
ALTER TABLE inventario_materiali_table ADD COLUMN drawing_id TEXT DEFAULT NULL;
ALTER TABLE inventario_materiali_table ADD COLUMN photo_id TEXT DEFAULT NULL;
ALTER TABLE inventario_materiali_table ADD COLUMN quota_usm REAL DEFAULT NULL;
ALTER TABLE inventario_materiali_table ADD COLUMN unita_misura_quota TEXT DEFAULT NULL;

-- Table: campioni_table
ALTER TABLE campioni_table ADD COLUMN version_number INTEGER DEFAULT 1;
ALTER TABLE campioni_table ADD COLUMN editing_by TEXT DEFAULT NULL;
ALTER TABLE campioni_table ADD COLUMN editing_since TEXT DEFAULT NULL;
ALTER TABLE campioni_table ADD COLUMN audit_trail TEXT DEFAULT NULL;

-- Table: periodizzazione_table
ALTER TABLE periodizzazione_table ADD COLUMN version_number INTEGER DEFAULT 1;
ALTER TABLE periodizzazione_table ADD COLUMN editing_by TEXT DEFAULT NULL;
ALTER TABLE periodizzazione_table ADD COLUMN editing_since TEXT DEFAULT NULL;
ALTER TABLE periodizzazione_table ADD COLUMN last_modified_by TEXT DEFAULT NULL;
ALTER TABLE periodizzazione_table ADD COLUMN last_modified_timestamp TEXT DEFAULT NULL;
ALTER TABLE periodizzazione_table ADD COLUMN audit_trail TEXT DEFAULT NULL;

-- Table: tomba_table
ALTER TABLE tomba_table ADD COLUMN version_number INTEGER DEFAULT 1;
ALTER TABLE tomba_table ADD COLUMN editing_by TEXT DEFAULT NULL;
ALTER TABLE tomba_table ADD COLUMN editing_since TEXT DEFAULT NULL;
ALTER TABLE tomba_table ADD COLUMN last_modified_by TEXT DEFAULT NULL;
ALTER TABLE tomba_table ADD COLUMN last_modified_timestamp TEXT DEFAULT NULL;
ALTER TABLE tomba_table ADD COLUMN audit_trail TEXT DEFAULT NULL;

-- Table: struttura_table
ALTER TABLE struttura_table ADD COLUMN version_number INTEGER DEFAULT 1;
ALTER TABLE struttura_table ADD COLUMN editing_by TEXT DEFAULT NULL;
ALTER TABLE struttura_table ADD COLUMN editing_since TEXT DEFAULT NULL;
ALTER TABLE struttura_table ADD COLUMN last_modified_by TEXT DEFAULT NULL;
ALTER TABLE struttura_table ADD COLUMN last_modified_timestamp TEXT DEFAULT NULL;
ALTER TABLE struttura_table ADD COLUMN audit_trail TEXT DEFAULT NULL;

-- Table: individui_table
ALTER TABLE individui_table ADD COLUMN version_number INTEGER DEFAULT 1;
ALTER TABLE individui_table ADD COLUMN editing_by TEXT DEFAULT NULL;
ALTER TABLE individui_table ADD COLUMN editing_since TEXT DEFAULT NULL;
ALTER TABLE individui_table ADD COLUMN audit_trail TEXT DEFAULT NULL;

-- Table: documentazione_table
ALTER TABLE documentazione_table ADD COLUMN version_number INTEGER DEFAULT 1;
ALTER TABLE documentazione_table ADD COLUMN editing_by TEXT DEFAULT NULL;
ALTER TABLE documentazione_table ADD COLUMN editing_since TEXT DEFAULT NULL;
ALTER TABLE documentazione_table ADD COLUMN audit_trail TEXT DEFAULT NULL;

-- Table: ut_table
ALTER TABLE ut_table ADD COLUMN accessibility TEXT DEFAULT NULL;
ALTER TABLE ut_table ADD COLUMN coordinate_precision REAL DEFAULT NULL;
ALTER TABLE ut_table ADD COLUMN foglio_catastale TEXT DEFAULT NULL;
ALTER TABLE ut_table ADD COLUMN gps_method TEXT DEFAULT NULL;
ALTER TABLE ut_table ADD COLUMN photo_documentation INTEGER DEFAULT NULL;
ALTER TABLE ut_table ADD COLUMN surface_condition TEXT DEFAULT NULL;
ALTER TABLE ut_table ADD COLUMN survey_type TEXT DEFAULT NULL;
ALTER TABLE ut_table ADD COLUMN team_members TEXT DEFAULT NULL;
ALTER TABLE ut_table ADD COLUMN vegetation_coverage TEXT DEFAULT NULL;
ALTER TABLE ut_table ADD COLUMN visibility_percent INTEGER DEFAULT NULL;
ALTER TABLE ut_table ADD COLUMN weather_conditions TEXT DEFAULT NULL;

-- Table: pottery_table
ALTER TABLE pottery_table ADD COLUMN version_number INTEGER DEFAULT 1;
ALTER TABLE pottery_table ADD COLUMN editing_by TEXT DEFAULT NULL;
ALTER TABLE pottery_table ADD COLUMN editing_since TEXT DEFAULT NULL;
ALTER TABLE pottery_table ADD COLUMN last_modified_by TEXT DEFAULT NULL;
ALTER TABLE pottery_table ADD COLUMN last_modified_timestamp TEXT DEFAULT NULL;
ALTER TABLE pottery_table ADD COLUMN audit_trail TEXT DEFAULT NULL;
ALTER TABLE pottery_table ADD COLUMN datazione TEXT DEFAULT NULL;
ALTER TABLE pottery_table ADD COLUMN decoration_motif TEXT DEFAULT NULL;
ALTER TABLE pottery_table ADD COLUMN decoration_position TEXT DEFAULT NULL;
ALTER TABLE pottery_table ADD COLUMN decoration_type TEXT DEFAULT NULL;

-- Table: archeozoology_table
ALTER TABLE archeozoology_table ADD COLUMN version_number INTEGER DEFAULT 1;
ALTER TABLE archeozoology_table ADD COLUMN editing_by TEXT DEFAULT NULL;
ALTER TABLE archeozoology_table ADD COLUMN editing_since TEXT DEFAULT NULL;
ALTER TABLE archeozoology_table ADD COLUMN audit_trail TEXT DEFAULT NULL;

-- Table: pyarchinit_thesaurus_sigle
ALTER TABLE pyarchinit_thesaurus_sigle ADD COLUMN version_number INTEGER DEFAULT 1;
ALTER TABLE pyarchinit_thesaurus_sigle ADD COLUMN editing_by TEXT DEFAULT NULL;
ALTER TABLE pyarchinit_thesaurus_sigle ADD COLUMN editing_since TEXT DEFAULT NULL;
ALTER TABLE pyarchinit_thesaurus_sigle ADD COLUMN last_modified_by TEXT DEFAULT NULL;
ALTER TABLE pyarchinit_thesaurus_sigle ADD COLUMN last_modified_timestamp TEXT DEFAULT NULL;


-- ============================================================
-- PART 3: UT GEOMETRY TABLES
-- ============================================================

-- Table: pyarchinit_ut_line
CREATE TABLE IF NOT EXISTS pyarchinit_ut_line (
    gid INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT,
    area TEXT,
    definizione TEXT,
    strapiombo TEXT,
    pendenza TEXT,
    quota_min REAL,
    quota_max REAL,
    the_geom TEXT
);

SELECT AddGeometryColumn('pyarchinit_ut_line', 'the_geom', 4326, 'LINESTRING', 'XY');

-- Table: pyarchinit_ut_point
CREATE TABLE IF NOT EXISTS pyarchinit_ut_point (
    gid INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT,
    area TEXT,
    definizione TEXT,
    strapiombo TEXT,
    pendenza TEXT,
    quota_min REAL,
    quota_max REAL,
    the_geom TEXT
);

SELECT AddGeometryColumn('pyarchinit_ut_point', 'the_geom', 4326, 'POINT', 'XY');

-- Table: pyarchinit_ut_polygon
CREATE TABLE IF NOT EXISTS pyarchinit_ut_polygon (
    gid INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT,
    area TEXT,
    definizione TEXT,
    strapiombo TEXT,
    pendenza TEXT,
    quota_min REAL,
    quota_max REAL,
    the_geom TEXT
);

SELECT AddGeometryColumn('pyarchinit_ut_polygon', 'the_geom', 4326, 'POLYGON', 'XY');

-- Table: pyarchinit_sync_lock
CREATE TABLE IF NOT EXISTS pyarchinit_sync_lock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_id INTEGER NOT NULL,
    locked_by TEXT NOT NULL,
    locked_at TEXT NOT NULL,
    lock_type TEXT DEFAULT 'edit',
    expires_at TEXT
);

-- Table: pyarchinit_tipologia_sepolture
CREATE TABLE IF NOT EXISTS pyarchinit_tipologia_sepolture (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sigla TEXT,
    descrizione TEXT
);

-- ============================================================
-- PART 4: TRIGGERS FOR CONCURRENCY CONTROL (SQLite version)
-- ============================================================

-- Trigger to auto-update last_modified_timestamp on us_table
CREATE TRIGGER IF NOT EXISTS trg_us_table_last_modified
AFTER UPDATE ON us_table
FOR EACH ROW
BEGIN
    UPDATE us_table SET last_modified_timestamp = datetime('now') WHERE id_us = NEW.id_us;
END;

-- Trigger to auto-update last_modified_timestamp on site_table
CREATE TRIGGER IF NOT EXISTS trg_site_table_last_modified
AFTER UPDATE ON site_table
FOR EACH ROW
BEGIN
    UPDATE site_table SET last_modified_timestamp = datetime('now') WHERE id_sito = NEW.id_sito;
END;

-- Trigger to auto-update last_modified_timestamp on inventario_materiali_table
CREATE TRIGGER IF NOT EXISTS trg_inventario_materiali_last_modified
AFTER UPDATE ON inventario_materiali_table
FOR EACH ROW
BEGIN
    UPDATE inventario_materiali_table SET last_modified_timestamp = datetime('now') WHERE id_invmat = NEW.id_invmat;
END;

-- ============================================================
-- PART 5: INDEXES FOR BETTER PERFORMANCE
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_us_table_sito ON us_table(sito);
CREATE INDEX IF NOT EXISTS idx_us_table_area ON us_table(area);
CREATE INDEX IF NOT EXISTS idx_inventario_sito ON inventario_materiali_table(sito);
CREATE INDEX IF NOT EXISTS idx_site_table_sito ON site_table(sito);
CREATE INDEX IF NOT EXISTS idx_pyarchinit_sync_lock_table ON pyarchinit_sync_lock(table_name, record_id);

