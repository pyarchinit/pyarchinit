# ![](icon.png) PyArchInit 5.0 - Qt6/PyQt6 Edition

[![GitHub release](https://img.shields.io/github/release/pyarchinit/pyarchinit.svg?style=flat-square)](https://github.com/pyarchinit/pyarchinit)
[![GitHub repo size in bytes](https://img.shields.io/github/repo-size/pyarchinit/pyarchinit.svg?style=flat-square)](https://github.com/pyarchinit/pyarchinit)
[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)

**PyArchInit** is a comprehensive QGIS plugin for archaeological data management, providing tools for excavation documentation, finds management, stratigraphic analysis, and GIS integration.

## What's New in Version 5.0

This major release brings full compatibility with modern QGIS versions and includes significant technical improvements:

### Qt6/PyQt6 Migration
- Full compatibility with **QGIS 3.34+** (Qt6/PyQt6)
- Updated all Qt enums to use proper Qt6 syntax (e.g., `Qt.ItemFlag.ItemIsEnabled`)
- Migrated all UI files to Qt6 format
- Backward compatible with Qt5-based QGIS versions

### SQLAlchemy 2.0 Compatibility
- Updated ORM mappings using `registry()` and `@registry.mapped` decorators
- Removed deprecated `declarative_base()` usage
- Improved session management and connection handling

### Security Improvements
- Replaced dangerous `eval()` calls with safe `getattr()` alternatives
- Improved input validation across all forms
- Safe locale handling to prevent crashes

### Database Improvements
- Enhanced PostgreSQL/PostGIS support with proper SSL handling
- Improved SQLite/Spatialite support with automatic extension loading on macOS
- Better concurrency management for multi-user environments

### Internationalization
- Full support for: Italian, English, German, French, Spanish, Arabic (Lebanon), Catalan
- Improved translation loading system
- Fixed language detection for all supported locales

## Requirements

### QGIS Version
- **Recommended:** QGIS >= 3.34 (Qt6/PyQt6)
- **Minimum:** QGIS >= 3.22 (Qt5/PyQt5)

### Database
- **PostgreSQL** >= 12 with PostGIS extension (recommended for multi-user)
- **SQLite** with Spatialite extension (for single-user/portable)

### Python Dependencies
Core dependencies are automatically installed on first run:
- SQLAlchemy >= 2.0
- reportlab
- matplotlib
- networkx
- graphviz
- pdf2docx
- opencv-python (optional, for image processing)
- openai/anthropic (optional, for AI features)

## Installation

### From QGIS Plugin Repository (Recommended)
1. Open QGIS
2. Go to **Plugins > Manage and Install Plugins**
3. Search for "pyArchInit"
4. Click **Install**

### From ZIP
1. Download the latest release from GitHub
2. In QGIS: **Plugins > Manage and Install Plugins > Install from ZIP**
3. Select the downloaded ZIP file

### From Repository URL (Development/Beta versions)
Add this URL in QGIS Plugin Manager settings to get the latest development versions:
```
https://raw.githubusercontent.com/enzococca/pyarchinit-repo/main/plugins.xml
```

### From Official Repository URL
For stable releases, you can also use:
```
http://pyarchinit.org/pyarchinit_repository
```

## Platform-Specific Notes

### macOS
- **Fonts:** Cambria font required for PDF reports. The plugin will prompt for installation on first run.
- **Spatialite:** Install via Homebrew: `brew install libspatialite`
- **Graphviz:** Install via Homebrew: `brew install graphviz`

### Windows
- **Graphviz:** Download and install from [graphviz.org](https://www.graphviz.org/download/)
- All other dependencies are installed automatically

### Linux
- **Spatialite:** `sudo apt install libsqlite3-mod-spatialite`
- **Graphviz:** `sudo apt install graphviz`

## Features

### Data Management Forms
- **Site Management** - Archaeological sites and projects
- **Stratigraphic Units (US/USM)** - Detailed stratigraphic recording
- **Finds Inventory** - Artifact cataloging and management
- **Structures** - Architectural features documentation
- **Burials/Tombs** - Funerary archaeology records
- **Samples** - Environmental and scientific samples
- **Pottery Analysis** - Ceramic typology and quantification
- **Periodization** - Chronological phase management
- **Documentation** - Photo, drawing, and document management

### GIS Integration
- Automatic layer creation and styling
- Spatial queries and analysis
- Map production and printing
- Harris Matrix generation

### Reporting
- PDF report generation for all record types
- Customizable templates
- Multi-language support
- Photo integration with thumbnails

### AI Features (Optional)
- GPT-powered data entry assistance
- Automated description generation
- Natural language database queries

## Project Structure

```
pyarchinit/
├── gui/                    # UI dialogs and forms
│   └── ui/                 # Qt Designer UI files
├── modules/
│   ├── db/                 # Database layer (SQLAlchemy)
│   │   ├── entities/       # ORM entity classes
│   │   └── structures/     # Table definitions
│   ├── gis/                # QGIS/GIS integration
│   └── utility/            # Utilities and PDF generation
├── tabs/                   # Form controllers
├── i18n/                   # Translations
├── resources/              # Icons and static files
└── scripts/                # Utility scripts
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests and ensure compatibility
5. Submit a pull request

## Authors

- **Luca Mandolesi** - Original author
- **Enzo Cocca** - Lead developer and maintainer

## License

This project is licensed under the GNU General Public License v2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

PyArchInit is used by numerous archaeological projects worldwide, including:
- Ludwig Maximilian Universität München
- Parco Archeologico Paestum - Ministero della Cultura
- Università di Salerno - Dipartimento di Archeologia
- Università di Pisa
- Università di Chieti
- adArte S.r.l. (150+ excavation contexts)
- Maasser el-Shouf Archaeological Project (Lebanon)
- And many more...

## Support

- **Documentation:** [Wiki](https://github.com/pyarchinit/pyarchinit/wiki)
- **Issues:** [GitHub Issues](https://github.com/pyarchinit/pyarchinit/issues)
- **Website:** [pyarchinit.org](http://pyarchinit.org)

---
*PyArchInit - Archaeological GIS Tools for QGIS*
