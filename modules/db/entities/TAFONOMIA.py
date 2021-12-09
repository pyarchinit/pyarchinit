'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class TOMBA(object):
    def __init__(self,
                 id_tomba,
                 sito,
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
                 orientamento_asse,
                 orientamento_azimut,
                 corredo_presenza,
                 corredo_tipo,
                 corredo_descrizione,
                 lunghezza_scheletro,
                 posizione_scheletro,
                 posizione_cranio,
                 posizione_arti_superiori,
                 posizione_arti_inferiori,
                 completo_si_no,
                 disturbato_si_no,
                 in_connessione_si_no,
                 caratteristiche,
                 periodo_iniziale,
                 fase_iniziale,
                 periodo_finale,
                 fase_finale,
                 datazione_estesa,
                 misure_tomba
                 ):
        self.id_tomba = id_tomba  # 0
        self.sito = sito  # 1
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
        self.orientamento_asse = orientamento_asse  # 15
        self.orientamento_azimut = orientamento_azimut  # 16
        self.corredo_presenza = corredo_presenza  # 17
        self.corredo_tipo = corredo_tipo  # 18
        self.corredo_descrizione = corredo_descrizione  # 19
        self.lunghezza_scheletro = lunghezza_scheletro  # 20
        self.posizione_scheletro = posizione_scheletro
        self.posizione_cranio = posizione_cranio
        self.posizione_arti_superiori = posizione_arti_superiori
        self.posizione_arti_inferiori = posizione_arti_inferiori
        self.completo_si_no = completo_si_no
        self.disturbato_si_no = disturbato_si_no
        self.in_connessione_si_no = in_connessione_si_no
        self.caratteristiche = caratteristiche
        self.periodo_iniziale = periodo_iniziale
        self.fase_iniziale = fase_iniziale
        self.periodo_finale = periodo_finale
        self.fase_finale = fase_finale
        self.datazione_estesa = datazione_estesa
        self.misure_tomba = misure_tomba
        # def __repr__"

    def __repr__(self):
        return "<TOMBA('%d', '%s', '%d', '%s', '%d', '%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%r', '%s', '%s', '%s', '%r', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%d','%d','%d','%d', '%s', '%s')>" % (
            self.id_tomba,
            self.sito,
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
            self.orientamento_asse,
            self.orientamento_azimut,
            self.corredo_presenza,
            self.corredo_tipo,
            self.corredo_descrizione,
            self.lunghezza_scheletro,
            self.posizione_scheletro,
            self.posizione_cranio,
            self.posizione_arti_superiori,
            self.posizione_arti_inferiori,
            self.completo_si_no,
            self.disturbato_si_no,
            self.in_connessione_si_no,
            self.caratteristiche,
            self.periodo_iniziale,
            self.fase_iniziale,
            self.periodo_finale,
            self.fase_finale,
            self.datazione_estesa,
            self.misure_tomba
        )
