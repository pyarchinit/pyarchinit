'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class PYQUOTEUSM(object):
    # def __init__"
    def __init__(self,
                id,
                sito_q, 
                area_q ,
                us_q ,
                unita_misu_q ,
                quota_q ,
                data ,
                disegnatore ,
                rilievo_originale ,
                the_geom,
                unita_tipo_q,
                ):
        self.id=id
        self.sito_q= sito_q
        self.area_q =area_q
        self.us_q =us_q
        self.unita_misu_q =unita_misu_q
        self.quota_q =quota_q
        self.data =data
        self.disegnatore =disegnatore
        self.rilievo_originale =rilievo_originale
        self.the_geom = the_geom
        self.unita_tipo_q=unita_tipo_q
    # def __repr__"
    @property
    def __repr__(self):
        return "<PYQUOTEUSM('%d','%s', '%d', '%d', '%s', '%r', '%s', '%s', '%s', '%s', '%s')>" % (
            self.id,
            self.sito_q,
            self.area_q,
            self.us_q,
            self.unita_misu_q,
            self.quota_q,
            self.data,
            self.disegnatore,
            self.rilievo_originale,
            self.the_geom,
            self.unita_tipo_q)
