'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class PYCAMPIONI(object):
    # def __init__"
    def __init__(self,
                id,
                id_campion, 
                sito, 
                tipo_camp ,
                dataz ,
                cronologia ,
                link_immag, 
                sigla_camp ,
                the_geom
                ):
        self.id=id
        self.id_campion=id_campion 
        self.sito=sito 
        self.tipo_camp=tipo_camp
        self.dataz=dataz
        self.cronologia=cronologia
        self.link_immag=link_immag 
        self.sigla_camp=sigla_camp
        self.the_geom=the_geom
    # def __repr__"
    @property
    def __repr__(self):
        return "<PYCAMPIONI('%d','%d', '%s', '%s', '%s','%d','%s','%s','%s')>" % (
            self.id,
            self.id_campion, 
            self.sito,
            self.tipo_camp,
            self.dataz,
            self.cronologia,
            self.link_immag, 
            self.sigla_camp,
            self.the_geom)
