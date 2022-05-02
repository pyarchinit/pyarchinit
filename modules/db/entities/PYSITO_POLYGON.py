'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class PYSITO_POLYGON(object):
    # def __init__"
    def __init__(self,
                 pkuid,  # 0
                 sito_id,  # 1
                 the_geom,
                 ):
        self.pkuid=pkuid  # 0
        self.sito_id=sito_id  # 1
        self.the_geom= the_geom # 4
    # def __repr__"
    @property
    def __repr__(self):
        return "<PYSITO_POLYGON('%d','%s', '%s')>" % (
            self.pkuid,
            self.sito_id,
            self.the_geom
        )
