'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class ARCHEOZOOLOGY(object):
    # def __init__"
    def __init__(self,
                 id_archzoo,
                 sito,
                 area,
                 us,
                 quadrato,
                 coord_x,
                 coord_y,
                 coord_z,
                 bos_bison,
                 calcinati,
                 camoscio,
                 capriolo,
                 cervo,
                 combusto,
                 coni,
                 pdi,
                 stambecco,
                 strie,
                 canidi,
                 ursidi,
                 megacero
                 ):
        self.id_archzoo = id_archzoo
        self.sito = sito
        self.area = area
        self.us = us
        self.quadrato = quadrato
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.coord_z = coord_z
        self.bos_bison = bos_bison
        self.calcinati = calcinati
        self.camoscio = camoscio
        self.capriolo = capriolo
        self.cervo = cervo
        self.combusto = combusto
        self.coni = coni
        self.pdi = pdi
        self.stambecco = stambecco
        self.strie = strie
        self.canidi = canidi
        self.ursidi = ursidi
        self.megacero = megacero

    # def __repr__"
    def __repr__(self):
        return "<ARCHEOZOOLOGY('%d', '%s', '%d', '%d', '%s', '%r', '%r', '%r', '%d', '%d', '%d', '%d', '%d', '%d', '%d', '%d', '%d', '%d', '%d', '%d', '%d')>" % (
            self.id_archzoo,
            self.sito,
            self.area,
            self.us,
            self.quadrato,
            self.coord_x,
            self.coord_y,
            self.coord_z,
            self.bos_bison,
            self.calcinati,
            self.camoscio,
            self.capriolo,
            self.cervo,
            self.combusto,
            self.coni,
            self.pdi,
            self.stambecco,
            self.strie,
            self.canidi,
            self.ursidi,
            self.megacero
        )
