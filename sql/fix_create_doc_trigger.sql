-- Fix create_doc trigger to handle permission issues properly
-- This trigger updates d_interpretativa field for related DOC records
-- It now properly handles INSERT vs UPDATE and permission errors

-- Drop existing trigger if exists
DROP TRIGGER IF EXISTS create_doc ON us_table;
DROP FUNCTION IF EXISTS create_doc();

-- Create improved function that handles permissions
CREATE OR REPLACE FUNCTION public.create_doc()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
BEGIN
    -- Only perform UPDATE if this is an UPDATE operation (not INSERT)
    -- and only if the user has UPDATE permission
    IF TG_OP = 'UPDATE' THEN
        -- Check if d_interpretativa has changed
        IF (NEW.d_interpretativa IS DISTINCT FROM OLD.d_interpretativa) THEN
            -- Try to update related DOC records
            -- This will fail if user doesn't have UPDATE permission, which is ok
            BEGIN
                UPDATE us_table
                SET d_interpretativa = NEW.doc_usv
                WHERE sito = NEW.sito
                  AND area = NEW.area
                  AND us = NEW.us
                  AND unita_tipo = 'DOC';
            EXCEPTION
                WHEN insufficient_privilege THEN
                    -- User doesn't have UPDATE permission, skip this operation
                    NULL;
                WHEN OTHERS THEN
                    -- Ignore other errors too
                    NULL;
            END;
        END IF;
    ELSIF TG_OP = 'INSERT' THEN
        -- For INSERT operations, only update if d_interpretativa is empty
        IF (NEW.d_interpretativa IS NULL OR NEW.d_interpretativa = '') THEN
            -- Try to update, but ignore if user lacks permissions
            BEGIN
                UPDATE us_table
                SET d_interpretativa = NEW.doc_usv
                WHERE sito = NEW.sito
                  AND area = NEW.area
                  AND us = NEW.us
                  AND unita_tipo = 'DOC';
            EXCEPTION
                WHEN insufficient_privilege THEN
                    -- User doesn't have UPDATE permission, skip this operation
                    NULL;
                WHEN OTHERS THEN
                    -- Ignore other errors too
                    NULL;
            END;
        END IF;
    END IF;

    RETURN NEW;
END;
$BODY$;

ALTER FUNCTION public.create_doc()
    OWNER TO postgres;

COMMENT ON FUNCTION public.create_doc()
    IS 'Updates d_interpretativa field for related DOC records with proper permission handling';

-- Create trigger
CREATE TRIGGER create_doc
    AFTER INSERT OR UPDATE ON us_table
    FOR EACH ROW
    EXECUTE FUNCTION public.create_doc();