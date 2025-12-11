"""
Created on 2024
Pottery Embeddings Metadata Table Structure for Visual Similarity Search

@author: Enzo Cocca <enzo.ccc@gmail.com>
"""
from sqlalchemy import Table, Column, Integer, Text, MetaData, create_engine, UniqueConstraint, DateTime
from sqlalchemy.sql import func

from modules.db.pyarchinit_conn_strings import Connection


class Pottery_embeddings_metadata_table:
    """
    SQLAlchemy table definition for tracking pottery image embeddings.
    Used by the visual similarity search system.
    """

    # connection string
    internal_connection = Connection()

    # create engine and metadata
    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    metadata = MetaData(engine)

    # define table
    pottery_embeddings_metadata_table = Table('pottery_embeddings_metadata_table', metadata,
        Column('id_embedding', Integer, primary_key=True),
        Column('id_rep', Integer, nullable=False),          # FK to pottery_table.id_rep
        Column('id_media', Integer, nullable=False),        # FK to media_table.id_media
        Column('image_hash', Text, nullable=False),         # SHA256 hash for change detection
        Column('model_name', Text, nullable=False),         # 'clip', 'openai', 'dinov2'
        Column('search_type', Text, nullable=False),        # 'general', 'decoration', 'shape'
        Column('embedding_version', Text, default='1.0'),   # Version for model updates
        Column('created_at', DateTime, server_default=func.now()),
        # Unique constraint: one embedding per media/model/search_type combination
        UniqueConstraint('id_media', 'model_name', 'search_type', name='unique_embedding_config')
    )

    # DO NOT create tables at module import time!
    # metadata.create_all(engine)
