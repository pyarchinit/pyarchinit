# Tutorial 19: Multi-user Work with PostgreSQL

## Introduction

PyArchInit supports **multi-user** work through the use of **PostgreSQL/PostGIS** as the database backend. This configuration allows multiple operators to work simultaneously on the same archaeological project from different workstations.

### Multi-user Advantages

| Aspect | SQLite | PostgreSQL Multi-user |
|--------|--------|----------------------|
| Simultaneous users | 1 | Unlimited |
| Remote access | No | Yes |
| Permission management | No | Yes |
| Centralized backup | Manual | Automatable |
| Performance | Good | Excellent |
| Scalability | Limited | High |

## Prerequisites

### PostgreSQL Server

1. **PostgreSQL** 12 or higher
2. **PostGIS** 3.0 or higher
3. Server accessible on network (LAN or Internet)

### Client

1. QGIS with PyArchInit installed
2. Network connection to server
3. Access credentials

## Server Configuration

### PostgreSQL Installation

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib postgis
```

#### Windows
- Download installer from [postgresql.org](https://www.postgresql.org/download/windows/)
- Install with Stack Builder for PostGIS

#### macOS
```bash
brew install postgresql postgis
brew services start postgresql
```

### Database Creation

```sql
-- Connect as superuser
sudo -u postgres psql

-- Create database
CREATE DATABASE pyarchinit_db;

-- Enable PostGIS
\c pyarchinit_db
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

-- Create application user
CREATE USER pyarchinit WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE pyarchinit_db TO pyarchinit;
```

### Network Access Configuration

Edit `pg_hba.conf`:
```
# Allow connections from local network
host    pyarchinit_db    pyarchinit    192.168.1.0/24    md5

# Or from any IP (less secure)
host    pyarchinit_db    pyarchinit    0.0.0.0/0    md5
```

Edit `postgresql.conf`:
```
listen_addresses = '*'
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## PyArchInit Client Configuration

### Initial Setup

1. **PyArchInit** → **Configuration**
2. **Database** tab
3. Select **PostgreSQL**
4. Fill in the fields:

| Field | Value |
|-------|-------|
| Server | IP address or hostname |
| Port | 5432 (default) |
| Database | pyarchinit_db |
| User | pyarchinit |
| Password | secure_password |

### Connection Test

1. Click **Test Connection**
2. Verify success message
3. Save configuration

### Schema Creation

If new database:
1. Click **Create Schema**
2. Wait for table creation
3. Verify structure

## User Management

### Creating Additional Users

```sql
-- User with full access
CREATE USER archaeologist1 WITH PASSWORD 'password1';
GRANT ALL ON ALL TABLES IN SCHEMA public TO archaeologist1;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO archaeologist1;

-- Read-only user
CREATE USER consultant1 WITH PASSWORD 'password2';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO consultant1;
```

### Suggested Access Levels

| Role | Permissions | Use |
|------|------------|-----|
| Admin | ALL | Configuration, management |
| Archaeologist | SELECT, INSERT, UPDATE, DELETE | Daily work |
| Specialist | SELECT, INSERT, UPDATE (specific tables) | Specialized data entry |
| Consultant | SELECT | Data consultation |
| Backup | SELECT | Backup scripts |

### Role Management

```sql
-- Create group role
CREATE ROLE archaeologists;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO archaeologists;

-- Assign users to group
GRANT archaeologists TO archaeologist1;
GRANT archaeologists TO archaeologist2;
```

## Multi-user Workflow

### Work Organization

#### By Area
- Assign different areas to different operators
- Avoid overlaps

#### By Type
- One operator: deposit SU
- Another operator: wall SU
- Another operator: Finds

#### By Site
- Different sites to different teams

### Conflict Management

#### Record Locking (recommended)
1. Before modifying, verify no one is working on the same record
2. Communicate with the team

#### Conflict Resolution
In case of concurrent modifications:
1. The last modification prevails
2. Verify data after each session
3. Use "modification date" field to track

### Synchronization

With PostgreSQL synchronization is automatic:
- Every modification is immediately visible to others
- No manual synchronization needed
- Refresh the form to see updates

## Backup and Security

### Automatic Backup

Daily backup script:
```bash
#!/bin/bash
# backup_pyarchinit.sh
DATE=$(date +%Y%m%d)
BACKUP_DIR=/var/backups/pyarchinit
pg_dump -U pyarchinit -h localhost pyarchinit_db > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

Schedule with cron:
```bash
# crontab -e
0 2 * * * /path/to/backup_pyarchinit.sh
```

### Restore

```bash
# Restore from backup
gunzip backup_20260114.sql.gz
psql -U pyarchinit -h localhost pyarchinit_db < backup_20260114.sql
```

### Security

1. **Strong passwords**: Minimum 12 characters, mix uppercase/lowercase/numbers
2. **SSL connections**: Enable SSL for remote connections
3. **Firewall**: Limit access to port 5432
4. **Updates**: Keep PostgreSQL updated
5. **Audit log**: Enable connection logging

### SSL for Remote Connections

In `postgresql.conf`:
```
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
```

In `pg_hba.conf`:
```
hostssl    pyarchinit_db    pyarchinit    0.0.0.0/0    md5
```

## Monitoring

### Active Connections

```sql
SELECT
    usename,
    client_addr,
    state,
    query_start,
    query
FROM pg_stat_activity
WHERE datname = 'pyarchinit_db';
```

### Database Size

```sql
SELECT pg_size_pretty(pg_database_size('pyarchinit_db'));
```

### Active Locks

```sql
SELECT
    l.locktype,
    l.relation::regclass,
    l.mode,
    l.granted,
    a.usename,
    a.query
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE l.database = (SELECT oid FROM pg_database WHERE datname = 'pyarchinit_db');
```

## Migration from SQLite

### Export from SQLite

1. Open PyArchInit with SQLite database
2. **PyArchInit** → **Utilities** → **Export Database**
3. Export in SQL format

### Import to PostgreSQL

1. Configure PostgreSQL connection
2. Create empty schema
3. Import exported data

### Migration Script

```python
# Conceptual example
# Use specific migration tools
from sqlalchemy import create_engine

sqlite_engine = create_engine('sqlite:///pyarchinit.db')
pg_engine = create_engine('postgresql://user:pass@server/pyarchinit_db')

# Copy tables
for table in tables:
    data = sqlite_engine.execute(f"SELECT * FROM {table}")
    pg_engine.execute(f"INSERT INTO {table} VALUES ...")
```

## Best Practices

### 1. Planning

- Define roles and responsibilities
- Establish work conventions
- Document procedures

### 2. Communication

- Team communication channel (chat, email)
- Signal start/end of work sessions
- Communicate areas being modified

### 3. Backup

- Daily automatic backups
- Periodic restore testing
- Off-site backup

### 4. Training

- Training on multi-user workflow
- Procedure documentation
- Technical support available

## Troubleshooting

### Connection Refused

**Causes**:
- Server unreachable
- Blocking firewall
- Wrong credentials

**Solutions**:
- Verify network connectivity
- Check firewall rules
- Verify credentials

### Connection Timeout

**Causes**:
- Slow network
- Overloaded server
- Too many connections

**Solutions**:
- Optimize network
- Increase server resources
- Limit simultaneous connections

### Database Lock

**Cause**: Uncompleted transactions

**Solution**:
```sql
-- Identify blocking processes
SELECT * FROM pg_locks WHERE NOT granted;

-- Terminate process (with caution)
SELECT pg_terminate_backend(pid);
```

## References

### Configuration
- `modules/db/pyarchinit_conn_strings.py` - Connection strings
- `gui/pyarchinit_Setting.py` - Configuration interface

### External Documentation
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PostGIS Documentation](https://postgis.net/documentation/)

---

## Video Tutorial

### Multi-user Setup
`[Placeholder: video_multiutente_setup.mp4]`

**Contents**:
- PostgreSQL installation
- Server configuration
- Client setup
- User management

**Expected duration**: 20-25 minutes

### Collaborative Workflow
`[Placeholder: video_multiutente_workflow.mp4]`

**Contents**:
- Work organization
- Conflict management
- Best practices

**Expected duration**: 12-15 minutes

---

*Last updated: January 2026*

---

## Interactive Animation

Explore the interactive animation to learn more about this topic.

[Open Interactive Animation](../../animations/pyarchinit_concurrency_animation.html)
