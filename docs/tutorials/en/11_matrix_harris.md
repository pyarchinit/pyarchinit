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
| PDF poster | Also produces a multi-page PDF poster for printing matrices wider than one sheet: sheets overlap by 2 cm and each sheet is labelled "foglio n/N - riga r/R, colonna c/C - A0 scala 1:x" (sheet n/N - row r/R, column c/C - A0 scale 1:x). For very large matrices (when the JPG DPI has to be reduced) the poster is produced anyway, even if unchecked | Yes (for printing) |
| Formato (Format) | Paper size of the poster sheets: A0, A1, A2, A3 | A0 |
| Scala (Scale) | Poster scale: "Adatta all'altezza" (fit height: one row of sheets, the matrix height fills the sheet), "Adatta alla pagina" (fit page: one single sheet with the whole matrix), 1:1, 1:2, 1:3 (fixed scale, more sheets). The drawing is never enlarged; the orientation (portrait/landscape) is chosen automatically to use fewer sheets | Adatta all'altezza |

The **PDF poster**, **Formato** and **Scala** controls are on the second row of the dialog (the labels are in Italian in every language of the UI).

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

### Very Large Matrices

With very large matrices (e.g. 1300 SU and about 2000 relationships) the export with orthogonal edges could take more than 25 minutes and produce an empty (0-byte) JPG. From this release **Export Matrix** and **View Matrix** adapt automatically:

| Situation | What happens |
|-----------|--------------|
| More than **600** relationships | Edges switch automatically from orthogonal (`ortho`) to straight polylines with tighter spacing: the same matrix is laid out in about one second. Below the threshold the orthogonal style is unchanged |
| Image exceeding the bitmap renderer limit (32,767 px per side) | The JPG/PNG DPI is reduced automatically (the value set in Setting_Matrix is a maximum) and vector copies `.svg` and `.pdf` are saved next to the image in `pyarchinit_Matrix_folder` (`Harris_matrix_tred.dot.svg/.pdf`; for View Matrix `Harris_matrix_viewtred.dot.svg/.pdf`) |
| Information dialog "Matrix molto grande" (very large matrix: the JPG was generated at N dpi, use the .svg / .pdf files) | Open the `.svg` or `.pdf` file (browser, Inkscape, PDF viewer) for a readable, zoomable version with no loss of quality |

The `.dot` files are still produced as before.

**Export with periodization** (periods checkbox in Setting_Matrix):

- The export no longer stops with the error `Errore durante il rendering del file DOT: 'NoneType' object has no attribute 'write'`, which appeared when Graphviz printed a warning and QGIS had no Python console open (typical on Windows). Graphviz warnings are now written to the QGIS Python console / log instead of aborting the export.
- On large DBs the period export is much faster (the same 1311-SU database went from about 25–45 s and a 51 MB DOT to about 3 s) and each phase gets its own invisible cluster, so no phase is silently ignored by Graphviz.
- For very wide period matrices the JPG can now be generated even below 12 dpi if needed (for reference, the 1311-SU matrix with periods comes out at 49 dpi): it is only an overview; for the readable version use the `.svg` / `.pdf` copies saved alongside.

**Vector copies and poster printing**:

- The `.pdf` / `.svg` copies now always stay within 200 inches (14,400 pt) per side, the limit beyond which Acrobat and Preview show only a part of the page: the whole matrix is therefore visible and zoomable (vector, no quality loss). On the 1311-SU database with periods the PDF measures 14,400 × 2,591 pt.
- To print it, use the poster PDF (**PDF poster** checkbox in Setting_Matrix): for the same database, A0 with "Adatta all'altezza" (fit height) gives 5 landscape A0 sheets at scale 1:3.4 (text ≈ 4 pt: readable on a plotter; use A0 "1:2" or "1:1" for larger text and more sheets). A single A0 sheet ("Adatta alla pagina", fit page) is only an overview.

### Warning "Periodization: start chronology later than the end"

**When it appears**: when exporting with **Print Periodizzazione** enabled, if at least one period/phase has an Initial Chronology later than its Final Chronology (e.g. `Periodo 6 Fase 1: 1650 → 1450`). The export still proceeds.

**Cause**: almost always BC years entered without the minus sign (pyArchInit's convention is BC = negative years). The period is sorted as AD: the Bronze Age ends up above the Roman phases and the cluster labels read "1650 d.C." instead of "1650 a.C.".

**Solution**:
1. Open the Periodization Form and fix the periods listed in the warning, entering BC years as negative numbers (e.g. `-1650` → `-1450`)
2. Regenerate the Matrix

## Output and Generated Files

### Output Folder

```
~/pyarchinit/pyarchinit_Matrix_folder/
├── Harris_matrix.dot           # Graphviz source
├── Harris_matrix_tred.dot      # After transitive reduction
├── Harris_matrix_tred.dot.jpg  # Final JPG image
├── Harris_matrix_tred.dot.png  # Final PNG image
├── Harris_matrix_tred.dot.svg  # Vector copy (large matrices only)
├── Harris_matrix_tred.dot.pdf  # Vector copy (large matrices only)
├── Harris_matrix_poster_A0.pdf # Multi-page PDF poster for printing
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
| *.svg/*.pdf | Zoomable vector version (large matrices) |
| _poster_A0.pdf | Multi-page PDF poster for printing; the name follows the chosen format (e.g. `_poster_A3.pdf`), for Export Matrix 2ED the prefix is `Harris_matrix2ED` |

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

[Open Interactive Animation](../../animations/harris_matrix_animation.html)
