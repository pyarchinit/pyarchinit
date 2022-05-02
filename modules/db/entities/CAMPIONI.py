'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class CAMPIONI(object):
    # def __init__"
    def __init__(self,
                 id_campione,  # 0
                 sito,  # 1
                 nr_campione,  # 2
                 tipo_campione,  # 3
                 descrizione,  # 4
                 area,  # 5
                 us,  # 6
                 numero_inventario_materiale,  # 7
                 nr_cassa,  # 8
                 luogo_conservazione  # 9
                 ):
        self.id_campione = id_campione  # 0
        self.sito = sito  # 1
        self.nr_campione = nr_campione  # 2
        self.tipo_campione = tipo_campione  # 3
        self.descrizione = descrizione  # 4
        self.area = area  # 5
        self.us = us  # 6
        self.numero_inventario_materiale = numero_inventario_materiale  # 7
        self.nr_cassa = nr_cassa  # 8
        self.luogo_conservazione = luogo_conservazione  # 9

    # def __repr__"
    def __repr__(self):
        return "<CAMPIONI('%d', '%s', '%d', '%s', '%s', '%s', '%d', '%d', '%d', '%s')>" % (
            self.id_campione,  # 0
            self.sito,  # 1
            self.nr_campione,  # 2
            self.tipo_campione,  # 3
            self.descrizione,  # 4
            self.area,  # 5
            self.us,  # 6
            self.numero_inventario_materiale,  # 7
            self.nr_cassa,  # 8
            self.luogo_conservazione  # 9
        )
