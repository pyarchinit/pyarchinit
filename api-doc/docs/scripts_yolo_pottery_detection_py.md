# scripts/yolo_pottery_detection.py

## Overview

This file contains 4 documented elements.

## Functions

### detect_pottery_contours(image_path, output_dir, min_area, padding)

Detect pottery drawings using contour detection (for scanned drawings)

Args:
    image_path: Path to input image
    output_dir: Directory to save extracted regions
    min_area: Minimum contour area to consider (filters out small noise)
    padding: Padding around detected regions

Returns:
    Dict with detection results

**Parameters:**
- `image_path: str`
- `output_dir: str`
- `min_area: int`
- `padding: int`

**Returns:** `dict`

### detect_pottery(image_path, model_path, output_dir, confidence, padding, fallback_contours)

Detect pottery in image using YOLO model

Args:
    image_path: Path to input image
    model_path: Path to YOLO .pt model
    output_dir: Directory to save extracted regions
    confidence: Detection confidence threshold
    padding: Padding around detected regions
    fallback_contours: Fall back to contour detection if YOLO finds nothing

Returns:
    Dict with detection results

**Parameters:**
- `image_path: str`
- `model_path: str`
- `output_dir: str`
- `confidence: float`
- `padding: int`
- `fallback_contours: bool`

**Returns:** `dict`

### main()

*No description available.*
Entry point for the YOLO Pottery Detection command-line interface. Parses arguments for input image path (`--input`), output directory (`--output`), model file (`--model`), confidence threshold (`--confidence`, default `0.5`), padding (`--padding`, default `20`), and mode flags (`--json-output`, `--contours-only`); validates that the specified input and model files exist before dispatching to either `detect_pottery_contours` or `detect_pottery` depending on whether `--contours-only` is set. Returns `0` on success or `1` on failure, and optionally prints results as a JSON block to stdout when `--json-output` is specified.

