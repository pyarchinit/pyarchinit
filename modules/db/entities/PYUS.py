'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class PYUS(object):
    # def __init__"
    def __init__(self,
                 gid,  # 0
                 area_s,  # 1
                 scavo_s,  # 2
                 us_s,  # 3
                 stratigraph_index_us,  # 5
                 tipo_us_s,  # 6
                 rilievo_originale,  # 7
                 disegnatore,  # 8
                 data,  # 9
                 tipo_doc,  # 10
                 nome_doc,  # 11
                 coord,
                 the_geom,
                 unita_tipo_s,# 4
                 ):
        self.gid=gid  # 0
        self.area_s=area_s  # 1
        self.scavo_s=scavo_s  # 2
        self.us_s= us_s # 3
        self.stratigraph_index_us=stratigraph_index_us  # 5
        self.tipo_us_s=tipo_us_s  # 6
        self.rilievo_originale=rilievo_originale  # 7
        self.disegnatore= disegnatore # 8
        self.data=data  # 9
        self.tipo_doc=tipo_doc  # 10
        self.nome_doc=nome_doc  # 11
        self.coord=coord
        self.the_geom= the_geom # 4
        self.unita_tipo_s=unita_tipo_s
    # def __repr__"
    @property
    def __repr__(self):
        return "<PYUS('%d','%d', '%s', '%d','%d','%s','%s','%s','%s','%s','%s','%s','%s','%s')>" % (
            self.gid,
            self.area_s,
            self.scavo_s,
            self.us_s,
            self.stratigraph_index_us,
            self.tipo_us_s,
            self.rilievo_originale,
            self.disegnatore,
            self.data,
            self.tipo_doc,
            self.nome_doc,
            self.coord,
            self.the_geom,
            self.unita_tipo_s
        )

