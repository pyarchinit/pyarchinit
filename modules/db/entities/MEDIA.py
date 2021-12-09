'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class MEDIA(object):
    # def __init__"
    def __init__(self,
                 id_media,
                 mediatype,
                 filename,
                 filetype,
                 filepath,
                 descrizione,
                 tags
                 ):
        self.id_media = id_media  # 0
        self.mediatype = mediatype  # 1
        self.filename = filename  # 2
        self.filetype = filetype  # 3
        self.filepath = filepath  # 4
        self.descrizione = descrizione  # 5
        self.tags = tags  # 5

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
