'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class MEDIA_THUMB(object):
    # def __init__"
    def __init__(self,
                 id_media_thumb,
                 id_media,
                 mediatype,
                 media_filename,
                 media_thumb_filename,
                 filetype,
                 filepath,
                 path_resize
                 ):
        self.id_media_thumb = id_media_thumb  # 0
        self.id_media = id_media  # 1
        self.mediatype = mediatype  # 2
        self.media_filename = media_filename  # 3
        self.media_thumb_filename = media_thumb_filename  # 4
        self.filetype = filetype  # 5
        self.filepath = filepath  # 6
        self.path_resize = path_resize
    # def __repr__"
    def __repr__(self):
        return "<MEDIA_THUMB('%d', '%d', '%s', '%s', %s, '%s', '%s','%s')>" % (
            self.id_media_thumb,
            self.id_media,
            self.mediatype,
            self.media_filename,
            self.media_thumb_filename,
            self.filetype,
            self.filepath,
            self.path_resize
        )
