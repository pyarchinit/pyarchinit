CREATE VIEW IF NOT EXISTS "mediaentity_view" AS
 SELECT media_thumb_table.id_media_thumb,
    media_thumb_table.id_media,
    media_thumb_table.filepath,
	media_thumb_table.path_resize,
    media_to_entity_table.entity_type,
    media_to_entity_table.id_media AS id_media_m,
    media_to_entity_table.id_entity
   FROM media_thumb_table
     JOIN media_to_entity_table ON (media_thumb_table.id_media = media_to_entity_table.id_media)
  ORDER BY media_to_entity_table.id_entity;