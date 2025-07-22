# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyArchInit is a QGIS plugin for archaeological data management. It provides comprehensive tools for managing excavations, finds, sites, and archaeological documentation within the QGIS GIS environment.

- **Language**: Python 3.x
- **Framework**: QGIS Plugin (>= 3.22)
- **Database Support**: PostgreSQL/PostGIS, SQLite/Spatialite
- **License**: GPL v2

## Key Commands

### Installation & Dependencies

```bash
# Install Python dependencies
python scripts/modules_installer.py

# Dependencies are listed in requirements.txt and include:
# - SQLAlchemy for database ORM
# - ReportLab for PDF generation
# - OpenCV for image processing
# - LangChain/OpenAI/Anthropic for AI features
```

### Development

Since this is a QGIS plugin, there are no traditional build/test commands. Development workflow:

1. Make changes to the plugin code
2. Reload the plugin in QGIS or restart QGIS
3. Test functionality through the QGIS interface

## Architecture Overview

### Core Structure

The plugin follows a Model-View-Controller pattern adapted for QGIS:

1. **Database Layer** (`modules/db/`)
   - `pyarchinit_db_manager.py`: Central database operations manager
   - `entities/`: SQLAlchemy entity classes for each archaeological record type
   - `structures/`: Database table definitions
   - Query methods support both PostgreSQL and SQLite with proper session management

2. **UI Layer** (`gui/` and `tabs/`)
   - `gui/ui/`: Qt Designer UI files defining forms
   - `tabs/`: Form controllers (e.g., `US_USM.py`, `Site.py`) that:
     - Load UI from .ui files
     - Handle user interactions
     - Manage record CRUD operations
     - Integrate with QGIS map canvas

3. **GIS Integration** (`modules/gis/`)
   - `pyarchinit_pyqgis.py`: Core QGIS integration handling layer creation and styling
   - Manages spatial data visualization on QGIS map
   - Handles layer styling with QML files

4. **Report Generation** (`modules/report/`)
   - PDF generation using ReportLab
   - Supports archaeological documentation standards
   - Integrates with AI for report analysis

### Key Architectural Patterns

- **Multi-Site Support**: The system supports multiple archaeological sites with proper data isolation
- **Session Management**: Database operations use SQLAlchemy sessions with proper cleanup
- **Internationalization**: Full i18n support with translations in IT, EN, DE, ES, FR, AR
- **Plugin Initialization**: Complex initialization in `__init__.py` handles:
  - Automatic dependency installation
  - Platform-specific setup (Windows/Mac/Linux)
  - Font installation for reports

### Critical Files to Understand

1. **`pyarchinit_Plugin.py`**: Main plugin entry point and menu initialization
2. **`modules/db/pyarchinit_db_manager.py`**: Central database operations
3. **`modules/gis/pyarchinit_pyqgis.py`**: QGIS layer management
4. **`tabs/pyarchinit_US_mainapp.py`**: Main application window controller

### Database Schema

The plugin manages archaeological data through multiple interconnected tables:
- `site_table`: Archaeological sites
- `us_table`/`us_table_usm`: Stratigraphic units
- `inventario_materiali_table`: Finds inventory
- `tomba_table`: Burial records
- `periodizzazione_table`: Period/phase definitions
- And many more specialized tables

Each table has corresponding:
- Entity class in `modules/db/entities/`
- Structure definition in `modules/db/structures/`
- UI form in `gui/ui/`
- Controller in `tabs/`

### AI Integration

Recent additions include LangChain integration for:
- Automated report generation
- Data analysis assistance
- Natural language queries to archaeological data

## Important Notes

- Always test database operations on both PostgreSQL and SQLite
- UI changes require editing both .ui files (Qt Designer) and corresponding Python controllers
- When modifying database schema, update both structure definitions and entity classes
- The plugin uses QGIS settings for configuration storage
- Report generation requires specific fonts (Cambria) installed on the system