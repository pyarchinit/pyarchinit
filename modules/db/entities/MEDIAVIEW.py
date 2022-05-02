'''
Created on 15 feb 2018

@author:  Enzo Cocca <enzo.ccc@gmail.com>
'''



class MEDIAVIEW(object):
    #def __init__"
    def __init__(self,
    id_media_thumb,
    id_media,
    filepath,
    path_resize,
    entity_type,
    id_media_m,
    id_entity,
    
    ):
            self.id_media_thumb = id_media_thumb #0
            self.id_media = id_media
            self.filepath = filepath
            self.path_resize = path_resize
            self.entity_type = entity_type
            self.id_media_m = id_media_m
            self.id_entity = id_entity
            
            

    #def __repr__"
    def __repr__(self):
            return "<MEDIAVIEW('%d', '%d', '%s', '%s','%s', '%d','%d' )>" % (
            self.id_media_thumb,
            self.id_media,
            self.filepath,
            self.path_resize,
            self.entity_type,
            self.id_media_m,
            self.id_entity,
            
            )
