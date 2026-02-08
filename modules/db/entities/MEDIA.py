'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
import uuid


class MEDIA(object):
    # def __init__"
    def __init__(self,
                 id_media,
                 mediatype,
                 filename,
                 filetype,
                 filepath,
                 descrizione,
                 tags,
                 entity_uuid=None
                 ):
        self.id_media = id_media  # 0
        self.mediatype = mediatype  # 1
        self.filename = filename  # 2
        self.filetype = filetype  # 3
        self.filepath = filepath  # 4
        self.descrizione = descrizione  # 5
        self.tags = tags  # 5
        self.entity_uuid = entity_uuid if entity_uuid else str(uuid.uuid4())

    # def __repr__"
    def __repr__(self):
        return "<MEDIA('%d', '%s', '%s', %s, '%s','%s')>" % (
            self.id_media,
            self.mediatype,
            self.filename,
            self.filetype,
            self.filepath,
            self.descrizione,
            self.tags
        )
