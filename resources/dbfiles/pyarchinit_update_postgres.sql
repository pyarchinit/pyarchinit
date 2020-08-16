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
drop view if exists mediaentity_view;

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
	
drop view pyarchinit_us_view;

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
     JOIN us_table ON pyunitastratigrafiche.scavo_s::text = us_table.sito AND pyunitastratigrafiche.area_s::text = us_table.area::text AND pyunitastratigrafiche.us_s = us_table.us
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
drop view pyarchinit_reperti_view;	
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
