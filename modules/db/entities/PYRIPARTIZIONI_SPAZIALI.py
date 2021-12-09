'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class PYRIPARTIZIONI_SPAZIALI(object):
    # def __init__"
    def __init__(self,
                id,
                id_rs, 
                sito_rs, 
                tip_rip, 
                descr_rs, 
                the_geom
                ):
        self.id=id
        self.id_rs=id_rs 
        self.sito_rs=sito_rs 
        self.tip_rip=tip_rip 
        self.descr_rs=descr_rs 
        self.the_geom=the_geom
    # def __repr__"
    @property
    def __repr__(self):
        return "<PYRIPARTIZIONI_SPAZIALI('%d','%s', '%s', '%s', '%s', '%s')>" % (
            self.id,
            self.id_rs, 
            self.sito_rs, 
            self.tip_rip, 
            self.descr_rs, 
            self.the_geom)
