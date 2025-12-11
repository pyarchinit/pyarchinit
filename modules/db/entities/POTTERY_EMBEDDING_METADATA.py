"""
Created on 2024
Pottery Embedding Metadata Entity for Visual Similarity Search

@author: Enzo Cocca <enzo.ccc@gmail.com>
"""


class POTTERY_EMBEDDING_METADATA(object):
    """
    Entity class for tracking pottery image embeddings.
    Used by the visual similarity search system to track which images
    have been indexed for each model and search type.
    """

    def __init__(self,
                 id_embedding,          # Primary key
                 id_rep,                # FK to pottery_table.id_rep
                 id_media,              # FK to media_table.id_media
                 image_hash,            # SHA256 hash of image file
                 model_name,            # 'clip', 'openai', 'dinov2'
                 search_type,           # 'general', 'decoration', 'shape'
                 embedding_version,     # Version string for model updates
                 created_at             # Timestamp of embedding creation
                 ):
        self.id_embedding = id_embedding
        self.id_rep = id_rep
        self.id_media = id_media
        self.image_hash = image_hash
        self.model_name = model_name
        self.search_type = search_type
        self.embedding_version = embedding_version
        self.created_at = created_at

    def __repr__(self):
        return "<POTTERY_EMBEDDING_METADATA('%d', '%d', '%d', '%s', '%s', '%s', '%s', '%s')>" % (
            self.id_embedding,
            self.id_rep,
            self.id_media,
            self.image_hash,
            self.model_name,
            self.search_type,
            self.embedding_version,
            self.created_at
        )

    @property
    def as_dict(self):
        """Return entity as dictionary"""
        return {
            'id_embedding': self.id_embedding,
            'id_rep': self.id_rep,
            'id_media': self.id_media,
            'image_hash': self.image_hash,
            'model_name': self.model_name,
            'search_type': self.search_type,
            'embedding_version': self.embedding_version,
            'created_at': self.created_at
        }
