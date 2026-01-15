# Tutorial 22: Media Manager

## Introduction

The **Media Manager** is PyArchInit's central tool for managing images and multimedia content associated with archaeological records. It allows linking photos, drawings, videos, and other media to SU, finds, graves, structures, and other entities.

### Main Features

- Centralized management of all media
- Linking to archaeological entities (SU, Finds, Pottery, Graves, Structures, TU)
- Thumbnail and full-size image viewing
- Tagging and categorization
- Advanced search
- GPT integration for image analysis

## Access

### From Menu
**PyArchInit** → **Media Manager**

### From Toolbar
**Media Manager** icon in PyArchInit toolbar

## Interface

### Main Panel

```
+----------------------------------------------------------+
|                    Media Manager                          |
+----------------------------------------------------------+
| Site: [ComboBox]  Area: [ComboBox]  SU: [ComboBox]       |
+----------------------------------------------------------+
| [Thumbnail Image Grid]                                    |
|  +------+  +------+  +------+  +------+                  |
|  | img1 |  | img2 |  | img3 |  | img4 |                  |
|  +------+  +------+  +------+  +------+                  |
|  +------+  +------+  +------+  +------+                  |
|  | img5 |  | img6 |  | img7 |  | img8 |                  |
|  +------+  +------+  +------+  +------+                  |
+----------------------------------------------------------+
| Tags: [Associated tag list]                               |
+----------------------------------------------------------+
| [Navigation] << < Record X of Y > >>                      |
+----------------------------------------------------------+
```

### Search Filters

| Field | Description |
|-------|-------------|
| Site | Filter by archaeological site |
| Area | Filter by excavation area |
| SU | Filter by Stratigraphic Unit |
| Structure Code | Filter by structure code |
| Structure No. | Filter by structure number |

### Thumbnail Controls

| Control | Function |
|---------|----------|
| Size slider | Adjust thumbnail size |
| Double-click | Open image at original size |
| Multiple selection | Ctrl+click to select multiple images |

## Media Management

### Adding New Images

1. Open Media Manager
2. Select destination site
3. Click **"New Record"** or use context menu
4. Select images to add
5. Fill in metadata

### Linking Media to Entities

1. Select image in grid
2. In Tags panel, select:
   - **Entity type**: SU, Find, Pottery, Grave, Structure, TU
   - **Identifier**: Entity number/code
3. Click **"Link"**

### Supported Entity Types

| Type | DB Table | Description |
|------|----------|-------------|
| SU | us_table | Stratigraphic Units |
| FIND | inventario_materiali_table | Finds/Materials |
| POTTERY | pottery_table | Pottery |
| GRAVE | tomba_table | Burials |
| STRUCTURE | struttura_table | Structures |
| TU | ut_table | Topographic Units |

### View Original Image

- **Double-click** on thumbnail
- Opens viewer with:
  - Zoom (mouse wheel)
  - Pan (dragging)
  - Rotation
  - Measurement

## Advanced Features

### Advanced Search

Media Manager supports search by:
- File name
- Entry date
- Linked entity
- Tags/categories

### GPT Integration

**"GPT Sketch"** button for:
- Automatic image analysis
- Description generation
- Classification suggestions

### Remote Loading

Support for images on remote servers:
- Direct URLs
- FTP servers
- Cloud storage

## Database

### Involved Tables

| Table | Description |
|-------|-------------|
| `media_table` | Media metadata |
| `media_thumb_table` | Thumbnails |
| `media_to_entity_table` | Entity links |

### Mapper Classes

- `MEDIA` - Main media entity
- `MEDIA_THUMB` - Thumbnails
- `MEDIATOENTITY` - Media-entity relationship

## Best Practices

### 1. File Organization

- Use descriptive file names
- Organize by site/area/year
- Keep original backups

### 2. Metadata

- Always fill in site and area
- Add meaningful descriptions
- Use consistent tags

### 3. Image Quality

- Minimum recommended resolution: 1920x1080
- Format: JPG for photos, PNG for drawings
- Moderate compression

### 4. Links

- Link each image to relevant entities
- Verify links after bulk import
- Use search for unlinked images

## Troubleshooting

### Thumbnails Not Displayed

**Causes**:
- Wrong image path
- Missing file
- Permission issues

**Solutions**:
- Verify path in database
- Check file existence
- Check folder permissions

### Image Cannot Be Linked

**Causes**:
- Entity doesn't exist
- Wrong entity type

**Solutions**:
- Verify record exists
- Check selected entity type

## References

### Source Files
- `tabs/Image_viewer.py` - Main interface
- `modules/utility/pyarchinit_media_utility.py` - Media utilities

### Database
- `media_table` - Media data
- `media_to_entity_table` - Links

---

## Video Tutorial

### Complete Media Manager
`[Placeholder: video_media_manager.mp4]`

**Contents**:
- Adding images
- Linking to entities
- Search and filters
- Advanced features

**Expected duration**: 15-18 minutes

---

*Last updated: January 2026*
