# Tutorial 24: Export Images

## Introduction

The **Export Images** function allows bulk export of images associated with archaeological records, automatically organizing them into folders by period, phase, and entity type.

## Access

### From Menu
**PyArchInit** → **Export Images**

## Interface

### Export Panel

```
+--------------------------------------------------+
|           Export Images                           |
+--------------------------------------------------+
| Site: [ComboBox site selection]                  |
| Year: [ComboBox excavation year]                 |
+--------------------------------------------------+
| Export Type:                                      |
|   [o] All images                                 |
|   [ ] SU only                                    |
|   [ ] Finds only                                 |
|   [ ] Pottery only                               |
+--------------------------------------------------+
| [Open Folder]           [Export]                 |
+--------------------------------------------------+
```

### Export Options

| Option | Description |
|--------|-------------|
| All images | Export all photographic material |
| SU only | Export only SU-linked images |
| Finds only | Export only find images |
| Pottery only | Export only pottery images |

## Output Structure

### Folder Organization

The export creates a hierarchical structure:

```
pyarchinit_image_export/
└── [Site Name] - All images/
    ├── Period - 1/
    │   ├── Phase - 1/
    │   │   ├── SU_001/
    │   │   │   ├── photo_001.jpg
    │   │   │   └── photo_002.jpg
    │   │   └── SU_002/
    │   │       └── photo_003.jpg
    │   └── Phase - 2/
    │       └── SU_003/
    │           └── photo_004.jpg
    └── Period - 2/
        └── ...
```

### Naming Convention

Files keep their original name, organized by:
1. **Period** - Initial chronological period
2. **Phase** - Initial chronological phase
3. **Entity** - SU, Find, etc.

## Export Process

### Step 1: Parameter Selection

1. Select **Site** from ComboBox
2. Select **Year** (optional)
3. Choose **Export type**

### Step 2: Execution

1. Click **"Export"**
2. Wait for completion
3. Confirmation message

### Step 3: Verification

1. Click **"Open Folder"**
2. Verify created structure
3. Check completeness

## Output Folder

### Standard Path

```
~/pyarchinit/pyarchinit_image_export/
```

### Contents

- Folders organized by site
- Subfolders by period/phase
- Original images (not resized)

## Year Filter

The **Year** ComboBox allows:
- Exporting only images from a specific campaign
- Organizing export by excavation year
- Reducing export size

## Best Practices

### 1. Before Export

- Verify image-entity links
- Check SU periodization
- Ensure sufficient disk space

### 2. During Export

- Don't interrupt the process
- Wait for completion message

### 3. After Export

- Verify folder structure
- Check image completeness
- Create backup if necessary

## Typical Uses

### Report Preparation

```
1. Select site
2. Export all images
3. Use structure for report chapters
```

### Superintendency Delivery

```
1. Select site and year
2. Export by required type
3. Organize according to ministerial standards
```

### Campaign Backup

```
1. At campaign end, export everything
2. Archive to external storage
3. Verify integrity
```

## Troubleshooting

### Incomplete Export

**Causes**:
- Unlinked images
- Wrong file paths

**Solutions**:
- Verify links in Media Manager
- Check source file existence

### Incorrect Structure

**Causes**:
- Missing periodization
- SU without period/phase

**Solutions**:
- Fill in SU periodization
- Assign period/phase to all SU

## References

### Source Files
- `tabs/Images_directory_export.py` - Export interface
- `gui/ui/Images_directory_export.ui` - UI layout

### Folders
- `~/pyarchinit/pyarchinit_image_export/` - Export output

---

## Video Tutorial

### Image Export
`[Placeholder: video_export_immagini.mp4]`

**Contents**:
- Export configuration
- Output structure
- Archive organization

**Expected duration**: 10-12 minutes

---

*Last updated: January 2026*

---

## Interactive Animation

Explore the interactive animation to learn more about this topic.

[Open Interactive Animation](../../animations/pyarchinit_image_export_animation.html)
