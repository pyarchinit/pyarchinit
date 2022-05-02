'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class PYSITO_POINT(object):
    # def __init__"
    def __init__(self,
                 gid,  # 0
                 sito_nome,  # 1
                 the_geom,
                 ):
        self.gid=gid  # 0
        self.sito_nome=sito_nome  # 1
        self.the_geom= the_geom # 4
    # def __repr__"
    @property
    def __repr__(self):
        return "<PYSITO_POINT('%d','%s', '%s')>" % (
            self.gid,
            self.sito_nome,
            self.the_geom
        )
