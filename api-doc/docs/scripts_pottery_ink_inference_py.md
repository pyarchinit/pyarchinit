# scripts/pottery_ink_inference.py

## Overview

This file contains 7 documented elements.

## Functions

### setup_environment()

Setup environment variables for MPS/CUDA

### get_device()

Get the best available device

### cleanup(device)

Clean up GPU memory

**Parameters:**
- `device`

### process_image(input_path, output_path, model_path, device, prompt, contrast_scale, patch_size, overlap, use_fp16, manual_contrast, manual_brightness, background_mode, bg_threshold)

Process a pottery drawing image using PyPotteryInk

Args:
    input_path: Path to input image
    output_path: Path for output image
    model_path: Path to .pkl model
    device: torch device
    prompt: Text prompt for conditioning
    contrast_scale: Contrast enhancement factor
    patch_size: Size of processing patches
    overlap: Overlap between patches
    use_fp16: Use half precision
    manual_contrast: Manual contrast adjustment (1.0 = no change)
    manual_brightness: Manual brightness adjustment (1.0 = no change)
    background_mode: Background treatment ("keep", "white", "transparent")
    bg_threshold: Brightness threshold for background detection (200-255)

Returns:
    True if successful

**Parameters:**
- `input_path: str`
- `output_path: str`
- `model_path: str`
- `device`
- `prompt: str`
- `contrast_scale: float`
- `patch_size: int`
- `overlap: int`
- `use_fp16: bool`
- `manual_contrast: float`
- `manual_brightness: float`
- `background_mode: str`
- `bg_threshold: int`

**Returns:** `bool`

### main()

*No description available.*
Entry point for the PotteryInk ML Inference command-line interface. Parses command-line arguments for input/output paths, model file, device selection, prompt, contrast, patch size, overlap, precision, background treatment, and manual adjustments — including legacy argument mappings for `--strength` and `--size` — then invokes `process_image()` with the resolved parameters. Returns `0` on success or `1` on failure, and optionally prints a JSON-formatted result summary to stdout when `--json-output` is specified.

### create_blend_mask(patch_size, overlap, row, col, n_rows, n_cols)

Create blending mask for patch stitching

**Parameters:**
- `patch_size`
- `overlap`
- `row`
- `col`
- `n_rows`
- `n_cols`

