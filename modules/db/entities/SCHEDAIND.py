'''
Created on 19 feb 2018

@author: Serena Sensini
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
                 osservazioni):
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

    # def __repr__"
    def __repr__(self):
        return "<SCHEDAIND('%d','%s', '%d','%s','%d','%s','%s','%s','%d','%d','%s','%s')>" % (
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
            self.osservazioni
        )
