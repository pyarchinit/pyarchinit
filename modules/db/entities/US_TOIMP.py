'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class US_TOIMP(object):
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
                 struttura
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

    # def __repr__"
    def __repr__(self):
        return "<US_TOIMP('%d', '%s', '%s', '%d','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % (
            self.id_us,
            self.sito,
            self.area,
            self.us,
            self.d_stratigrafica,
            self.d_interpretativa,
            self.descrizione,
            self.interpretazione,
            self.periodo_iniziale,
            self.fase_iniziale,
            self.periodo_finale,
            self.fase_finale,
            self.scavato,
            self.attivita,
            self.anno_scavo,
            self.metodo_di_scavo,
            self.inclusi,
            self.campioni,
            self.rapporti,
            self.data_schedatura,
            self.schedatore,
            self.formazione,
            self.stato_di_conservazione,
            self.colore,
            self.consistenza,
            self.struttura
        )
