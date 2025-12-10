#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PotteryInk ML Inference Script
Uses PyPotteryInk original implementation (https://github.com/lrncrd/PyPotteryInk)

Usage:
    python pottery_ink_inference.py --input IMAGE_PATH --output OUTPUT_PATH --model MODEL_PATH [options]
"""

import argparse
import os
import sys
import json
import gc
from pathlib import Path

# Add scripts directory to path for local imports
scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)


def setup_environment():
    """Setup environment variables for MPS/CUDA"""
    os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'


def get_device():
    """Get the best available device"""
    import torch
    if torch.backends.mps.is_available():
        return torch.device("mps")
    elif torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def cleanup(device):
    """Clean up GPU memory"""
    import torch
    gc.collect()
    if device.type == "cuda":
        torch.cuda.empty_cache()
    elif device.type == "mps":
        if hasattr(torch.backends.mps, 'empty_cache'):
            torch.backends.mps.empty_cache()


def process_image(
    input_path: str,
    output_path: str,
    model_path: str,
    device,
    prompt: str = "make it ready for publication",
    contrast_scale: float = 1.0,
    patch_size: int = 512,
    overlap: int = 64,
    use_fp16: bool = False,
    manual_contrast: float = 1.0,
    manual_brightness: float = 1.0,
    background_mode: str = "keep",
    bg_threshold: int = 240
) -> bool:
    """
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
    """
    import torch
    from PIL import Image, ImageEnhance, ImageOps
    from torchvision import transforms
    import torchvision.transforms.functional as F
    import numpy as np

    # Import the Pix2Pix_Turbo model from downloaded PyPotteryInk code
    from pix2pix_turbo import Pix2Pix_Turbo

    print(f"Loading model from: {model_path}")
    model = Pix2Pix_Turbo(pretrained_path=model_path)
    model.set_eval()

    # Move to device with correct dtype
    if device.type == "mps":
        model = model.to(device)
        # MPS requires float32
    elif device.type == "cuda" and use_fp16:
        model = model.half().to(device)
    else:
        model = model.to(device)

    print("Model loaded successfully")

    # Load and prepare image
    print(f"Loading image: {input_path}")
    input_image = Image.open(input_path).convert("RGB")
    original_size = input_image.size
    print(f"Original size: {original_size}")

    # Apply manual adjustments if specified
    if manual_contrast != 1.0 or manual_brightness != 1.0:
        print(f"Applying manual adjustments: contrast={manual_contrast}, brightness={manual_brightness}")
        if manual_brightness != 1.0:
            input_image = ImageEnhance.Brightness(input_image).enhance(manual_brightness)
        if manual_contrast != 1.0:
            input_image = ImageEnhance.Contrast(input_image).enhance(manual_contrast)

    # Pad if smaller than patch_size
    width, height = input_image.size
    if width < patch_size or height < patch_size:
        new_width = max(width, patch_size)
        new_height = max(height, patch_size)
        padded = Image.new('RGB', (new_width, new_height), (255, 255, 255))
        padded.paste(input_image, (0, 0))
        input_image = padded
        width, height = new_width, new_height

    # Ensure dimensions are multiples of 4
    width = width - width % 4
    height = height - height % 4
    input_image = input_image.resize((width, height), Image.LANCZOS)
    print(f"Processing size: {width}x{height}")

    # Calculate patch grid
    stride = patch_size - overlap
    n_cols = max(1, (width - overlap) // stride + (1 if (width - overlap) % stride else 0))
    n_rows = max(1, (height - overlap) // stride + (1 if (height - overlap) % stride else 0))
    total_patches = n_rows * n_cols
    print(f"Processing {n_cols}x{n_rows} = {total_patches} patches")

    # Create output image
    output_image = Image.new("RGB", (width, height), (255, 255, 255))

    def create_blend_mask(patch_size, overlap, row, col, n_rows, n_cols):
        """Create blending mask for patch stitching"""
        mask = np.ones((patch_size, patch_size), dtype=np.float32)
        if col > 0:
            for i in range(overlap):
                mask[:, i] = i / overlap
        if row > 0:
            for i in range(overlap):
                mask[i, :] *= i / overlap
        return Image.fromarray((mask * 255).astype(np.uint8), mode='L')

    # Process patches
    with torch.no_grad():
        patch_idx = 0
        for row in range(n_rows):
            for col in range(n_cols):
                # Calculate patch coordinates
                x_start = col * stride
                y_start = row * stride
                x_end = min(x_start + patch_size, width)
                y_end = min(y_start + patch_size, height)

                # Adjust for edge patches
                if x_end - x_start < patch_size:
                    x_start = max(0, x_end - patch_size)
                if y_end - y_start < patch_size:
                    y_start = max(0, y_end - patch_size)

                # Extract patch
                patch = input_image.crop((x_start, y_start, x_end, y_end))

                # Apply contrast enhancement
                if contrast_scale != 1.0:
                    patch = ImageEnhance.Contrast(patch).enhance(contrast_scale)

                # Convert to tensor [0, 1]
                patch_tensor = F.to_tensor(patch).unsqueeze(0)

                # Move to device with correct dtype
                if device.type == "mps":
                    patch_tensor = patch_tensor.float().to(device)
                elif device.type == "cuda" and use_fp16:
                    patch_tensor = patch_tensor.half().to(device)
                else:
                    patch_tensor = patch_tensor.to(device)

                # Process through model
                output_tensor = model(patch_tensor, prompt)

                # Convert output: from [-1, 1] to [0, 1]
                output_tensor = output_tensor[0].cpu().float() * 0.5 + 0.5
                output_tensor = torch.clamp(output_tensor, 0, 1)

                # Convert to PIL
                output_patch = transforms.ToPILImage()(output_tensor)

                # Create blend mask
                mask = create_blend_mask(patch_size, overlap, row, col, n_rows, n_cols)

                # Paste with blending
                output_image.paste(output_patch, (x_start, y_start), mask)

                patch_idx += 1
                print(f"  Processed patch {patch_idx}/{total_patches}")

                # Cleanup
                cleanup(device)

    # Post-processing
    print("Post-processing...")

    # Resize to original if needed
    if output_image.size != original_size:
        output_image = output_image.resize(original_size, Image.LANCZOS)

    # Convert to grayscale
    output_image = output_image.convert('L')

    # Enhanced post-processing to improve faint lines
    arr = np.array(output_image, dtype=np.float32)

    # Use adaptive contrast enhancement
    # Find the actual range of values
    min_val = arr.min()
    max_val = arr.max()

    # If image is very uniform (all similar values), skip aggressive processing
    if max_val - min_val > 20:
        # Normalize to full range
        arr = (arr - min_val) / (max_val - min_val + 1e-6) * 255

        # Slight enhancement of darker areas (lines)
        # Only darken pixels significantly below the mean
        mean_val = arr.mean()
        dark_threshold = mean_val * 0.7
        mask = arr < dark_threshold
        arr[mask] = arr[mask] * 0.7

    arr = np.clip(arr, 0, 255)
    output_image = Image.fromarray(arr.astype(np.uint8))

    # Moderate contrast enhancement
    output_image = ImageEnhance.Contrast(output_image).enhance(1.5)

    # Apply background treatment
    if background_mode != "keep":
        print(f"Applying background treatment: {background_mode} (threshold={bg_threshold})")
        # Get grayscale values for threshold
        gray_arr = np.array(output_image)

        # Create background mask
        bg_mask = gray_arr >= bg_threshold

        if background_mode == "white":
            # Force background to pure white
            gray_arr[bg_mask] = 255
            output_image = Image.fromarray(gray_arr)
            # Convert to RGB
            output_image = output_image.convert('RGB')
        elif background_mode == "transparent":
            # Convert to RGBA with transparent background
            rgb_image = output_image.convert('RGB')
            rgba_arr = np.dstack((np.array(rgb_image), np.full(gray_arr.shape, 255, dtype=np.uint8)))
            # Set alpha to 0 for background pixels
            rgba_arr[bg_mask, 3] = 0
            output_image = Image.fromarray(rgba_arr, mode='RGBA')
    else:
        # Convert to RGB for saving
        output_image = output_image.convert('RGB')

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Save
    output_image.save(output_path, 'PNG', dpi=(300, 300))
    print(f"Saved: {output_path}")

    return True


def main():
    parser = argparse.ArgumentParser(description='PotteryInk ML Inference')
    parser.add_argument('--input', '-i', required=True, help='Input image path')
    parser.add_argument('--output', '-o', required=True, help='Output image path')
    parser.add_argument('--model', '-m', required=True, help='Path to .pkl model file')
    parser.add_argument('--device', '-d', default='auto', choices=['auto', 'cpu', 'cuda', 'mps'],
                       help='Device to use for inference')
    parser.add_argument('--prompt', '-p', default='make it ready for publication',
                       help='Text prompt for model')
    parser.add_argument('--contrast', '-c', type=float, default=1.0,
                       help='Contrast scale factor (default 1.0)')
    parser.add_argument('--patch-size', type=int, default=512,
                       help='Patch size for processing (default 512)')
    parser.add_argument('--overlap', type=int, default=64,
                       help='Overlap between patches (default 64)')
    parser.add_argument('--fp16', action='store_true',
                       help='Use FP16 precision (CUDA only)')
    parser.add_argument('--json-output', action='store_true',
                       help='Output results as JSON')

    # Manual adjustment parameters
    parser.add_argument('--manual-contrast', type=float, default=1.0,
                       help='Manual contrast adjustment (1.0 = no change)')
    parser.add_argument('--manual-brightness', type=float, default=1.0,
                       help='Manual brightness adjustment (1.0 = no change)')

    # Background treatment parameters
    parser.add_argument('--background', default='keep',
                       choices=['keep', 'white', 'transparent'],
                       help='Background treatment (keep, white, transparent)')
    parser.add_argument('--bg-threshold', type=int, default=240,
                       help='Brightness threshold for background detection (200-255)')

    # Legacy arguments for compatibility
    parser.add_argument('--strength', '-s', type=float, default=None,
                       help='(Legacy) Maps to contrast')
    parser.add_argument('--steps', '-n', type=int, default=None,
                       help='(Legacy) Ignored - single-step model')
    parser.add_argument('--size', type=int, default=None,
                       help='(Legacy) Maps to patch-size')

    args = parser.parse_args()

    # Handle legacy arguments
    if args.strength is not None:
        args.contrast = args.strength
    if args.size is not None:
        args.patch_size = args.size

    # Setup environment
    setup_environment()

    # Determine device
    import torch
    if args.device == 'auto':
        device = get_device()
    else:
        device = torch.device(args.device)

    print(f"Using device: {device}")

    result_info = {
        'success': False,
        'input': args.input,
        'output': args.output,
        'model': args.model,
        'device': str(device),
        'error': None
    }

    try:
        # Validate files
        if not os.path.exists(args.input):
            raise FileNotFoundError(f"Input file not found: {args.input}")
        if not os.path.exists(args.model):
            raise FileNotFoundError(f"Model file not found: {args.model}")

        # Process image
        success = process_image(
            args.input,
            args.output,
            args.model,
            device,
            prompt=args.prompt,
            contrast_scale=args.contrast,
            patch_size=args.patch_size,
            overlap=args.overlap,
            use_fp16=args.fp16,
            manual_contrast=args.manual_contrast,
            manual_brightness=args.manual_brightness,
            background_mode=args.background,
            bg_threshold=args.bg_threshold
        )

        result_info['success'] = success

    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Error: {error_msg}")
        traceback.print_exc()
        result_info['error'] = error_msg

    # Output JSON if requested
    if args.json_output:
        print("---JSON_OUTPUT---")
        print(json.dumps(result_info, indent=2))

    return 0 if result_info['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
