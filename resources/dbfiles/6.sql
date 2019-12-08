CREATE TRIGGER IF NOT EXISTS delete_media_table 
After delete 
ON media_thumb_table 

BEGIN 
DELETE from media_table 
where id_media = OLD.id_media ; 
END; 