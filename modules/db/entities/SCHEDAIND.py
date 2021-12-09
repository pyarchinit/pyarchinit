'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class SCHEDAIND(object):
    # def __init__"
    def __init__(self,
                 id_scheda_ind,
                 sito,
                 area,
                 us,
                 nr_individuo,
                 data_schedatura,
                 schedatore,
                 sesso,
                 eta_min,
                 eta_max,
                 classi_eta,
                 osservazioni,
                 sigla_struttura,
                 nr_struttura,
                 completo_si_no,
                 disturbato_si_no,
                 in_connessione_si_no,
                 lunghezza_scheletro,
                 posizione_scheletro,
                 posizione_cranio,
                 posizione_arti_superiori,
                 posizione_arti_inferiori,
                 orientamento_asse,
                 orientamento_azimut                 
                 ):
        self.id_scheda_ind = id_scheda_ind  # 1
        self.sito = sito  # 2
        self.area = area
        self.us = us  # 3
        self.nr_individuo = nr_individuo  # 6
        self.data_schedatura = data_schedatura  # 4
        self.schedatore = schedatore  # 5
        self.sesso = sesso  # 7
        self.eta_min = eta_min  # 8
        self.eta_max = eta_max  # 9
        self.classi_eta = eta_max  # 10
        self.osservazioni = osservazioni  # 11
        self.sigla_struttura=sigla_struttura
        self.nr_struttura=nr_struttura
        self.completo_si_no=completo_si_no
        self.disturbato_si_no=disturbato_si_no
        self.in_connessione_si_no=in_connessione_si_no
        self.lunghezza_scheletro=lunghezza_scheletro
        self.posizione_scheletro=posizione_scheletro
        self.posizione_cranio=posizione_cranio
        self.posizione_arti_superiori=posizione_arti_superiori
        self.posizione_arti_inferiori=posizione_arti_inferiori
        self.orientamento_asse=orientamento_asse
        self.orientamento_azimut=orientamento_azimut       

    # def __repr__"
    def __repr__(self):
        return "<SCHEDAIND('%d','%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%r','%s','%s','%s','%s','%s','%s')>" % (
            self.id_scheda_ind,
            self.sito,
            self.area,
            self.us,
            self.nr_individuo,
            self.data_schedatura,
            self.schedatore,
            self.sesso,
            self.eta_min,
            self.eta_max,
            self.classi_eta,
            self.osservazioni,
            self.sigla_struttura,
            self.nr_struttura,
            self.completo_si_no,
            self.disturbato_si_no,
            self.in_connessione_si_no,
            self.lunghezza_scheletro,
            self.posizione_scheletro,
            self.posizione_cranio,
            self.posizione_arti_superiori,
            self.posizione_arti_inferiori,
            self.orientamento_asse,
            self.orientamento_azimut   
        )
