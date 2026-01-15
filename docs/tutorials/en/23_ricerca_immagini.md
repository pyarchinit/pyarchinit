# Tutorial 23: Image Search

## Introduction

The **Image Search** function allows you to quickly search for images in the PyArchInit database by filtering by site, entity type, and other criteria. It's a complementary tool to the Media Manager for global searching.

## Access

### From Menu
**PyArchInit** → **Image Search**

## Interface

### Search Panel

```
+--------------------------------------------------+
|           Image Search                            |
+--------------------------------------------------+
| Filters:                                          |
|   Site: [ComboBox]                               |
|   Entity Type: [-- All -- | SU | Pottery | ...]  |
|   [ ] Only untagged images                       |
+--------------------------------------------------+
| [Search]  [Clear]                                |
+--------------------------------------------------+
| Results:                                          |
|  +------+  +------+  +------+                    |
|  | img  |  | img  |  | img  |                    |
|  | info |  | info |  | info |                    |
|  +------+  +------+  +------+                    |
+--------------------------------------------------+
| [Open Image] [Export] [Go to Record]             |
+--------------------------------------------------+
```

### Available Filters

| Filter | Description |
|--------|-------------|
| Site | Select specific site or all |
| Entity Type | SU, Pottery, Materials, Grave, Structure, TU |
| Only untagged | Show only images without links |

### Entity Types

| Type | Description |
|------|-------------|
| -- All -- | All entities |
| SU | Stratigraphic Units |
| Pottery | Pottery |
| Materials | Finds/Inventory |
| Grave | Burials |
| Structure | Structures |
| TU | Topographic Units |

## Features

### Basic Search

1. Select desired filters
2. Click **"Search"**
3. View results in grid

### Actions on Results

| Button | Function |
|--------|----------|
| Open Image | View image at original size |
| Export | Export selected image |
| Go to Record | Open linked entity form |
| Open Media Manager | Open Media Manager with selected image |

### Context Menu (Right-click)

- **Open image**
- **Export image...**
- **Go to record**

### Untagged Image Search

**"Only untagged images"** checkbox:
- Finds images in database without links
- Useful for cleanup and organization
- Allows identifying images to catalog

## Typical Workflow

### 1. Find Site Images

```
1. Select site from ComboBox
2. Leave "-- All --" for entity type
3. Click Search
4. Browse results
```

### 2. Find Specific SU Images

```
1. Select site
2. Select "SU" as entity type
3. Click Search
4. Double-click to open image
```

### 3. Identify Uncatalogued Images

```
1. Select site (or all)
2. Enable "Only untagged images"
3. Click Search
4. For each result:
   - Open image
   - Identify content
   - Link via Media Manager
```

## Export

### Single Image Export

1. Select image in results
2. Click **"Export"** or context menu
3. Select destination
4. Save

### Multiple Export

For exporting multiple images, use the dedicated **Export Images** function (Tutorial 24).

## Best Practices

### 1. Efficient Search

- Use specific filters for targeted results
- Start with broad filters, then narrow down
- Use untagged search periodically

### 2. Organization

- Catalog untagged images regularly
- Verify links after import
- Maintain consistent naming

## Troubleshooting

### No Results

**Causes**:
- Filters too restrictive
- No images for criteria

**Solutions**:
- Broaden filters
- Verify data exists

### Image Not Viewable

**Causes**:
- File not found
- Unsupported format

**Solutions**:
- Verify file path
- Check image format

## References

### Source Files
- `tabs/Image_search.py` - Search interface
- `gui/ui/pyarchinit_image_search_dialog.ui` - UI layout

### Database
- `media_table` - Media data
- `media_to_entity_table` - Links

---

## Video Tutorial

### Image Search
`[Placeholder: video_ricerca_immagini.mp4]`

**Contents**:
- Using filters
- Advanced search
- Results export

**Expected duration**: 8-10 minutes

---

*Last updated: January 2026*
