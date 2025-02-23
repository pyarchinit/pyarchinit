'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, String, Text, UniqueConstraint


# Table representing media files associated with archaeological records
class Media_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('media_table', metadata,
                     # Unique identifier for each media record
                     Column('id_media', Integer, primary_key=True),

                     # Type of media (e.g., image, video, document)
                     Column('mediatype', Text),

                     # Name of the media file
                     Column('filename', Text),

                     # File extension/type (e.g., jpg, pdf, mp4)
                     Column('filetype', String(10)),

                     # Complete path to the media file
                     Column('filepath', Text),

                     # Description of the media content
                     Column('descrizione', Text),

                     # Keywords/tags for searching and categorizing media
                     Column('tags', Text),

                     # Unique constraint ensuring the filepath is unique
                     UniqueConstraint('filepath', name='ID_media_unico')
                     )

