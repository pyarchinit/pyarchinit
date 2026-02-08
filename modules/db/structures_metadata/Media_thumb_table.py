'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, String, Text,  UniqueConstraint


# Table representing thumbnails of media files
class Media_thumb_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('media_thumb_table', metadata,
                     # Unique identifier for each thumbnail record
                     Column('id_media_thumb', Integer, primary_key=True),

                     # Reference to the original media file ID
                     Column('id_media', Integer),

                     # Type of media (e.g., image, video)
                     Column('mediatype', Text),

                     # Original media filename
                     Column('media_filename', Text),

                     # Thumbnail filename
                     Column('media_thumb_filename', Text),

                     # File extension/type of the thumbnail
                     Column('filetype', String(10)),

                     # Path to the original media file
                     Column('filepath', Text),

                     # Path to the resized thumbnail file
                     Column('path_resize', Text),

                     # StratiGraph persistent identifier (UUID v4)
                     Column('entity_uuid', Text),

                     # Unique constraint ensuring the thumbnail filename is unique
                     UniqueConstraint('media_thumb_filename', name='ID_media_thumb_unico')
                     )

