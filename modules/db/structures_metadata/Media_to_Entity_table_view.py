'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, Text


# View table representing relationships between media thumbnails and archaeological entities
class Media_to_Entity_table_view:
    @classmethod
    def define_table(self, metadata):
        return Table('mediaentity_view', metadata,
                     # Unique identifier for each media thumbnail
                     Column('id_media_thumb', Integer, primary_key=True),

                     # ID of the original media file
                     Column('id_media', Integer),

                     # Path to the original media file
                     Column('filepath', Text),

                     # Path to the resized thumbnail
                     Column('path_resize', Text),

                     # Type of archaeological entity (e.g., US, Finds, Structures)
                     Column('entity_type', Text),

                     # Secondary media ID reference
                     Column('id_media_m', Integer),

                     # ID of the related archaeological entity
                     Column('id_entity', Integer)
                     )

