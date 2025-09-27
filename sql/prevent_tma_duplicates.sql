-- Prevent TMA duplicate records at database level
-- This script adds a unique constraint to prevent duplicate records

-- First, remove any existing duplicates (keeping the one with the lowest ID)
DELETE FROM tma_materiali_archeologici a
WHERE EXISTS (
    SELECT 1
    FROM tma_materiali_archeologici b
    WHERE a.sito = b.sito
    AND a.area = b.area
    AND a.inventario = b.inventario
    AND a.dscu = b.dscu
    AND a.id > b.id
    AND a.inventario IS NOT NULL
    AND a.inventario != ''
);

-- Add a unique constraint to prevent future duplicates
-- This constraint ensures that the combination of sito, area, inventario, and dscu is unique
-- We use a partial index to handle NULL values correctly
CREATE UNIQUE INDEX IF NOT EXISTS idx_tma_unique_record
ON tma_materiali_archeologici(sito, area, inventario, dscu)
WHERE inventario IS NOT NULL AND inventario != '';

-- Also add an index on created_at for performance when checking recent records
CREATE INDEX IF NOT EXISTS idx_tma_created_at
ON tma_materiali_archeologici(created_at);

-- Add a trigger to prevent rapid duplicate inserts (within 2 seconds)
CREATE OR REPLACE FUNCTION prevent_rapid_tma_insert()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if a similar record was inserted in the last 2 seconds
    IF EXISTS (
        SELECT 1
        FROM tma_materiali_archeologici
        WHERE sito = NEW.sito
        AND area = NEW.area
        AND (inventario = NEW.inventario OR dscu = NEW.dscu)
        AND created_at > NOW() - INTERVAL '2 seconds'
        AND id != COALESCE(NEW.id, -1)
    ) THEN
        RAISE EXCEPTION 'Un record simile è stato inserito di recente. Attendere prima di inserire di nuovo.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists and create new one
DROP TRIGGER IF EXISTS trig_prevent_rapid_tma_insert ON tma_materiali_archeologici;

CREATE TRIGGER trig_prevent_rapid_tma_insert
BEFORE INSERT ON tma_materiali_archeologici
FOR EACH ROW
EXECUTE FUNCTION prevent_rapid_tma_insert();

-- Update the created_at and updated_at triggers to use proper timestamps
CREATE OR REPLACE FUNCTION update_tma_timestamps()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        NEW.created_at = COALESCE(NEW.created_at, NOW());
        NEW.updated_at = NOW();
    ELSIF TG_OP = 'UPDATE' THEN
        NEW.updated_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop and recreate the timestamp trigger
DROP TRIGGER IF EXISTS trig_update_tma_timestamps ON tma_materiali_archeologici;

CREATE TRIGGER trig_update_tma_timestamps
BEFORE INSERT OR UPDATE ON tma_materiali_archeologici
FOR EACH ROW
EXECUTE FUNCTION update_tma_timestamps();