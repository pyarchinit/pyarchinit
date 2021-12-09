'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class PYSTRUTTURE(object):
    # def __init__"
    def __init__(self,
                id,
                sito ,
                id_strutt ,
                per_iniz, 
                per_fin ,
                dataz_ext ,
                fase_iniz, 
                fase_fin ,
                descrizione, 
                the_geom ,
                sigla_strut, 
                nr_strut
                ):
        self.id=id
        self.sito=sito
        self.id_strutt=id_strutt
        self.per_iniz=per_iniz
        self.per_fin=per_fin
        self.dataz_ext=dataz_ext
        self.fase_iniz=fase_iniz 
        self.fase_fin=fase_fin
        self.descrizione=descrizione 
        self.the_geom=the_geom
        self.sigla_strut=sigla_strut 
        self.nr_strut=nr_strut
    # def __repr__"
    @property
    def __repr__(self):
        return "<PYSTRUTTURE('%d','%s', '%s', '%d', '%d', '%s', '%d', '%d', '%s', '%s', '%s', '%d')>" % (
            self.id,
            self.sito,
            self.id_strutt,
            self.per_iniz,
            self.per_fin,
            self.dataz_ext,
            self.fase_iniz,
            self.fase_fin,
            self.descrizione,
            self.the_geom,
            self.sigla_strut,
            self.nr_strut)
