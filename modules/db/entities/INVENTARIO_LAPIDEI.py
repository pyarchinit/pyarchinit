'''
Created on 15 feb 2018

@author: Enzo Cocca <enzo.ccc@gmail.com>
'''
class INVENTARIO_LAPIDEI(object):
    # def __init__"
    def __init__(self,
                 id_invlap,
                 sito,
                 scheda_numero,
                 collocazione,
                 oggetto,
                 tipologia,
                 materiale,
                 d_letto_posa,
                 d_letto_attesa,
                 toro,
                 spessore,
                 larghezza,
                 lunghezza,
                 h,
                 descrizione,
                 lavorazione_e_stato_di_conservazione,
                 confronti,
                 cronologia,
                 bibliografia,
                 compilatore
                 ):
        self.id_invlap = id_invlap  # 0
        self.sito = sito  # 1
        self.scheda_numero = scheda_numero  # 2
        self.collocazione = collocazione  # 3
        self.oggetto = oggetto  # 4
        self.tipologia = tipologia  # 5
        self.materiale = materiale  # 6
        self.d_letto_posa = d_letto_posa  # 7
        self.d_letto_attesa = d_letto_attesa  # 8
        self.toro = toro  # 9
        self.spessore = spessore  # 10
        self.larghezza = larghezza  # 11
        self.lunghezza = lunghezza  # 12
        self.h = h  # 13
        self.descrizione = descrizione  # 14
        self.lavorazione_e_stato_di_conservazione = lavorazione_e_stato_di_conservazione  # 15
        self.confronti = confronti  # 16
        self.cronologia = cronologia  # 17
        self.bibliografia = bibliografia  # 18
        self.compilatore = compilatore  # 19

    # def __repr__"
    def __repr__(self):
        return "<INVENTARIO_LAPIDEI('%d', '%s', '%d', '%s', '%s', '%s', '%s', '%d', '%d', '%d', '%d', '%d', '%d', '%d', '%s', '%s', '%s', '%s', '%s', '%s' )>" % (
            self.id_invlap,
            self.sito,
            self.scheda_numero,
            self.collocazione,
            self.oggetto,
            self.tipologia,
            self.materiale,
            self.d_letto_posa,
            self.d_letto_attesa,
            self.toro,
            self.spessore,
            self.larghezza,
            self.lunghezza,
            self.h,
            self.descrizione,
            self.lavorazione_e_stato_di_conservazione,
            self.confronti,
            self.cronologia,
            self.bibliografia,
            self.compilatore,
        )
