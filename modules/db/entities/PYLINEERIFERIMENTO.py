'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class PYLINEERIFERIMENTO(object):
    # def __init__"
    def __init__(self,
                id,
                sito, 
                definizion ,
                descrizion, 
                the_geom
                ):
        self.id=id
        self.sito=sito 
        self.definizion=definizion
        self.descrizion=descrizion 
        self.the_geom=the_geom
    # def __repr__"
    @property
    def __repr__(self):
        return "<PYLINEERIFERIMENTO('%d','%s', '%s', '%s', '%s')>" % (
            self.id,
            self.sito, 
            self.definizion,
            self.descrizion,
            self.the_geom)
