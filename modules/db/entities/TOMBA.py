'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class TOMBA(object):
    def __init__(self,
                 id_tomba,
                 sito,
                 area,
                 nr_scheda_taf,
                 sigla_struttura,
                 nr_struttura,
                 nr_individuo,
                 rito,
                 descrizione_taf,
                 interpretazione_taf,
                 segnacoli,
                 canale_libatorio_si_no,
                 oggetti_rinvenuti_esterno,
                 stato_di_conservazione,
                 copertura_tipo,
                 tipo_contenitore_resti,
                 tipo_deposizione,
                 tipo_sepoltura,
                 corredo_presenza,
                 corredo_tipo,
                 corredo_descrizione,
                 periodo_iniziale,
                 fase_iniziale,
                 periodo_finale,
                 fase_finale,
                 datazione_estesa
                 ):
        self.id_tomba = id_tomba  # 0
        self.sito = sito  # 1
        self.area=area
        self.nr_scheda_taf = nr_scheda_taf  # 2
        self.sigla_struttura = sigla_struttura  # 3
        self.nr_struttura = nr_struttura  # 4
        self.nr_individuo = nr_individuo  # 5
        self.rito = rito  # 6
        self.descrizione_taf = descrizione_taf  # 7
        self.interpretazione_taf = interpretazione_taf  # 8
        self.segnacoli = segnacoli  # 9
        self.canale_libatorio_si_no = canale_libatorio_si_no  # 10
        self.oggetti_rinvenuti_esterno = oggetti_rinvenuti_esterno  # 11
        self.stato_di_conservazione = stato_di_conservazione  # 12
        self.copertura_tipo = copertura_tipo  # 13
        self.tipo_contenitore_resti = tipo_contenitore_resti  # 14
        self.tipo_deposizione=tipo_deposizione
        self.tipo_sepoltura=tipo_sepoltura
        self.corredo_presenza = corredo_presenza  # 17
        self.corredo_tipo = corredo_tipo  # 18
        self.corredo_descrizione = corredo_descrizione  # 19
        self.periodo_iniziale = periodo_iniziale
        self.fase_iniziale = fase_iniziale
        self.periodo_finale = periodo_finale
        self.fase_finale = fase_finale
        self.datazione_estesa = datazione_estesa
        
        
    def __repr__(self):
        return "<TOMBA('%d', '%s', '%d', '%d', '%s','%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%d','%d','%d','%d','%s')>" % (
            id_tomba,
            self.sito,
            self.area,
            self.nr_scheda_taf,
            self.sigla_struttura,
            self.nr_struttura,
            self.nr_individuo,
            self.rito,
            self.descrizione_taf,
            self.interpretazione_taf,
            self.segnacoli,
            self.canale_libatorio_si_no,
            self.oggetti_rinvenuti_esterno,
            self.stato_di_conservazione,
            self.copertura_tipo,
            self.tipo_contenitore_resti,
            self.tipo_deposizione,
            self.tipo_sepoltura,
            self.corredo_presenza,
            self.corredo_tipo,
            self.corredo_descrizione,
            self.periodo_iniziale,
            self.fase_iniziale,
            self.periodo_finale,
            self.fase_finale,
            self.datazione_estesa
        )
