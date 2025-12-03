#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PotteryInk ML Inference Script
Runs in the pottery_venv to process pottery drawings using actual ML models

Usage:
    python pottery_ink_inference.py --input IMAGE_PATH --output OUTPUT_PATH --model MODEL_PATH [options]
"""

import argparse
import os
import sys
import json
from pathlib import Path

def setup_environment():
    """Setup environment variables for MPS/CUDA"""
    # For MPS (Apple Silicon)
    os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'


def load_potteryink_model(model_path, device='cpu'):
    """
    Load PotteryInk LoRA model

    Args:
        model_path: Path to .pkl model file
        device: Device to load model on ('cpu', 'cuda', 'mps')

    Returns:
        Loaded pipeline and model data
    """
    import torch
    from diffusers import StableDiffusionImg2ImgPipeline
    from peft import LoraConfig, inject_adapter_in_model

    # Load model checkpoint
    print(f"Loading model from: {model_path}")
    ckpt = torch.load(model_path, map_location='cpu', weights_only=False)

    # Extract LoRA configuration
    unet_lora_modules = ckpt.get('unet_lora_target_modules', [])
    vae_lora_modules = ckpt.get('vae_lora_target_modules', [])
    rank_unet = ckpt.get('rank_unet', 8)
    rank_vae = ckpt.get('rank_vae', 8)

    print(f"Model info: UNet rank={rank_unet}, VAE rank={rank_vae}")

    # Load base Stable Diffusion pipeline
    print("Loading base Stable Diffusion pipeline...")
    base_model_id = "stabilityai/sd-turbo"

    # Use appropriate dtype for device
    if device == 'cuda':
        dtype = torch.float16
    else:
        dtype = torch.float32

    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
        base_model_id,
        torch_dtype=dtype,
        safety_checker=None,
        requires_safety_checker=False
    )

    # Apply LoRA weights to UNet
    if unet_lora_modules and 'state_dict_unet' in ckpt:
        print(f"Applying UNet LoRA weights ({len(unet_lora_modules)} modules)...")
        unet_config = LoraConfig(
            r=rank_unet,
            lora_alpha=rank_unet,
            target_modules=unet_lora_modules,
            lora_dropout=0.0,
        )
        pipe.unet = inject_adapter_in_model(unet_config, pipe.unet)

        # Load state dict
        unet_state = ckpt['state_dict_unet']
        missing_keys, unexpected_keys = pipe.unet.load_state_dict(unet_state, strict=False)
        if missing_keys:
            print(f"UNet missing keys: {len(missing_keys)}")

    # Apply LoRA weights to VAE
    if vae_lora_modules and 'state_dict_vae' in ckpt:
        print(f"Applying VAE LoRA weights ({len(vae_lora_modules)} modules)...")
        vae_config = LoraConfig(
            r=rank_vae,
            lora_alpha=rank_vae,
            target_modules=vae_lora_modules,
            lora_dropout=0.0,
        )
        pipe.vae = inject_adapter_in_model(vae_config, pipe.vae)

        # Load state dict
        vae_state = ckpt['state_dict_vae']
        missing_keys, unexpected_keys = pipe.vae.load_state_dict(vae_state, strict=False)
        if missing_keys:
            print(f"VAE missing keys: {len(missing_keys)}")

    # Move to device
    pipe = pipe.to(device)

    return pipe


def preprocess_image(image_path, target_size=512):
    """
    Preprocess image for model input

    Args:
        image_path: Path to input image
        target_size: Target size for processing (should be multiple of 8)

    Returns:
        Preprocessed PIL Image
    """
    from PIL import Image, ImageOps
    import numpy as np

    print(f"Loading image: {image_path}")
    img = Image.open(image_path)

    # Convert to RGB
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Get original size
    orig_width, orig_height = img.size
    print(f"Original size: {orig_width}x{orig_height}")

    # Calculate new size maintaining aspect ratio
    aspect = orig_width / orig_height
    if aspect > 1:
        new_width = target_size
        new_height = int(target_size / aspect)
    else:
        new_height = target_size
        new_width = int(target_size * aspect)

    # Make dimensions divisible by 8
    new_width = (new_width // 8) * 8
    new_height = (new_height // 8) * 8

    # Resize image
    img = img.resize((new_width, new_height), Image.LANCZOS)
    print(f"Resized to: {new_width}x{new_height}")

    return img, (orig_width, orig_height)


def process_image(pipe, image, prompt="", negative_prompt="",
                 strength=0.7, guidance_scale=7.5, num_inference_steps=4):
    """
    Process image through the PotteryInk pipeline

    Args:
        pipe: Loaded pipeline
        image: Preprocessed PIL Image
        prompt: Generation prompt (usually empty for ink processing)
        negative_prompt: Negative prompt
        strength: Denoising strength (0-1)
        guidance_scale: Classifier-free guidance scale
        num_inference_steps: Number of inference steps

    Returns:
        Processed PIL Image
    """
    print(f"Processing with strength={strength}, steps={num_inference_steps}")

    # Default prompts for pottery ink style
    if not prompt:
        prompt = "clean black ink drawing, archaeological pottery illustration, publication quality, clear lines"
    if not negative_prompt:
        negative_prompt = "blurry, noisy, color, photograph, low quality"

    # Run inference
    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        image=image,
        strength=strength,
        guidance_scale=guidance_scale,
        num_inference_steps=num_inference_steps,
    )

    return result.images[0]


def main():
    parser = argparse.ArgumentParser(description='PotteryInk ML Inference')
    parser.add_argument('--input', '-i', required=True, help='Input image path')
    parser.add_argument('--output', '-o', required=True, help='Output image path')
    parser.add_argument('--model', '-m', required=True, help='Path to .pkl model file')
    parser.add_argument('--device', '-d', default='auto', choices=['auto', 'cpu', 'cuda', 'mps'],
                       help='Device to use for inference')
    parser.add_argument('--strength', '-s', type=float, default=0.6,
                       help='Denoising strength (0-1, default 0.6)')
    parser.add_argument('--steps', '-n', type=int, default=4,
                       help='Number of inference steps (default 4)')
    parser.add_argument('--size', type=int, default=512,
                       help='Processing size (default 512)')
    parser.add_argument('--prompt', default='', help='Generation prompt')
    parser.add_argument('--json-output', action='store_true',
                       help='Output results as JSON')

    args = parser.parse_args()

    # Setup environment
    setup_environment()

    # Determine device
    import torch
    if args.device == 'auto':
        if torch.backends.mps.is_available():
            device = 'mps'
        elif torch.cuda.is_available():
            device = 'cuda'
        else:
            device = 'cpu'
    else:
        device = args.device

    print(f"Using device: {device}")

    result_info = {
        'success': False,
        'input': args.input,
        'output': args.output,
        'model': args.model,
        'device': device,
        'error': None
    }

    try:
        # Validate input file
        if not os.path.exists(args.input):
            raise FileNotFoundError(f"Input file not found: {args.input}")

        if not os.path.exists(args.model):
            raise FileNotFoundError(f"Model file not found: {args.model}")

        # Load model
        pipe = load_potteryink_model(args.model, device)

        # Preprocess image
        image, orig_size = preprocess_image(args.input, args.size)

        # Process image
        result_image = process_image(
            pipe, image,
            prompt=args.prompt,
            strength=args.strength,
            num_inference_steps=args.steps
        )

        # Resize back to original size if needed
        if result_image.size != orig_size:
            from PIL import Image
            result_image = result_image.resize(orig_size, Image.LANCZOS)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

        # Save result
        result_image.save(args.output, 'PNG', dpi=(300, 300))
        print(f"Saved result to: {args.output}")

        result_info['success'] = True
        result_info['output_size'] = result_image.size

    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Error: {error_msg}")
        traceback.print_exc()
        result_info['error'] = error_msg

    # Output JSON if requested
    if args.json_output:
        print(json.dumps(result_info, indent=2))

    return 0 if result_info['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
