'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class PYREPERTI(object):
    # def __init__"
    def __init__(self,
                id,
                id_rep ,
                siti ,
                link ,
                the_geom
                ):
        self.id=id
        self.id_rep=id_rep
        self.siti=siti
        self.link=link
        self.the_geom=the_geom
    # def __repr__"
    @property
    def __repr__(self):
        return "<PYREPERTI('%d','%s', '%s', '%s', '%s')>" % (
            self.id,
            self.id_rep,
            self.siti,
            self.link,
            self.the_geom)
