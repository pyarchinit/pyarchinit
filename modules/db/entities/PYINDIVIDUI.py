'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class PYINDIVIDUI(object):
    # def __init__"
    def __init__(self,
                id,
                sito, 
                sigla_struttura, 
                note, 
                id_individuo, 
                the_geom
                ):
        self.id=id
        self.sito=sito 
        self.sigla_struttura=sigla_struttura
        self.note=note 
        self.id_individuo=id_individuo
        self.the_geom=the_geom
    # def __repr__"
    @property
    def __repr__(self):
        return "<PYINDIVIDUI('%d','%s', '%s', '%s', '%d','%s')>" % (
            self.id,
            self.sito, 
            self.sigla_struttura,
            self.note, 
            self.id_individuo,
            self.the_geom)
