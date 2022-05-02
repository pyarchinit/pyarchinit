'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class PYTOMBA(object):
    # def __init__"
    def __init__(self,
                id,
                sito, 
                nr_scheda, 
                the_geom
                ):
        self.id=id
        self.sito=sito 
        self.nr_scheda=nr_scheda 
        self.the_geom=the_geom
    # def __repr__"
    @property
    def __repr__(self):
        return "<PYTOMBA('%d','%s', '%d', '%s')>" % (
            self.id,
            self.sito,
            self.nr_scheda,
            self.the_geom)
