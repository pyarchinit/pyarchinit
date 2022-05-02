'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class PYUS_NEGATIVE(object):
    # def __init__"
    def __init__(self,
                pkuid,
                sito_n ,
                area_n ,
                us_n ,
                tipo_doc_n ,
                nome_doc_n, 
                the_geom
                ):
        self.pkuid=pkuid
        sito_n=sito_n
        area_n=area_n
        us_n=us_n
        tipo_doc_n=tipo_doc_n
        nome_doc_n=nome_doc_n 
        the_geom=the_geom
    # def __repr__"
    @property
    def __repr__(self):
        return "<PYUS_NEGATIVE('%d','%s', '%s', '%s', '%s', '%s', '%s')>" % (
            self.pkuid,
            sito_n,
            area_n,
            us_n,
            tipo_doc_n,
            nome_doc_n, 
            the_geom)
