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
		  ON public.media_thumb_table
		  FOR EACH ROW
		  EXECUTE PROCEDURE public.delete_media_table();

    END IF;
END
$$;  
  
 ---------------------------------------------------------------------------  
CREATE OR REPLACE FUNCTION public.delete_media_to_entity_table()
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
ALTER FUNCTION public.delete_media_to_entity_table()
  OWNER TO postgres;

 
 
 
 DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'delete_media_to_entity_table') THEN
        CREATE TRIGGER delete_media_to_entity_table
  AFTER UPDATE OR DELETE
  ON public.media_thumb_table
  FOR EACH ROW
  EXECUTE PROCEDURE delete_media_to_entity_table();

    END IF;
END
$$;  


  

  




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
CREATE OR REPLACE VIEW public.mediaentity_view AS 
 SELECT media_thumb_table.id_media_thumb,
    media_thumb_table.id_media,
    media_thumb_table.filepath,
    media_to_entity_table.entity_type,
    media_to_entity_table.id_media AS id_media_m,
    media_to_entity_table.id_entity
   FROM media_thumb_table
     JOIN media_to_entity_table ON media_thumb_table.id_media = media_to_entity_table.id_media
  ORDER BY media_to_entity_table.id_entity;

ALTER TABLE public.mediaentity_view
  OWNER TO postgres;
ALTER TABLE public.mediaentity_view ALTER COLUMN id_media_thumb SET DEFAULT nextval('mediaentity_view_id_media_thumb_seq'::regclass);

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
  
	CREATE OR REPLACE VIEW public.pyarchinit_us_negative_doc_view AS SELECT 
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


ALTER TABLE public.pyarchinit_us_negative_doc_view
    OWNER TO postgres;