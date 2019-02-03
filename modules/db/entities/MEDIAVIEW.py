'''
Created on 22 gennaio 2019

@author: enzo cocca
'''


class MEDIAVIEW(object):
    #def __init__"
    def __init__(self,
    id_media_thumb,
    id_media,
    filepath,
    entity_type,
    id_media_m,
    id_entity,
    path_resize,
    ):
            self.id_media_thumb = id_media_thumb #0
            self.id_media = id_media
            self.filepath = filepath
            self.entity_type = entity_type
            self.id_media_m = id_media_m
            self.id_entity = id_entity
            self.path_resize = path_resize
            

    #def __repr__"
    def __repr__(self):
            return "<MEDIAVIEW('%d', '%d', '%s', '%s','%d', '%d','%s' )>" % (
            self.id_media_thumb,
            self.id_media,
            self.filepath,
            self.path_resize,
            self.entity_type,
            self.id_media_m,
            self.id_entity
            )
