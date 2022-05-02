SELECT pg_catalog.set_config('search_path', 'public', false);

CREATE EXTENSION postgis;

SET default_tablespace = '';
----SET default_with_oids = false;


--
-- TOC entry 266 (class 1259 OID 32422)
-- Name: archeozoology_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.archeozoology_table (
    id_archzoo integer NOT NULL,
    sito text,
    area text,
    us integer,
    quadrato text,
    coord_x integer,
    coord_y integer,
    bos_bison integer,
    calcinati integer,
    camoscio integer,
    capriolo integer,
    cervo integer,
    combusto integer,
    coni integer,
    pdi integer,
    stambecco integer,
    strie integer,
    canidi integer,
    ursidi integer,
    megacero integer
);


ALTER TABLE public.archeozoology_table OWNER TO postgres;

--
-- TOC entry 267 (class 1259 OID 32428)
-- Name: archeozoology_table_id_archzoo_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.archeozoology_table_id_archzoo_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.archeozoology_table_id_archzoo_seq OWNER TO postgres;

--
-- TOC entry 5013 (class 0 OID 0)
-- Dependencies: 267
-- Name: archeozoology_table_id_archzoo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.archeozoology_table_id_archzoo_seq OWNED BY public.archeozoology_table.id_archzoo;


--
-- TOC entry 268 (class 1259 OID 32430)
-- Name: campioni_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.campioni_table (
    id_campione integer NOT NULL,
    sito text,
    nr_campione integer,
    tipo_campione text,
    descrizione text,
    area character varying(20),
    us integer,
    numero_inventario_materiale integer,
    nr_cassa integer,
    luogo_conservazione text
);


ALTER TABLE public.campioni_table OWNER TO postgres;

--
-- TOC entry 269 (class 1259 OID 32436)
-- Name: campioni_table_id_campione_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.campioni_table_id_campione_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.campioni_table_id_campione_seq OWNER TO postgres;

--
-- TOC entry 5017 (class 0 OID 0)
-- Dependencies: 269
-- Name: campioni_table_id_campione_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.campioni_table_id_campione_seq OWNED BY public.campioni_table.id_campione;


--
-- TOC entry 296 (class 1259 OID 32566)
-- Name: deteta_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deteta_table (
    id_det_eta integer NOT NULL,
    sito text,
    nr_individuo integer,
    sinf_min integer,
    sinf_max integer,
    sinf_min_2 integer,
    sinf_max_2 integer,
    "SSPIA" integer,
    "SSPIB" integer,
    "SSPIC" integer,
    "SSPID" integer,
    sup_aur_min integer,
    sup_aur_max integer,
    sup_aur_min_2 integer,
    sup_aur_max_2 integer,
    ms_sup_min integer,
    ms_sup_max integer,
    ms_inf_min integer,
    ms_inf_max integer,
    usura_min integer,
    usura_max integer,
    "Id_endo" integer,
    "Is_endo" integer,
    "IId_endo" integer,
    "IIs_endo" integer,
    "IIId_endo" integer,
    "IIIs_endo" integer,
    "IV_endo" integer,
    "V_endo" integer,
    "VI_endo" integer,
    "VII_endo" integer,
    "VIIId_endo" integer,
    "VIIIs_endo" integer,
    "IXd_endo" integer,
    "IXs_endo" integer,
    "Xd_endo" integer,
    "Xs_endo" integer,
    endo_min integer,
    endo_max integer,
    volta_1 integer,
    volta_2 integer,
    volta_3 integer,
    volta_4 integer,
    volta_5 integer,
    volta_6 integer,
    volta_7 integer,
    lat_6 integer,
    lat_7 integer,
    lat_8 integer,
    lat_9 integer,
    lat_10 integer,
    volta_min integer,
    volta_max integer,
    ant_lat_min integer,
    ant_lat_max integer,
    ecto_min integer,
    ecto_max integer
);


ALTER TABLE public.deteta_table OWNER TO postgres;

--
-- TOC entry 297 (class 1259 OID 32572)
-- Name: deteta_table_id_det_eta_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.deteta_table_id_det_eta_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.deteta_table_id_det_eta_seq OWNER TO postgres;

--
-- TOC entry 5033 (class 0 OID 0)
-- Dependencies: 297
-- Name: deteta_table_id_det_eta_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.deteta_table_id_det_eta_seq OWNED BY public.deteta_table.id_det_eta;


--
-- TOC entry 298 (class 1259 OID 32574)
-- Name: detsesso_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.detsesso_table (
    id_det_sesso integer NOT NULL,
    sito text,
    num_individuo integer,
    glab_grado_imp integer,
    pmast_grado_imp integer,
    pnuc_grado_imp integer,
    pzig_grado_imp integer,
    arcsop_grado_imp integer,
    tub_grado_imp integer,
    pocc_grado_imp integer,
    inclfr_grado_imp integer,
    zig_grado_imp integer,
    msorb_grado_imp integer,
    glab_valori integer,
    pmast_valori integer,
    pnuc_valori integer,
    pzig_valori integer,
    arcsop_valori integer,
    tub_valori integer,
    pocc_valori integer,
    inclfr_valori integer,
    zig_valori integer,
    msorb_valori integer,
    palato_grado_imp integer,
    mfmand_grado_imp integer,
    mento_grado_imp integer,
    anmand_grado_imp integer,
    minf_grado_imp integer,
    brmont_grado_imp integer,
    condm_grado_imp integer,
    palato_valori integer,
    mfmand_valori integer,
    mento_valori integer,
    anmand_valori integer,
    minf_valori integer,
    brmont_valori integer,
    condm_valori integer,
    sex_cr_tot real,
    ind_cr_sex character varying(100),
    "sup_p_I" character varying(1),
    "sup_p_II" character varying(1),
    "sup_p_III" character varying(1),
    sup_p_sex character varying(1),
    "in_isch_I" character varying(1),
    "in_isch_II" character varying(1),
    "in_isch_III" character varying(1),
    in_isch_sex character varying(1),
    arco_c_sex character varying(1),
    "ramo_ip_I" character varying(1),
    "ramo_ip_II" character varying(1),
    "ramo_ip_III" character varying(1),
    ramo_ip_sex character varying(1),
    prop_ip_sex character varying(1),
    ind_bac_sex character varying(100)
);


ALTER TABLE public.detsesso_table OWNER TO postgres;

--
-- TOC entry 299 (class 1259 OID 32580)
-- Name: detsesso_table_id_det_sesso_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.detsesso_table_id_det_sesso_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.detsesso_table_id_det_sesso_seq OWNER TO postgres;

--
-- TOC entry 5034 (class 0 OID 0)
-- Dependencies: 299
-- Name: detsesso_table_id_det_sesso_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.detsesso_table_id_det_sesso_seq OWNED BY public.detsesso_table.id_det_sesso;


--
-- TOC entry 302 (class 1259 OID 32590)
-- Name: documentazione_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.documentazione_table (
    id_documentazione integer NOT NULL,
    sito text,
    nome_doc text,
    data text,
    tipo_documentazione text,
    sorgente text,
    scala text,
    disegnatore text,
    note text
);


ALTER TABLE public.documentazione_table OWNER TO postgres;

--
-- TOC entry 303 (class 1259 OID 32596)
-- Name: documentazione_table_id_documentazione_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.documentazione_table_id_documentazione_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.documentazione_table_id_documentazione_seq OWNER TO postgres;

--
-- TOC entry 5036 (class 0 OID 0)
-- Dependencies: 303
-- Name: documentazione_table_id_documentazione_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.documentazione_table_id_documentazione_seq OWNED BY public.documentazione_table.id_documentazione;


--
-- TOC entry 309 (class 1259 OID 32623)
-- Name: individui_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.individui_table (
    id_scheda_ind integer NOT NULL,
    sito text,
    area character varying(20),
    us text,
    nr_individuo integer,
    data_schedatura character varying(100),
    schedatore character varying(100),
    sesso character varying(100),
    eta_min text,
    eta_max text,
    classi_eta character varying(100),
    osservazioni text,
	sigla_struttura character varying(100),
	nr_struttura integer,
	completo_si_no character varying(4),
    disturbato_si_no character varying(4),
    in_connessione_si_no character varying(4),
	lunghezza_scheletro real,
    posizione_scheletro character varying(250),
    posizione_cranio character varying(250),
    posizione_arti_superiori character varying(250),
    posizione_arti_inferiori character varying(250),
	orientamento_asse text,
	orientamento_azimut text
	);


ALTER TABLE public.individui_table OWNER TO postgres;

--
-- TOC entry 310 (class 1259 OID 32629)
-- Name: individui_table_id_scheda_ind_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.individui_table_id_scheda_ind_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.individui_table_id_scheda_ind_seq OWNER TO postgres;

--
-- TOC entry 5040 (class 0 OID 0)
-- Dependencies: 310
-- Name: individui_table_id_scheda_ind_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.individui_table_id_scheda_ind_seq OWNED BY public.individui_table.id_scheda_ind;


--
-- TOC entry 311 (class 1259 OID 32631)
-- Name: inventario_materiali_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inventario_materiali_table (
    id_invmat integer NOT NULL,
    sito text,
    numero_inventario integer,
    tipo_reperto text,
    criterio_schedatura text,
    definizione text,
    descrizione text,
    area integer,
    us integer,
    lavato character varying(3),
    nr_cassa integer,
    luogo_conservazione text,
    stato_conservazione character varying (200) DEFAULT ''::character varying,
    datazione_reperto character varying(200) DEFAULT ''::character varying,
    elementi_reperto text,
    misurazioni text,
    rif_biblio text,
    tecnologie text,
    forme_minime integer DEFAULT 0,
    forme_massime integer DEFAULT 0,
    totale_frammenti integer DEFAULT 0,
    corpo_ceramico character varying(200),
    rivestimento character varying(200),
    diametro_orlo numeric(7,3) DEFAULT 0,
    peso numeric(9,3) DEFAULT 0,
    tipo character varying(200),
    eve_orlo numeric(7,3) DEFAULT 0,
    repertato character varying(3),
    diagnostico character varying(3),
	n_reperto integer,
	tipo_contenitore character varying(200),
	struttura character varying(200)
);


ALTER TABLE public.inventario_materiali_table OWNER TO postgres;

--
-- TOC entry 312 (class 1259 OID 32645)
-- Name: inventario_materiali_table_id_invmat_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inventario_materiali_table_id_invmat_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.inventario_materiali_table_id_invmat_seq OWNER TO postgres;

--
-- TOC entry 5042 (class 0 OID 0)
-- Dependencies: 312
-- Name: inventario_materiali_table_id_invmat_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventario_materiali_table_id_invmat_seq OWNED BY public.inventario_materiali_table.id_invmat;


--
-- TOC entry 313 (class 1259 OID 32647)
-- Name: inventario_materiali_table_toimp; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inventario_materiali_table_toimp (
    id_invmat integer NOT NULL,
    sito text,
    numero_inventario integer,
    tipo_reperto text,
    criterio_schedatura text,
    definizione text,
    descrizione text,
    area integer,
    us integer,
    lavato character varying(2),
    nr_cassa integer,
    luogo_conservazione text,
    stato_conservazione character varying(20),
    datazione_reperto character varying(30),
    elementi_reperto text,
    misurazioni text,
    rif_biblio text,
    tecnologie text
);


ALTER TABLE public.inventario_materiali_table_toimp OWNER TO postgres;

--
-- TOC entry 314 (class 1259 OID 32653)
-- Name: inventario_materiali_table_toimp_id_invmat_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inventario_materiali_table_toimp_id_invmat_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.inventario_materiali_table_toimp_id_invmat_seq OWNER TO postgres;

--
-- TOC entry 5043 (class 0 OID 0)
-- Dependencies: 314
-- Name: inventario_materiali_table_toimp_id_invmat_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventario_materiali_table_toimp_id_invmat_seq OWNED BY public.inventario_materiali_table_toimp.id_invmat;



--
-- TOC entry 319 (class 1259 OID 32672)
-- Name: media_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.media_table (
    id_media integer NOT NULL,
    mediatype text,
    filename text,
    filetype character varying(10),
    filepath text,
    descrizione text,
    tags text
);


ALTER TABLE public.media_table OWNER TO postgres;

--
-- TOC entry 320 (class 1259 OID 32678)
-- Name: media_table_id_media_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.media_table_id_media_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.media_table_id_media_seq OWNER TO postgres;

--
-- TOC entry 5046 (class 0 OID 0)
-- Dependencies: 320
-- Name: media_table_id_media_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.media_table_id_media_seq OWNED BY public.media_table.id_media;


--
-- TOC entry 321 (class 1259 OID 32680)
-- Name: media_thumb_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.media_thumb_table (
    id_media_thumb integer NOT NULL,
    id_media integer,
    mediatype text,
    media_filename text,
    media_thumb_filename text,
    filetype character varying(10),
    filepath text,
	path_resize text
);


ALTER TABLE public.media_thumb_table OWNER TO postgres;

--
-- TOC entry 322 (class 1259 OID 32686)
-- Name: media_thumb_table_id_media_thumb_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.media_thumb_table_id_media_thumb_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.media_thumb_table_id_media_thumb_seq OWNER TO postgres;

--
-- TOC entry 5047 (class 0 OID 0)
-- Dependencies: 322
-- Name: media_thumb_table_id_media_thumb_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.media_thumb_table_id_media_thumb_seq OWNED BY public.media_thumb_table.id_media_thumb;


--
-- TOC entry 323 (class 1259 OID 32688)
-- Name: media_to_entity_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.media_to_entity_table (
    "id_mediaToEntity" integer NOT NULL,
    id_entity integer,
    entity_type text,
    table_name text,
    id_media integer,
    filepath text,
    media_name text
);


ALTER TABLE public.media_to_entity_table OWNER TO postgres;

--
-- TOC entry 324 (class 1259 OID 32694)
-- Name: media_to_entity_table_id_mediaToEntity_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."media_to_entity_table_id_mediaToEntity_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."media_to_entity_table_id_mediaToEntity_seq" OWNER TO postgres;

--
-- TOC entry 5048 (class 0 OID 0)
-- Dependencies: 324
-- Name: media_to_entity_table_id_mediaToEntity_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."media_to_entity_table_id_mediaToEntity_seq" OWNED BY public.media_to_entity_table."id_mediaToEntity";


--
-- TOC entry 325 (class 1259 OID 32696)
-- Name: media_to_us_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.media_to_us_table (
    "id_mediaToUs" integer NOT NULL,
    id_us integer,
    sito text,
    area character varying(20),
    us integer,
    id_media integer,
    filepath text
);


ALTER TABLE public.media_to_us_table OWNER TO postgres;

--
-- TOC entry 326 (class 1259 OID 32702)
-- Name: media_to_us_table_id_mediaToUs_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."media_to_us_table_id_mediaToUs_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."media_to_us_table_id_mediaToUs_seq" OWNER TO postgres;

--
-- TOC entry 5049 (class 0 OID 0)
-- Dependencies: 326
-- Name: media_to_us_table_id_mediaToUs_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."media_to_us_table_id_mediaToUs_seq" OWNED BY public.media_to_us_table."id_mediaToUs";


CREATE TABLE public.pdf_administrator_table (
    id_pdf_administrator integer NOT NULL,
    table_name text,
    schema_griglia text,
    schema_fusione_celle text,
    modello text
);


ALTER TABLE public.pdf_administrator_table OWNER TO postgres;

--
-- TOC entry 328 (class 1259 OID 32710)
-- Name: pdf_administrator_table_id_pdf_administrator_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pdf_administrator_table_id_pdf_administrator_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pdf_administrator_table_id_pdf_administrator_seq OWNER TO postgres;

--
-- TOC entry 5050 (class 0 OID 0)
-- Dependencies: 328
-- Name: pdf_administrator_table_id_pdf_administrator_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pdf_administrator_table_id_pdf_administrator_seq OWNED BY public.pdf_administrator_table.id_pdf_administrator;


--
-- TOC entry 329 (class 1259 OID 32712)
-- Name: periodizzazione_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.periodizzazione_table (
    id_perfas integer NOT NULL,
    sito text,
    periodo integer,
    fase text,
    cron_iniziale integer,
    cron_finale integer,
    descrizione text,
    datazione_estesa character varying(300),
    cont_per integer,
	area integer
);


ALTER TABLE public.periodizzazione_table OWNER TO postgres;

--
-- TOC entry 330 (class 1259 OID 32718)
-- Name: periodizzazione_table_id_perfas_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.periodizzazione_table_id_perfas_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.periodizzazione_table_id_perfas_seq OWNER TO postgres;

--
-- TOC entry 5051 (class 0 OID 0)
-- Dependencies: 330
-- Name: periodizzazione_table_id_perfas_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.periodizzazione_table_id_perfas_seq OWNED BY public.periodizzazione_table.id_perfas;

--
-- TOC entry 333 (class 1259 OID 32728)
-- Name: pyarchinit_campionature; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_campionature (
    gid integer NOT NULL,
    id_campion integer,
    sito character varying(200),
    tipo_campi character varying(200),
    datazione_ character varying(200),
    cronologia integer,
    link_immag character varying(500),
    sigla_camp character varying,
    the_geom public.geometry(Point,-1)
);


ALTER TABLE public.pyarchinit_campionature OWNER TO postgres;

--
-- TOC entry 334 (class 1259 OID 32734)
-- Name: pyarchinit_codici_tipologia_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyarchinit_codici_tipologia_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyarchinit_codici_tipologia_id_seq OWNER TO postgres;

--
-- TOC entry 335 (class 1259 OID 32736)
-- Name: pyarchinit_codici_tipologia; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_codici_tipologia (
    id integer DEFAULT nextval('public.pyarchinit_codici_tipologia_id_seq'::regclass) NOT NULL,
    tipologia_progetto character varying,
    tipologia_definizione_tipologia character varying,
    tipologia_gruppo character varying,
    tipologia_definizione_gruppo character varying,
    tipologia_codice character(5),
    tipologia_sottocodice character varying,
    tipologia_definizione_codice character varying,
    tipologia_descrizione character varying
);


ALTER TABLE public.pyarchinit_codici_tipologia OWNER TO postgres;

--
-- TOC entry 336 (class 1259 OID 32743)
-- Name: pyarchinit_individui; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_individui (
    gid integer NOT NULL,
    sito character varying(255),
    sigla_struttura character varying(255),
    note character varying(255),
    the_geom public.geometry(Point,-1),
    id_individuo integer
);


ALTER TABLE public.pyarchinit_individui OWNER TO postgres;

--
-- TOC entry 337 (class 1259 OID 32749)
-- Name: pyarchinit_individui_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyarchinit_individui_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyarchinit_individui_gid_seq OWNER TO postgres;

--
-- TOC entry 5053 (class 0 OID 0)
-- Dependencies: 337
-- Name: pyarchinit_individui_gid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pyarchinit_individui_gid_seq OWNED BY public.pyarchinit_individui.gid;


--
-- TOC entry 339 (class 1259 OID 32756)
-- Name: pyarchinit_inventario_materiali; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_inventario_materiali (
    idim_pk integer NOT NULL,
    sito character varying(150),
    area integer,
    us integer,
    nr_cassa integer,
    tipo_materiale character varying(120) DEFAULT 'Ceramica'::character varying,
    nr_reperto integer,
    lavato_si_no character(2) DEFAULT 'si'::bpchar,
    descrizione_rep character varying
);


ALTER TABLE public.pyarchinit_inventario_materiali OWNER TO postgres;

--SET default_with_oids = true;


--
-- TOC entry 342 (class 1259 OID 32778)
-- Name: pyarchinit_linee_rif_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyarchinit_linee_rif_gid_seq
    START WITH 6375
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyarchinit_linee_rif_gid_seq OWNER TO postgres;

--SET default_with_oids = false;

--
-- TOC entry 343 (class 1259 OID 32780)
-- Name: pyarchinit_linee_rif; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_linee_rif (
    gid integer DEFAULT nextval('public.pyarchinit_linee_rif_gid_seq'::regclass) NOT NULL,
    sito character varying(300),
    definizion character varying(80),
    descrizion character varying(80),
    the_geom public.geometry(LineString,-1),
    distanza numeric(10,2)
);


ALTER TABLE public.pyarchinit_linee_rif OWNER TO postgres;

--
-- TOC entry 344 (class 1259 OID 32787)
-- Name: pyarchinit_punti_rif_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyarchinit_punti_rif_gid_seq
    START WITH 4928
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyarchinit_punti_rif_gid_seq OWNER TO postgres;

--
-- TOC entry 345 (class 1259 OID 32789)
-- Name: pyarchinit_punti_rif; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_punti_rif (
    gid integer DEFAULT nextval('public.pyarchinit_punti_rif_gid_seq'::regclass) NOT NULL,
    sito character varying(80),
    def_punto character varying(80),
    id_punto character varying(80),
    quota double precision,
    the_geom public.geometry(Point,-1),
    unita_misura_quota character varying,
    area integer,
    orientamento numeric(5,2)
);


ALTER TABLE public.pyarchinit_punti_rif OWNER TO postgres;

--
-- TOC entry 346 (class 1259 OID 32796)
-- Name: pyuscarlinee; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyuscarlinee (
    gid integer NOT NULL,
    sito_l character varying(150),
    area_l integer,
    us_l integer,
    tipo_us_l character varying(150),
    the_geom public.geometry(LineString,-1)
);


ALTER TABLE public.pyuscarlinee OWNER TO postgres;

--
-- TOC entry 347 (class 1259 OID 32802)
-- Name: us_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.us_table (
    id_us integer NOT NULL,
    sito text,
    area character varying(20),
    us integer,
    d_stratigrafica character varying(255),
    d_interpretativa character varying(255),
    descrizione text,
    interpretazione text,
    periodo_iniziale character varying(4),
    fase_iniziale character varying(4),
    periodo_finale character varying(4),
    fase_finale character varying(4),
    scavato character varying(3),
    attivita character varying(4),
    anno_scavo character varying(4),
    metodo_di_scavo character varying(20),
    inclusi text,
    campioni text,
    rapporti text,
    data_schedatura character varying(20),
    schedatore character varying(45),
    formazione character varying(20),
    stato_di_conservazione character varying(20),
    colore character varying(20),
    consistenza character varying(20),
    struttura character varying(30),
    cont_per character varying(200),
    order_layer integer DEFAULT 0,
    documentazione text,
    unita_tipo character varying DEFAULT 'US'::character varying,
    settore text DEFAULT ''::text,
    quad_par text DEFAULT ''::text,
    ambient text DEFAULT ''::text,
    saggio text DEFAULT ''::text,
    elem_datanti text DEFAULT ''::text,
    funz_statica text DEFAULT ''::text,
    lavorazione text DEFAULT ''::text,
    spess_giunti text DEFAULT ''::text,
    letti_posa text DEFAULT ''::text,
    alt_mod text DEFAULT ''::text,
    un_ed_riass text DEFAULT ''::text,
    reimp text DEFAULT ''::text,
    posa_opera text DEFAULT ''::text,
    quota_min_usm numeric(6,2),
    quota_max_usm numeric(6,2),
    cons_legante text DEFAULT ''::text,
    col_legante text DEFAULT ''::text,
    aggreg_legante text DEFAULT ''::text,
    con_text_mat text DEFAULT ''::text,
    col_materiale text DEFAULT ''::text,
    inclusi_materiali_usm text DEFAULT '[]'::text,
    n_catalogo_generale text DEFAULT ''::text,
    n_catalogo_interno text DEFAULT ''::text,
    n_catalogo_internazionale text DEFAULT ''::text,
    soprintendenza text DEFAULT ''::text,
    quota_relativa numeric(6,2),
    quota_abs numeric(6,2),
    ref_tm text DEFAULT ''::text,
    ref_ra text DEFAULT ''::text,
    ref_n text DEFAULT ''::text,
    posizione text DEFAULT ''::text,
    criteri_distinzione text DEFAULT ''::text,
    modo_formazione text DEFAULT ''::text,
    componenti_organici text DEFAULT ''::text,
    componenti_inorganici text DEFAULT ''::text,
    lunghezza_max numeric(6,2),
    altezza_max numeric(6,2),
    altezza_min numeric(6,2),
    profondita_max numeric(6,2),
    profondita_min numeric(6,2),
    larghezza_media numeric(6,2),
    quota_max_abs numeric(6,2),
    quota_max_rel numeric(6,2),
    quota_min_abs numeric(6,2),
    quota_min_rel numeric(6,2),
    osservazioni text DEFAULT ''::text,
    datazione text DEFAULT ''::text,
    flottazione text DEFAULT ''::text,
    setacciatura text DEFAULT ''::text,
    affidabilita text DEFAULT ''::text,
    direttore_us text DEFAULT ''::text,
    responsabile_us text DEFAULT ''::text,
    cod_ente_schedatore text DEFAULT ''::text,
    data_rilevazione text DEFAULT ''::text,
    data_rielaborazione text DEFAULT ''::text,
    lunghezza_usm numeric(6,2),
    altezza_usm numeric(6,2),
    spessore_usm numeric(6,2),
    tecnica_muraria_usm text DEFAULT ''::text,
    modulo_usm text DEFAULT ''::text,
    campioni_malta_usm text DEFAULT ''::text,
    campioni_mattone_usm text DEFAULT ''::text,
    campioni_pietra_usm text DEFAULT ''::text,
    provenienza_materiali_usm text DEFAULT ''::text,
    criteri_distinzione_usm text DEFAULT ''::text,
    uso_primario_usm text DEFAULT ''::text,
	doc_usv text DEFAULT ''::text
);


ALTER TABLE public.us_table OWNER TO postgres;

--
-- TOC entry 349 (class 1259 OID 32814)
-- Name: pyarchinit_quote_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyarchinit_quote_gid_seq
    START WITH 73833
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyarchinit_quote_gid_seq OWNER TO postgres;

--
-- TOC entry 349 (class 1259 OID 32814)
-- Name: pyarchinit_quote_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyarchinit_quote_usm_gid_seq
    START WITH 73833
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyarchinit_quote_usm_gid_seq OWNER TO postgres;

--
-- TOC entry 350 (class 1259 OID 32816)
-- Name: pyarchinit_quote; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_quote (
    gid integer DEFAULT nextval('public.pyarchinit_quote_gid_seq'::regclass) NOT NULL,
    sito_q character varying(80),
    area_q integer,
    us_q integer,
    unita_misu_q character varying(80),
    quota_q double precision,
    the_geom public.geometry(Point,-1),
    data character varying,
    disegnatore character varying,
    rilievo_originale character varying,
	unita_tipo_q character varying
);


ALTER TABLE public.pyarchinit_quote OWNER TO postgres;
--
-- TOC entry 350 (class 1259 OID 32816)
-- Name: pyarchinit_quote; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_quote_usm (
    gid integer DEFAULT nextval('public.pyarchinit_quote_usm_gid_seq'::regclass) NOT NULL,
    sito_q character varying(80),
    area_q integer,
    us_q integer,
    unita_misu_q character varying(80),
    quota_q double precision,
    the_geom public.geometry(Point,-1),
    data character varying,
    disegnatore character varying,
    rilievo_originale character varying,
	unita_tipo_q character varying
);


ALTER TABLE public.pyarchinit_quote_usm OWNER TO postgres;
--
-- TOC entry 352 (class 1259 OID 32828)
-- Name: pyarchinit_ripartizioni_spaziali_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyarchinit_ripartizioni_spaziali_gid_seq
    START WITH 2007
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyarchinit_ripartizioni_spaziali_gid_seq OWNER TO postgres;

--
-- TOC entry 353 (class 1259 OID 32830)
-- Name: pyarchinit_ripartizioni_spaziali; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_ripartizioni_spaziali (
    gid integer DEFAULT nextval('public.pyarchinit_ripartizioni_spaziali_gid_seq'::regclass) NOT NULL,
    id_rs character varying(80),
    sito_rs character varying(80),
    the_geom public.geometry(Polygon,-1),
    tip_rip character varying,
    descr_rs character varying
);


ALTER TABLE public.pyarchinit_ripartizioni_spaziali OWNER TO postgres;

--
-- TOC entry 354 (class 1259 OID 32837)
-- Name: pyarchinit_ripartizioni_temporali; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_ripartizioni_temporali (
    sito character varying,
    sigla_periodo character varying(10),
    sigla_fase character varying(10),
    cronologia_numerica integer,
    cronologia_numerica_finale integer,
    datazione_estesa_stringa character varying,
    id_periodo integer NOT NULL,
    descrizione character varying
);


ALTER TABLE public.pyarchinit_ripartizioni_temporali OWNER TO postgres;

--
-- TOC entry 355 (class 1259 OID 32843)
-- Name: pyarchinit_ripartizioni_temporali_id_periodo_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyarchinit_ripartizioni_temporali_id_periodo_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyarchinit_ripartizioni_temporali_id_periodo_seq OWNER TO postgres;

--
-- TOC entry 5054 (class 0 OID 0)
-- Dependencies: 355
-- Name: pyarchinit_ripartizioni_temporali_id_periodo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pyarchinit_ripartizioni_temporali_id_periodo_seq OWNED BY public.pyarchinit_ripartizioni_temporali.id_periodo;


--
-- TOC entry 356 (class 1259 OID 32845)
-- Name: pyarchinit_rou_thesaurus; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_rou_thesaurus (
    "ID_rou" integer NOT NULL,
    valore_ro character varying,
    rou_descrizione character varying
);


ALTER TABLE public.pyarchinit_rou_thesaurus OWNER TO postgres;

--
-- TOC entry 357 (class 1259 OID 32851)
-- Name: pyarchinit_rou_thesaurus_ID_rou_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."pyarchinit_rou_thesaurus_ID_rou_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."pyarchinit_rou_thesaurus_ID_rou_seq" OWNER TO postgres;

--
-- TOC entry 5055 (class 0 OID 0)
-- Dependencies: 357
-- Name: pyarchinit_rou_thesaurus_ID_rou_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."pyarchinit_rou_thesaurus_ID_rou_seq" OWNED BY public.pyarchinit_rou_thesaurus."ID_rou";


--
-- TOC entry 358 (class 1259 OID 32853)
-- Name: pyarchinit_sezioni_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyarchinit_sezioni_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyarchinit_sezioni_gid_seq OWNER TO postgres;

--
-- TOC entry 359 (class 1259 OID 32855)
-- Name: pyarchinit_sezioni; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_sezioni (
    gid integer DEFAULT nextval('public.pyarchinit_sezioni_gid_seq'::regclass) NOT NULL,
    id_sezione character varying(80),
    sito character varying(80),
    area integer,
    descr character varying(80),
    the_geom public.geometry(LineString,-1),
	tipo_doc text,
	nome_doc text
);


ALTER TABLE public.pyarchinit_sezioni OWNER TO postgres;

--
-- TOC entry 360 (class 1259 OID 32862)
-- Name: pyarchinit_siti_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyarchinit_siti_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyarchinit_siti_gid_seq OWNER TO postgres;

--
-- TOC entry 361 (class 1259 OID 32864)
-- Name: pyarchinit_siti; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_siti (
    gid integer DEFAULT nextval('public.pyarchinit_siti_gid_seq'::regclass) NOT NULL,
    sito_nome character varying(80),
    the_geom public.geometry(Point,-1),
    link character varying(300)
);


ALTER TABLE public.pyarchinit_siti OWNER TO postgres;




--
-- TOC entry 360 (class 1259 OID 32862)
-- Name: pyarchinit_siti_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyarchinit_siti_polygonal_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyarchinit_siti_polygonal_gid_seq OWNER TO postgres;

--
-- TOC entry 361 (class 1259 OID 32864)
-- Name: pyarchinit_siti_polygon; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_siti_polygonal (
    gid integer DEFAULT nextval('public.pyarchinit_siti_polygonal_gid_seq'::regclass) NOT NULL,
    sito_id character varying(80),
    the_geom public.geometry(Polygon,-1)
);


ALTER TABLE public.pyarchinit_siti_polygonal OWNER TO postgres;





--
-- TOC entry 362 (class 1259 OID 32871)
-- Name: pyarchinit_sondaggi_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyarchinit_sondaggi_gid_seq
    START WITH 1262
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyarchinit_sondaggi_gid_seq OWNER TO postgres;



--
-- TOC entry 363 (class 1259 OID 32873)
-- Name: pyarchinit_sondaggi; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_sondaggi (
    gid integer DEFAULT nextval('public.pyarchinit_sondaggi_gid_seq'::regclass) NOT NULL,
    sito character varying(80),
    id_sondagg character varying(80),
    the_geom public.geometry(Polygon,-1)
);


ALTER TABLE public.pyarchinit_sondaggi OWNER TO postgres;

--
-- TOC entry 364 (class 1259 OID 32880)
-- Name: pyarchinit_strutture_ipotesi_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyarchinit_strutture_ipotesi_gid_seq
    START WITH 842
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyarchinit_strutture_ipotesi_gid_seq OWNER TO postgres;

--
-- TOC entry 365 (class 1259 OID 32882)
-- Name: pyarchinit_strutture_ipotesi; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_strutture_ipotesi (
    gid integer DEFAULT nextval('public.pyarchinit_strutture_ipotesi_gid_seq'::regclass) NOT NULL,
    sito character varying(80),
    id_strutt character varying(80),
    per_iniz integer,
    per_fin integer,
    dataz_ext character varying(80),
    the_geom public.geometry(Polygon,-1),
    fase_iniz integer,
    fase_fin integer,
    descrizione character varying,
    nr_strut integer DEFAULT 0,
    sigla_strut character varying(3) DEFAULT 'NoD'::character varying
);


ALTER TABLE public.pyarchinit_strutture_ipotesi OWNER TO postgres;

--
-- TOC entry 400 (class 1259 OID 33070)
-- Name: struttura_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.struttura_table (
    id_struttura integer NOT NULL,
    sito text,
    sigla_struttura text,
    numero_struttura integer,
    categoria_struttura text,
    tipologia_struttura text,
    definizione_struttura text,
    descrizione text,
    interpretazione text,
    periodo_iniziale integer,
    fase_iniziale integer,
    periodo_finale integer,
    fase_finale integer,
    datazione_estesa character varying(300),
    materiali_impiegati text,
    elementi_strutturali text,
    rapporti_struttura text,
    misure_struttura text
);


ALTER TABLE public.struttura_table OWNER TO postgres;


--
-- TOC entry 366 (class 1259 OID 32891)
-- Name: pyarchinit_tafonomia; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_tafonomia (
    gid integer NOT NULL,
    the_geom public.geometry(Point,-1),
    id_tafonomia_pk bigint,
    sito character varying,
    nr_scheda bigint
);


ALTER TABLE public.pyarchinit_tafonomia OWNER TO postgres;

--
-- TOC entry 367 (class 1259 OID 32897)
-- Name: pyarchinit_tafonomia_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyarchinit_tafonomia_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyarchinit_tafonomia_gid_seq OWNER TO postgres;

--
-- TOC entry 5056 (class 0 OID 0)
-- Dependencies: 367
-- Name: pyarchinit_tafonomia_gid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pyarchinit_tafonomia_gid_seq OWNED BY public.pyarchinit_tafonomia.gid;


--
-- TOC entry 368 (class 1259 OID 32899)
-- Name: tomba_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tomba_table (
    id_tomba integer NOT NULL,
    sito text,
	area integer,
    nr_scheda_taf integer,
    sigla_struttura text,
    nr_struttura integer,
    nr_individuo text,
    rito text,
    descrizione_taf text,
    interpretazione_taf text,
    segnacoli text,
    canale_libatorio_si_no text,
    oggetti_rinvenuti_esterno text,
    stato_di_conservazione text,
    copertura_tipo text,
    tipo_contenitore_resti text,
    tipo_deposizione text,
	tipo_sepoltura text,
    corredo_presenza text,
    corredo_tipo text,
    corredo_descrizione text,    
    periodo_iniziale integer,
    fase_iniziale integer,
    periodo_finale integer,
    fase_finale integer,
    datazione_estesa text
);


ALTER TABLE public.tomba_table OWNER TO postgres;


--
-- TOC entry 370 (class 1259 OID 32911)
-- Name: pyarchinit_thesaurus_sigle; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_thesaurus_sigle (
    id_thesaurus_sigle integer NOT NULL,
    nome_tabella character varying,
    sigla character(3),
    sigla_estesa character varying,
    descrizione character varying,
    tipologia_sigla character varying
);


ALTER TABLE public.pyarchinit_thesaurus_sigle OWNER TO postgres;

--
-- TOC entry 371 (class 1259 OID 32917)
-- Name: pyarchinit_thesaurus_sigle_id_thesaurus_sigle_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyarchinit_thesaurus_sigle_id_thesaurus_sigle_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyarchinit_thesaurus_sigle_id_thesaurus_sigle_seq OWNER TO postgres;

--
-- TOC entry 5057 (class 0 OID 0)
-- Dependencies: 371
-- Name: pyarchinit_thesaurus_sigle_id_thesaurus_sigle_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pyarchinit_thesaurus_sigle_id_thesaurus_sigle_seq OWNED BY public.pyarchinit_thesaurus_sigle.id_thesaurus_sigle;


--
-- TOC entry 372 (class 1259 OID 32919)
-- Name: pyarchinit_tipologia_sepolture_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyarchinit_tipologia_sepolture_gid_seq
    START WITH 452
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyarchinit_tipologia_sepolture_gid_seq OWNER TO postgres;

--
-- TOC entry 373 (class 1259 OID 32921)
-- Name: pyarchinit_tipologia_sepolture; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_tipologia_sepolture (
    gid integer DEFAULT nextval('public.pyarchinit_tipologia_sepolture_gid_seq'::regclass) NOT NULL,
    id_sepoltura character varying(80),
    azimut double precision,
    tipologia character varying(80),
    the_geom public.geometry(Point,-1),
    sito_ts character varying,
    t_progetto character varying,
    t_gruppo character varying,
    t_codice character varying,
    t_sottocodice character varying,
    corredo character varying
);


ALTER TABLE public.pyarchinit_tipologia_sepolture OWNER TO postgres;


--
-- TOC entry 376 (class 1259 OID 32938)
-- Name: pyarchinit_us_negative_doc; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyarchinit_us_negative_doc (
    gid integer NOT NULL,
    the_geom public.geometry(LineString,-1),
    sito_n character varying,
    area_n character varying,
    us_n bigint,
    tipo_doc_n character varying,
    nome_doc_n character varying,
    "LblSize" integer,
    "LblColor" character varying(7),
    "LblBold" integer,
    "LblItalic" integer,
    "LblUnderl" integer,
    "LblStrike" integer,
    "LblFont" character varying(100),
    "LblX" numeric(20,5),
    "LblY" numeric(20,5),
    "LblSclMin" integer,
    "LblSclMax" integer,
    "LblAlignH" character varying(15),
    "LblAlignV" character varying(15),
    "LblRot" numeric(20,5)
);


ALTER TABLE public.pyarchinit_us_negative_doc OWNER TO postgres;

--
-- TOC entry 377 (class 1259 OID 32944)
-- Name: pyarchinit_us_negative_doc_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyarchinit_us_negative_doc_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyarchinit_us_negative_doc_gid_seq OWNER TO postgres;

--
-- TOC entry 5058 (class 0 OID 0)
-- Dependencies: 377
-- Name: pyarchinit_us_negative_doc_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pyarchinit_us_negative_doc_gid_seq OWNED BY public.pyarchinit_us_negative_doc.gid;


--
-- TOC entry 378 (class 1259 OID 32946)
-- Name: pyunitastratigrafiche_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyunitastratigrafiche_gid_seq
    START WITH 61400
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyunitastratigrafiche_gid_seq OWNER TO postgres;

--
-- TOC entry 378 (class 1259 OID 32946)
-- Name: pyunitastratigrafiche_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyunitastratigrafiche_usm_gid_seq
    START WITH 61400
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyunitastratigrafiche_usm_gid_seq OWNER TO postgres;

--
-- TOC entry 379 (class 1259 OID 32948)
-- Name: pyunitastratigrafiche; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyunitastratigrafiche (
    gid integer DEFAULT nextval('public.pyunitastratigrafiche_gid_seq'::regclass) NOT NULL,
    area_s integer,
    scavo_s character varying(80),
    us_s integer,
    stratigraph_index_us integer,
    tipo_us_s character varying(250),
    rilievo_originale character varying(250),
    disegnatore character varying(250),
    data date,
    tipo_doc character varying(250),
    nome_doc character varying(250),
	coord text,
	the_geom public.geometry(MultiPolygon,-1),
	unita_tipo_s character varying
);


ALTER TABLE public.pyunitastratigrafiche OWNER TO postgres;

--
-- TOC entry 379 (class 1259 OID 32948)
-- Name: pyunitastratigrafiche; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyunitastratigrafiche_usm (
    gid integer DEFAULT nextval('public.pyunitastratigrafiche_usm_gid_seq'::regclass) NOT NULL,
    area_s integer,
    scavo_s character varying(80),
    us_s integer,
    stratigraph_index_us integer,
    tipo_us_s character varying(250),
    rilievo_originale character varying(250),
    disegnatore character varying(250),
    data date,
    tipo_doc character varying(250),
    nome_doc character varying(250),
	coord text,
	the_geom public.geometry(MultiPolygon,-1),
	unita_tipo_s character varying
);


ALTER TABLE public.pyunitastratigrafiche_usm OWNER TO postgres;

--
-- TOC entry 384 (class 1259 OID 32975)
-- Name: pyuscaratterizzazioni; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pyuscaratterizzazioni (
    gid integer NOT NULL,
    area_c integer,
    scavo_c character varying(80),
    us_c integer,
    the_geom public.geometry(MultiPolygon,-1),
    stratigraph_index_car integer DEFAULT 1,
    tipo_us_c character varying
);


ALTER TABLE public.pyuscaratterizzazioni OWNER TO postgres;

--
-- TOC entry 387 (class 1259 OID 32992)
-- Name: pyuscarlinee_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pyuscarlinee_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyuscarlinee_gid_seq OWNER TO postgres;

--
-- TOC entry 5059 (class 0 OID 0)
-- Dependencies: 387
-- Name: pyuscarlinee_gid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pyuscarlinee_gid_seq OWNED BY public.pyuscarlinee.gid;


--
-- TOC entry 417 (class 1259 OID 41273)
-- Name: relashionship_check_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.relashionship_check_table (
    id_rel_check integer NOT NULL,
    sito text,
    area text,
    us integer,
    rel_type text,
    sito_rel text,
    area_rel text,
    us_rel text,
    error_type text,
    note text
);


ALTER TABLE public.relashionship_check_table OWNER TO postgres;

--
-- TOC entry 416 (class 1259 OID 41271)
-- Name: relashionship_check_table_id_rel_check_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.relashionship_check_table_id_rel_check_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.relashionship_check_table_id_rel_check_seq OWNER TO postgres;

--
-- TOC entry 5060 (class 0 OID 0)
-- Dependencies: 416
-- Name: relashionship_check_table_id_rel_check_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.relashionship_check_table_id_rel_check_seq OWNED BY public.relashionship_check_table.id_rel_check;

--
-- TOC entry 422 (class 1259 OID 66359)
-- Name: riipartizione_territoriale; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.riipartizione_territoriale (
    id_div_terr_pk integer NOT NULL,
    tipo text NOT NULL,
    nome text NOT NULL,
    tipo_localizzazione text NOT NULL,
    the_geom public.geometry(Point,-1)
);


ALTER TABLE public.riipartizione_territoriale OWNER TO postgres;

--
-- TOC entry 421 (class 1259 OID 66357)
-- Name: riipartizione_territoriale_id_div_terr_pk_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.riipartizione_territoriale_id_div_terr_pk_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.riipartizione_territoriale_id_div_terr_pk_seq OWNER TO postgres;

--
-- TOC entry 5061 (class 0 OID 0)
-- Dependencies: 421
-- Name: riipartizione_territoriale_id_div_terr_pk_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.riipartizione_territoriale_id_div_terr_pk_seq OWNED BY public.riipartizione_territoriale.id_div_terr_pk;


--
-- TOC entry 424 (class 1259 OID 66371)
-- Name: riipartizione_territoriale_to_rip_terr; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.riipartizione_territoriale_to_rip_terr (
    id_rel_rip_ter_pk integer NOT NULL,
    id_rip_prim integer NOT NULL,
    id_rip_second integer NOT NULL
);


ALTER TABLE public.riipartizione_territoriale_to_rip_terr OWNER TO postgres;

--
-- TOC entry 423 (class 1259 OID 66369)
-- Name: riipartizione_territoriale_to_rip_terr_id_rel_rip_ter_pk_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.riipartizione_territoriale_to_rip_terr_id_rel_rip_ter_pk_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.riipartizione_territoriale_to_rip_terr_id_rel_rip_ter_pk_seq OWNER TO postgres;

--
-- TOC entry 5062 (class 0 OID 0)
-- Dependencies: 423
-- Name: riipartizione_territoriale_to_rip_terr_id_rel_rip_ter_pk_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.riipartizione_territoriale_to_rip_terr_id_rel_rip_ter_pk_seq OWNED BY public.riipartizione_territoriale_to_rip_terr.id_rel_rip_ter_pk;

--
-- TOC entry 391 (class 1259 OID 33019)
-- Name: site_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.site_table (
    id_sito integer NOT NULL,
    sito text,
    nazione character varying(100),
    regione character varying(100),
    comune character varying(100),
    descrizione text,
    provincia character varying DEFAULT 'inserici un valore'::character varying,
    definizione_sito character varying DEFAULT 'inserici un valore'::character varying,
    find_check integer DEFAULT 0
);


ALTER TABLE public.site_table OWNER TO postgres;

--
-- TOC entry 392 (class 1259 OID 33028)
-- Name: site_table_id_sito_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.site_table_id_sito_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.site_table_id_sito_seq OWNER TO postgres;

--
-- TOC entry 5066 (class 0 OID 0)
-- Dependencies: 392
-- Name: site_table_id_sito_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.site_table_id_sito_seq OWNED BY public.site_table.id_sito;



--
-- TOC entry 401 (class 1259 OID 33076)
-- Name: struttura_table_id_struttura_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.struttura_table_id_struttura_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.struttura_table_id_struttura_seq OWNER TO postgres;

--
-- TOC entry 5073 (class 0 OID 0)
-- Dependencies: 401
-- Name: struttura_table_id_struttura_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.struttura_table_id_struttura_seq OWNED BY public.struttura_table.id_struttura;

--
-- TOC entry 406 (class 1259 OID 33096)
-- Name: tomba_table_id_tomba_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tomba_table_id_tomba_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tomba_table_id_tomba_seq OWNER TO postgres;

--
-- TOC entry 5077 (class 0 OID 0)
-- Dependencies: 406
-- Name: tomba_table_id_tomba_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tomba_table_id_tomba_seq OWNED BY public.tomba_table.id_tomba;


--
-- TOC entry 411 (class 1259 OID 33117)
-- Name: us_table_id_us_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.us_table_id_us_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.us_table_id_us_seq OWNER TO postgres;

--
-- TOC entry 5079 (class 0 OID 0)
-- Dependencies: 411
-- Name: us_table_id_us_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.us_table_id_us_seq OWNED BY public.us_table.id_us;


--
-- TOC entry 412 (class 1259 OID 33119)
-- Name: us_table_toimp; Type: TABLE; Schema: public; Owner: postgres
--
--------------------------------------------------------------------------------------
CREATE SEQUENCE public.pyarchinit_reperti_gid_seq
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;
ALTER TABLE public.pyarchinit_reperti_gid_seq OWNER TO postgres;

--ALTER SEQUENCE public.pyarchinit_reperti_gid_seq OWNED BY public.pyarchinit_reperti_gid_seq.id_rep;

---------------------------------------------------------------

CREATE TABLE public.pyarchinit_reperti
(
    gid integer NOT NULL ,
    the_geom geometry(Point,-1),
    id_rep integer,
    siti character varying(255),
    link character varying(255)
);

ALTER TABLE public.pyarchinit_reperti
    OWNER to postgres;

-- Index: sidx_pyarchinit_reperti_the_geom

-- DROP INDEX public.sidx_pyarchinit_reperti_the_geom;
CREATE TABLE public.us_table_toimp (
    id_us integer NOT NULL,
    sito text,
    area character varying(20),
    us integer,
    d_stratigrafica character varying(255),
    d_interpretativa character varying(255),
    descrizione text,
    interpretazione text,
    periodo_iniziale character varying(4),
    fase_iniziale character varying(4),
    periodo_finale character varying(4),
    fase_finale character varying(4),
    scavato character varying(100),
    attivita character varying(4),
    anno_scavo character varying(4),
    metodo_di_scavo character varying(20),
    inclusi text,
    campioni text,
    rapporti text,
    data_schedatura character varying(20),
    schedatore character varying(25),
    formazione character varying(20),
    stato_di_conservazione character varying(20),
    colore character varying(20),
    consistenza character varying(20),
    struttura character varying(30),
    cont_per character varying,
    order_layer integer,
    documentazione text
);


ALTER TABLE public.us_table_toimp OWNER TO postgres;

--
-- TOC entry 413 (class 1259 OID 33125)
-- Name: us_table_toimp_id_us_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.us_table_toimp_id_us_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.us_table_toimp_id_us_seq OWNER TO postgres;

--
-- TOC entry 5080 (class 0 OID 0)
-- Dependencies: 413
-- Name: us_table_toimp_id_us_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.us_table_toimp_id_us_seq OWNED BY public.us_table_toimp.id_us;


--
-- TOC entry 414 (class 1259 OID 33127)
-- Name: ut_table; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ut_table (
    id_ut integer NOT NULL,
    progetto character varying(100),
    nr_ut integer,
    ut_letterale character varying(100),
    def_ut character varying(100),
    descrizione_ut text,
    interpretazione_ut character varying(100),
    nazione character varying(100),
    regione character varying(100),
    provincia character varying(100),
    comune character varying(100),
    frazione character varying(100),
    localita character varying(100),
    indirizzo character varying(100),
    nr_civico character varying(100),
    carta_topo_igm character varying(100),
    carta_ctr character varying(100),
    coord_geografiche character varying(100),
    coord_piane character varying(100),
    quota real,
    andamento_terreno_pendenza character varying(100),
    utilizzo_suolo_vegetazione character varying(100),
    descrizione_empirica_suolo text,
    descrizione_luogo text,
    metodo_rilievo_e_ricognizione character varying(100),
    geometria character varying(100),
    bibliografia text,
    data character varying(100),
    ora_meteo character varying(100),
    responsabile character varying(100),
    dimensioni_ut character varying(100),
    rep_per_mq character varying(100),
    rep_datanti character varying(100),
    "periodo_I" character varying(100),
    "datazione_I" character varying(100),
    "interpretazione_I" character varying(100),
    "periodo_II" character varying(100),
    "datazione_II" character varying(100),
    "interpretazione_II" character varying(100),
    documentazione text,
    enti_tutela_vincoli character varying(100),
    indagini_preliminari character varying(100)
);


ALTER TABLE public.ut_table OWNER TO postgres;

--
-- TOC entry 415 (class 1259 OID 33133)
-- Name: ut_table_id_ut_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ut_table_id_ut_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ut_table_id_ut_seq OWNER TO postgres;


CREATE TABLE pyarchinit_documentazione
(
  gid integer NOT NULL,
  the_geom geometry(LineString,-1),
  id_doc integer,
  sito character varying(200),
  nome_doc character varying(200),
  tipo_doc character varying(200),
  path_qgis_pj character varying(500)
  
);


ALTER TABLE pyarchinit_documentazione
  OWNER TO postgres;

-- Index: sidx_pyarchinit_documentazione_geom

-- DROP INDEX sidx_pyarchinit_documentazione_geom;
CREATE SEQUENCE public.pyarchinit_documentazione_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;






--
-- TOC entry 5081 (class 0 OID 0)
-- Dependencies: 415
-- Name: ut_table_id_ut_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ut_table_id_ut_seq OWNED BY public.ut_table.id_ut;


--
-- TOC entry 4410 (class 2604 OID 33136)
-- Name: archeozoology_table id_archzoo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.archeozoology_table ALTER COLUMN id_archzoo SET DEFAULT nextval('public.archeozoology_table_id_archzoo_seq'::regclass);

--
-- TOC entry 4411 (class 2604 OID 33137)
-- Name: campioni_table id_campione; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.campioni_table ALTER COLUMN id_campione SET DEFAULT nextval('public.campioni_table_id_campione_seq'::regclass);

--
-- TOC entry 4449 (class 2604 OID 33151)
-- Name: deteta_table id_det_eta; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deteta_table ALTER COLUMN id_det_eta SET DEFAULT nextval('public.deteta_table_id_det_eta_seq'::regclass);


--
-- TOC entry 4450 (class 2604 OID 33152)
-- Name: detsesso_table id_det_sesso; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detsesso_table ALTER COLUMN id_det_sesso SET DEFAULT nextval('public.detsesso_table_id_det_sesso_seq'::regclass);

--
-- TOC entry 4452 (class 2604 OID 33154)
-- Name: documentazione_table id_documentazione; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documentazione_table ALTER COLUMN id_documentazione SET DEFAULT nextval('public.documentazione_table_id_documentazione_seq'::regclass);


--
-- TOC entry 4458 (class 2604 OID 33157)
-- Name: individui_table id_scheda_ind; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.individui_table ALTER COLUMN id_scheda_ind SET DEFAULT nextval('public.individui_table_id_scheda_ind_seq'::regclass);



--
-- TOC entry 4467 (class 2604 OID 33158)
-- Name: inventario_materiali_table id_invmat; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventario_materiali_table ALTER COLUMN id_invmat SET DEFAULT nextval('public.inventario_materiali_table_id_invmat_seq'::regclass);


--
-- TOC entry 4468 (class 2604 OID 33159)
-- Name: inventario_materiali_table_toimp id_invmat; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventario_materiali_table_toimp ALTER COLUMN id_invmat SET DEFAULT nextval('public.inventario_materiali_table_toimp_id_invmat_seq'::regclass);



--
-- TOC entry 4472 (class 2604 OID 33162)
-- Name: media_table id_media; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.media_table ALTER COLUMN id_media SET DEFAULT nextval('public.media_table_id_media_seq'::regclass);


--
-- TOC entry 4473 (class 2604 OID 33163)
-- Name: media_thumb_table id_media_thumb; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.media_thumb_table ALTER COLUMN id_media_thumb SET DEFAULT nextval('public.media_thumb_table_id_media_thumb_seq'::regclass);


--
-- TOC entry 4474 (class 2604 OID 33164)
-- Name: media_to_entity_table id_mediaToEntity; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.media_to_entity_table ALTER COLUMN "id_mediaToEntity" SET DEFAULT nextval('public."media_to_entity_table_id_mediaToEntity_seq"'::regclass);


--
-- TOC entry 4475 (class 2604 OID 33165)
-- Name: media_to_us_table id_mediaToUs; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.media_to_us_table ALTER COLUMN "id_mediaToUs" SET DEFAULT nextval('public."media_to_us_table_id_mediaToUs_seq"'::regclass);


--
-- TOC entry 4476 (class 2604 OID 33166)
-- Name: pdf_administrator_table id_pdf_administrator; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pdf_administrator_table ALTER COLUMN id_pdf_administrator SET DEFAULT nextval('public.pdf_administrator_table_id_pdf_administrator_seq'::regclass);


--
-- TOC entry 4477 (class 2604 OID 33167)
-- Name: periodizzazione_table id_perfas; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.periodizzazione_table ALTER COLUMN id_perfas SET DEFAULT nextval('public.periodizzazione_table_id_perfas_seq'::regclass);



--
-- TOC entry 4480 (class 2604 OID 33169)
-- Name: pyarchinit_individui gid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_individui ALTER COLUMN gid SET DEFAULT nextval('public.pyarchinit_individui_gid_seq'::regclass);


--
-- TOC entry 4543 (class 2604 OID 33170)
-- Name: pyarchinit_ripartizioni_temporali id_periodo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_ripartizioni_temporali ALTER COLUMN id_periodo SET DEFAULT nextval('public.pyarchinit_ripartizioni_temporali_id_periodo_seq'::regclass);


--
-- TOC entry 4544 (class 2604 OID 33171)
-- Name: pyarchinit_rou_thesaurus ID_rou; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_rou_thesaurus ALTER COLUMN "ID_rou" SET DEFAULT nextval('public."pyarchinit_rou_thesaurus_ID_rou_seq"'::regclass);


--
-- TOC entry 4551 (class 2604 OID 33172)
-- Name: pyarchinit_tafonomia gid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_tafonomia ALTER COLUMN gid SET DEFAULT nextval('public.pyarchinit_tafonomia_gid_seq'::regclass);


--
-- TOC entry 4554 (class 2604 OID 33173)
-- Name: pyarchinit_thesaurus_sigle id_thesaurus_sigle; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_thesaurus_sigle ALTER COLUMN id_thesaurus_sigle SET DEFAULT nextval('public.pyarchinit_thesaurus_sigle_id_thesaurus_sigle_seq'::regclass);


--
-- TOC entry 4556 (class 2604 OID 33174)
-- Name: pyarchinit_us_negative_doc id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_us_negative_doc ALTER COLUMN gid SET DEFAULT nextval('public.pyarchinit_us_negative_doc_gid_seq'::regclass);

--
-- TOC entry 4556 (class 2604 OID 33174)
-- Name: pyarchinit_us_negative_doc id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_documentazione ALTER COLUMN gid SET DEFAULT nextval('public.pyarchinit_documentazione_gid_seq'::regclass);

--
-- TOC entry 4488 (class 2604 OID 33175)
-- Name: pyuscarlinee gid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyuscarlinee ALTER COLUMN gid SET DEFAULT nextval('public.pyuscarlinee_gid_seq'::regclass);


--
-- TOC entry 4592 (class 2604 OID 41276)
-- Name: relashionship_check_table id_rel_check; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.relashionship_check_table ALTER COLUMN id_rel_check SET DEFAULT nextval('public.relashionship_check_table_id_rel_check_seq'::regclass);


--
-- TOC entry 4594 (class 2604 OID 66362)
-- Name: riipartizione_territoriale id_div_terr_pk; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.riipartizione_territoriale ALTER COLUMN id_div_terr_pk SET DEFAULT nextval('public.riipartizione_territoriale_id_div_terr_pk_seq'::regclass);


--
-- TOC entry 4595 (class 2604 OID 66374)
-- Name: riipartizione_territoriale_to_rip_terr id_rel_rip_ter_pk; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.riipartizione_territoriale_to_rip_terr ALTER COLUMN id_rel_rip_ter_pk SET DEFAULT nextval('public.riipartizione_territoriale_to_rip_terr_id_rel_rip_ter_pk_seq'::regclass);

--
-- TOC entry 4595 (class 2604 OID 66374)
-- Name: riipartizione_territoriale_to_rip_terr id_rel_rip_ter_pk; Type: DEFAULT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.pyarchinit_reperti ALTER COLUMN gid SET DEFAULT nextval('public.pyarchinit_reperti_gid_seq'::regclass);

--
-- TOC entry 4570 (class 2604 OID 33176)
-- Name: site_table id_sito; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.site_table ALTER COLUMN id_sito SET DEFAULT nextval('public.site_table_id_sito_seq'::regclass);

--
-- TOC entry 4584 (class 2604 OID 33180)
-- Name: struttura_table id_struttura; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.struttura_table ALTER COLUMN id_struttura SET DEFAULT nextval('public.struttura_table_id_struttura_seq'::regclass);

--
-- TOC entry 4553 (class 2604 OID 33183)
-- Name: tomba_table id_tomba; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tomba_table ALTER COLUMN id_tomba SET DEFAULT nextval('public.tomba_table_id_tomba_seq'::regclass);



--
-- TOC entry 4494 (class 2604 OID 33185)
-- Name: us_table id_us; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.us_table ALTER COLUMN id_us SET DEFAULT nextval('public.us_table_id_us_seq'::regclass);


--
-- TOC entry 4590 (class 2604 OID 33186)
-- Name: us_table_toimp id_us; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.us_table_toimp ALTER COLUMN id_us SET DEFAULT nextval('public.us_table_toimp_id_us_seq'::regclass);


--
-- TOC entry 4591 (class 2604 OID 33187)
-- Name: ut_table id_ut; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ut_table ALTER COLUMN id_ut SET DEFAULT nextval('public.ut_table_id_ut_seq'::regclass);


--
-- TOC entry 4614 (class 2606 OID 41014)
-- Name: archeozoology_table ID_archzoo_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.archeozoology_table
    ADD CONSTRAINT "ID_archzoo_unico" UNIQUE (sito, quadrato);


--
-- TOC entry 4651 (class 2606 OID 41016)
-- Name: deteta_table ID_det_eta_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deteta_table
    ADD CONSTRAINT "ID_det_eta_unico" UNIQUE (sito, nr_individuo);


--
-- TOC entry 4655 (class 2606 OID 41018)
-- Name: detsesso_table ID_det_sesso_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detsesso_table
    ADD CONSTRAINT "ID_det_sesso_unico" UNIQUE (sito, num_individuo);


--
-- TOC entry 4673 (class 2606 OID 41020)
-- Name: individui_table ID_individuo_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.individui_table
    ADD CONSTRAINT "ID_individuo_unico" UNIQUE (sito, nr_individuo);


--
-- TOC entry 4618 (class 2606 OID 41022)
-- Name: campioni_table ID_invcamp_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.campioni_table
    ADD CONSTRAINT "ID_invcamp_unico" UNIQUE (sito, nr_campione);


--
-- TOC entry 4661 (class 2606 OID 41024)
-- Name: documentazione_table ID_invdoc_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documentazione_table
    ADD CONSTRAINT "ID_invdoc_unico" UNIQUE (sito, tipo_documentazione, nome_doc);


--
-- TOC entry 4677 (class 2606 OID 41026)
-- Name: inventario_materiali_table ID_invmat_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventario_materiali_table
    ADD CONSTRAINT "ID_invmat_unico" UNIQUE (sito, numero_inventario);
	

--
-- TOC entry 4681 (class 2606 OID 41028)
-- Name: inventario_materiali_table_toimp ID_invmat_unico_toimp; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventario_materiali_table_toimp
    ADD CONSTRAINT "ID_invmat_unico_toimp" UNIQUE (sito, numero_inventario);

--
-- TOC entry 4699 (class 2606 OID 41032)
-- Name: media_to_entity_table ID_mediaToEntity_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.media_to_entity_table
    ADD CONSTRAINT "ID_mediaToEntity_unico" UNIQUE (id_entity, entity_type, id_media);


--
-- TOC entry 4703 (class 2606 OID 41034)
-- Name: media_to_us_table ID_mediaToUs_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.media_to_us_table
    ADD CONSTRAINT "ID_mediaToUs_unico" UNIQUE (id_media, id_us);


--
-- TOC entry 4695 (class 2606 OID 41036)
-- Name: media_thumb_table ID_media_thumb_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.media_thumb_table
    ADD CONSTRAINT "ID_media_thumb_unico" UNIQUE (media_thumb_filename);


--
-- TOC entry 4691 (class 2606 OID 41038)
-- Name: media_table ID_media_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.media_table
    ADD CONSTRAINT "ID_media_unico" UNIQUE (filepath);


--
-- TOC entry 4707 (class 2606 OID 41040)
-- Name: pdf_administrator_table ID_pdf_administrator_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pdf_administrator_table
    ADD CONSTRAINT "ID_pdf_administrator_unico" UNIQUE (table_name, modello);


--
-- TOC entry 4711 (class 2606 OID 41042)
-- Name: periodizzazione_table ID_perfas_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.periodizzazione_table
    ADD CONSTRAINT "ID_perfas_unico" UNIQUE (sito, periodo, fase);


--
-- TOC entry 4749 (class 2606 OID 41044)
-- Name: pyarchinit_rou_thesaurus ID_rou_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_rou_thesaurus
    ADD CONSTRAINT "ID_rou_pk" PRIMARY KEY ("ID_rou");


--
-- TOC entry 4784 (class 2606 OID 41046)
-- Name: site_table ID_sito_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.site_table
    ADD CONSTRAINT "ID_sito_unico" UNIQUE (sito);


--
-- TOC entry 4797 (class 2606 OID 41048)
-- Name: struttura_table ID_struttura_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.struttura_table
    ADD CONSTRAINT "ID_struttura_unico" UNIQUE (sito, sigla_struttura, numero_struttura);


--
-- TOC entry 4763 (class 2606 OID 41050)
-- Name: tomba_table ID_tomba_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tomba_table
    ADD CONSTRAINT "ID_tomba_unico" UNIQUE (sito, nr_scheda_taf);


--
-- TOC entry 4718 (class 2606 OID 41052)
-- Name: pyarchinit_codici_tipologia ID_tipologia_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_codici_tipologia
    ADD CONSTRAINT "ID_tipologia_unico" UNIQUE (tipologia_progetto, tipologia_gruppo, tipologia_codice, tipologia_sottocodice);

--
-- TOC entry 4718 (class 2606 OID 41052)
-- Name: pyarchinit_documentazione ID_documentazione_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_documentazione
    ADD CONSTRAINT "ID_documentazione_unico" UNIQUE (gid, sito);
--
-- TOC entry 4735 (class 2606 OID 41054)
-- Name: us_table ID_us_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.us_table
    ADD CONSTRAINT "ID_us_unico" UNIQUE (sito, area, us, unita_tipo);


--
-- TOC entry 4810 (class 2606 OID 41056)
-- Name: us_table_toimp ID_us_unico_toimp; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.us_table_toimp
    ADD CONSTRAINT "ID_us_unico_toimp" UNIQUE (sito, area, us);


--
-- TOC entry 4814 (class 2606 OID 41058)
-- Name: ut_table ID_ut_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ut_table
    ADD CONSTRAINT "ID_ut_unico" UNIQUE (progetto, nr_ut, ut_letterale);


--
-- TOC entry 4616 (class 2606 OID 41060)
-- Name: archeozoology_table archeozoology_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.archeozoology_table
    ADD CONSTRAINT archeozoology_table_pkey PRIMARY KEY (id_archzoo);


--
-- TOC entry 4620 (class 2606 OID 41062)
-- Name: campioni_table campioni_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.campioni_table
    ADD CONSTRAINT campioni_table_pkey PRIMARY KEY (id_campione);


--
-- TOC entry 4653 (class 2606 OID 41088)
-- Name: deteta_table deteta_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deteta_table
    ADD CONSTRAINT deteta_table_pkey PRIMARY KEY (id_det_eta);


--
-- TOC entry 4657 (class 2606 OID 41090)
-- Name: detsesso_table detsesso_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detsesso_table
    ADD CONSTRAINT detsesso_table_pkey PRIMARY KEY (id_det_sesso);


--
-- TOC entry 4663 (class 2606 OID 41092)
-- Name: documentazione_table documentazione_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documentazione_table
    ADD CONSTRAINT documentazione_table_pkey PRIMARY KEY (id_documentazione);



--
-- TOC entry 4724 (class 2606 OID 41106)
-- Name: pyarchinit_inventario_materiali id_im_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_inventario_materiali
    ADD CONSTRAINT id_im_pk PRIMARY KEY (idim_pk);


--
-- TOC entry 4745 (class 2606 OID 41108)
-- Name: pyarchinit_ripartizioni_temporali id_periodo_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_ripartizioni_temporali
    ADD CONSTRAINT id_periodo_pk PRIMARY KEY (id_periodo);


--
-- TOC entry 4767 (class 2606 OID 41110)
-- Name: pyarchinit_thesaurus_sigle id_thesaurus_sigle_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_thesaurus_sigle
    ADD CONSTRAINT id_thesaurus_sigle_pk PRIMARY KEY (id_thesaurus_sigle);


--
-- TOC entry 4720 (class 2606 OID 41112)
-- Name: pyarchinit_codici_tipologia id_tip_tombe_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_codici_tipologia
    ADD CONSTRAINT id_tip_tombe_pk PRIMARY KEY (id);


--
-- TOC entry 4675 (class 2606 OID 41114)
-- Name: individui_table individui_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.individui_table
    ADD CONSTRAINT individui_table_pkey PRIMARY KEY (id_scheda_ind);


--
-- TOC entry 4679 (class 2606 OID 41116)
-- Name: inventario_materiali_table inventario_materiali_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventario_materiali_table
    ADD CONSTRAINT inventario_materiali_table_pkey PRIMARY KEY (id_invmat);


--
-- TOC entry 4683 (class 2606 OID 41118)
-- Name: inventario_materiali_table_toimp inventario_materiali_table_toimp_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventario_materiali_table_toimp
    ADD CONSTRAINT inventario_materiali_table_toimp_pkey PRIMARY KEY (id_invmat);



--
-- TOC entry 4728 (class 2606 OID 41124)
-- Name: pyarchinit_linee_rif linee_riferimento_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_linee_rif
    ADD CONSTRAINT linee_riferimento_pkey PRIMARY KEY (gid);


--
-- TOC entry 4693 (class 2606 OID 41126)
-- Name: media_table media_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.media_table
    ADD CONSTRAINT media_table_pkey PRIMARY KEY (id_media);


--
-- TOC entry 4697 (class 2606 OID 41128)
-- Name: media_thumb_table media_thumb_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.media_thumb_table
    ADD CONSTRAINT media_thumb_table_pkey PRIMARY KEY (id_media_thumb);


--
-- TOC entry 4701 (class 2606 OID 41130)
-- Name: media_to_entity_table media_to_entity_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.media_to_entity_table
    ADD CONSTRAINT media_to_entity_table_pkey PRIMARY KEY ("id_mediaToEntity");


--
-- TOC entry 4705 (class 2606 OID 41132)
-- Name: media_to_us_table media_to_us_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.media_to_us_table
    ADD CONSTRAINT media_to_us_table_pkey PRIMARY KEY ("id_mediaToUs");


--
-- TOC entry 4709 (class 2606 OID 41134)
-- Name: pdf_administrator_table pdf_administrator_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pdf_administrator_table
    ADD CONSTRAINT pdf_administrator_table_pkey PRIMARY KEY (id_pdf_administrator);


--
-- TOC entry 4713 (class 2606 OID 41136)
-- Name: periodizzazione_table periodizzazione_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.periodizzazione_table
    ADD CONSTRAINT periodizzazione_table_pkey PRIMARY KEY (id_perfas);


--
-- TOC entry 4747 (class 2606 OID 41138)
-- Name: pyarchinit_ripartizioni_temporali periodo_fase_unico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_ripartizioni_temporali
    ADD CONSTRAINT periodo_fase_unico UNIQUE (sito, sigla_periodo, sigla_fase);


--
-- TOC entry 4722 (class 2606 OID 41142)
-- Name: pyarchinit_individui pyarchinit_individui_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_individui
    ADD CONSTRAINT pyarchinit_individui_pkey PRIMARY KEY (gid);


--
-- TOC entry 4740 (class 2606 OID 41144)
-- Name: pyarchinit_quote pyarchinit_quote_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_quote
    ADD CONSTRAINT pyarchinit_quote_pkey PRIMARY KEY (gid);

--
-- TOC entry 4740 (class 2606 OID 41144)
-- Name: pyarchinit_quote pyarchinit_quote_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_quote_usm
    ADD CONSTRAINT pyarchinit_quote_usm_pkey PRIMARY KEY (gid);

--
-- TOC entry 4742 (class 2606 OID 41146)
-- Name: pyarchinit_ripartizioni_spaziali pyarchinit_ripartizioni_spaziali_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_ripartizioni_spaziali
    ADD CONSTRAINT pyarchinit_ripartizioni_spaziali_pkey PRIMARY KEY (gid);


--
-- TOC entry 4751 (class 2606 OID 41148)
-- Name: pyarchinit_sezioni pyarchinit_sezioni_29092009_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_sezioni
    ADD CONSTRAINT pyarchinit_sezioni_29092009_pkey PRIMARY KEY (gid);


--
-- TOC entry 4753 (class 2606 OID 41150)
-- Name: pyarchinit_siti pyarchinit_siti_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_siti
    ADD CONSTRAINT pyarchinit_siti_pkey PRIMARY KEY (gid);

--
-- TOC entry 4753 (class 2606 OID 41150)
-- Name: pyarchinit_siti pyarchinit_siti__polygon_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_siti_polygonal
    ADD CONSTRAINT pyarchinit_siti_polygonal_pkey PRIMARY KEY (gid);	

--
-- TOC entry 4756 (class 2606 OID 41152)
-- Name: pyarchinit_sondaggi pyarchinit_sondaggi_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_sondaggi
    ADD CONSTRAINT pyarchinit_sondaggi_pkey PRIMARY KEY (gid);


--
-- TOC entry 4758 (class 2606 OID 41154)
-- Name: pyarchinit_strutture_ipotesi pyarchinit_strutture_ipotesi_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_strutture_ipotesi
    ADD CONSTRAINT pyarchinit_strutture_ipotesi_pkey PRIMARY KEY (gid);


--
-- TOC entry 4760 (class 2606 OID 41156)
-- Name: pyarchinit_tafonomia pyarchinit_tafonomia_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_tafonomia
    ADD CONSTRAINT pyarchinit_tafonomia_pkey PRIMARY KEY (gid);


--
-- TOC entry 4769 (class 2606 OID 41158)
-- Name: pyarchinit_tipologia_sepolture pyarchinit_tipologia_sepolture_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_tipologia_sepolture
    ADD CONSTRAINT pyarchinit_tipologia_sepolture_pkey PRIMARY KEY (gid);


--
-- TOC entry 4771 (class 2606 OID 41160)
-- Name: pyarchinit_us_negative_doc pyarchinit_us_negative_doc_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_us_negative_doc
    ADD CONSTRAINT pyarchinit_us_negative_doc_pkey PRIMARY KEY (gid);


--
-- TOC entry 4731 (class 2606 OID 41162)
-- Name: pyarchinit_punti_rif pyarchnit_punti_riferimento_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyarchinit_punti_rif
    ADD CONSTRAINT pyarchnit_punti_riferimento_pkey PRIMARY KEY (gid);


--
-- TOC entry 4774 (class 2606 OID 41164)
-- Name: pyunitastratigrafiche pyunitastratigrafiche_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyunitastratigrafiche
    ADD CONSTRAINT pyunitastratigrafiche_pkey PRIMARY KEY (gid);

--
-- TOC entry 4774 (class 2606 OID 41164)
-- Name: pyunitastratigrafiche pyunitastratigrafiche_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyunitastratigrafiche_usm
    ADD CONSTRAINT pyunitastratigrafiche_usm_pkey PRIMARY KEY (gid);


--
-- TOC entry 4777 (class 2606 OID 41166)
-- Name: pyuscaratterizzazioni pyuscaratterizzazioni_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyuscaratterizzazioni
    ADD CONSTRAINT pyuscaratterizzazioni_pkey PRIMARY KEY (gid);

ALTER TABLE public.pyuscaratterizzazioni CLUSTER ON pyuscaratterizzazioni_pkey;


--
-- TOC entry 4733 (class 2606 OID 41168)
-- Name: pyuscarlinee pyuscarlinee_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pyuscarlinee
    ADD CONSTRAINT pyuscarlinee_pkey PRIMARY KEY (gid);


--
-- TOC entry 4818 (class 2606 OID 41281)
-- Name: relashionship_check_table relashionship_check_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.relashionship_check_table
    ADD CONSTRAINT relashionship_check_table_pkey PRIMARY KEY (id_rel_check);


--
-- TOC entry 4824 (class 2606 OID 66367)
-- Name: riipartizione_territoriale riipartizione_territoriale_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.riipartizione_territoriale
    ADD CONSTRAINT riipartizione_territoriale_pkey PRIMARY KEY (id_div_terr_pk);


--
-- TOC entry 4827 (class 2606 OID 66376)
-- Name: riipartizione_territoriale_to_rip_terr riipartizione_territoriale_to_rip_terr_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.riipartizione_territoriale_to_rip_terr
    ADD CONSTRAINT riipartizione_territoriale_to_rip_terr_pkey PRIMARY KEY (id_rel_rip_ter_pk);

--
-- TOC entry 4786 (class 2606 OID 41174)
-- Name: site_table site_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.site_table
    ADD CONSTRAINT site_table_pkey PRIMARY KEY (id_sito);


--
-- TOC entry 4786 (class 2606 OID 41174)
-- Name: site_table site_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.pyarchinit_reperti
    ADD CONSTRAINT pyarchinit_reperti_pkey PRIMARY KEY (gid);
--
-- TOC entry 4799 (class 2606 OID 41184)
-- Name: struttura_table struttura_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.struttura_table
    ADD CONSTRAINT struttura_table_pkey PRIMARY KEY (id_struttura);


--
-- TOC entry 4765 (class 2606 OID 41190)
-- Name: tomba_table tomba_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tomba_table
    ADD CONSTRAINT tomba_table_pkey PRIMARY KEY (id_tomba);


--
-- TOC entry 4738 (class 2606 OID 41196)
-- Name: us_table us_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.us_table
    ADD CONSTRAINT us_table_pkey PRIMARY KEY (id_us);


--
-- TOC entry 4812 (class 2606 OID 41198)
-- Name: us_table_toimp us_table_toimp_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.us_table_toimp
    ADD CONSTRAINT us_table_toimp_pkey PRIMARY KEY (id_us);


--
-- TOC entry 4816 (class 2606 OID 41200)
-- Name: ut_table ut_table_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ut_table
    ADD CONSTRAINT ut_table_pkey PRIMARY KEY (id_ut);


--
-- TOC entry 4736 (class 1259 OID 41203)
-- Name: order_layer_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX order_layer_index ON public.us_table USING btree (order_layer DESC);

ALTER TABLE public.us_table CLUSTER ON order_layer_index;

--
-- TOC entry 4729 (class 1259 OID 41210)
-- Name: sidx_pyarchinit_linee_rif_geom; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sidx_pyarchinit_linee_rif_geom ON public.pyarchinit_linee_rif USING gist (the_geom);

CREATE INDEX sidx_pyarchinit_reperti_geom ON public.pyarchinit_reperti USING gist (the_geom);
--
-- TOC entry 4743 (class 1259 OID 41211)
-- Name: sidx_pyarchinit_ripartizioni_spaziali_geom; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sidx_pyarchinit_ripartizioni_spaziali_geom ON public.pyarchinit_ripartizioni_spaziali USING gist (the_geom);


--
-- TOC entry 4754 (class 1259 OID 41212)
-- Name: sidx_pyarchinit_siti_geom; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sidx_pyarchinit_siti_geom ON public.pyarchinit_siti USING gist (the_geom);


--
-- TOC entry 4754 (class 1259 OID 41212)
-- Name: sidx_pyarchinit_siti_polygon_geom; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sidx_pyarchinit_siti_polygonal_geom ON public.pyarchinit_siti_polygonal USING gist (the_geom);


--
-- TOC entry 4761 (class 1259 OID 41213)
-- Name: sidx_pyarchinit_tafonomia_geom; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sidx_pyarchinit_tafonomia_geom ON public.pyarchinit_tafonomia USING gist (the_geom);


--
-- TOC entry 4772 (class 1259 OID 41214)
-- Name: sidx_pyarchinit_us_negative_doc_geom; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sidx_pyarchinit_us_negative_doc_geom ON public.pyarchinit_us_negative_doc USING gist (the_geom);


--
-- TOC entry 4775 (class 1259 OID 41215)
-- Name: sidx_pyunitastratigrafiche_geom; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sidx_pyunitastratigrafiche_geom ON public.pyunitastratigrafiche USING gist (the_geom);

--
-- TOC entry 4775 (class 1259 OID 41215)
-- Name: sidx_pyunitastratigrafiche_geom; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sidx_pyunitastratigrafiche_usm_geom ON public.pyunitastratigrafiche_usm USING gist (the_geom);
--
-- TOC entry 4825 (class 1259 OID 66368)
-- Name: sidx_riipartizione_territoriale_geom; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sidx_riipartizione_territoriale_geom ON public.riipartizione_territoriale USING gist (the_geom);

CREATE UNIQUE INDEX IF NOT EXISTS idx_n_reperto ON inventario_materiali_table(sito, n_reperto);
--
-- TOC entry 5011 (class 0 OID 0)
-- Dependencies: 20
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--
CREATE OR REPLACE FUNCTION delete_media_table()
  RETURNS trigger AS
$BODY$

BEGIN
IF OLD.id_media!=OLD.id_media THEN
update media_table set id_media=OLD.id_media;

else 

DELETE from media_table 
where id_media = OLD.id_media ;
end if;
RETURN OLD;
END;


$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION delete_media_table()
  OWNER TO postgres; 

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'delete_media_table') THEN
        CREATE TRIGGER delete_media_table
		  AFTER UPDATE OR DELETE
		  ON media_thumb_table
		  FOR EACH ROW
		  EXECUTE PROCEDURE delete_media_table();

    END IF;
END
$$;  
  
 ---------------------------------------------------------------------------  
CREATE OR REPLACE FUNCTION delete_media_to_entity_table()
  RETURNS trigger AS
$BODY$






BEGIN
IF OLD.id_media!=OLD.id_media THEN
update media_to_entity_table set id_media=OLD.id_media;

else 

DELETE from media_to_entity_table 
where id_media = OLD.id_media ;
end if;
RETURN OLD;
END;


$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION delete_media_to_entity_table()
  OWNER TO postgres;

 
 
 
 DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'delete_media_to_entity_table') THEN
        CREATE TRIGGER delete_media_to_entity_table
  AFTER UPDATE OR DELETE
  ON media_thumb_table
  FOR EACH ROW
  EXECUTE PROCEDURE delete_media_to_entity_table();

    END IF;
END
$$;  

CREATE OR REPLACE FUNCTION public.create_geom()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
BEGIN
 if new.coord is null or new.coord!= old.coord then

  update pyunitastratigrafiche set coord = ST_AsText(ST_Centroid(the_geom)) where scavo_s=New.scavo_s and area_s=New.area_s and us_s=New.us_s ;
END IF;
RETURN NEW;
END;
$BODY$;

ALTER FUNCTION public.create_geom()
    OWNER TO postgres;

COMMENT ON FUNCTION public.create_geom()
    IS 'When a new record is added to write coordinates if coord is null in coord field';
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'create_geom') THEN
CREATE TRIGGER create_geom
    AFTER INSERT OR UPDATE 
    ON public.pyunitastratigrafiche
    FOR EACH ROW
    EXECUTE PROCEDURE public.create_geom();


END IF;
END
$$;  

CREATE OR REPLACE FUNCTION public.create_doc()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
BEGIN
 if new.d_interpretativa is null or new.d_interpretativa = '' or new.d_interpretativa!= old.d_interpretativa then

  update us_table set d_interpretativa = doc_usv where sito=New.sito and area=New.area and us=New.us and unita_tipo='DOC' ;
END IF;
RETURN NEW;
END;
$BODY$;

ALTER FUNCTION public.create_doc()
    OWNER TO postgres;

COMMENT ON FUNCTION public.create_doc()
    IS 'When a new record is added to write coordinates if coord is null in coord field';
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'create_doc') THEN
CREATE TRIGGER create_doc
    AFTER INSERT OR UPDATE 
    ON public.us_table
    FOR EACH ROW
    EXECUTE PROCEDURE public.create_doc();


END IF;
END
$$;  

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2018-10-02 21:35:07

--
-- PostgreSQL database dump complete
--

