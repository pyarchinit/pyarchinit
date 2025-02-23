'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, Text, UniqueConstraint


# Table representing relationships between media files and archaeological entities
class Media_to_Entity_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('media_to_entity_table', metadata,
                     # Unique identifier for each media-entity relationship
                     Column('id_mediaToEntity', Integer, primary_key=True),

                     # ID of the related archaeological entity
                     Column('id_entity', Integer),

                     # Type of archaeological entity (e.g., US, Finds, Structures)
                     Column('entity_type', Text),

                     # Name of the database table containing the entity
                     Column('table_name', Text),

                     # ID of the related media file
                     Column('id_media', Integer),

                     # Path to the media file
                     Column('filepath', Text),

                     # Name of the media file
                     Column('media_name', Text),

                     # Unique constraint ensuring the combination of entity ID, entity type, and media ID is unique
                     UniqueConstraint('id_entity', 'entity_type', 'id_media',
                                      name='ID_mediaToEntity_unico')
                     )

