'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class US(object):
    # def __init__"
    def __init__(self,
                 id_us,  # 0
                 sito,  # 1
                 area,  # 2
                 us,  # 3
                 d_stratigrafica,  # 4
                 d_interpretativa,  # 5
                 descrizione,  # 6
                 interpretazione,  # 7
                 periodo_iniziale,  # 8
                 fase_iniziale,  # 9
                 periodo_finale,  # 10
                 fase_finale,  # 11
                 scavato,  # 12
                 attivita,  # 13
                 anno_scavo,  # 14
                 metodo_di_scavo,  # 15
                 inclusi,  # 16
                 campioni,  # 17
                 rapporti,  # 18
                 data_schedatura,  # 19
                 schedatore,  # 20
                 formazione,  # 21
                 stato_di_conservazione,  # 22
                 colore,  # 23
                 consistenza,  # 24
                 struttura,  # 25
                 cont_per,  # 26
                 order_layer,  # 27
                 documentazione,  # 28
                 unita_tipo,  # 29 campi aggiunti per USM
                 settore,  # 30
                 quad_par,  # 31
                 ambient,  # 32
                 saggio,  # 33
                 elem_datanti,  # 34
                 funz_statica,  # 35
                 lavorazione,  # 36
                 spess_giunti,  # 37
                 letti_posa,  # 38
                 alt_mod,  # 39
                 un_ed_riass,  # 40
                 reimp,  # 41
                 posa_opera,  # 42
                 quota_min_usm,  # 43
                 quota_max_usm,  # 44
                 cons_legante,  # 45
                 col_legante,  # 46
                 aggreg_legante,  # 47
                 con_text_mat,  # 48
                 col_materiale,  # 49
                 inclusi_materiali_usm,  # 50
                 n_catalogo_generale,  # 51 campi aggiunti per archeo 3.0 e allineamento ICCD
                 n_catalogo_interno,  # 52
                 n_catalogo_internazionale,  # 53
                 soprintendenza,  # 54
                 quota_relativa,  # 55
                 quota_abs,  # 56
                 ref_tm,  # 57
                 ref_ra,  # 58
                 ref_n,  # 59
                 posizione,  # 60
                 criteri_distinzione,  # 61
                 modo_formazione,  # 62
                 componenti_organici,  # 63
                 componenti_inorganici,  # 64
                 lunghezza_max,  # 65
                 altezza_max,  # 66
                 altezza_min,  # 67
                 profondita_max,  # 68
                 profondita_min,  # 69
                 larghezza_media,  # 70
                 quota_max_abs,  # 71
                 quota_max_rel,  # 72
                 quota_min_abs,  # 73
                 quota_min_rel,  # 74
                 osservazioni,  # 75
                 datazione,  # 76
                 flottazione,  # 77
                 setacciatura,  # 78
                 affidabilita,  # 79
                 direttore_us,  # 80
                 responsabile_us,  # 81
                 cod_ente_schedatore,  # 82
                 data_rilevazione,  # 83
                 data_rielaborazione,  # 84
                 lunghezza_usm,  # 85
                 altezza_usm,  # 86
                 spessore_usm,  # 87
                 tecnica_muraria_usm,  # 88
                 modulo_usm,  # 89
                 campioni_malta_usm,  # 90
                 campioni_mattone_usm,  # 91
                 campioni_pietra_usm,  # 92
                 provenienza_materiali_usm,  # 93
                 criteri_distinzione_usm,
                 uso_primario_usm,# 94
                 tipologia_opera,
                 sezione_muraria,
                 superficie_analizzata,
                 orientamento,
                 materiali_lat,
                 lavorazione_lat,
                 consistenza_lat,
                 forma_lat,
                 colore_lat,
                 impasto_lat,
                 forma_p,
                 colore_p,
                 taglio_p,
                 posa_opera_p,
                 inerti_usm,
                 tipo_legante_usm,
                 rifinitura_usm,
                 materiale_p,
                 consistenza_p,
                 rapporti2,
                 doc_usv
                 ):
        self.id_us = id_us  # 0
        self.sito = sito  # 1
        self.area = area  # 2
        self.us = us  # 3
        self.d_stratigrafica = d_stratigrafica  # 4
        self.d_interpretativa = d_interpretativa  # 5
        self.descrizione = descrizione  # 6
        self.interpretazione = interpretazione  # 7
        self.periodo_iniziale = periodo_iniziale  # 8
        self.fase_iniziale = fase_iniziale  # 9
        self.periodo_finale = periodo_finale  # 10
        self.fase_finale = fase_finale  # 11
        self.scavato = scavato  # 12
        self.attivita = attivita  # 13
        self.anno_scavo = anno_scavo  # 14
        self.metodo_di_scavo = metodo_di_scavo  # 15
        self.inclusi = inclusi  # 16
        self.campioni = campioni  # 17
        self.rapporti = rapporti  # 18
        self.data_schedatura = data_schedatura  # 19
        self.schedatore = schedatore  # 20
        self.formazione = formazione  # 21
        self.stato_di_conservazione = stato_di_conservazione  # 22
        self.colore = colore  # 23
        self.consistenza = consistenza  # 24
        self.struttura = struttura  # 25
        self.cont_per = cont_per  # 26
        self.order_layer = order_layer  # 27
        self.documentazione = documentazione  # 28
        self.unita_tipo = unita_tipo  # campi aggiunti per USM #29
        self.settore = settore  # 30
        self.quad_par = quad_par  # 31
        self.ambient = ambient  # 32
        self.saggio = saggio  # 33
        self.elem_datanti = elem_datanti  # 34
        self.funz_statica = funz_statica  # 35
        self.lavorazione = lavorazione  # 36
        self.spess_giunti = spess_giunti  # 37
        self.letti_posa = letti_posa  # 38
        self.alt_mod = alt_mod  # 39
        self.un_ed_riass = un_ed_riass  # 40
        self.reimp = reimp  # 41
        self.posa_opera = posa_opera  # 42
        self.quota_min_usm = quota_min_usm  # 43
        self.quota_max_usm = quota_max_usm  # 44
        self.cons_legante = cons_legante  # 45
        self.col_legante = col_legante  # 46
        self.aggreg_legante = aggreg_legante  # 47
        self.con_text_mat = con_text_mat  # 48
        self.col_materiale = col_materiale  # 49
        self.inclusi_materiali_usm = inclusi_materiali_usm  # 50
        self.n_catalogo_generale = n_catalogo_generale  # 51 campi aggiunti per archeo 3.0 e allineamento ICCD
        self.n_catalogo_interno = n_catalogo_interno  # 52
        self.n_catalogo_internazionale = n_catalogo_internazionale  # 53
        self.soprintendenza = soprintendenza  # 54
        self.quota_relativa = quota_relativa  # 55
        self.quota_abs = quota_abs  # 56
        self.ref_tm = ref_tm  # 57
        self.ref_ra = ref_ra  # 58
        self.ref_n = ref_n  # 59
        self.posizione = posizione  # 60
        self.criteri_distinzione = criteri_distinzione  # 61
        self.modo_formazione = modo_formazione  # 62
        self.componenti_organici = componenti_organici  # 63
        self.componenti_inorganici = componenti_inorganici  # 64
        self.lunghezza_max = lunghezza_max  # 65
        self.altezza_max = altezza_max  # 66 ok
        self.altezza_min = altezza_min  # 67
        self.profondita_max = profondita_max  # 68
        self.profondita_min = profondita_min  # 69 ok
        self.larghezza_media = larghezza_media  # 70 ok
        self.quota_max_abs = quota_max_abs  # 71
        self.quota_max_rel = quota_max_rel  # 72
        self.quota_min_abs = quota_min_abs  # 73
        self.quota_min_rel = quota_min_rel  # 74 ok
        self.osservazioni = osservazioni  # 75
        self.datazione = datazione  # 76
        self.flottazione = flottazione  # 77
        self.setacciatura = setacciatura  # 78
        self.affidabilita = affidabilita  # 79
        self.direttore_us = direttore_us  # 80
        self.responsabile_us = responsabile_us  # 81
        self.cod_ente_schedatore = cod_ente_schedatore  # 82 ok
        self.data_rilevazione = data_rilevazione  # 83
        self.data_rielaborazione = data_rielaborazione  # 84
        self.lunghezza_usm = lunghezza_usm  # 85
        self.altezza_usm = altezza_usm  # 86
        self.spessore_usm = spessore_usm  # 87
        self.tecnica_muraria_usm = tecnica_muraria_usm  # 88 ok
        self.modulo_usm = modulo_usm  # 89
        self.campioni_malta_usm = campioni_malta_usm  # 90
        self.campioni_mattone_usm = campioni_mattone_usm  # 91
        self.campioni_pietra_usm = campioni_pietra_usm  # 92 ok
        self.provenienza_materiali_usm = provenienza_materiali_usm  # 93
        self.criteri_distinzione_usm = criteri_distinzione_usm  # 94
        self.uso_primario_usm = uso_primario_usm  # 95
        self.tipologia_opera=tipologia_opera
        self.sezione_muraria=sezione_muraria
        self.superficie_analizzata=superficie_analizzata
        self.orientamento=orientamento
        self.materiali_lat=materiali_lat
        self.lavorazione_lat=lavorazione_lat
        self.consistenza_lat=consistenza_lat
        self.forma_lat=forma_lat
        self.colore_lat=colore_lat
        self.impasto_lat=impasto_lat
        self.forma_p=forma_p
        self.colore_p=colore_p
        self.taglio_p=taglio_p
        self.posa_opera_p=posa_opera_p
        self.inerti_usm=inerti_usm
        self.tipo_legante_usm=tipo_legante_usm
        self.rifinitura_usm=rifinitura_usm
        self.materiale_p=materiale_p
        self.consistenza_p=consistenza_p
        self.rapporti2=rapporti2
        self.doc_usv=doc_usv
    # def __repr__"
    @property
    def __repr__(self):
        return "<US('%d','%s', '%s', '%d','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%r','%r','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%r','%r','%s','%s','%s','%s','%s','%s','%s','%s','%r','%r','%r','%r','%r','%r','%r','%r','%r','%r','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%r','%r','%r','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')>" % (
            self.id_us,  # 0
            self.sito,  # 1
            self.area,  # 2
            self.us,  # 3
            self.d_stratigrafica,  # 4
            self.d_interpretativa,  # 5
            self.descrizione,  # 6
            self.interpretazione,  # 7
            self.periodo_iniziale,  # 8
            self.fase_iniziale,  # 9
            self.periodo_finale,  # 10
            self.fase_finale,  # 11
            self.scavato,  # 12
            self.attivita,  # 13
            self.anno_scavo,  # 14
            self.metodo_di_scavo,  # 15
            self.inclusi,  # 16
            self.campioni,  # 17
            self.rapporti,  # 18
            self.data_schedatura,  # 19
            self.schedatore,  # 20
            self.formazione,  # 21
            self.stato_di_conservazione,  # 22
            self.colore,  # 23
            self.consistenza,  # 24
            self.struttura,  # 25
            self.cont_per,  # 26
            self.order_layer,  # 27
            self.documentazione,  # 28
            self.unita_tipo,  # campi aggiunti per USM #29
            self.settore,  # 30
            self.quad_par,  # 31
            self.ambient,  # 32
            self.saggio,  # 33
            self.elem_datanti,  # 34
            self.funz_statica,  # 35
            self.lavorazione,  # 36
            self.spess_giunti,  # 37
            self.letti_posa,  # 38
            self.alt_mod,  # 39
            self.un_ed_riass,  # 40
            self.reimp,  # 41
            self.posa_opera,  # 42
            self.quota_min_usm,  # 43
            self.quota_max_usm,  # 44
            self.cons_legante,  # 45
            self.col_legante,  # 46
            self.aggreg_legante,  # 47
            self.con_text_mat,  # 48
            self.col_materiale,  # 49
            self.inclusi_materiali_usm,  # 50
            self.n_catalogo_generale,  # 51 campi aggiunti per archeo 30 e allineamento ICCD
            self.n_catalogo_interno,  # 52
            self.n_catalogo_internazionale,  # 53
            self.soprintendenza,  # 54
            self.quota_relativa,  # 55
            self.quota_abs,  # 56
            self.ref_tm,  # 57
            self.ref_ra,  # 58
            self.ref_n,  # 59
            self.posizione,  # 60
            self.criteri_distinzione,  #61
            self.modo_formazione,  # 62
            self.componenti_organici,  # 63
            self.componenti_inorganici,  # 64
            self.lunghezza_max,  # 65
            self.altezza_max,  # 66 ok
            self.altezza_min,  # 67
            self.profondita_max,  # 68
            self.profondita_min,  # 69 ok
            self.larghezza_media,  # 70 ok
            self.quota_max_abs,  # 71
            self.quota_max_rel,  # 72
            self.quota_min_abs,  # 73
            self.quota_min_rel,  # 74 ok
            self.osservazioni,  # 75
            self.datazione,  # 76
            self.flottazione,  # 77
            self.setacciatura,  # 78
            self.affidabilita,  # 79
            self.direttore_us,  #80
            self.responsabile_us,  # 81
            self.cod_ente_schedatore,  # 82 ok
            self.data_rilevazione,  # 83
            self.data_rielaborazione,  # 84
            self.lunghezza_usm,  # 85
            self.altezza_usm,  # 86
            self.spessore_usm,  # 87
            self.tecnica_muraria_usm,  # 88 ok
            self.modulo_usm,  # 89
            self.campioni_malta_usm,  # 90
            self.campioni_mattone_usm,  # 91
            self.campioni_pietra_usm,  # 92 ok
            self.provenienza_materiali_usm,  # 93
            self.criteri_distinzione_usm,  # 94
            self.uso_primario_usm,  # 95
            self.tipologia_opera,
            self.sezione_muraria,
            self.superficie_analizzata,
            self.orientamento,
            self.materiali_lat,
            self.lavorazione_lat,
            self.consistenza_lat,
            self.forma_lat,
            self.colore_lat,
            self.impasto_lat,
            self.forma_p,
            self.colore_p,
            self.taglio_p,
            self.posa_opera_p,
            self.inerti_usm,
            self.tipo_legante_usm,
            self.rifinitura_usm,
            self.materiale_p,
            self.consistenza_p,
            self.rapporti2,
            self.doc_usv
            
        )
