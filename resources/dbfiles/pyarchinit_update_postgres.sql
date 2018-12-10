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