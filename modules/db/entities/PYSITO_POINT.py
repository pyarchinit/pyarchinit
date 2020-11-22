'''
Created on 19 feb 2018

@author: Serena Sensini
'''


class PYSITO_POINT(object):
    # def __init__"
    def __init__(self,
                 id,  # 0
                 sito_nome,  # 1
                 the_geom,
                 ):
        self.id=id  # 0
        self.sito_nome=sito_nome  # 1
        self.the_geom= the_geom # 4
    # def __repr__"
    @property
    def __repr__(self):
        return "<PYSITO_POINT('%d','%s', '%s')>" % (
            self.id,
            self.sito_nome,
            self.the_geom
        )
