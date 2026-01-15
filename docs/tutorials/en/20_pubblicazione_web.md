# Tutorial 20: Web Publishing with Lizmap

## Introduction

PyArchInit supports **web publishing** of archaeological data through **Lizmap**, an application that allows transforming QGIS projects into interactive web applications.

### What is Lizmap?

Lizmap consists of:
- **QGIS Plugin**: To configure publishing
- **Lizmap Web Client**: Web application to view maps
- **QGIS Server**: Backend to serve maps

### Web Publishing Advantages

| Aspect | Description |
|--------|-------------|
| Accessibility | Data accessible from browser |
| Sharing | Easy distribution to stakeholders |
| Interactivity | Zoom, pan, query, popup |
| Updating | Synchronization with database |
| Mobile | Access from smartphone/tablet |

## Prerequisites

### Server

1. **QGIS Server** installed
2. **Lizmap Web Client** configured
3. Web server (Apache/Nginx)
4. PHP 7.4+
5. PostgreSQL/PostGIS (recommended)

### Client

1. **QGIS Desktop** with Lizmap plugin
2. **PyArchInit** configured
3. QGIS project saved

## Lizmap Plugin Installation

### From QGIS

1. **Plugins** → **Manage Plugins**
2. Search for "Lizmap"
3. Install **Lizmap**
4. Restart QGIS

## Project Preparation

### 1. Layer Organization

Recommended structure:
```
QGIS Project
├── Group: Base
│   ├── Orthophoto
│   └── CTR/Cadastral
├── Group: Excavation
│   ├── pyunitastratigrafiche
│   ├── pyunitastratigrafiche_usm
│   └── pyarchinit_quote
├── Group: Documentation
│   ├── Georeferenced photos
│   └── Surveys
└── Group: Analysis
    └── Harris Matrix (image)
```

### 2. Layer Styling

For each layer:
1. Apply appropriate style
2. Configure labels
3. Set scale visibility

### 3. Popups and Attributes

Configure popups for each layer:
1. Right-click on layer → **Properties**
2. **Display** tab
3. Configure **HTML Map Tip**

Example SU popup:
```html
<h3>SU [% "us_s" %]</h3>
<p><b>Area:</b> [% "area_s" %]</p>
<p><b>Type:</b> [% "tipo_us_s" %]</p>
<p><b>Definition:</b> [% "definizione" %]</p>
```

### 4. Project Saving

1. Save the project (.qgz) in the Lizmap folder
2. Use relative paths for data
3. Verify all layers are accessible

## Lizmap Configuration

### Opening Plugin

1. **Web** → **Lizmap** → **Lizmap**

### General Tab

| Field | Description | Value |
|-------|-------------|-------|
| Map title | Displayed name | "Via Roma Excavation" |
| Abstract | Description | "Archaeological documentation..." |
| Image | Project thumbnail | project_thumb.png |
| Repository | Server folder | /var/www/lizmap/projects |

### Layer Tab

For each layer configure:

| Option | Description |
|--------|-------------|
| Enabled | Layer visible in Lizmap |
| Base layer | Background layer (orthophoto, etc.) |
| Popup | Enable popup on click |
| Editing | Allow online editing |
| Filter | User filters |

### Basemap Tab

Configure backgrounds:
- OpenStreetMap
- Google Maps (requires API key)
- Bing Maps
- Custom orthophoto

### Locate Tab

Location search:
- Configure layers for search
- Fields to search
- Display format

### Editing Tab (Optional)

To allow online editing:
1. Select editable layers
2. Configure editable fields
3. Set permissions

### Tools Tab

Enable/disable:
- Print
- Measurements
- Selection
- Permalink
- etc.

### Save Configuration

Click **Save** to generate the `.qgs.cfg` file

## Publishing

### Upload to Server

1. Copy `.qgz` and `.qgz.cfg` files to server
2. Verify file permissions
3. Configure QGIS Server

### Server Structure

```
/var/www/lizmap/
├── lizmap/           # Lizmap application
├── projects/         # QGIS projects
│   ├── scavo_roma.qgz
│   └── scavo_roma.qgz.cfg
└── var/              # Application data
```

### QGIS Server Configuration

File `/etc/apache2/sites-available/lizmap.conf`:
```apache
<VirtualHost *:80>
    ServerName lizmap.example.com
    DocumentRoot /var/www/lizmap/lizmap/www

    <Directory /var/www/lizmap/lizmap/www>
        AllowOverride All
        Require all granted
    </Directory>

    # QGIS Server
    ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
    <Directory "/usr/lib/cgi-bin">
        AllowOverride All
        Require all granted
    </Directory>

    FcgidInitialEnv QGIS_SERVER_LOG_FILE /var/log/qgis/qgis_server.log
    FcgidInitialEnv QGIS_SERVER_LOG_LEVEL 0
</VirtualHost>
```

## Web Access

### Application URL

```
http://lizmap.example.com/
```

### Navigation

1. Project selection from home
2. Interactive map view
3. Tools in toolbar

### User Features

| Function | Description |
|----------|-------------|
| Zoom | Mouse wheel, +/- buttons |
| Pan | Map dragging |
| Popup | Click on feature |
| Search | Search bar |
| Print | Export to PDF |
| Permalink | Shareable URL |

## PyArchInit Integration

### Real-time Data

With PostgreSQL:
- Data is always up to date
- Changes in PyArchInit visible immediately
- No manual synchronization

### Recommended Layers

| PyArchInit Layer | Publishing |
|------------------|------------|
| pyunitastratigrafiche | Yes, with popup |
| pyunitastratigrafiche_usm | Yes, with popup |
| pyarchinit_quote | Yes |
| pyarchinit_siti | Yes, as overview |
| Harris Matrix | As static image |

### Advanced SU Popup Configuration

Advanced HTML template:
```html
<div class="us-popup">
    <h3 style="color:#2c3e50;">SU [% "us_s" %]</h3>
    <table>
        <tr><td><b>Site:</b></td><td>[% "scavo_s" %]</td></tr>
        <tr><td><b>Area:</b></td><td>[% "area_s" %]</td></tr>
        <tr><td><b>Type:</b></td><td>[% "tipo_us_s" %]</td></tr>
        <tr><td><b>Definition:</b></td><td>[% "definizione" %]</td></tr>
        <tr><td><b>Period:</b></td><td>[% "periodo" %]</td></tr>
    </table>
    [% if "foto_url" %]
    <img src="[% "foto_url" %]" style="max-width:200px;"/>
    [% end %]
</div>
```

## Security

### Authentication

Lizmap supports:
- Local users
- LDAP
- OAuth2

### User Configuration

In Lizmap admin:
1. Create groups (admin, archaeologist, public)
2. Create users
3. Assign permissions per project

### Layer Permissions

| Group | View | Edit | Print |
|-------|------|------|-------|
| Admin | All | All | Yes |
| Archaeologist | All | Some | Yes |
| Public | Base only | No | No |

## Maintenance

### Project Updates

1. Edit project in QGIS Desktop
2. Regenerate Lizmap configuration
3. Upload to server

### Cache

Tile cache management:
```bash
# Clear cache
lizmap-cache-clearer.php -project scavo_roma

# Regenerate tiles
lizmap-tiles-seeder.php -project scavo_roma -bbox xmin,ymin,xmax,ymax
```

### Logging and Debug

```bash
# QGIS Server log
tail -f /var/log/qgis/qgis_server.log

# Lizmap log
tail -f /var/www/lizmap/var/log/messages.log
```

## Best Practices

### 1. Performance Optimization

- Use pre-tiled raster layers
- Limit number of features per layer
- Configure scale visibility
- Use spatial indexes

### 2. User Experience

- Informative but concise popups
- Clear and readable styles
- Logical layer organization
- User documentation

### 3. Security

- HTTPS required
- Regular updates
- Configuration backups
- Access monitoring

### 4. Backup

- Backup `.qgz` and `.cfg` files
- Backup PostgreSQL database
- Version configurations

## Troubleshooting

### Map Not Displayed

**Causes**:
- QGIS Server not configured
- Wrong file paths
- Insufficient permissions

**Solutions**:
- Check QGIS Server log
- Verify paths in project
- Check file permissions

### Popups Not Working

**Causes**:
- Layer not configured for popup
- Incorrect HTML in template

**Solutions**:
- Enable popup in Lizmap
- Verify HTML syntax

### Slow Performance

**Causes**:
- Too much data
- Cache not configured
- Undersized server

**Solutions**:
- Reduce visible data
- Configure tile cache
- Increase server resources

## References

### Software
- [Lizmap](https://www.lizmap.com/)
- [QGIS Server](https://docs.qgis.org/latest/en/docs/server_manual/)

### Documentation
- [Lizmap Documentation](https://docs.lizmap.com/)
- [QGIS Server Documentation](https://docs.qgis.org/latest/en/docs/server_manual/)

---

## Video Tutorial

### Lizmap Setup
`[Placeholder: video_lizmap_setup.mp4]`

**Contents**:
- Plugin installation
- Project configuration
- Publishing

**Expected duration**: 20-25 minutes

### Web Customization
`[Placeholder: video_lizmap_custom.mp4]`

**Contents**:
- Advanced popups
- Custom styles
- User management

**Expected duration**: 15-18 minutes

---

*Last updated: January 2026*
