# Tutorial 11: Harris Matrix

## Introduction

The **Harris Matrix** (or stratigraphic diagram) is a fundamental tool in archaeology for graphically representing stratigraphic relationships between different Stratigraphic Units (SU). PyArchInit automatically generates the Harris Matrix from the stratigraphic relationships entered in the SU forms.

### What is the Harris Matrix?

The Harris Matrix is a diagram that represents:
- The **temporal sequence** of SUs (from most recent at top to oldest at bottom)
- The **physical relationships** between SUs (covers/covered by, cuts/cut by, bonds with)
- The **periodization** of the excavation (grouping by periods and phases)

### Types of Relationships Represented

| Relationship | Meaning | Representation |
|--------------|---------|----------------|
| Covers/Covered by | Physical superimposition | Solid line downward |
| Cuts/Cut by | Negative action (interface) | Dashed line |
| Bonds with/Same as | Contemporaneity | Horizontal bidirectional line |
| Fills/Filled by | Cut filling | Solid line |
| Abuts/Supports | Structural support | Solid line |

## Accessing the Function

### From Main Menu
1. **PyArchInit** in menu bar
2. Select **Harris Matrix**

### From SU Form
1. Open SU Form
2. **Map** Tab
3. **"Export Matrix"** or **"View Matrix"** button

### Prerequisites
- Database correctly connected
- SUs with completed stratigraphic relationships
- Defined periodization (optional but recommended)
- Graphviz installed on system

## Matrix Configuration

### Settings Window (Setting_Matrix)

Before generation, a configuration window appears:

#### General Tab

| Field | Description | Recommended Value |
|-------|-------------|-------------------|
| DPI | Image resolution | 150-300 |
| Show Periods | Group SU by period/phase | Yes |
| Show Legend | Include legend in chart | Yes |

#### "Ante/Post" Nodes Tab (Normal Relationships)

| Parameter | Description | Options |
|-----------|-------------|---------|
| Node shape | Geometric shape | box, ellipse, diamond |
| Fill color | Internal color | white, lightblue, etc. |
| Style | Border appearance | solid, dashed |
| Line width | Border width | 0.5 - 2.0 |
| Arrow type | Arrow head | normal, diamond, none |
| Arrow size | Head size | 0.5 - 1.5 |

#### "Negative" Nodes Tab (Cuts)

| Parameter | Description | Options |
|-----------|-------------|---------|
| Node shape | Geometric shape | box, ellipse, diamond |
| Fill color | Distinctive color | gray, lightcoral |
| Line style | Connection appearance | dashed |

#### "Contemporary" Nodes Tab

| Parameter | Description | Options |
|-----------|-------------|---------|
| Node shape | Geometric shape | box, ellipse |
| Fill color | Distinctive color | lightyellow, white |
| Line style | Connection appearance | solid |
| Arrow | Connection type | none (bidirectional) |

## Export Types

### 1. Standard Matrix Export

Generates basic matrix with:
- All stratigraphic relationships
- Period/phase grouping
- Vertical layout (TB - Top to Bottom)

**Output**: `pyarchinit_Matrix_folder/Harris_matrix.jpg`

### 2. Extended Matrix Export (2ED)

Extended version with:
- Additional node information (SU + definition + dating)
- Special connections (>, >>)
- GraphML format export

**Output**: `pyarchinit_Matrix_folder/Harris_matrix2ED.jpg`

### 3. View Matrix (Quick Visualization)

For quick viewing without configuration options:
- Uses default settings
- Faster generation
- Ideal for quick checks

## Generation Process

### Step 1: Data Collection

System automatically collects:
```
For each SU in selected site/area:
  - SU number
  - Unit type (SU/WSU)
  - Stratigraphic relationships
  - Initial period and phase
  - Interpretive definition
```

### Step 2: Graph Construction

Creating relationships:
```
Sequence (Ante/Post):
  US1 -> US2 (US1 covers US2)

Negative (Cuts):
  US3 -> US4 (US3 cuts US4)

Contemporary:
  US5 <-> US6 (US5 bonds with US6)
```

### Step 3: Period Clustering

Hierarchical grouping:
```
Site
  └── Area
      └── Period 1 : Phase 1 : "Roman Age"
          ├── US101
          ├── US102
          └── US103
      └── Period 1 : Phase 2 : "Late Antiquity"
          ├── US201
          └── US202
```

### Step 4: Transitive Reduction (tred)

Graphviz `tred` command removes redundant relationships:
- If US1 -> US2 and US2 -> US3, removes US1 -> US3
- Simplifies diagram
- Keeps only direct relationships

### Step 5: Final Rendering

Image generation with multiple formats:
- DOT (Graphviz source)
- JPG (compressed image)
- PNG (lossless image)

## Matrix Interpretation

### Vertical Reading

```
     [Most recent SU]
           ↓
        US 001
           ↓
        US 002
           ↓
        US 003
           ↓
     [Oldest SU]
```

### Cluster Reading

Colored boxes represent periods/phases:
- **Light blue**: Period cluster
- **Yellow**: Phase cluster
- **Gray**: Site background

### Connection Types

```
─────────→  Solid line = Covers/Fills/Abuts
- - - - →  Dashed line = Cuts
←────────→  Bidirectional = Contemporary/Same as
```

### Node Colors

| Color | Typical Meaning |
|-------|-----------------|
| White | Normal deposit SU |
| Gray | Negative SU (cut) |
| Yellow | Contemporary SU |
| Blue | SU with special relationships |

## Troubleshooting

### Error: "Loop Detected"

**Cause**: Cycles exist in relationships (A covers B, B covers A)

**Solution**:
1. Open SU Form
2. Verify relationships of indicated SUs
3. Correct circular relationships
4. Regenerate matrix

### Error: "tred command not found"

**Cause**: Graphviz not installed

**Solution**:
- **Windows**: Install Graphviz from graphviz.org
- **macOS**: `brew install graphviz`
- **Linux**: `sudo apt install graphviz`

### Matrix Not Generated

**Possible causes**:
1. No stratigraphic relationships entered
2. SU without assigned period/phase
3. Permission problems in output folder

**Check**:
1. Verify SUs have relationships
2. Verify periodization
3. Check permissions on `pyarchinit_Matrix_folder`

### Matrix Too Large

**Problem**: Unreadable image with many SUs

**Solutions**:
1. Reduce DPI (100-150)
2. Filter by specific area
3. Use View Matrix for single areas
4. Export to vector format (DOT) and open with yEd

## Output and Generated Files

### Output Folder

```
~/pyarchinit/pyarchinit_Matrix_folder/
├── Harris_matrix.dot           # Graphviz source
├── Harris_matrix_tred.dot      # After transitive reduction
├── Harris_matrix_tred.dot.jpg  # Final JPG image
├── Harris_matrix_tred.dot.png  # Final PNG image
├── Harris_matrix2ED.dot        # Extended version
├── Harris_matrix2ED_graphml.dot # For GraphML export
└── matrix_error.txt            # Error log
```

### File Usage

| File | Use |
|------|-----|
| *.jpg/*.png | Insert in reports |
| *.dot | Edit with Graphviz editor |
| _graphml.dot | Import to yEd for advanced editing |

## Best Practices

### 1. Before Generation

- Verify stratigraphic relationship completeness
- Check for absence of cycles
- Assign period/phase to all SUs
- Fill interpretive definition

### 2. During SU Compilation

- Enter correct bidirectional relationships
- Use consistent terminology
- Verify correct area in relationships

### 3. Output Optimization

- For print: DPI 300
- For screen: DPI 150
- For complex excavations: divide by areas

### 4. Quality Control

- Compare matrix with excavation documentation
- Verify logical sequences
- Check period groupings

## Integration with Other Tools

### Export for yEd

The `_graphml.dot` file can be opened in yEd for:
- Manual layout editing
- Adding annotations
- Export to different formats

### Export for s3egraph

PyArchInit supports export for the s3egraph system:
- Compatible format
- Maintains stratigraphic relationships
- Support for 3D visualization

## References

### Source Files
- `tabs/Interactive_matrix.py` - Interactive interface
- `modules/utility/pyarchinit_matrix_exp.py` - HarrisMatrix and ViewHarrisMatrix classes

### Database
- `us_table` - SU data and relationships
- `periodizzazione_table` - Periods and phases

### Dependencies
- Graphviz (dot, tred)
- Python graphviz library

---

## Video Tutorial

### Harris Matrix - Complete Generation
`[Placeholder: video_matrix_harris.mp4]`

**Contents**:
- Settings configuration
- Matrix generation
- Result interpretation
- Common problem resolution

**Expected duration**: 15-20 minutes

---

*Last updated: January 2026*

---

## Interactive Animation

Explore the interactive animation to learn more about this topic.

[Open Interactive Animation](../animations/harris_matrix_animation.html)
