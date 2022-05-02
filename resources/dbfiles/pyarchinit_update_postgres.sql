drop view if exists mediaentity_view;
DROP TABLE IF EXISTS mediaentity_view;
DROP VIEW IF EXISTS pyarchinit_us_view;
DROP VIEW IF EXISTS pyarchinit_tafonomia_view;
CREATE UNIQUE INDEX IF NOT EXISTS idx_n_reperto ON inventario_materiali_table(sito, n_reperto);

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


-------------------------------------------------------------------------------------

Alter TABLE media_thumb_table ADD COLUMN if not exists path_resize text;
        
-------------------------------------------------------------------------------------


-------------------------------------------------------------------------------------
CREATE SEQUENCE IF NOT EXISTS mediaentity_view_id_media_thumb_seq
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE mediaentity_view_id_media_thumb_seq
  OWNER TO postgres;


--------------------------------------------------------------------------------------
--drop view if exists mediaentity_view;

CREATE OR REPLACE VIEW mediaentity_view AS 
 SELECT media_thumb_table.id_media_thumb,
    media_thumb_table.id_media,
    media_thumb_table.filepath,
	media_thumb_table.path_resize,
	media_to_entity_table.entity_type,
	media_to_entity_table.id_media AS id_media_m,
    media_to_entity_table.id_entity
	
   FROM media_thumb_table
     JOIN media_to_entity_table ON media_thumb_table.id_media = media_to_entity_table.id_media
  ORDER BY media_to_entity_table.id_entity;

ALTER TABLE mediaentity_view
  OWNER TO postgres;
/* ALTER TABLE IF EXISTS mediaentity_view ALTER COLUMN id_media_thumb SET DEFAULT nextval('mediaentity_view_id_media_thumb_seq'::regclass); */

--------------------------------------------------------------------------------------
CREATE SEQUENCE IF NOT EXISTS pyarchinit_documentazione_gid_seq
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE pyarchinit_documentazione_gid_seq
  OWNER TO postgres;

--------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS pyarchinit_documentazione
(
  gid integer NOT NULL DEFAULT nextval('pyarchinit_documentazione_gid_seq'::regclass),
  the_geom geometry(LineString,-1),
  id_doc integer,
  sito character varying(200),
  nome_doc character varying(200),
  tipo_doc character varying(200),
  path_qgis_pj character varying(500),
  CONSTRAINT "ID_documentazione_unico" UNIQUE (gid, sito)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE pyarchinit_documentazione
  OWNER TO postgres;
--------------------------------------------------------------------------------------
CREATE SEQUENCE IF NOT EXISTS pyarchinit_us_negative_doc_gid_seq
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE pyarchinit_us_negative_doc_gid_seq
  OWNER TO postgres;

-------------------------------------------------------------------------------------- 
CREATE TABLE IF NOT EXISTS pyarchinit_us_negative_doc
(
  gid serial NOT NULL,
  the_geom geometry(LineString,-1),
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
  "LblRot" numeric(20,5),
  CONSTRAINT pyarchinit_us_negative_doc_pkey PRIMARY KEY (gid)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE pyarchinit_us_negative_doc
  OWNER TO postgres;

-- Index: sidx_pyarchinit_us_negative_doc_geom

-- DROP INDEX sidx_pyarchinit_us_negative_doc_geom;

CREATE INDEX IF NOT EXISTS sidx_pyarchinit_us_negative_doc_geom
  ON pyarchinit_us_negative_doc
  USING gist
  (the_geom);


--------------------------------------------------------------------------------------
CREATE OR REPLACE VIEW pyarchinit_doc_view AS 
 SELECT a.id_documentazione,
    a.sito,
    a.nome_doc,
    a.data,
    a.tipo_documentazione,
    a.sorgente,
    a.scala,
    a.disegnatore,
    a.note,
    b.gid,
    b.sito AS sito_1,
    b.nome_doc AS nome_doc_1,
    b.tipo_doc,
    b.path_qgis_pj,
    b.the_geom
   FROM documentazione_table a
     JOIN pyarchinit_documentazione b ON a.sito ::text = b.sito AND a.nome_doc ::text = b.nome_doc AND a.tipo_documentazione ::text = b.tipo_doc;
    
ALTER TABLE pyarchinit_doc_view
  OWNER TO postgres;
 SELECT a.id_documentazione,
    a.sito,
    a.nome_doc,
    a.data,
    a.tipo_documentazione,
    a.sorgente,
    a.scala,
    a.disegnatore,
    a.note,
    b.gid,
    b.sito AS sito_1,
    b.nome_doc AS nome_doc_1,
    b.tipo_doc,
    b.path_qgis_pj,
    b.the_geom
   FROM documentazione_table a
     JOIN pyarchinit_documentazione b ON a.sito = b.sito::text AND a.nome_doc = b.nome_doc::text AND a.tipo_documentazione = b.tipo_doc::text;

ALTER TABLE pyarchinit_doc_view
  OWNER TO postgres;
  
--------------------------------------------------------------------------------------  
  
	CREATE OR REPLACE VIEW pyarchinit_us_negative_doc_view AS SELECT 
	gid,
	sito_n ,
	area_n ,
	us_n , 
	tipo_doc_n ,
	nome_doc_n ,
	the_geom,
	id_us ,
	sito ,
	us ,
	d_stratigrafica ,
	d_interpretativa ,
	descrizione ,
	interpretazione ,
	periodo_iniziale ,
	fase_iniziale ,
	periodo_finale , 
	fase_finale ,
	scavato ,
	attivita,
	anno_scavo ,
	metodo_di_scavo ,
	inclusi ,
	campioni ,
	rapporti ,
	data_schedatura ,
	schedatore ,
	formazione ,
	stato_di_conservazione ,
	colore ,
	consistenza,
	struttura,
	cont_per ,
	order_layer ,
	documentazione 
	FROM pyarchinit_us_negative_doc 
	JOIN us_table ON  sito_n ::text = sito AND area_n ::text = area AND us_n = us;


ALTER TABLE pyarchinit_us_negative_doc_view
    OWNER TO postgres;
	




CREATE OR REPLACE VIEW pyarchinit_us_view AS
 SELECT pyunitastratigrafiche.gid,
    pyunitastratigrafiche.the_geom,
    pyunitastratigrafiche.scavo_s,
    pyunitastratigrafiche.area_s,
    pyunitastratigrafiche.us_s,
    pyunitastratigrafiche.stratigraph_index_us,
    pyunitastratigrafiche.tipo_us_s,
	pyunitastratigrafiche.rilievo_originale,
    pyunitastratigrafiche.disegnatore,
    pyunitastratigrafiche.data,
    pyunitastratigrafiche.tipo_doc,
    pyunitastratigrafiche.nome_doc,
	pyunitastratigrafiche.unita_tipo_s,
    us_table.id_us,
    us_table.sito,
	us_table.area,
	us_table.us,
	us_table.d_stratigrafica,
	us_table.d_interpretativa,
	us_table.descrizione,
	us_table.interpretazione,
	us_table.periodo_iniziale,
	us_table.fase_iniziale,
	us_table.periodo_finale,
	us_table.fase_finale,
	us_table.scavato,
	us_table.attivita,
	us_table.anno_scavo,
	us_table.metodo_di_scavo,
	us_table.inclusi,
	us_table.campioni,
	us_table.rapporti,
	us_table.data_schedatura,
	us_table.schedatore,
	us_table.formazione,
	us_table.stato_di_conservazione,
	us_table.colore,
	us_table.consistenza,
	us_table.struttura,
	us_table.cont_per,
	us_table.order_layer,
	us_table.documentazione,
	us_table.unita_tipo,
	us_table.settore,
	us_table.quad_par,
	us_table.ambient,
	us_table.saggio,
	us_table.elem_datanti,
	us_table.funz_statica,
	us_table.lavorazione,
	us_table.spess_giunti,
	us_table.letti_posa,
	us_table.alt_mod,
	us_table.un_ed_riass,
	us_table.reimp,
	us_table.posa_opera,
	us_table.quota_min_usm,
	us_table.quota_max_usm,
	us_table.cons_legante,
	us_table.col_legante,
	us_table.aggreg_legante,
	us_table.con_text_mat,
	us_table.col_materiale,
	us_table.inclusi_materiali_usm,
	us_table.n_catalogo_generale,
	us_table.n_catalogo_interno,
	us_table.n_catalogo_internazionale,
	us_table.soprintendenza,
	us_table.quota_relativa,
	us_table.quota_abs,
	us_table.ref_tm,
	us_table.ref_ra,
	us_table.ref_n,
	us_table.posizione,
	us_table.criteri_distinzione,
	us_table.modo_formazione,
	us_table.componenti_organici,
	us_table.componenti_inorganici,
	us_table.lunghezza_max,
	us_table.altezza_max,
	us_table.altezza_min,
	us_table.profondita_max,
	us_table.profondita_min,
	us_table.larghezza_media,
	us_table.quota_max_abs,
	us_table.quota_max_rel,
	us_table.quota_min_abs,
	us_table.quota_min_rel,
	us_table.osservazioni,
	us_table.datazione,
	us_table.flottazione,
	us_table.setacciatura,
	us_table.affidabilita,
	us_table.direttore_us,
	us_table.responsabile_us,
	us_table.cod_ente_schedatore,
	us_table.data_rilevazione,
	us_table.data_rielaborazione,
	us_table.lunghezza_usm,
	us_table.altezza_usm,
	us_table.spessore_usm,
	us_table.tecnica_muraria_usm,
	us_table.modulo_usm,
	us_table.campioni_malta_usm,
	us_table.campioni_mattone_usm,
	us_table.campioni_pietra_usm,
	us_table.provenienza_materiali_usm,
	us_table.criteri_distinzione_usm,
	us_table.uso_primario_usm
   FROM pyunitastratigrafiche
     JOIN us_table ON pyunitastratigrafiche.scavo_s::text = us_table.sito AND pyunitastratigrafiche.area_s::text = us_table.area::text AND pyunitastratigrafiche.us_s = us_table.us AND pyunitastratigrafiche.unita_tipo_s = us_table.unita_tipo
  ORDER BY us_table.order_layer, pyunitastratigrafiche.stratigraph_index_us DESC, pyunitastratigrafiche.gid;

ALTER TABLE pyarchinit_us_view
    OWNER TO postgres;	

--------------------------------------------------------------------------------------
CREATE SEQUENCE IF NOT EXISTS pyarchinit_reperti_gid_seq
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE pyarchinit_reperti_gid_seq
  OWNER TO postgres;



---------------------------------------------------------------

CREATE TABLE if not exists pyarchinit_reperti
(
     gid integer NOT NULL DEFAULT nextval('pyarchinit_reperti_gid_seq'::regclass),
    the_geom geometry(Point,-1),
    id_rep integer,
    siti character varying(255) COLLATE pg_catalog."default",
    link character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT pyarchinit_reperti_pkey PRIMARY KEY (gid)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE pyarchinit_reperti
    OWNER to postgres;

-- Index: sidx_pyarchinit_reperti_the_geom

-- DROP INDEX public.sidx_pyarchinit_reperti_the_geom;


------------------------------------------------------------------------------------------------------------------------------------------------------
drop view if exists pyarchinit_reperti_view;	
	CREATE OR REPLACE VIEW pyarchinit_reperti_view AS 
	SELECT
	the_geom,
	id_rep,
	siti,
	id_invmat ,
    sito,
    numero_inventario,
    tipo_reperto,
    criterio_schedatura,
    definizione,
    descrizione,
    area,
    us,
    lavato ,
    nr_cassa,
    luogo_conservazione,
    stato_conservazione,
    datazione_reperto,
    elementi_reperto,
    misurazioni,
    rif_biblio,
    tecnologie,
    forme_minime,
    forme_massime,
    totale_frammenti,
    corpo_ceramico,
    rivestimento,
    diametro_orlo,
    peso,
    tipo,
    eve_orlo ,
    repertato ,
    diagnostico
	FROM pyarchinit_reperti
     JOIN inventario_materiali_table ON siti::text = sito AND id_rep = numero_inventario;

ALTER TABLE pyarchinit_reperti_view
    OWNER TO postgres;	
-- DROP FUNCTION public.create_geom();

CREATE OR REPLACE FUNCTION public.create_geom()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
BEGIN
 if new.coord is null or new.coord!= old.coord then

  update pyunitastratigrafiche set coord = ST_AsText(ST_Centroid(the_geom))where scavo_s=New.scavo_s and area_s=New.area_s and us_s=New.us_s;
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

	
        /* ALTER TABLE individui_table ADD COLUMN IF NOT EXISTS sigla_struttura text;

        ALTER TABLE individui_table ADD COLUMN IF NOT EXISTS nr_struttura integer;

        ALTER TABLE individui_table ADD COLUMN IF NOT EXISTS completo_si_no character varying(5);

        ALTER TABLE individui_table ADD COLUMN IF NOT EXISTS disturbato_si_no character varying(5);

        ALTER TABLE individui_table ADD COLUMN IF NOT EXISTS in_connessione_si_no character varying(5);

        ALTER TABLE individui_table ADD COLUMN IF NOT EXISTS lunghezza_scheletro NUMERIC(20,5);

        ALTER TABLE individui_table ADD COLUMN IF NOT EXISTS posizione_scheletro character varying(255);

        ALTER TABLE individui_table ADD COLUMN IF NOT EXISTS posizione_cranio character varying(255);

        ALTER TABLE individui_table ADD COLUMN IF NOT EXISTS posizione_arti_superiori character varying(255);

        ALTER TABLE individui_table ADD COLUMN IF NOT EXISTS posizione_arti_inferiori character varying(255);
        
        ALTER TABLE individui_table ADD COLUMN IF NOT EXISTS orientamento_asse text;

        ALTER TABLE individui_table ADD COLUMN IF NOT EXISTS orientamento_azimut NUMERIC(20,5); */

CREATE TABLE IF NOT EXISTS public.tomba_table (
    id_tomba integer NOT NULL,
    sito text,
	area integer,
    nr_scheda_taf integer,
    sigla_struttura text,
    nr_struttura integer,
    nr_individuo integer,
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

CREATE SEQUENCE IF NOT EXISTS public.tomba_table_id_tomba_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tomba_table_id_tomba_seq OWNER TO postgres;

ALTER TABLE ONLY public.tomba_table ALTER COLUMN id_tomba SET DEFAULT nextval('public.tomba_table_id_tomba_seq'::regclass);
ALTER TABLE ONLY public.tomba_table DROP CONSTRAINT IF EXISTS "ID_tomba_unico";
ALTER TABLE ONLY public.tomba_table DROP CONSTRAINT IF EXISTS tomba_table_pkey;
ALTER TABLE ONLY public.tomba_table  ADD CONSTRAINT  "ID_tomba_unico" UNIQUE (sito, nr_scheda_taf);
ALTER TABLE ONLY public.tomba_table  ADD CONSTRAINT  tomba_table_pkey PRIMARY KEY (id_tomba);	
	

/* INSERT INTO tomba_table (
            id_tomba,
			sito,
			nr_scheda_taf ,
			sigla_struttura, 
			nr_struttura ,
			nr_individuo ,
			rito ,
			descrizione_taf ,
			interpretazione_taf ,
			segnacoli ,
			canale_libatorio_si_no, 
			oggetti_rinvenuti_esterno ,
			stato_di_conservazione, 
			copertura_tipo ,
			tipo_contenitore_resti ,
			corredo_presenza ,
			corredo_tipo ,
			corredo_descrizione ,
			periodo_iniziale ,
			fase_iniziale ,
			periodo_finale ,
			fase_finale ,
			datazione_estesa 
			)
                
                  SELECT
				    id_tafonomia,
					sito,
					nr_scheda_taf ,
					sigla_struttura, 
					nr_struttura ,
					nr_individuo ,
					rito ,
					descrizione_taf ,
					interpretazione_taf ,
					segnacoli ,
					canale_libatorio_si_no, 
					oggetti_rinvenuti_esterno ,
					stato_di_conservazione, 
					copertura_tipo ,
					tipo_contenitore_resti ,
					corredo_presenza ,
					corredo_tipo ,
					corredo_descrizione ,
					periodo_iniziale ,
					fase_iniziale ,
					periodo_finale ,
					fase_finale ,
					datazione_estesa 

                  FROM tafonomia_table
				  ON CONFLICT (sito, nr_scheda_taf) DO NOTHING; */
				  
				  
/* INSERT INTO individui_table (
            	sito,
				nr_individuo,
				sigla_struttura,
				nr_struttura,
				completo_si_no ,
				disturbato_si_no ,
				in_connessione_si_no, 
				lunghezza_scheletro ,
				posizione_scheletro ,
				posizione_cranio ,
				posizione_arti_superiori ,
				posizione_arti_inferiori, 
				orientamento_asse ,
				orientamento_azimut 

			)
                
                  SELECT
					sito,
					nr_individuo,
					sigla_struttura,
					nr_struttura,
					completo_si_no ,
					disturbato_si_no ,
					in_connessione_si_no, 
					lunghezza_scheletro ,
					posizione_scheletro ,
					posizione_cranio ,
					posizione_arti_superiori ,
					posizione_arti_inferiori, 
					orientamento_asse ,
					orientamento_azimut 

                  FROM tafonomia_table; */
				  
				  /* ON CONFLICT (id_scheda_ind,nr_individuo) DO UPDATE
				  set sito=EXCLUDED.sito, nr_individuo=EXCLUDED.nr_individuo; */
				  

CREATE SEQUENCE IF NOT EXISTS public.pyarchinit_quote_usm_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyarchinit_quote_usm_gid_seq OWNER TO postgres;


CREATE TABLE IF NOT EXISTS public.pyarchinit_quote_usm (
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
	unita_tipo_q character varying(250),
	CONSTRAINT pyarchinit_quote_usm_pkey PRIMARY KEY (gid)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;



ALTER TABLE public.pyarchinit_quote_usm OWNER TO postgres;


CREATE SEQUENCE IF NOT EXISTS public.pyunitastratigrafiche_usm_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pyunitastratigrafiche_usm_gid_seq OWNER TO postgres;

CREATE TABLE IF NOT EXISTS public.pyunitastratigrafiche_usm (
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
	unita_tipo_s character varying(250),
    CONSTRAINT pyunitastratigrafiche_usm_pkey PRIMARY KEY (gid)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;


ALTER TABLE public.pyunitastratigrafiche_usm OWNER TO postgres;



CREATE OR REPLACE VIEW public.pyarchinit_strutture_view AS
 SELECT a.gid,
    a.sito,
    a.id_strutt,
    a.per_iniz,
    a.per_fin,
    a.dataz_ext,
    a.fase_iniz,
    a.fase_fin,
    a.descrizione,
    a.the_geom,
    a.sigla_strut,
    a.nr_strut,
    b.id_struttura,
    b.sito AS sito_1,
    b.sigla_struttura,
    b.numero_struttura,
    b.categoria_struttura,
    b.tipologia_struttura,
    b.definizione_struttura,
    b.descrizione AS descrizione_1,
    b.interpretazione,
    b.periodo_iniziale,
    b.fase_iniziale,
    b.periodo_finale,
    b.fase_finale,
    b.datazione_estesa,
    b.materiali_impiegati,
    b.elementi_strutturali,
    b.rapporti_struttura,
    b.misure_struttura
   FROM pyarchinit_strutture_ipotesi a
     JOIN struttura_table b ON a.sito::text = b.sito AND a.sigla_strut::text = b.sigla_struttura AND a.nr_strut = b.numero_struttura;

ALTER TABLE public.pyarchinit_strutture_view
    OWNER TO postgres;
CREATE OR REPLACE VIEW public.pyarchinit_individui_view AS
 SELECT pyarchinit_individui.gid,
    pyarchinit_individui.the_geom,
    pyarchinit_individui.sito AS scavo,
    pyarchinit_individui.id_individuo,
    pyarchinit_individui.note,
    individui_table.id_scheda_ind,
    individui_table.sito,
    individui_table.area,
    individui_table.us,
    individui_table.nr_individuo,
    individui_table.data_schedatura,
    individui_table.schedatore,
    individui_table.sesso,
    individui_table.eta_min,
    individui_table.eta_max,
    individui_table.classi_eta,
    individui_table.osservazioni
   FROM pyarchinit_individui
     JOIN individui_table ON pyarchinit_individui.sito::text = individui_table.sito AND pyarchinit_individui.id_individuo::text = individui_table.nr_individuo::text;

ALTER TABLE public.pyarchinit_individui_view
    OWNER TO postgres;
	
CREATE OR REPLACE VIEW public.pyarchinit_tomba_view AS
 SELECT a.id_tomba,
    a.sito,
	a.area,
    a.nr_scheda_taf,
    a.sigla_struttura,
    a.nr_struttura,
    a.nr_individuo,
    a.rito,
    a.descrizione_taf,
    a.interpretazione_taf,
    a.segnacoli,
    a.canale_libatorio_si_no,
    a.oggetti_rinvenuti_esterno,
    a.stato_di_conservazione,
    a.copertura_tipo,
    a.tipo_contenitore_resti,
    a.tipo_deposizione,
    a.tipo_sepoltura,
    a.corredo_presenza,
    a.corredo_tipo,
    a.corredo_descrizione,
    b.gid,
    b.id_tafonomia_pk,
    b.sito AS sito_1,
    b.nr_scheda,
    b.the_geom
   FROM tomba_table a
     JOIN pyarchinit_tafonomia b ON a.sito = b.sito::text AND a.nr_scheda_taf = b.nr_scheda;

ALTER TABLE public.pyarchinit_tomba_view
    OWNER TO postgres;	
	
CREATE OR REPLACE VIEW pyarchinit_sezioni_view AS 
	
SELECT 
pyarchinit_sezioni.gid,
pyarchinit_sezioni.sito as site,
pyarchinit_sezioni.area,
pyarchinit_sezioni.the_geom,
pyarchinit_sezioni.tipo_doc,
pyarchinit_sezioni.nome_doc,
documentazione_table.id_documentazione,
documentazione_table.sito,
documentazione_table.nome_doc as nome_documentazione,
documentazione_table.data,
documentazione_table.tipo_documentazione,
documentazione_table.sorgente,
documentazione_table.scala,
documentazione_table.disegnatore,
documentazione_table.note
FROM pyarchinit_sezioni 
JOIN documentazione_table  ON pyarchinit_sezioni.sito::text=documentazione_table.sito and pyarchinit_sezioni.tipo_doc::text=documentazione_table.tipo_documentazione and pyarchinit_sezioni.nome_doc::text=documentazione_table.nome_doc;
ALTER TABLE pyarchinit_sezioni_view
    OWNER TO postgres;



CREATE OR REPLACE VIEW public.pyarchinit_usm_view AS
 SELECT pyunitastratigrafiche_usm.gid,
    pyunitastratigrafiche_usm.the_geom,
    pyunitastratigrafiche_usm.area_s,
	pyunitastratigrafiche_usm.scavo_s,
    pyunitastratigrafiche_usm.us_s,
    pyunitastratigrafiche_usm.stratigraph_index_us,
    pyunitastratigrafiche_usm.tipo_us_s,
	pyunitastratigrafiche_usm.rilievo_originale,
    pyunitastratigrafiche_usm.disegnatore,
    pyunitastratigrafiche_usm.data,
    pyunitastratigrafiche_usm.tipo_doc,
    pyunitastratigrafiche_usm.nome_doc,
	pyunitastratigrafiche_usm.unita_tipo_s,
    us_table.id_us,
    us_table.sito,
	us_table.area,
	us_table.us,
	us_table.d_stratigrafica,
	us_table.d_interpretativa,
	us_table.descrizione,
	us_table.interpretazione,
	us_table.periodo_iniziale,
	us_table.fase_iniziale,
	us_table.periodo_finale,
	us_table.fase_finale,
	us_table.scavato,
	us_table.attivita,
	us_table.anno_scavo,
	us_table.metodo_di_scavo,
	us_table.inclusi,
	us_table.campioni,
	us_table.rapporti,
	us_table.data_schedatura,
	us_table.schedatore,
	us_table.formazione,
	us_table.stato_di_conservazione,
	us_table.colore,
	us_table.consistenza,
	us_table.struttura,
	us_table.cont_per,
	us_table.order_layer,
	us_table.documentazione,
	us_table.unita_tipo,
	us_table.settore,
	us_table.quad_par,
	us_table.ambient,
	us_table.saggio,
	us_table.elem_datanti,
	us_table.funz_statica,
	us_table.lavorazione,
	us_table.spess_giunti,
	us_table.letti_posa,
	us_table.alt_mod,
	us_table.un_ed_riass,
	us_table.reimp,
	us_table.posa_opera,
	us_table.quota_min_usm,
	us_table.quota_max_usm,
	us_table.cons_legante,
	us_table.col_legante,
	us_table.aggreg_legante,
	us_table.con_text_mat,
	us_table.col_materiale,
	us_table.inclusi_materiali_usm,
	us_table.n_catalogo_generale,
	us_table.n_catalogo_interno,
	us_table.n_catalogo_internazionale,
	us_table.soprintendenza,
	us_table.quota_relativa,
	us_table.quota_abs,
	us_table.ref_tm,
	us_table.ref_ra,
	us_table.ref_n,
	us_table.posizione,
	us_table.criteri_distinzione,
	us_table.modo_formazione,
	us_table.componenti_organici,
	us_table.componenti_inorganici,
	us_table.lunghezza_max,
	us_table.altezza_max,
	us_table.altezza_min,
	us_table.profondita_max,
	us_table.profondita_min,
	us_table.larghezza_media,
	us_table.quota_max_abs,
	us_table.quota_max_rel,
	us_table.quota_min_abs,
	us_table.quota_min_rel,
	us_table.osservazioni,
	us_table.datazione,
	us_table.flottazione,
	us_table.setacciatura,
	us_table.affidabilita,
	us_table.direttore_us,
	us_table.responsabile_us,
	us_table.cod_ente_schedatore,
	us_table.data_rilevazione,
	us_table.data_rielaborazione,
	us_table.lunghezza_usm,
	us_table.altezza_usm,
	us_table.spessore_usm,
	us_table.tecnica_muraria_usm,
	us_table.modulo_usm,
	us_table.campioni_malta_usm,
	us_table.campioni_mattone_usm,
	us_table.campioni_pietra_usm,
	us_table.provenienza_materiali_usm,
	us_table.criteri_distinzione_usm,
	us_table.uso_primario_usm
   FROM pyunitastratigrafiche_usm
     JOIN us_table ON pyunitastratigrafiche_usm.scavo_s::text = us_table.sito AND pyunitastratigrafiche_usm.area_s::text = us_table.area::text AND pyunitastratigrafiche_usm.us_s = us_table.us AND pyunitastratigrafiche_usm.unita_tipo_s::text = us_table.unita_tipo::text
  ORDER BY us_table.order_layer, pyunitastratigrafiche_usm.stratigraph_index_us DESC, pyunitastratigrafiche_usm.gid;

ALTER TABLE public.pyarchinit_usm_view
    OWNER TO postgres;

CREATE OR REPLACE VIEW public.pyarchinit_quote_usm_view AS
 SELECT pyarchinit_quote_usm.gid,
    pyarchinit_quote_usm.sito_q,
    pyarchinit_quote_usm.area_q,
    pyarchinit_quote_usm.us_q,
    pyarchinit_quote_usm.unita_misu_q,
    pyarchinit_quote_usm.quota_q,	
    pyarchinit_quote_usm.the_geom,
	pyarchinit_quote_usm.unita_tipo_q,	
    us_table.id_us,
    us_table.sito,
    us_table.area,
    us_table.us,
    us_table.struttura,
    us_table.d_stratigrafica,
    us_table.d_interpretativa,
    us_table.descrizione,
    us_table.interpretazione,
    us_table.rapporti,
    us_table.periodo_iniziale,
    us_table.fase_iniziale,
    us_table.periodo_finale,
    us_table.fase_finale,
    us_table.anno_scavo,
    us_table.cont_per
   FROM pyarchinit_quote_usm
     JOIN us_table ON pyarchinit_quote_usm.sito_q::text = us_table.sito AND pyarchinit_quote_usm.area_q::text = us_table.area::text AND pyarchinit_quote_usm.us_q::text = us_table.us::text AND pyarchinit_quote_usm.unita_tipo_q::text = us_table.unita_tipo::text ;

ALTER TABLE public.pyarchinit_quote_usm_view
    OWNER TO postgres;	