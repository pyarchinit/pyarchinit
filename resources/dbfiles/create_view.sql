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
     JOIN us_table ON pyarchinit_quote.sito_q::text = us_table.sito AND pyarchinit_quote.area_q::text = us_table.area::text AND pyarchinit_quote.us_q::text = us_table.us::text;

ALTER TABLE public.pyarchinit_quote_view
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

-- View: public.pyarchinit_tafonomia_view

-- DROP VIEW public.pyarchinit_tafonomia_view;

CREATE OR REPLACE VIEW public.pyarchinit_tafonomia_view AS
 SELECT a.id_tafonomia,
    a.sito,
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
    a.orientamento_asse,
    a.orientamento_azimut,
    a.riferimenti_stratigrafici,
    a.corredo_presenza,
    a.corredo_tipo,
    a.corredo_descrizione,
    a.lunghezza_scheletro,
    a.posizione_scheletro,
    a.posizione_cranio,
    a.posizione_arti_superiori,
    a.posizione_arti_inferiori,
    a.completo_si_no,
    a.disturbato_si_no,
    a.in_connessione_si_no,
    a.caratteristiche,
    b.gid,
    b.id_tafonomia_pk,
    b.sito AS sito_1,
    b.nr_scheda,
    b.the_geom
   FROM tafonomia_table a
     JOIN pyarchinit_tafonomia b ON a.sito = b.sito::text AND a.nr_scheda_taf = b.nr_scheda;

ALTER TABLE public.pyarchinit_tafonomia_view
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
    pyunitastratigrafiche.tipo_us_s,
    pyunitastratigrafiche.scavo_s,
    pyunitastratigrafiche.area_s,
    pyunitastratigrafiche.us_s,
    pyunitastratigrafiche.stratigraph_index_us,
    us_table.id_us,
    us_table.sito,
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
    us_table.cont_per,
    us_table.order_layer,
    us_table.attivita
   FROM pyunitastratigrafiche
     JOIN us_table ON pyunitastratigrafiche.scavo_s::text = us_table.sito AND pyunitastratigrafiche.area_s::text = us_table.area::text AND pyunitastratigrafiche.us_s = us_table.us
  ORDER BY us_table.order_layer, pyunitastratigrafiche.stratigraph_index_us DESC, pyunitastratigrafiche.gid;

ALTER TABLE public.pyarchinit_us_view
    OWNER TO postgres;

-- View: public.pyarchinit_us_view_f

-- DROP VIEW public.pyarchinit_us_view_f;

CREATE OR REPLACE VIEW public.pyarchinit_us_view_f AS
 SELECT pyunitastratigrafiche.gid,
    pyunitastratigrafiche.the_geom,
    pyunitastratigrafiche.tipo_us_s,
    pyunitastratigrafiche.scavo_s,
    pyunitastratigrafiche.area_s,
    pyunitastratigrafiche.us_s,
    pyunitastratigrafiche.stratigraph_index_us,
    pyunitastratigrafiche.rilievo_orginale,
    pyunitastratigrafiche.disegnatore,
    pyunitastratigrafiche.data,
    pyunitastratigrafiche.tipo_doc,
    pyunitastratigrafiche.nome_doc,
    us_table.id_us,
    us_table.sito,
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
    us_table.cont_per,
    us_table.order_layer,
    us_table.attivita
   FROM pyunitastratigrafiche
     JOIN us_table ON pyunitastratigrafiche.scavo_s::text = us_table.sito AND pyunitastratigrafiche.area_s::text = us_table.area::text AND pyunitastratigrafiche.us_s = us_table.us
  ORDER BY us_table.order_layer, pyunitastratigrafiche.stratigraph_index_us DESC, pyunitastratigrafiche.gid;

ALTER TABLE public.pyarchinit_us_view_f
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

