# scripts/ink_utils.py

## Overview

This file contains 7 documented elements.

## Functions

### cleanup()

Perform a memory cleanup. Call this after heavy GPU/MPS usage.

This helper centralises gc.collect() and cache emptying across CUDA/MPS.

### calculate_patches(width, height, patch_size, overlap)

Calculate total patches, patches per row and number of rows.

This function preserves the original signature used in other code but unifies
the two previously duplicated implementations.

Args:
    width: image width (px)
    height: image height (px)
    patch_size: patch size (px)
    overlap: overlap between patches (px)

Returns:
    (total_patches, patches_per_row, num_rows)

**Parameters:**
- `width: int`
- `height: int`
- `patch_size: int`
- `overlap: int`

**Returns:** `Tuple[int, int, int]`

### get_patch_coordinates(idx, patches_per_row, num_rows, width, height, patch_size, overlap)

Return coordinates for patch index `idx`.

The function keeps the original contract returning (x_start, y_start, x_end, y_end, row, col).

**Parameters:**
- `idx: int`
- `patches_per_row: int`
- `num_rows: int`
- `width: int`
- `height: int`
- `patch_size: int`
- `overlap: int`

**Returns:** `Tuple[int, int, int, int, int, int]`

### create_blend_mask(patch_width, patch_height, row, col, overlap)

Create a simple linear blending mask for a patch.

The mask fades from 0..255 across the overlap region on top and left edges when required.
Returns None for the top-left patch (no blending needed).

**Parameters:**
- `patch_width: int`
- `patch_height: int`
- `row: int`
- `col: int`
- `overlap: int`

**Returns:** `Optional[Image.Image]`

### run_diagnostics(input_folder, model_path, prompt, patch_size, overlap, num_sample_images, contrast_values, output_dir, progress_callback)

Run diagnostic visualisations before main processing.

Behaviour and parameters are kept identical to the original implementation so this
function can be used by the app without changes. The function now reuses a cached
model instance when possible.

**Parameters:**
- `input_folder`
- `model_path`
- `prompt: str`
- `patch_size: int`
- `overlap: int`
- `num_sample_images: int`
- `contrast_values: List[float]`
- `output_dir: str`
- `progress_callback`

### process_single_image(input_image_path_or_pil, model_path, prompt, output_dir, use_fp16, output_name, contrast_scale, return_pil, patch_size, overlap, upscale)

Process a single image with improved patch strategy and device support.

The public signature is kept identical to the original to ensure app compatibility.

Returns either a PIL.Image (if return_pil=True) or the saved output path.

**Parameters:**
- `input_image_path_or_pil`
- `model_path`
- `prompt: str`
- `output_dir: str`
- `use_fp16: bool`
- `output_name: Optional[str]`
- `contrast_scale: float`
- `return_pil: bool`
- `patch_size: int`
- `overlap: int`
- `upscale: float`

### process_folder(input_folder, model_path, prompt, output_dir, use_fp16, contrast_scale, patch_size, overlap, file_extensions, upscale, progress_callback, export_elements, export_svg)

Process a folder of images using improved patch strategy.

Public API kept identical. The function now reuses a cached model instance
and centralises logging and cleanup behaviour.

**Parameters:**
- `input_folder`
- `model_path`
- `prompt: str`
- `output_dir: str`
- `use_fp16: bool`
- `contrast_scale: float`
- `patch_size: int`
- `overlap: int`
- `file_extensions: Tuple[str, ...]`
- `upscale: float`
- `progress_callback`
- `export_elements: bool`
- `export_svg: bool`

