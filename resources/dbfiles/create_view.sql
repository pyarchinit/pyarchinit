-- View: public.pyarchinit_individui_view

-- DROP VIEW public.pyarchinit_individui_view;

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

-- View: public.pyarchinit_pyuscarlinee_view

-- DROP VIEW public.pyarchinit_pyuscarlinee_view;

CREATE OR REPLACE VIEW public.pyarchinit_pyuscarlinee_view AS
 SELECT pyuscarlinee.gid,
    pyuscarlinee.the_geom,
    pyuscarlinee.tipo_us_l,
    pyuscarlinee.sito_l,
    pyuscarlinee.area_l,
    pyuscarlinee.us_l,
    us_table.sito,
    us_table.id_us,
    us_table.area,
    us_table.us,
    us_table.struttura,
    us_table.d_stratigrafica AS definizione_stratigrafica,
    us_table.d_interpretativa AS definizione_interpretativa,
    us_table.descrizione,
    us_table.interpretazione,
    us_table.rapporti,
    us_table.periodo_iniziale,
    us_table.fase_iniziale,
    us_table.periodo_finale,
    us_table.fase_finale,
    us_table.anno_scavo,
    us_table.cont_per
   FROM pyuscarlinee
     JOIN us_table ON pyuscarlinee.sito_l::text = us_table.sito AND pyuscarlinee.area_l::text = us_table.area::text AND pyuscarlinee.us_l = us_table.us;

ALTER TABLE public.pyarchinit_pyuscarlinee_view
    OWNER TO postgres;

-- View: public.pyarchinit_quote_view

-- DROP VIEW public.pyarchinit_quote_view;

CREATE OR REPLACE VIEW public.pyarchinit_quote_view AS
 SELECT pyarchinit_quote.gid,
    pyarchinit_quote.sito_q,
    pyarchinit_quote.area_q,
    pyarchinit_quote.us_q,
    pyarchinit_quote.unita_misu_q,
    pyarchinit_quote.quota_q,
    pyarchinit_quote.the_geom,
	pyarchinit_quote.unita_tipo_q,
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
   FROM pyarchinit_quote
     JOIN us_table ON pyarchinit_quote.sito_q::text = us_table.sito AND pyarchinit_quote.area_q::text = us_table.area::text AND pyarchinit_quote.us_q::text = us_table.us::text  AND pyarchinit_quote.unita_tipo_q::text = us_table.unita_tipo::text;

ALTER TABLE public.pyarchinit_quote_view
    OWNER TO postgres;


-- DROP VIEW public.pyarchinit_quote_view;

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
     JOIN us_table ON pyarchinit_quote_usm.sito_q::text = us_table.sito AND pyarchinit_quote_usm.area_q::text = us_table.area::text AND pyarchinit_quote_usm.us_q::text = us_table.us::text AND pyarchinit_quote_usm.unita_tipo_q::text = us_table.unita_tipo::text;;

ALTER TABLE public.pyarchinit_quote_usm_view
    OWNER TO postgres;



-- View: public.pyarchinit_strutture_view

-- DROP VIEW public.pyarchinit_strutture_view;

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

-- View: public.pyarchinit_tomba_view

-- DROP VIEW public.pyarchinit_tomba_view;

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

-- View: public.pyarchinit_tipologie_sepolture_view

-- DROP VIEW public.pyarchinit_tipologie_sepolture_view;

CREATE OR REPLACE VIEW public.pyarchinit_tipologie_sepolture_view AS
 SELECT pyarchinit_quote_view.gid,
    pyarchinit_quote_view.sito_q,
    pyarchinit_quote_view.area_q,
    pyarchinit_quote_view.us_q,
    pyarchinit_quote_view.unita_misu_q,
    pyarchinit_quote_view.quota_q,
    pyarchinit_quote_view.id_us,
    pyarchinit_quote_view.sito,
    pyarchinit_quote_view.area,
    pyarchinit_quote_view.us,
    pyarchinit_quote_view.struttura,
    pyarchinit_quote_view.d_stratigrafica,
    pyarchinit_quote_view.d_interpretativa,
    pyarchinit_quote_view.descrizione,
    pyarchinit_quote_view.interpretazione,
    pyarchinit_quote_view.rapporti,
    pyarchinit_quote_view.periodo_iniziale,
    pyarchinit_quote_view.fase_iniziale,
    pyarchinit_quote_view.periodo_finale,
    pyarchinit_quote_view.fase_finale,
    pyarchinit_quote_view.anno_scavo,
    pyarchinit_tipologia_sepolture.id_sepoltura,
    pyarchinit_tipologia_sepolture.azimut,
    pyarchinit_tipologia_sepolture.tipologia,
    pyarchinit_tipologia_sepolture.the_geom,
    pyarchinit_tipologia_sepolture.sito_ts,
    pyarchinit_tipologia_sepolture.t_progetto AS tipologia_progetto,
    pyarchinit_tipologia_sepolture.t_gruppo AS tipologia_gruppo,
    pyarchinit_tipologia_sepolture.t_codice AS tipologia_codice,
    pyarchinit_tipologia_sepolture.t_sottocodice AS tipologia_sottocodice
   FROM pyarchinit_quote_view
     JOIN pyarchinit_tipologia_sepolture ON pyarchinit_quote_view.struttura::text = pyarchinit_tipologia_sepolture.id_sepoltura::text;

ALTER TABLE public.pyarchinit_tipologie_sepolture_view
    OWNER TO postgres;

-- View: public.pyarchinit_tipologie_view

-- DROP VIEW public.pyarchinit_tipologie_view;

CREATE OR REPLACE VIEW public.pyarchinit_tipologie_view AS
 SELECT pyarchinit_tipologia_sepolture.gid,
    pyarchinit_tipologia_sepolture.id_sepoltura,
    pyarchinit_tipologia_sepolture.azimut,
    pyarchinit_tipologia_sepolture.the_geom,
    pyarchinit_tipologia_sepolture.sito_ts,
    pyarchinit_tipologia_sepolture.t_progetto,
    pyarchinit_tipologia_sepolture.t_gruppo,
    pyarchinit_tipologia_sepolture.t_codice,
    pyarchinit_tipologia_sepolture.t_sottocodice,
    pyarchinit_tipologia_sepolture.corredo,
    pyarchinit_codici_tipologia.tipologia_progetto,
    pyarchinit_codici_tipologia.tipologia_definizione_tipologia,
    pyarchinit_codici_tipologia.tipologia_gruppo,
    pyarchinit_codici_tipologia.tipologia_definizione_gruppo,
    pyarchinit_codici_tipologia.tipologia_codice,
    pyarchinit_codici_tipologia.tipologia_sottocodice,
    pyarchinit_codici_tipologia.tipologia_definizione_codice,
    pyarchinit_codici_tipologia.tipologia_descrizione
   FROM pyarchinit_tipologia_sepolture
     JOIN pyarchinit_codici_tipologia ON pyarchinit_tipologia_sepolture.t_progetto::text = pyarchinit_codici_tipologia.tipologia_progetto::text AND pyarchinit_tipologia_sepolture.t_gruppo::text = pyarchinit_codici_tipologia.tipologia_gruppo::text AND pyarchinit_tipologia_sepolture.t_codice::text = pyarchinit_codici_tipologia.tipologia_codice::text AND pyarchinit_tipologia_sepolture.t_sottocodice::text = pyarchinit_codici_tipologia.tipologia_sottocodice::text;

ALTER TABLE public.pyarchinit_tipologie_view
    OWNER TO postgres;


-- View: public.pyarchinit_us_view

-- DROP VIEW public.pyarchinit_us_view;

CREATE OR REPLACE VIEW public.pyarchinit_us_view AS
 SELECT pyunitastratigrafiche.gid,
    pyunitastratigrafiche.the_geom,
    pyunitastratigrafiche.area_s,
	pyunitastratigrafiche.scavo_s,
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
     JOIN us_table ON pyunitastratigrafiche.scavo_s::text = us_table.sito AND pyunitastratigrafiche.area_s::text = us_table.area::text AND pyunitastratigrafiche.us_s = us_table.us AND pyunitastratigrafiche.unita_tipo_s::text = us_table.unita_tipo::text
  ORDER BY us_table.order_layer, pyunitastratigrafiche.stratigraph_index_us DESC, pyunitastratigrafiche.gid;

ALTER TABLE public.pyarchinit_us_view
    OWNER TO postgres;


-- View: public.pyarchinit_us_view

-- DROP VIEW public.pyarchinit_us_view;

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




-- View: public.pyarchinit_uscaratterizzazioni_view

-- DROP VIEW public.pyarchinit_uscaratterizzazioni_view;

CREATE OR REPLACE VIEW public.pyarchinit_uscaratterizzazioni_view AS
 SELECT pyuscaratterizzazioni.gid,
    pyuscaratterizzazioni.the_geom,
    pyuscaratterizzazioni.tipo_us_c,
    pyuscaratterizzazioni.scavo_c,
    pyuscaratterizzazioni.area_c,
    pyuscaratterizzazioni.us_c,
    us_table.sito,
    us_table.id_us,
    us_table.area,
    us_table.us,
    us_table.struttura,
    us_table.d_stratigrafica AS definizione_stratigrafica,
    us_table.d_interpretativa AS definizione_interpretativa,
    us_table.descrizione,
    us_table.interpretazione,
    us_table.rapporti,
    us_table.periodo_iniziale,
    us_table.fase_iniziale,
    us_table.periodo_finale,
    us_table.fase_finale,
    us_table.anno_scavo,
    us_table.cont_per
   FROM pyuscaratterizzazioni
     JOIN us_table ON pyuscaratterizzazioni.scavo_c::text = us_table.sito AND pyuscaratterizzazioni.area_c::text = us_table.area::text AND pyuscaratterizzazioni.us_c = us_table.us;

ALTER TABLE public.pyarchinit_uscaratterizzazioni_view
    OWNER TO postgres;


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

CREATE OR REPLACE VIEW pyarchinit_site_view AS 
 SELECT 
    sito,
	regione,
    comune,
    provincia,
    descrizione,
    definizione_sito,
	gid,
    the_geom,
    sito_nome
   FROM site_table
     JOIN pyarchinit_siti ON sito ::text = sito_nome;

ALTER TABLE pyarchinit_site_view
  OWNER TO postgres;  
  
CREATE OR REPLACE VIEW pyarchinit_site_polygonal_view AS 
 SELECT 
    sito,
	regione,
    comune,
    provincia,
    descrizione,
    definizione_sito,
	
    the_geom,
    sito_id
   FROM site_table
     JOIN pyarchinit_siti_polygonal ON sito ::text = sito_id;

ALTER TABLE pyarchinit_site_polygonal_view
  OWNER TO postgres;    
  
	
CREATE OR REPLACE VIEW public.pyarchinit_doc_view_b AS SELECT 
	gid , 
	area_s ,
	the_geom ,
	scavo_s ,
	us_s ,
	stratigraph_index_us ,
	tipo_us_s , 
	rilievo_originale,
	disegnatore, 
	data ,
	tipo_doc , 
	nome_doc ,
	
	gid AS gid_1,
	id_us AS id_us, 
	sito AS sito, 
	area AS area,
	us AS us, 
	d_stratigrafica AS d_stratigrafica,
	d_interpretativa AS d_interpretativa, 
	descrizione AS descrizione,
	interpretazione AS interpretazione, 
	periodo_iniziale AS periodo_iniziale,
	fase_iniziale AS fase_iniziale, 
	periodo_finale AS periodo_finale,
	fase_finale AS fase_finale, 
	scavato AS scavato,
	attivita AS attivita, 
	anno_scavo AS anno_scavo,
	metodo_di_scavo AS metodo_di_scavo, 
	inclusi AS inclusi,
	campioni AS campioni, 
	rapporti AS rapporti,
	data_schedatura AS data_schedatura, 
	schedatore AS schedatore,
	formazione AS formazione, 
	stato_di_conservazione AS stato_di_conservazione,
	colore AS colore, 
	consistenza AS consistenza,
	struttura AS struttura, 
	cont_per AS cont_per,
	order_layer AS order_layer, 
	documentazione AS documentazione
	FROM pyunitastratigrafiche AS a
	JOIN us_table ON scavo_s ::text = sito AND area_s ::text = area AND us_s  = us;
	ALTER TABLE public.pyarchinit_doc_view_b OWNER TO postgres;

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

CREATE SEQUENCE IF NOT EXISTS mediaentity_view_id_media_thumb_seq
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE mediaentity_view_id_media_thumb_seq
  OWNER TO postgres;
CREATE OR REPLACE VIEW public.mediaentity_view AS 
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

ALTER TABLE public.mediaentity_view
  OWNER TO postgres;
ALTER TABLE public.mediaentity_view ALTER COLUMN id_media_thumb SET DEFAULT nextval('mediaentity_view_id_media_thumb_seq'::regclass);
	

	CREATE OR REPLACE VIEW pyarchinit_reperti_view AS 
	SELECT
	gid
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