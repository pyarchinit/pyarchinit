# Pottery Tools Documentation

## Overview
Pottery Tools is a specialized module for archaeological pottery analysis that integrates machine learning (YOLO) for automatic pottery detection and extraction from PDFs and images.

## System Architecture

### Python Environment Separation
To avoid conflicts between QGIS and machine learning libraries, Pottery Tools uses a **dual Python system**:

1. **QGIS Python**: Runs the main plugin interface and basic operations
2. **External System Python**: Runs YOLO/ultralytics for pottery detection

This separation prevents library conflicts and ensures stable operation across all platforms.

## Installation

### Automatic Installation
When you first use Pottery Tools:

1. The system automatically detects available Python installations
2. If `ultralytics` is not installed, it prompts to install it automatically
3. Installation happens in the external Python, NOT in QGIS Python

### Manual Installation
If automatic installation fails, install manually:

**macOS/Linux:**
```bash
python3 -m pip install ultralytics
```

**Windows:**
```cmd
python -m pip install ultralytics
```

## Supported Python Locations

### macOS
- `/usr/bin/python3` (System Python - most common)
- `/opt/homebrew/bin/python3` (Homebrew on Apple Silicon)
- `/usr/local/bin/python3` (Homebrew on Intel)
- `/Library/Frameworks/Python.framework/...` (Python.org installer)
- `/opt/anaconda3/bin/python3` (Anaconda, if installed)

### Windows
- `C:\Python311\python.exe` (Standard Python installation)
- `C:\Program Files\Python311\python.exe`
- `C:\ProgramData\Anaconda3\python.exe` (Anaconda)
- `C:\Users\[username]\Anaconda3\python.exe`
- Python from system PATH

### Linux
- `/usr/bin/python3` (System Python)
- `/usr/local/bin/python3`
- Python from system PATH

## Workflow

### 1. PDF Extraction
- Load PDF containing pottery images/drawings
- Extract pages as individual images
- Images saved to `{pdf_name}_extracted/` folder

### 2. Apply YOLO Model
- Automatically downloads model to `~/pyarchinit/bin/`
- Detects pottery instances in extracted images
- Confidence threshold adjustable (default 50%)
- Morphological operations: kernel size 2, iterations 10

### 3. Extract Pottery Instances
- Extracts each detected pottery as separate image
- Applies segmentation masks for clean extraction
- White background for isolated pottery
- Saves to `pottery_cards/` folder

### 4. Tabular Data
- Manage metadata for each pottery instance
- ID, Type, Date, Notes
- Export capabilities

### 5. Post-Processing
- Flip horizontally (for profile views)
- Classification (rim, base, fragment)
- Background removal
- Color adjustments
- **PotteryInk AI Enhancement** (NEW):
  - Transform pencil drawings to publication-ready illustrations
  - AI-powered inking using diffusion models
  - Support for different archaeological periods
  - Batch processing with progress tracking

### 6. Layout Creation
- Professional catalog layouts
- Scale bars and grids
- Multiple layout modes:
  - Catalog (grid layout)
  - Typology (organized by type)
  - Single (detailed view)

### 7. Database Integration
- Save to PyArchInit database
- Link to excavation contexts
- CIDOC-CRM export support

## Troubleshooting

### "No module named 'ultralytics'" Error
- Click "Yes" when prompted to install automatically
- Or install manually: `pip install ultralytics`

### QGIS Opens Multiple Instances
- This has been fixed by using external Python
- Update to latest version if still occurring

### Model Not Found
- Models are downloaded to `~/pyarchinit/bin/`
- Click "Download Model" button
- Supported models: `BasicModelv8_v01.pt`, `pottery_yolo.pt`

### GPU Not Detected
- Apple Silicon: Automatically uses Metal Performance Shaders
- NVIDIA: Requires CUDA installation
- Falls back to CPU if no GPU available

### Numpy Broadcasting Error
- Fixed in latest version
- Update plugin if error persists

## Technical Details

### Environment Isolation
The system removes QGIS environment variables when running external Python:
- `PYTHONHOME` - Removed to prevent path conflicts
- `PYTHONPATH` - Removed to use system libraries
- `PYTHONSTARTUP`, `VIRTUAL_ENV` - Cleaned for isolation

### YOLO Runner Script
Located at `~/pyarchinit/bin/yolo_runner.py`
- Standalone script executed by external Python
- Communicates via JSON with main plugin
- Handles all YOLO operations

### Mask Extraction
- Uses YOLO segmentation models (not just detection)
- Morphological operations for mask refinement
- Proper dimension handling for numpy arrays

## Requirements

### System Requirements
- Python 3.9 or higher (external)
- QGIS 3.22 or higher
- 4GB RAM minimum (8GB recommended for large PDFs)

### Python Packages (External Python)
**For YOLO Detection:**
- ultralytics >= 8.2.0
- opencv-python
- numpy
- pillow

**For PotteryInk AI Enhancement:**
- torch >= 2.0.0
- torchvision
- diffusers >= 0.24.0
- transformers >= 4.25.0
- peft
- scikit-image
- seaborn
- scipy

### Python Packages (QGIS Python)
- PyMuPDF (for PDF extraction)
- PIL/Pillow (for image processing)
- Already included in PyArchInit requirements

## Performance Tips

1. **Use GPU when available**: Significantly faster inference
2. **Adjust confidence threshold**: Lower = more detections, higher = fewer false positives
3. **Batch processing**: Process multiple PDFs sequentially
4. **Image resolution**: Higher resolution improves detection but slower

## Support

For issues or questions:
1. Check this documentation
2. Update to latest plugin version
3. Report issues on GitHub: pyarchinit/pyarchinit