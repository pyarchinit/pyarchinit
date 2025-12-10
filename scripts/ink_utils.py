import os
import random
import time
import datetime
import gc
import warnings
from typing import Tuple, List, Dict, Optional

from PIL import Image, ImageEnhance
import torch
from torchvision import transforms
import torchvision.transforms.functional as F
from tqdm import tqdm

# Set matplotlib to use non-interactive backend for macOS compatibility
import matplotlib
matplotlib.use('Agg')  # Must be before importing pyplot
import matplotlib.pyplot as plt

# Local imports (keep unchanged for compatibility with your app)
from models import Pix2Pix_Turbo
from utils import visualize_patches, print_disclosure_reminder

# --- Device selection with MPS support ---
# Prefer MPS (Apple silicon) if available, otherwise CUDA, otherwise CPU.
if torch.backends.mps.is_available():
    device = torch.device("mps")
elif torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")

# We'll enable FP16 only when running on CUDA.
use_fp16_default = (device.type == "cuda")
print(f"⚙️ Using device: {device} ({'FP16 enabled by default' if use_fp16_default else 'FP32'})")

warnings.filterwarnings("ignore")

# --- Global model cache ---
# We cache the loaded model so run_diagnostics and process_folder/process_single_image
# don't repeatedly reload the same model (saves time and VRAM).
_GLOBAL_MODEL = None
_GLOBAL_MODEL_PATH = None


def cleanup():
    """Perform a memory cleanup. Call this after heavy GPU/MPS usage.

    This helper centralises gc.collect() and cache emptying across CUDA/MPS.
    """
    gc.collect()
    # torch.cuda.empty_cache exists only for CUDA; for MPS there is no direct equivalent,
    # but calling empty_cache on CUDA is safe to call only when CUDA is available.
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    # For MPS, we can try to clear the cache if available
    if hasattr(torch.backends.mps, 'empty_cache'):
        try:
            torch.backends.mps.empty_cache()
        except:
            pass


def _load_model_cached(model_path: str, to_device: torch.device, use_fp16: bool) -> Pix2Pix_Turbo:
    """Load Pix2Pix_Turbo model and cache it globally.

    - If the requested model_path differs from the cached one, we reload.
    - We only apply .half() when running on CUDA and when use_fp16 is True.

    Args:
        model_path: path to pretrained model
        to_device: torch.device to move the model to
        use_fp16: whether to attempt FP16 precision (effective only on CUDA)

    Returns:
        Instantiated and prepared model (set to eval)
    """
    global _GLOBAL_MODEL, _GLOBAL_MODEL_PATH

    # If we already have the exact model loaded, just return it
    if _GLOBAL_MODEL is not None and _GLOBAL_MODEL_PATH == os.path.abspath(model_path):
        return _GLOBAL_MODEL

    # Otherwise load a fresh model instance
    print(f"🔄 Loading model from: {model_path}")
    model = Pix2Pix_Turbo(pretrained_path=model_path)
    model.set_eval()

    # Move to device - for MPS, ensure we're using float32
    try:
        model.to(to_device)
        # Force float32 for MPS to avoid precision issues
        if to_device.type == "mps":
            model.float()
            print("🍎 Model set to float32 for MPS compatibility")
    except Exception as e:
        # Some model implementations may not support direct .to(mps) — handle gracefully.
        print(f"⚠️ Warning moving model to {to_device}: {e}")

    # Use FP16 only when CUDA is used and requested
    if use_fp16 and to_device.type == "cuda":
        try:
            model.half()
            print("🚀 Model converted to FP16 (half precision)")
        except Exception as e:
            print(f"⚠️ Could not convert model to FP16: {e}")
    else:
        print("ℹ️ Using FP32 precision for model (FP16 not applied)")

    _GLOBAL_MODEL = model
    _GLOBAL_MODEL_PATH = os.path.abspath(model_path)
    return _GLOBAL_MODEL


# --- Patch utilities ---

def calculate_patches(width: int, height: int, patch_size: int = 512, overlap: int = 64) -> Tuple[int, int, int]:
    """Calculate total patches, patches per row and number of rows.

    This function preserves the original signature used in other code but unifies
    the two previously duplicated implementations.

    Args:
        width: image width (px)
        height: image height (px)
        patch_size: patch size (px)
        overlap: overlap between patches (px)

    Returns:
        (total_patches, patches_per_row, num_rows)
    """
    stride = patch_size - overlap
    if stride <= 0:
        raise ValueError("patch_size must be larger than overlap")

    patches_per_row = (width - overlap) // stride
    if width > patches_per_row * stride + overlap:
        patches_per_row += 1

    num_rows = (height - overlap) // stride
    if height > num_rows * stride + overlap:
        num_rows += 1

    total_patches = patches_per_row * num_rows
    return total_patches, patches_per_row, num_rows


def get_patch_coordinates(idx: int, patches_per_row: int, num_rows: int, width: int, height: int, patch_size: int, overlap: int) -> Tuple[int, int, int, int, int, int]:
    """Return coordinates for patch index `idx`.

    The function keeps the original contract returning (x_start, y_start, x_end, y_end, row, col).
    """
    stride = patch_size - overlap
    row = idx // patches_per_row
    col = idx % patches_per_row

    x_start = col * stride
    y_start = row * stride

    if col == patches_per_row - 1:
        x_end = width
        x_start = max(0, x_end - patch_size)
    else:
        x_end = min(x_start + patch_size, width)

    if row == num_rows - 1:
        y_end = height
        y_start = max(0, y_end - patch_size)
    else:
        y_end = min(y_start + patch_size, height)

    return x_start, y_start, x_end, y_end, row, col


def create_blend_mask(patch_width: int, patch_height: int, row: int, col: int, overlap: int) -> Optional[Image.Image]:
    """Create a simple linear blending mask for a patch.

    The mask fades from 0..255 across the overlap region on top and left edges when required.
    Returns None for the top-left patch (no blending needed).
    """
    if row == 0 and col == 0:
        return None

    mask = Image.new('L', (patch_width, patch_height), 255)
    # left blend
    if col > 0:
        for k in range(overlap):
            alpha = int(255 * k / max(1, overlap))
            mask.paste(alpha, (k, 0, k + 1, patch_height))
    # top blend
    if row > 0:
        for k in range(overlap):
            alpha = int(255 * k / max(1, overlap))
            mask.paste(alpha, (0, k, patch_width, k + 1))

    return mask


# --- Processing functions (public API preserved) ---

def run_diagnostics(
    input_folder,
    model_path,
    prompt: str = "make it ready for publication",
    patch_size: int = 512,
    overlap: int = 64,
    num_sample_images: int = 5,
    contrast_values: List[float] = [0.5, 0.75, 1, 1.5, 2, 3],
    output_dir: str = 'diagnostics',
    progress_callback=None,
):
    """Run diagnostic visualisations before main processing.

    Behaviour and parameters are kept identical to the original implementation so this
    function can be used by the app without changes. The function now reuses a cached
    model instance when possible.
    """
    print("\n🔍 Running pre-processing diagnostics...")
    os.makedirs(output_dir, exist_ok=True)

    # Collect image files (including TIFF)
    image_files = []
    for ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
        image_files.extend([f for f in os.listdir(input_folder) if f.lower().endswith(ext)])

    if not image_files:
        print("❌ No images found for diagnostics!")
        return False

    num_samples = min(num_sample_images, len(image_files), 5)
    sample_images = random.sample(image_files, num_samples)

    print(f"\n📊 Running diagnostics on {num_samples} sample images...")

    # Load model once (cached)
    model = _load_model_cached(model_path, device, use_fp16_default)

    total_steps = num_samples * max(1, len(contrast_values))
    completed_steps = 0

    if progress_callback:
        try:
            progress_callback({'progress': 5, 'message': 'Starting diagnostics'})
        except Exception:
            pass

    for idx, img_file in enumerate(sample_images):
        print(f"\n🖼️ Analysing sample image {idx+1}/{num_samples}: {img_file}")
        input_path = os.path.join(input_folder, img_file)

        try:
            # 1. Patch visualisation (utility kept as-is)
            print("  📐 Generating patch visualisation...")
            patch_viz_path = os.path.join(output_dir, f'patches_{idx+1}.png')
            visualize_patches(input_path, patch_size, overlap, patch_viz_path)

            # 2. Contrast analysis
            print("  🎨 Analysing contrast effects...")
            fig, ax = plt.subplots(len(contrast_values), 2, figsize=(10, 4 * len(contrast_values)))

            for i, value in enumerate(contrast_values):
                my_img = Image.open(input_path).convert('RGB')
                img_contrast = ImageEnhance.Contrast(my_img).enhance(value)
                original_img_size = my_img.size

                ax[i, 0].imshow(img_contrast)
                ax[i, 0].set_ylabel(f"Contrast: {value}")

                print(f"    Processing contrast value {value}...")
                res_img = process_single_image(
                    input_image_path_or_pil=my_img,
                    prompt=prompt,
                    model_path=model_path,
                    patch_size=patch_size,
                    contrast_scale=value,
                    overlap=overlap,
                    use_fp16=use_fp16_default,
                    return_pil=True,
                    output_dir=None,
                )

                ax[i, 1].imshow(res_img.resize(original_img_size))

                # progress update for each contrast value processed
                completed_steps += 1
                if progress_callback:
                    try:
                        pct = int((completed_steps / total_steps) * 100)
                        progress_callback({
                            'progress': pct,
                            'message': f'Processed {completed_steps}/{total_steps} contrast tests',
                            'current_image_index': idx + 1,
                            'total_images': num_samples,
                            'current_contrast_index': i + 1,
                            'total_contrasts': len(contrast_values),
                        })
                    except Exception:
                        pass
                ax[i, 0].set_xticks([])
                ax[i, 0].set_yticks([])
                ax[i, 1].set_xticks([])
                ax[i, 1].set_yticks([])

            ax[0, 0].set_title("Input with Contrast")
            ax[0, 1].set_title("Model Output")

            contrast_path = os.path.join(output_dir, f'contrast_analysis_{idx+1}.png')
            plt.tight_layout()
            plt.savefig(contrast_path, bbox_inches='tight', dpi=300)
            plt.close()

            # 3. Summary info
            print("  📝 Generating image summary...")
            img = Image.open(input_path)
            total_patches, patches_per_row, num_rows = calculate_patches(img.width, img.height, patch_size, overlap)
            summary = {
                "filename": img_file,
                "original_size": img.size,
                "num_patches": total_patches,
                "estimated_memory": f"{(img.width * img.height * 4) / (1024 * 1024):.2f}MB",
            }

            with open(os.path.join(output_dir, f'summary_{idx+1}.txt'), 'w') as f:
                for key, value in summary.items():
                    f.write(f"{key}: {value}\n")

        except Exception as e:
            print(f"❌ Error during diagnostics for {img_file}: {str(e)}")
            continue

    print("\n✅ Diagnostics complete!")
    print(f"📁 Results saved in: {output_dir}")
    return True


def process_single_image(
    input_image_path_or_pil,
    model_path,
    prompt: str = "make it ready for publication",
    output_dir: str = 'output',
    use_fp16: bool = False,
    output_name: Optional[str] = None,
    contrast_scale: float = 1,
    return_pil: bool = False,
    patch_size: int = 512,
    overlap: int = 64,
    upscale: float = 1,
):
    """Process a single image with improved patch strategy and device support.

    The public signature is kept identical to the original to ensure app compatibility.

    Returns either a PIL.Image (if return_pil=True) or the saved output path.
    """
    print_disclosure_reminder()
    print(f"\n🚀 Initialising pix2pix_turbo processing...")
    print(f"📁 Model path: {model_path}")
    print(f"⚙️ Configuration:\n  - Device: {device}\n  - FP16 mode: {use_fp16}\n  - Patch size: {patch_size}px\n  - Overlap: {overlap}px\n  - Contrast scale: {contrast_scale}\n  - Prompt: {prompt}")

    if output_dir is not None:
        os.makedirs(output_dir, exist_ok=True)

    # Load cached model (or load fresh if path changed)
    model = _load_model_cached(model_path, device, use_fp16)

    # Load input image
    if isinstance(input_image_path_or_pil, str):
        input_image = Image.open(input_image_path_or_pil).convert('RGB')
    else:
        input_image = input_image_path_or_pil.convert('RGB')

    if input_image.width < patch_size or input_image.height < patch_size:
        new_width = max(input_image.width, patch_size)
        new_height = max(input_image.height, patch_size)
        padded_image = Image.new('RGB', (new_width, new_height), (255, 255, 255))
        padded_image.paste(input_image, (0, 0))
        input_image = padded_image
        print(f"  - Image padded to: {input_image.size}")

        ############ end padding #############################
    
    

    # Upscale/downscale logic preserved
    if upscale >= 1:
        new_width = round(input_image.width * upscale)
        new_height = round(input_image.height * upscale)
        input_image = input_image.resize((new_width, new_height), Image.LANCZOS)
        print(f"  - Upscaled size: {input_image.size}")
    else:
        new_width = max(1, round(input_image.width * upscale))
        new_height = max(1, round(input_image.height * upscale))
        input_image = input_image.resize((new_width, new_height), Image.BICUBIC)
        print(f"  - Downscaled size: {input_image.size}")

    original_size = (input_image.width, input_image.height)

    # Ensure dimensions are multiples of 4 for model stability
    width = input_image.width - input_image.width % 4
    height = input_image.height - input_image.height % 4
    input_image = input_image.resize((width, height), Image.BICUBIC)

    output_image = Image.new('RGB', (width, height))

    total_patches, patches_per_row, num_rows = calculate_patches(width, height, patch_size, overlap)

    try:
        with torch.no_grad():
            for idx in tqdm(range(total_patches), desc=f"Processing image"):
                x_start, y_start, x_end, y_end, row, col = get_patch_coordinates(
                    idx, patches_per_row, num_rows, width, height, patch_size, overlap
                )

                patch = input_image.crop((x_start, y_start, x_end, y_end))
                patch = ImageEnhance.Contrast(patch).enhance(contrast_scale)

                # Convert to tensor and ensure proper dtype for MPS
                c_t = F.to_tensor(patch).unsqueeze(0)
                
                # Ensure float32 for MPS, handle FP16 only for CUDA
                if device.type == "mps":
                    c_t = c_t.float().to(device)
                elif device.type == "cuda" and use_fp16:
                    c_t = c_t.half().to(device)
                else:
                    c_t = c_t.to(device)

                # Run model: assume model callable signature model(tensor, prompt) -> tensor
                output_patch = model(c_t, prompt)

                # Convert model output to PIL - ensure CPU and float32 for processing
                output_tensor = output_patch[0].cpu().float() * 0.5 + 0.5
                patch_pil = transforms.ToPILImage()(output_tensor)

                mask = create_blend_mask(x_end - x_start, y_end - y_start, row, col, overlap)
                output_image.paste(patch_pil, (x_start, y_start), mask)

                # tidy up per-iteration tensors
                del c_t, output_patch, output_tensor
                cleanup()

    except Exception as e:
        print(f"\n❌ Error during processing: {str(e)}")
        print(f"🔍 Debug info - Device: {device}, Use FP16: {use_fp16}")
        raise
    finally:
        print("\n🧹 Cleaning up resources...")
        cleanup()

    # Return or save
    if return_pil:
        print("\n✅ Processing complete! Returning PIL image \n ---------------------------------")
        # restore original size
        output_image = output_image.resize(original_size, Image.BICUBIC)
        return output_image
    else:
        if isinstance(input_image_path_or_pil, str):
            bname = os.path.basename(input_image_path_or_pil)
        else:
            bname = output_name if output_name else "output.png"
        output_path = os.path.join(output_dir, bname)

        # Back to original size
        output_image = output_image.resize(original_size, Image.BICUBIC)
        output_image = output_image.convert('L')
        output_image = ImageEnhance.Contrast(output_image).enhance(1.5)
        output_image.save(output_path)
        print(f"\n✅ Processing complete! Saving to: {output_path}")
        print("💾 Image saved successfully")
        return output_path


def process_folder(
    input_folder,
    model_path,
    prompt: str = "make it ready for publication",
    output_dir: str = 'output',
    use_fp16: bool = False,
    contrast_scale: float = 1,
    patch_size: int = 512,
    overlap: int = 64,
    file_extensions: Tuple[str, ...] = ('.jpg', '.jpeg', '.png', '.tif', '.tiff'),
    upscale: float = 1,
    progress_callback=None,
    export_elements: bool = True,
    export_svg: bool = True,
):
    """Process a folder of images using improved patch strategy.

    Public API kept identical. The function now reuses a cached model instance
    and centralises logging and cleanup behaviour.
    """
    print_disclosure_reminder()
    print(f"\n🚀 Initialising batch processing with pix2pix_turbo...")
    print(f"📁 Input folder: {input_folder}\n📁 Model path: {model_path}\n📁 Output directory: {output_dir}")
    print(f"\n⚙️ Configuration:\n  - FP16 mode: {use_fp16}\n  - Patch size: {patch_size}px\n  - Overlap: {overlap}px\n  - Contrast scale: {contrast_scale}\n  - Upscale: {upscale}x\n  - Prompt: {prompt}")

    os.makedirs(output_dir, exist_ok=True)
    log_dir = os.path.join(output_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Gather files
    image_files = []
    for ext in file_extensions:
        image_files.extend([f for f in os.listdir(input_folder) if f.lower().endswith(ext)])

    if not image_files:
        print("❌ No images found in input folder!")
        return

    print(f"\n📸 Found {len(image_files)} images to process")

    # Load model once (cached)
    model = _load_model_cached(model_path, device, use_fp16)

    # Logging setup
    successful_conversions = 0
    failed_conversions = 0
    failed_files: List[str] = []
    processing_times: List[float] = []

    log_file = os.path.join(log_dir, f'processing_log_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')

    with open(log_file, 'w') as log:
        log.write(f"Processing started at: {datetime.datetime.now()}\n")
        log.write("Configuration:\n")
        log.write(f"- Input folder: {input_folder}\n")
        log.write(f"- Output directory: {output_dir}\n")
        log.write(f"- Model path: {model_path}\n")
        log.write(f"- FP16 mode: {use_fp16 and device.type == 'cuda'}\n")
        log.write(f"- Patch size: {patch_size}px\n")
        log.write(f"- Overlap: {overlap}px\n")
        log.write(f"- Contrast scale: {contrast_scale}\n")
        log.write(f"- Upscale: {upscale}x\n")
        log.write(f"- Prompt: {prompt}\n\n")

        for idx, image_file in enumerate(image_files, 1):
            input_path = os.path.join(input_folder, image_file)
            print(f"\n\n🖼️ Processing image {idx}/{len(image_files)}: {image_file}")
            log.write(f"\nProcessing image {idx}/{len(image_files)}: {image_file}\n")
            
            # Update progress if callback provided
            if progress_callback:
                progress = (idx - 1) / len(image_files)
                status_text = f"Processing image {idx}/{len(image_files)}: {image_file}"
                try:
                    progress_callback(progress, status_text, 0, f"Starting patch processing...")
                except Exception as e:
                    print(f"Warning: Progress callback error: {e}")

            start_time = time.time()

            try:
                input_image = Image.open(input_path).convert('RGB')

                ### pad image if needed ##############################
                if input_image.width < patch_size or input_image.height < patch_size:
                    new_width = max(input_image.width, patch_size)
                    new_height = max(input_image.height, patch_size)
                    padded_image = Image.new('RGB', (new_width, new_height), (255, 255, 255))
                    padded_image.paste(input_image, (0, 0))
                    input_image = padded_image
                    print(f"  - Image padded to: {input_image.size}")

                ############ end padding ##############################



                original_size = (input_image.width, input_image.height)
                print(f"  - Original size: {original_size}")
                log.write(f"Original size: {original_size}\n")

                # Upscale / downscale
                if upscale >= 1:
                    new_width = round(input_image.width * upscale)
                    new_height = round(input_image.height * upscale)
                    input_image = input_image.resize((new_width, new_height), Image.LANCZOS)
                    print(f"  - Upscaled size: {input_image.size}")
                else:
                    new_width = max(1, round(input_image.width * upscale))
                    new_height = max(1, round(input_image.height * upscale))
                    input_image = input_image.resize((new_width, new_height), Image.BICUBIC)
                    print(f"  - Downscaled size: {input_image.size}")

                # Ensure multiples of 4
                width = input_image.width - input_image.width % 4
                height = input_image.height - input_image.height % 4
                input_image = input_image.resize((width, height), Image.LANCZOS)
                print(f"  - Processing size: ({width}, {height})")
                log.write(f"Processing size: ({width}, {height})\n")

                output_image = Image.new('RGB', (width, height))

                total_patches, patches_per_row, num_rows = calculate_patches(width, height, patch_size, overlap)
                print(f"🧩 Processing {total_patches} patches ({patches_per_row}x{num_rows})")
                log.write(f"Patches: {total_patches} ({patches_per_row}x{num_rows})\n")

                with torch.no_grad():
                    for patch_idx in tqdm(range(total_patches), desc=f"Processing {image_file}"):
                        # Update progress for each patch if callback provided
                        if progress_callback:
                            overall_progress = (idx - 1) / len(image_files)
                            patch_progress = patch_idx / total_patches
                            patch_status = f"Patch {patch_idx+1}/{total_patches}"
                            try:
                                progress_callback(overall_progress, f"Image {idx}/{len(image_files)}", patch_progress, patch_status)
                            except Exception as e:
                                print(f"Warning: Progress callback error: {e}")
                        
                        x_start, y_start, x_end, y_end, row, col = get_patch_coordinates(
                            patch_idx, patches_per_row, num_rows, width, height, patch_size, overlap
                        )

                        patch = input_image.crop((x_start, y_start, x_end, y_end))
                        patch = ImageEnhance.Contrast(patch).enhance(contrast_scale)

                        # Convert to tensor and ensure proper dtype for MPS
                        c_t = F.to_tensor(patch).unsqueeze(0)
                        
                        # Ensure float32 for MPS, handle FP16 only for CUDA
                        if device.type == "mps":
                            c_t = c_t.float().to(device)
                        elif device.type == "cuda" and use_fp16:
                            c_t = c_t.half().to(device)
                        else:
                            c_t = c_t.to(device)

                        output_patch = model(c_t, prompt)
                        
                        # Convert model output to PIL - ensure CPU and float32 for processing
                        output_tensor = output_patch[0].cpu().float() * 0.5 + 0.5
                        patch_pil = transforms.ToPILImage()(output_tensor)

                        mask = create_blend_mask(x_end - x_start, y_end - y_start, row, col, overlap)
                        output_image.paste(patch_pil, (x_start, y_start), mask)

                        del c_t, output_patch, output_tensor
                        cleanup()

                # Save output image (back to original size)
                output_filename = os.path.join(output_dir, image_file)
                output_image = output_image.resize(original_size, Image.BICUBIC)
                output_image = output_image.convert('L')
                output_image = ImageEnhance.Contrast(output_image).enhance(1.5)
                output_image.save(output_filename)

                end_time = time.time()
                processing_time = end_time - start_time
                processing_times.append(processing_time)

                print(f"✅ Saved: {output_filename}")
                print(f"⏱️ Processing time: {processing_time:.2f}s")
                log.write(f"Processing time: {processing_time:.2f}s\n")
                log.write("Status: Success\n")

                successful_conversions += 1
                
                # Update progress to complete this image
                if progress_callback:
                    progress = idx / len(image_files)
                    status_text = f"Completed {idx}/{len(image_files)} images"
                    try:
                        progress_callback(progress, status_text, 1.0, "All patches completed")
                    except Exception as e:
                        print(f"Warning: Progress callback error: {e}")

            except Exception as e:
                print(f"❌ Error processing {image_file}: {str(e)}")
                log.write(f"Status: Failed - {str(e)}\n")
                failed_conversions += 1
                failed_files.append(image_file)
                
                # Update progress even on error
                if progress_callback:
                    progress = idx / len(image_files)
                    status_text = f"Error on image {idx}/{len(image_files)}: {image_file}"
                    try:
                        progress_callback(progress, status_text)
                    except Exception as e:
                        print(f"Warning: Progress callback error: {e}")
                    
                continue

            finally:
                cleanup()

        # Final stats
        log.write("\n\nFinal Statistics:\n")
        log.write(f"Successfully processed: {successful_conversions} images\n")
        log.write(f"Failed to process: {failed_conversions} images\n")
        if processing_times:
            log.write(f"Average processing time: {sum(processing_times)/len(processing_times):.2f}s\n")
        if failed_files:
            log.write("\nFailed files:\n")
            for file in failed_files:
                log.write(f"- {file}\n")

    # Print summary to console
    print("\n📊 Processing Summary:")
    print(f"  ✅ Successfully processed: {successful_conversions} images")
    print(f"  ❌ Failed to process: {failed_conversions} images")
    if processing_times:
        print(f"  ⏱️ Average processing time: {sum(processing_times)/len(processing_times):.2f}s")
    if failed_files:
        print("\n⚠️ Failed files:")
        for file in failed_files:
            print(f"  - {file}")

    print(f"\n📝 Detailed log saved to: {log_file}")

    # Generate comparisons
    print("\n📊 Generating comparison visualisations...")
    comparison_dir = os.path.join(output_dir, 'comparisons')
    os.makedirs(comparison_dir, exist_ok=True)

    for idx, image_file in enumerate(image_files, 1):
        if image_file not in failed_files:
            try:
                print(f"\rGenerating comparison {idx}/{len(image_files)}", end="")

                input_path = os.path.join(input_folder, image_file)
                output_path = os.path.join(output_dir, image_file)

                fig, ax = plt.subplots(1, 2, figsize=(15, 7))
                image_input = Image.open(input_path).convert('RGB')
                ax[0].imshow(image_input)
                ax[0].axis('off')
                ax[0].set_title('Original Image', pad=20)

                image_output = Image.open(output_path)
                ax[1].imshow(image_output, cmap='gray')
                ax[1].axis('off')
                ax[1].set_title('Processed Image', pad=20)

                plt.suptitle(f'Comparison for {image_file}\nSize: {image_input.size}', y=1.05)
                comparison_path = os.path.join(comparison_dir, f'comparison_{image_file}')
                plt.savefig(comparison_path, bbox_inches='tight', dpi=300, pad_inches=0.5)
                plt.close()

            except Exception as e:
                print(f"\n❌ Error generating comparison for {image_file}: {str(e)}")
                continue

    print(f"\n✅ Comparison visualisations saved in: {comparison_dir}")
    
    # Export additional formats if requested
    if export_elements or export_svg:
        print("\n🎨 Generating advanced exports...")
        from export_utils import export_all_formats, create_enhanced_comparison
        
        enhanced_comparisons = []
        exported_elements = []
        exported_svgs = []
        
        for idx, image_file in enumerate(image_files, 1):
            if image_file not in failed_files:
                try:
                    print(f"\rExporting formats for {image_file} ({idx}/{len(image_files)})", end="")
                    
                    output_path = os.path.join(output_dir, image_file)
                    input_path = os.path.join(input_folder, image_file)
                    
                    # Export in multiple formats
                    export_results = export_all_formats(output_path, output_dir)
                    
                    # Create enhanced comparison with elements
                    if export_results['elements']:
                        enhanced_comp = create_enhanced_comparison(
                            input_path, output_path, 
                            export_results['elements'], output_dir
                        )
                        if enhanced_comp:
                            enhanced_comparisons.append(enhanced_comp)
                    
                    exported_elements.extend(export_results['elements'])
                    if export_results['svg']:
                        exported_svgs.append(export_results['svg'])
                    exported_svgs.extend(export_results['elements_svg'])
                    
                except Exception as e:
                    print(f"\n⚠️ Error exporting formats for {image_file}: {str(e)}")
                    continue
        
        print(f"\n✅ Advanced exports complete!")
        if exported_elements:
            print(f"  📦 Extracted {len(exported_elements)} pottery elements")
        if exported_svgs:
            print(f"  🎨 Created {len(exported_svgs)} SVG files")
        if enhanced_comparisons:
            print(f"  🖼️ Generated {len(enhanced_comparisons)} enhanced comparisons")

    results = {
        'successful': successful_conversions,
        'failed': failed_conversions,
        'failed_files': failed_files,
        'average_time': sum(processing_times)/len(processing_times) if processing_times else 0,
        'log_file': log_file,
        'comparison_dir': comparison_dir,
        'exported_elements': exported_elements if export_elements else [],
        'exported_svgs': exported_svgs if export_svg else [],
        'enhanced_comparisons': enhanced_comparisons if export_elements else []
    }

    return results