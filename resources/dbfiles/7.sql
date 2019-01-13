CREATE TRIGGER IF NOT EXISTS media_entity_delete 
After delete 
ON media_thumb_table 

BEGIN 
DELETE from media_to_entity_table 
where id_media = OLD.id_media ; 
END;
