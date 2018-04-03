'''
Created on 19 feb 2018

@author: Serena Sensini
'''


class US(object):
    # def __init__"
    def __init__(self,
                 id_us,
                 sito,
                 area,
                 us,
                 d_stratigrafica,
                 d_interpretativa,
                 descrizione,
                 interpretazione,
                 periodo_iniziale,
                 fase_iniziale,
                 periodo_finale,
                 fase_finale,
                 scavato,
                 attivita,
                 anno_scavo,
                 metodo_di_scavo,
                 inclusi,
                 campioni,
                 rapporti,
                 data_schedatura,
                 schedatore,
                 formazione,
                 stato_di_conservazione,
                 colore,
                 consistenza,
                 struttura,
                 cont_per,
                 order_layer,
                 documentazione,
                 unita_tipo,  # campi aggiunti per USM
                 settore,
                 quad_par,
                 ambient,
                 saggio,
                 elem_datanti,
                 funz_statica,
                 lavorazione,
                 spess_giunti,
                 letti_posa,
                 alt_mod,
                 un_ed_riass,
                 reimp,
                 posa_opera,
                 quota_min_usm,
                 quota_max_usm,
                 cons_legante,
                 col_legante,
                 aggreg_legante,
                 con_text_mat,
                 col_materiale,
                 inclusi_materiali_usm
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

    # def __repr__"
    def __repr__(self):
        return "<US('%d','%s', '%s', '%d','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%r','%r','%s','%s','%s','%s','%s','%s')>" % (
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
            self.inclusi_materiali_usm  # 50
        )
