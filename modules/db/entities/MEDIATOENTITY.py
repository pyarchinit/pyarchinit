'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class MEDIATOENTITY(object):
    def __init__(self,
                 id_mediaToEntity,
                 id_entity,
                 entity_type,
                 table_name,
                 id_media,
                 filepath,
                 media_name
                 ):
        self.id_mediaToEntity = id_mediaToEntity  # 0
        self.id_entity = id_entity
        self.entity_type = entity_type
        self.table_name = table_name
        self.id_media = id_media
        self.filepath = filepath
        self.media_name = media_name

    def __repr__(self):
        return "<MEDIATOENTITY('%d', '%d', '%s', '%s', '%d', '%s', '%s')>" % (
            self.id_mediaToEntity,
            self.id_entity,
            self.entity_type,
            self.table_name,
            self.id_media,
            self.filepath,
            self.media_name
        )
