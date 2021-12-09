'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class STRUTTURA(object):
    def __init__(self,
                 id_struttura,
                 sito,
                 sigla_struttura,
                 numero_struttura,
                 categoria_struttura,
                 tipologia_struttura,
                 definizione_struttura,
                 descrizione,
                 interpretazione,
                 periodo_iniziale,
                 fase_iniziale,
                 periodo_finale,
                 fase_finale,
                 datazione_estesa,
                 materiali_impiegati,
                 elementi_strutturali,
                 rapporti_struttura,
                 misure_struttura
                 ):
        self.id_struttura = id_struttura  # 0
        self.sito = sito  # 1
        self.sigla_struttura = sigla_struttura  # 2
        self.numero_struttura = numero_struttura  # 3
        self.categoria_struttura = categoria_struttura  # 4
        self.tipologia_struttura = tipologia_struttura  # 5
        self.definizione_struttura = definizione_struttura  # 6
        self.descrizione = descrizione  # 7
        self.interpretazione = interpretazione  # 8
        self.periodo_iniziale = periodo_iniziale  # 9
        self.fase_iniziale = fase_iniziale  # 10
        self.periodo_finale = periodo_finale  # 11
        self.fase_finale = fase_finale  # 12
        self.datazione_estesa = datazione_estesa  # 13
        self.materiali_impiegati = materiali_impiegati  # 14
        self.elementi_strutturali = elementi_strutturali  # 15
        self.rapporti_struttura = rapporti_struttura  # 16
        self.misure_struttura = misure_struttura  # 17

    def __repr__(self):
        return "<STRUTTURA('%d', '%s', '%s', '%d', '%s', '%s', '%s', '%s', '%s', '%d', '%d', '%d', '%d', '%s', '%s', '%s', '%s', '%s')>" % (
            self.id_struttura,
            self.sito,
            self.sigla_struttura,
            self.numero_struttura,
            self.categoria_struttura,
            self.tipologia_struttura,
            self.definizione_struttura,
            self.descrizione,
            self.interpretazione,
            self.periodo_iniziale,
            self.fase_iniziale,
            self.periodo_finale,
            self.fase_finale,
            self.datazione_estesa,
            self.materiali_impiegati,
            self.elementi_strutturali,
            self.rapporti_struttura,
            self.misure_struttura
        )
