-- Create pyarchinit_access_log table if not exists
CREATE TABLE IF NOT EXISTS pyarchinit_access_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    username VARCHAR(100),
    action VARCHAR(50),
    table_accessed VARCHAR(100),
    record_id INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    ip_address VARCHAR(45),
    session_id VARCHAR(100)
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_access_log_timestamp ON pyarchinit_access_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_access_log_username ON pyarchinit_access_log(username);
CREATE INDEX IF NOT EXISTS idx_access_log_table ON pyarchinit_access_log(table_accessed);