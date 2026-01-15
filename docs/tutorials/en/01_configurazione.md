# PyArchInit - Configuration Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Accessing Configuration](#accessing-configuration)
3. [Connection Parameters Tab](#connection-parameters-tab)
4. [DB Installation Tab](#db-installation-tab)
5. [Import Tools Tab](#import-tools-tab)
6. [Graphviz Tab](#graphviz-tab)
7. [PostgreSQL Tab](#postgresql-tab)
8. [Help Tab](#help-tab)
9. [FTP to Lizmap Tab](#ftp-to-lizmap-tab)

---

## Introduction

The PyArchInit configuration window allows you to set all the parameters necessary for the proper functioning of the plugin. Before starting to document an archaeological excavation, you need to correctly configure the database connection and resource paths.

> **Video Tutorial**: [Insert video link for configuration introduction]

---

## Accessing Configuration

To access the configuration:
1. Open QGIS
2. Menu **PyArchInit** → **Config**

Or from the PyArchInit toolbar click on the **Settings** icon.

![Accessing configuration](images/01_configurazione/01_menu_config.png)
*Figure 1: Accessing the configuration window from the PyArchInit menu*

![PyArchInit Toolbar](images/01_configurazione/02_toolbar_config.png)
*Figure 2: Configuration icon in the toolbar*

---

## Connection Parameters Tab

This is the main tab for configuring the database connection.

![Connection Parameters Tab](images/01_configurazione/03_tab_parametri_connessione.png)
*Figure 3: Connection Parameters Tab - Complete view*

### DB Settings Section

| Field | Description |
|-------|-------------|
| **Database** | Select the database type: `sqlite` (local) or `postgres` (server) |
| **Host** | PostgreSQL server address (e.g., `localhost` or server IP) |
| **DBname** | Database name (e.g., `pyarchinit`) |
| **Port** | Connection port (default: `5432` for PostgreSQL) |
| **User** | Username for connection |
| **Password** | User password |
| **SSL Mode** | SSL mode for PostgreSQL: `allow`, `prefer`, `require`, `disable` |

![DB Settings](images/01_configurazione/04_db_settings.png)
*Figure 4: DB Settings Section*

#### Database Choice

**SQLite/Spatialite** (Recommended for single user):
- Local database, no server required
- Ideal for individual or small projects
- The `.sqlite` file is saved in the `pyarchinit_DB_folder` folder

![SQLite Configuration](images/01_configurazione/05_config_sqlite.png)
*Figure 5: SQLite configuration example*

**PostgreSQL/PostGIS** (Recommended for teams):
- Server database, multi-user access
- Requires PostgreSQL with PostGIS extension installed
- Supports user management and permissions
- Ideal for large projects with multiple operators

![PostgreSQL Configuration](images/01_configurazione/06_config_postgres.png)
*Figure 6: PostgreSQL configuration example*

> **Video Tutorial**: [Insert video link for database configuration]

### Path Settings Section

| Field | Description | Button |
|-------|-------------|--------|
| **Thumbnail path** | Path to save image thumbnails | `...` to browse |
| **Image resize** | Path for resized images | `...` to browse |
| **Logo path** | Path to custom logo for reports | `...` to browse |

![Path Settings](images/01_configurazione/07_path_settings.png)
*Figure 7: Path Settings Section*

#### Supported Remote Paths

PyArchInit also supports remote storage:
- **Google Drive**: `gdrive://folder/path/`
- **Dropbox**: `dropbox://folder/path/`
- **Amazon S3**: `s3://bucket/path/`
- **Cloudinary**: `cloudinary://cloud_name/folder/`
- **WebDAV**: `webdav://server/path/`
- **HTTP/HTTPS**: `https://server/path/`

![Remote Storage](images/01_configurazione/08_remote_storage.png)
*Figure 8: Remote storage configuration example*

### Site Settings Section

| Field | Description |
|-------|-------------|
| **Site** | Default site name for new records |
| **Experimental features** | Enable experimental features (Yes/No) |

---

## DB Installation Tab

This tab allows you to install or upgrade the PyArchInit database.

![DB Installation Tab](images/01_configurazione/08_tab_installazione_db.png)
*Figure 8: DB Installation Tab*

### New Installation

1. Select **sqlite** or **postgres** as database type
2. Click **Connect**
3. If the database doesn't exist, click **Install Database**
4. The system will create all necessary tables

### Database Upgrade

For existing installations:
1. Click **Database Check/Update**
2. The system verifies the structure and applies any updates

> **Warning**: Always backup your database before upgrading!

---

## Import Tools Tab

Tools for importing data from external sources.

### CSV Import

1. Select the CSV file
2. Map columns to database fields
3. Click **Import**

### Shapefile Import

For importing GIS data directly into PyArchInit layers.

---

## Graphviz Tab

Graphviz configuration for generating Harris Matrix diagrams.

| Field | Description |
|-------|-------------|
| **Graphviz Path** | Path to Graphviz installation (e.g., `/usr/bin/` on Linux) |
| **Check Graphviz** | Verify Graphviz installation |

### Installing Graphviz

**Windows**: Download from [graphviz.org](https://graphviz.org/download/)

**macOS**: `brew install graphviz`

**Linux**: `sudo apt install graphviz`

---

## PostgreSQL Tab

Advanced PostgreSQL server settings.

| Field | Description |
|-------|-------------|
| **pg_dump path** | Path to pg_dump for backups |
| **psql path** | Path to psql command |

---

## Help Tab

Contains useful links and resources.

| Resource | Description |
|----------|-------------|
| Video Tutorial | Link to YouTube video tutorials |
| Online Documentation | https://pyarchinit.github.io/pyarchinit_doc/index.html |
| Facebook | UnaQuantum page |

---

## FTP to Lizmap Tab

Configuration for web publishing with Lizmap.

| Field | Description |
|-------|-------------|
| **FTP Host** | FTP server address |
| **FTP User** | FTP username |
| **FTP Password** | FTP password |
| **Remote Path** | Destination path on server |

---

## Troubleshooting

### Connection Failed

**Causes**:
- Incorrect credentials
- Server not running
- Firewall blocking connection

**Solutions**:
- Verify username and password
- Check if PostgreSQL service is running
- Check firewall rules

### Database Not Found

**Cause**: Database not yet installed

**Solution**: Go to DB Installation tab and click Install Database

---

## Best Practices

1. **Backup regularly**: Use the Backup & Restore function
2. **Use PostgreSQL for teams**: Better multi-user support
3. **Set correct paths**: Ensure all path settings point to valid directories
4. **Test connection**: Always verify connection before starting work

---

*Last updated: January 2026*
