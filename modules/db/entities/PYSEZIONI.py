'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class PYSEZIONI(object):
    # def __init__"
    def __init__(self,
                id,
                id_sezione, 
                sito, 
                area, 
                descr, 
                the_geom,
                tipo_doc,
                nome_doc
                ):
        self.id=id
        self.id_sezione=id_sezione 
        self.sito=sito 
        self.area=area
        self.descr=descr
        self.the_geom=the_geom
        self.tipo_doc=tipo_doc
        self.nome_doc=nome_doc
    # def __repr__"
    @property
    def __repr__(self):
        return "<PYSEZIONI('%d','%s', '%s', '%d', '%s', '%s', '%s', '%s')>" % (
            self.id,
            self.id_sezione, 
            self.sito, 
            self.area, 
            self.descr, 
            self.the_geom,
            self.tipo_doc,
            self.nome_doc)
