-- Add missing concurrency columns to us_table
ALTER TABLE us_table
ADD COLUMN IF NOT EXISTS last_modified_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS last_modified_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Add similar columns to other tables if needed
ALTER TABLE tma_table
ADD COLUMN IF NOT EXISTS last_modified_by VARCHAR(100),
ADD COLUMN IF NOT EXISTS last_modified_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Update existing records with default values
UPDATE us_table
SET last_modified_by = 'system',
    last_modified_timestamp = CURRENT_TIMESTAMP
WHERE last_modified_by IS NULL;

UPDATE tma_table
SET last_modified_by = 'system',
    last_modified_timestamp = CURRENT_TIMESTAMP
WHERE last_modified_by IS NULL;