'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class PYDOCUMENTAZIONE(object):
    # def __init__"
    def __init__(self,
                pkuid,
                sito, 
                nome_doc, 
                tipo_doc, 
                path_qgis_pj, 
                the_geom
                ):
        self.pkuid=pkuid
        self.sito=sito 
        self.nome_doc=nome_doc 
        self.tipo_doc=tipo_doc 
        self.path_qgis_pj=path_qgis_pj
        self.the_geom=the_geom
    # def __repr__"
    @property
    def __repr__(self):
        return "<PYDOCUMENTAZIONE('%d','%s', '%s', '%s', '%s', '%s')>" % (
            self.pkuid,
            self.sito, 
            self.nome_doc, 
            self.tipo_doc, 
            self.path_qgis_pj,
            self.the_geom)
