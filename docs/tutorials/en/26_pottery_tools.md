# Tutorial 26: Pottery Tools

## Introduction

**Pottery Tools** is an advanced module for processing ceramic images. It offers tools to extract images from PDFs, generate plate layouts, process drawings with AI (PotteryInk), and other specialized features for ceramic documentation.

### Main Features

- Image extraction from PDFs
- Ceramic plate layout generation
- Image processing with AI
- Drawing format conversion
- Integration with Pottery Form

## Access

### From Menu
**PyArchInit** → **Pottery Tools**

## Interface

### Main Panel

```
+--------------------------------------------------+
|              Pottery Tools                        |
+--------------------------------------------------+
| [Tab: PDF Extraction]                            |
| [Tab: Layout Generator]                          |
| [Tab: Image Processing]                          |
| [Tab: PotteryInk AI]                             |
+--------------------------------------------------+
| [Progress Bar]                                   |
| [Log Messages]                                   |
+--------------------------------------------------+
```

## PDF Extraction Tab

### Function

Automatically extracts images from PDF documents containing ceramic plates.

### Usage

1. Select source PDF file
2. Specify destination folder
3. Click **"Extract"**
4. Images are saved as separate files

### Options

| Option | Description |
|--------|-------------|
| DPI | Extraction resolution (150-600) |
| Format | PNG, JPG, TIFF |
| Pages | All or specific range |

## Layout Generator Tab

### Function

Automatically generates ceramic plates with standardized layout.

### Layout Types

| Layout | Description |
|--------|-------------|
| Grid | Images in regular grid |
| Sequence | Images in numbered sequence |
| Comparison | Layout for comparison |
| Catalog | Catalog format with captions |

### Usage

1. Select images to include
2. Choose layout type
3. Configure parameters (dimensions, margins)
4. Generate plate

### Layout Parameters

| Parameter | Description |
|-----------|-------------|
| Page size | A4, A3, Custom |
| Orientation | Portrait, Landscape |
| Margins | Border spacing |
| Spacing | Distance between images |
| Captions | Text under images |

## Image Processing Tab

### Function

Batch processing of ceramic images.

### Available Operations

| Operation | Description |
|-----------|-------------|
| Resize | Scale images |
| Crop | Automatic/manual crop |
| Rotate | Degree rotation |
| Convert | Format change |
| Optimize | Quality compression |

### Batch Processing

1. Select source folder
2. Choose operations to apply
3. Specify destination
4. Execute processing

## PotteryInk AI Tab

### Function

Uses artificial intelligence for:
- Photo → technical drawing conversion
- Ceramic form recognition
- Classification suggestions
- Automatic measurement

### Requirements

- Configured Python virtual environment
- Downloaded AI models (YOLO, etc.)
- GPU recommended (but not required)

### AI Models

**Inking models (PotteryInk).** In the **🏺 PotteryInk** tab, **Enhancement Settings** group, the **Model:** drop-down lists the PyPotteryInk 2.1.2 models; the **Download** button next to it downloads the selected model from Hugging Face (`lrncrd/PyPotteryInk`) into `~/pyarchinit_5/bin/models/` (if the file is already there, it asks whether to download it again). Each model is about 38 MB.

| Model (drop-down entry) | File | Use |
|-------------------------|------|-----|
| 10k Model (General) | `model_10k.pkl` | General-purpose model for pottery drawings |
| 6h-MCG Model (Bronze Age) | `6h-MCG.pkl` | Bronze Age drawings |
| 6h-MC Model (Protohistoric) | `6h-MC.pkl` | Protohistoric and historic drawings |
| 4h-PAINT Model (Historic/Painted) | `4h-PAINT.pkl` | Historic and painted pottery |
| 5h-PAPERGRID Model (Paper grid tables) | `5h_PAPERGRID.pkl` | Drawings on graph paper (grid tables); does not support shadows |

**Drawing detector (YOLO).** The PyPotteryLens model `BasicModelv8_v01.pt`, which finds the drawings in the pages extracted from PDFs (**Auto-detect pottery (ML)** option and **2. Apply Model** tab), is installed with the **Download YOLO Model** button of the **PDF Extraction** tab: if a local copy of PyPotteryLens is found it is copied, otherwise the model is downloaded from Hugging Face (`lrncrd/PyPotteryLens`, about 144 MB) and, if that fails, from the GitHub fork as a fallback. The file is saved in `~/pyarchinit_5/bin/`; a failed download leaves no partial file behind.

### Usage

1. Load ceramic image
2. Select processing type
3. Wait for AI processing
4. Verify and save result

### AI Processing Types

| Type | Description |
|------|-------------|
| Ink Conversion | Converts photo to technical drawing |
| Shape Detection | Recognizes vessel shape |
| Profile Extraction | Extracts ceramic profile |
| Decoration Analysis | Analyzes decorations |

## Virtual Environment

### Automatic Setup

On first launch, Pottery Tools:
1. Creates virtual environment in `~/pyarchinit_5/bin/pottery_venv/`
2. Installs required dependencies
3. Downloads AI models (if required)

### Dependencies

- PyTorch
- Ultralytics (YOLO)
- OpenCV
- Pillow

### Installation Verification

The log shows status:
```
✓ Virtual environment created
✓ Dependencies installed
✓ Models downloaded
✓ Pottery Tools initialized successfully!
```

## Database Integration

### Linking to Pottery Form

Processed images can be:
- Automatically linked to Pottery records
- Saved with appropriate metadata
- Organized by site/inventory

## Best Practices

### 1. Input Image Quality

- Minimum resolution: 300 DPI
- Uniform lighting
- Neutral background (white/gray)
- Visible metric scale

### 2. AI Processing

- Always verify AI results
- Manually correct if necessary
- Save originals and processed

### 3. Output Organization

- Use consistent naming
- Organize by site/campaign
- Maintain traceability

## Troubleshooting

### Virtual Environment Not Created

**Causes**:
- Python not found
- Insufficient permissions

**Solutions**:
- Verify Python installation
- Check folder permissions

### Slow AI Processing

**Causes**:
- No GPU available
- Images too large

**Solutions**:
- Reduce image size
- Use CPU (slower but works)

### PDF Extraction Failed

**Causes**:
- Protected PDF
- Unsupported format

**Solutions**:
- Verify PDF protection
- Try with other PDF software

## References

### Source Files
- `tabs/Pottery_tools.py` - Main interface
- `modules/utility/pottery_utilities.py` - Processing utilities
- `modules/utility/pottery_models.py` - Model registry (PotteryInk and YOLO detector)
- `gui/ui/Pottery_tools.ui` - UI layout

### Folders
- `~/pyarchinit_5/bin/pottery_venv/` - Virtual environment
- `~/pyarchinit_5/bin/models/` - PotteryInk models (`.pkl`)
- `~/pyarchinit_5/bin/BasicModelv8_v01.pt` - YOLO detector

---

## Video Tutorial

### Complete Pottery Tools
`[Placeholder: video_pottery_tools.mp4]`

**Contents**:
- PDF extraction
- Layout generation
- AI processing
- Database integration

**Expected duration**: 20-25 minutes

---

*Last updated: October 2026*
