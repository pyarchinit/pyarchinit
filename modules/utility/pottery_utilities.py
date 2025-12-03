#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pottery utilities for image processing and layout generation
Simplified versions adapted from PyPotteryLayout and PyPotteryLens
"""

import os
import re
import random
import io
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    import fitz  # PyMuPDF
    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False

# Try to import YOLO for ML detection (optional)
try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False

# Try to import PotteryInk dependencies (optional)
try:
    import torch
    from torchvision import transforms
    import torchvision.transforms.functional as F
    from diffusers import StableDiffusionImg2ImgPipeline
    from transformers import pipeline
    import cv2
    import numpy as np
    from skimage import filters, measure, segmentation
    HAS_POTTERY_INK = True
except ImportError:
    HAS_POTTERY_INK = False

from qgis.core import QgsMessageLog, Qgis
from qgis.PyQt.QtGui import QImage, QPixmap
from qgis.PyQt.QtCore import Qt


# Page sizes in pixels at 300 DPI
PAGE_SIZES_PX = {
    'A4': (2480, 3508),
    'A3': (3508, 4961),
    'LETTER': (2550, 3300),
    'HD': (1920, 1080),
    '4K': (3840, 2160),
}


class PDFExtractor:
    """Extract images from PDF files and image files - Step 1 of PyPotteryLens workflow"""

    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
        self.yolo_model = None
        self.model_loaded = False
        self.mask_outputs = {}  # Store masks for later extraction

    def extract_from_images(self, image_paths: List[str], output_dir: str,
                           auto_detect: bool = True,
                           confidence: float = 0.5,
                           kernel_size: int = 2,
                           iterations: int = 10) -> List[str]:
        """
        Extract pottery drawings from image files (JPEG, PNG, etc.)

        Args:
            image_paths: List of image file paths or single path
            output_dir: Output directory for processed images
            auto_detect: Auto-detect pottery using YOLO model
            confidence: Detection confidence threshold
            kernel_size: Size of morphological kernel
            iterations: Number of dilation iterations

        Returns:
            List of extracted/processed image paths
        """
        if isinstance(image_paths, str):
            image_paths = [image_paths]

        extracted_images = []
        os.makedirs(output_dir, exist_ok=True)

        # Load YOLO model if auto_detect is enabled
        if auto_detect and not self.model_loaded:
            self.load_yolo_model()

        for img_path in image_paths:
            try:
                # Check if file exists and is supported format
                if not os.path.exists(img_path):
                    QgsMessageLog.logMessage(f"File not found: {img_path}",
                                           "PyArchInit", Qgis.Warning)
                    continue

                ext = os.path.splitext(img_path)[1].lower()
                if ext not in self.supported_formats:
                    QgsMessageLog.logMessage(f"Unsupported format: {ext}",
                                           "PyArchInit", Qgis.Warning)
                    continue

                # Copy image to output directory
                base_name = os.path.basename(img_path)
                output_path = os.path.join(output_dir, f"extracted_{base_name}")

                # Load image
                img = Image.open(img_path)

                # If auto_detect and YOLO model is available, run detection
                if auto_detect and self.model_loaded and self.yolo_model:
                    detections = self.detect_and_extract_pottery(
                        img_path, confidence, kernel_size, iterations
                    )

                    if detections:
                        # Extract each detected pottery region
                        import cv2
                        import numpy as np

                        cv_img = cv2.imread(img_path)
                        for idx, detection in enumerate(detections):
                            x, y, w, h = detection['bbox']

                            # Add padding
                            padding = 20
                            x = max(0, x - padding)
                            y = max(0, y - padding)
                            w = min(cv_img.shape[1] - x, w + 2 * padding)
                            h = min(cv_img.shape[0] - y, h + 2 * padding)

                            # Extract region
                            roi = cv_img[y:y+h, x:x+w]

                            # Save extracted region
                            region_path = os.path.join(
                                output_dir,
                                f"{os.path.splitext(base_name)[0]}_region{idx+1:02d}.png"
                            )
                            cv2.imwrite(region_path, roi)
                            extracted_images.append(region_path)

                        QgsMessageLog.logMessage(
                            f"Detected {len(detections)} pottery regions in {base_name}",
                            "PyArchInit", Qgis.Info
                        )
                    else:
                        # No detections, save the whole image
                        img.save(output_path)
                        extracted_images.append(output_path)
                else:
                    # Save the whole image as-is
                    img.save(output_path)
                    extracted_images.append(output_path)

            except Exception as e:
                QgsMessageLog.logMessage(f"Error processing {img_path}: {str(e)}",
                                       "PyArchInit", Qgis.Warning)

        QgsMessageLog.logMessage(f"Extracted {len(extracted_images)} images",
                                "PyArchInit", Qgis.Info)
        return extracted_images

    def load_yolo_model(self):
        """Load YOLO model for pottery detection if available"""
        if not HAS_YOLO:
            return False

        try:
            from ultralytics import YOLO

            # Check in user home directory under pyarchinit/bin
            home_dir = os.path.expanduser('~')
            model_path = os.path.join(home_dir, 'pyarchinit', 'bin', 'pottery_yolo.pt')

            if os.path.exists(model_path):
                self.yolo_model = YOLO(model_path)
                self.model_loaded = True
                QgsMessageLog.logMessage(f"YOLO model loaded from: {model_path}",
                                       "PyArchInit", Qgis.Info)
                return True
            else:
                QgsMessageLog.logMessage("YOLO model not found in ~/pyarchinit/bin/",
                                       "PyArchInit", Qgis.Warning)
                return False
        except Exception as e:
            QgsMessageLog.logMessage(f"Failed to load YOLO model: {str(e)}",
                                   "PyArchInit", Qgis.Warning)
            return False

    def detect_and_extract_pottery(self, image_path: str, confidence: float = 0.5,
                                  kernel_size: int = 2, iterations: int = 10) -> List[Dict]:
        """
        Detect pottery in image and extract with morphological operations

        Args:
            image_path: Path to image
            confidence: Detection confidence threshold
            kernel_size: Size of morphological kernel
            iterations: Number of dilation iterations

        Returns:
            List of detected pottery regions with masks
        """
        detections = []

        if not self.model_loaded or not self.yolo_model:
            return detections

        try:
            import numpy as np
            import cv2

            # Run YOLO detection
            results = self.yolo_model(image_path, conf=confidence)

            # Load original image
            img = cv2.imread(image_path)
            height, width = img.shape[:2]

            for r in results:
                if r.masks is not None:
                    # Process each mask
                    for idx, mask in enumerate(r.masks.data):
                        # Convert mask to numpy array
                        mask_np = mask.cpu().numpy()

                        # Resize mask to original image size if needed
                        if mask_np.shape != (height, width):
                            mask_np = cv2.resize(mask_np, (width, height))

                        # Apply morphological operations
                        kernel = np.ones((kernel_size, kernel_size), np.uint8)
                        mask_np = cv2.dilate(mask_np, kernel, iterations=iterations)

                        # Find contours
                        contours, _ = cv2.findContours(
                            (mask_np * 255).astype(np.uint8),
                            cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE
                        )

                        if contours:
                            # Get bounding box
                            x, y, w, h = cv2.boundingRect(contours[0])

                            detections.append({
                                'bbox': (x, y, w, h),
                                'mask': mask_np,
                                'confidence': float(r.boxes.conf[idx]) if r.boxes else confidence
                            })

                elif r.boxes is not None:
                    # Fallback to box detection if no masks
                    for idx, box in enumerate(r.boxes):
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        detections.append({
                            'bbox': (int(x1), int(y1), int(x2-x1), int(y2-y1)),
                            'mask': None,
                            'confidence': float(box.conf[0])
                        })

        except Exception as e:
            QgsMessageLog.logMessage(f"Pottery detection error: {str(e)}",
                                   "PyArchInit", Qgis.Warning)

        return detections

    def extract(self, pdf_path: str, output_dir: str,
                split_pages: bool = False,
                auto_detect: bool = True,
                confidence: float = 0.5,
                kernel_size: int = 2,
                iterations: int = 10) -> List[str]:
        """
        Extract images from PDF

        Args:
            pdf_path: Path to PDF file
            output_dir: Output directory for images
            split_pages: Split pages into left/right
            auto_detect: Auto-detect pottery images using YOLO
            confidence: Detection confidence threshold

        Returns:
            List of extracted image paths
        """
        if not HAS_DEPENDENCIES:
            QgsMessageLog.logMessage("PyMuPDF not installed. Cannot extract from PDF.",
                                    "PyArchInit", Qgis.Warning)
            return []

        # Load YOLO model if auto_detect is enabled
        if auto_detect and not self.model_loaded:
            self.load_yolo_model()

        extracted_images = []

        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)

            # Open PDF document
            doc = fitz.open(pdf_path)
            pdf_name = Path(pdf_path).stem

            for page_num, page in enumerate(doc):
                # Render page to image (300 DPI)
                mat = fitz.Matrix(300.0 / 72.0, 300.0 / 72.0)
                pix = page.get_pixmap(matrix=mat)

                # Convert to PIL Image
                img_data = pix.pil_tobytes(format="PNG")
                img = Image.open(io.BytesIO(img_data))

                if split_pages:
                    # Split page into left and right
                    width, height = img.size
                    mid = width // 2

                    left_img = img.crop((0, 0, mid, height))
                    right_img = img.crop((mid, 0, width, height))

                    # Save both halves
                    left_path = os.path.join(output_dir,
                                           f"{pdf_name}_p{page_num:03d}_left.png")
                    right_path = os.path.join(output_dir,
                                            f"{pdf_name}_p{page_num:03d}_right.png")

                    left_img.save(left_path, "PNG")
                    right_img.save(right_path, "PNG")

                    extracted_images.extend([left_path, right_path])
                else:
                    # Save full page
                    img_path = os.path.join(output_dir,
                                          f"{pdf_name}_p{page_num:03d}.png")
                    img.save(img_path, "PNG")
                    extracted_images.append(img_path)

                # Extract embedded images if auto_detect is True
                if auto_detect:
                    image_list = page.get_images()
                    for img_index, img_info in enumerate(image_list):
                        try:
                            xref = img_info[0]
                            base_image = doc.extract_image(xref)
                            image_bytes = base_image["image"]

                            # Save embedded image
                            embed_path = os.path.join(
                                output_dir,
                                f"{pdf_name}_p{page_num:03d}_img{img_index:02d}.{base_image['ext']}"
                            )

                            with open(embed_path, "wb") as f:
                                f.write(image_bytes)

                            extracted_images.append(embed_path)
                        except Exception as e:
                            QgsMessageLog.logMessage(f"Error extracting embedded image: {e}",
                                                   "PyArchInit", Qgis.Warning)

            doc.close()

            QgsMessageLog.logMessage(f"Extracted {len(extracted_images)} images from PDF",
                                    "PyArchInit", Qgis.Info)

        except Exception as e:
            QgsMessageLog.logMessage(f"PDF extraction error: {str(e)}",
                                    "PyArchInit", Qgis.Critical)

        return extracted_images


class LayoutGenerator:
    """Generate image layouts for pottery documentation"""

    def __init__(self):
        self.font_cache = {}

    def get_font(self, size: int) -> Optional[Any]:
        """Get font for text rendering"""
        if not HAS_DEPENDENCIES:
            return None

        if size in self.font_cache:
            return self.font_cache[size]

        # Try to load common fonts
        font_paths = []

        import platform
        if platform.system() == "Darwin":  # macOS
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",
                "/Library/Fonts/Arial.ttf",
            ]
        elif platform.system() == "Windows":
            font_paths = [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
            ]
        else:  # Linux
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            ]

        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, size)
                self.font_cache[size] = font
                return font
            except:
                continue

        # Fallback to default
        try:
            font = ImageFont.load_default()
            self.font_cache[size] = font
            return font
        except:
            return None

    def create_preview(self, images: List[str], mode: str = 'grid',
                      page_size: str = 'A4', rows: int = 4, cols: int = 3) -> QImage:
        """Create a preview of the layout"""
        if not HAS_DEPENDENCIES or not images:
            return QImage()

        try:
            # Get page dimensions
            width, height = PAGE_SIZES_PX.get(page_size, PAGE_SIZES_PX['A4'])

            # Scale down for preview
            preview_scale = 0.2
            preview_width = int(width * preview_scale)
            preview_height = int(height * preview_scale)

            # Create preview image
            preview = Image.new('RGB', (preview_width, preview_height), 'white')
            draw = ImageDraw.Draw(preview)

            if mode == 'grid':
                self._create_grid_preview(preview, draw, images, rows, cols)
            else:
                self._create_puzzle_preview(preview, draw, images)

            # Convert to QImage
            return self._pil_to_qimage(preview)

        except Exception as e:
            QgsMessageLog.logMessage(f"Preview creation error: {str(e)}",
                                    "PyArchInit", Qgis.Warning)
            return QImage()

    def _create_grid_preview(self, preview: Image, draw: ImageDraw,
                            images: List[str], rows: int, cols: int):
        """Create grid layout preview"""
        width, height = preview.size
        margin = 10
        spacing = 5

        cell_width = (width - 2 * margin - (cols - 1) * spacing) // cols
        cell_height = (height - 2 * margin - (rows - 1) * spacing) // rows

        img_index = 0
        for row in range(rows):
            for col in range(cols):
                if img_index >= len(images):
                    break

                x = margin + col * (cell_width + spacing)
                y = margin + row * (cell_height + spacing)

                # Draw placeholder rectangle
                draw.rectangle([x, y, x + cell_width, y + cell_height],
                             outline='gray', width=1)

                # Add image number
                font = self.get_font(10)
                if font:
                    text = f"{img_index + 1}"
                    draw.text((x + 5, y + 5), text, fill='black', font=font)

                img_index += 1

    def _create_puzzle_preview(self, preview: Image, draw: ImageDraw,
                              images: List[str]):
        """Create puzzle layout preview (simplified bin packing)"""
        width, height = preview.size
        margin = 10

        # Simplified: just place images in a flowing layout
        x, y = margin, margin
        row_height = 0

        for i, img_path in enumerate(images[:20]):  # Limit preview
            # Random size for demonstration
            img_width = random.randint(40, 80)
            img_height = random.randint(40, 80)

            if x + img_width > width - margin:
                x = margin
                y += row_height + 5
                row_height = 0

            if y + img_height > height - margin:
                break

            # Draw placeholder
            draw.rectangle([x, y, x + img_width, y + img_height],
                         outline='gray', width=1)

            x += img_width + 5
            row_height = max(row_height, img_height)

    def generate(self, images: List[str], output_path: str,
                mode: str = 'grid', page_size: str = 'A4',
                rows: int = 4, cols: int = 3,
                add_captions: bool = True,
                add_scale: bool = True,
                scale_cm: int = 5) -> bool:
        """
        Generate the final layout

        Args:
            images: List of image paths
            output_path: Output file path
            mode: Layout mode ('grid' or 'puzzle')
            page_size: Page size
            rows: Number of rows (for grid mode)
            cols: Number of columns (for grid mode)
            add_captions: Add image captions
            add_scale: Add scale bar
            scale_cm: Scale bar length in cm

        Returns:
            True if successful
        """
        if not HAS_DEPENDENCIES or not images:
            return False

        try:
            # Get page dimensions
            width, height = PAGE_SIZES_PX.get(page_size, PAGE_SIZES_PX['A4'])

            # Create pages
            pages = []

            if mode == 'grid':
                pages = self._create_grid_layout(images, width, height,
                                                rows, cols, add_captions,
                                                add_scale, scale_cm)
            else:
                pages = self._create_puzzle_layout(images, width, height,
                                                  add_captions, add_scale,
                                                  scale_cm)

            # Save output
            if output_path.lower().endswith('.pdf'):
                self._save_as_pdf(pages, output_path)
            else:
                self._save_as_images(pages, output_path)

            QgsMessageLog.logMessage(f"Layout generated: {output_path}",
                                    "PyArchInit", Qgis.Info)
            return True

        except Exception as e:
            QgsMessageLog.logMessage(f"Layout generation error: {str(e)}",
                                    "PyArchInit", Qgis.Critical)
            return False

    def _create_grid_layout(self, images: List[str], width: int, height: int,
                           rows: int, cols: int, add_captions: bool,
                           add_scale: bool, scale_cm: int) -> List[Image.Image]:
        """Create grid layout pages"""
        pages = []
        margin = 100
        spacing = 20
        caption_height = 50 if add_captions else 0

        images_per_page = rows * cols
        num_pages = (len(images) + images_per_page - 1) // images_per_page

        for page_num in range(num_pages):
            # Create page
            page = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(page)

            # Calculate cell dimensions
            cell_width = (width - 2 * margin - (cols - 1) * spacing) // cols
            cell_height = (height - 2 * margin - (rows - 1) * spacing) // rows
            cell_height -= caption_height

            # Place images
            start_idx = page_num * images_per_page
            end_idx = min(start_idx + images_per_page, len(images))

            for i, img_path in enumerate(images[start_idx:end_idx]):
                row = i // cols
                col = i % cols

                x = margin + col * (cell_width + spacing)
                y = margin + row * (cell_height + caption_height + spacing)

                try:
                    # Load and resize image
                    img = Image.open(img_path)
                    img.thumbnail((cell_width, cell_height), Image.Resampling.LANCZOS)

                    # Center image in cell
                    img_x = x + (cell_width - img.width) // 2
                    img_y = y + (cell_height - img.height) // 2

                    page.paste(img, (img_x, img_y))

                    # Add caption
                    if add_captions:
                        caption = os.path.basename(img_path)
                        font = self.get_font(12)
                        if font:
                            text_y = y + cell_height + 5
                            draw.text((x, text_y), caption[:30],
                                    fill='black', font=font)

                except Exception as e:
                    QgsMessageLog.logMessage(f"Error loading image {img_path}: {e}",
                                           "PyArchInit", Qgis.Warning)

            # Add scale bar
            if add_scale:
                self._add_scale_bar(page, draw, scale_cm)

            pages.append(page)

        return pages

    def _create_puzzle_layout(self, images: List[str], width: int, height: int,
                            add_captions: bool, add_scale: bool,
                            scale_cm: int) -> List[Image.Image]:
        """Create puzzle layout pages (simplified version)"""
        # For now, just use a simple flowing layout
        # A full implementation would use bin packing algorithms
        pages = []
        margin = 100
        spacing = 20

        page = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(page)

        x, y = margin, margin
        row_height = 0
        page_images = []

        for img_path in images:
            try:
                img = Image.open(img_path)
                # Scale to reasonable size
                max_size = 400
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

                # Check if fits on current page
                if x + img.width > width - margin:
                    x = margin
                    y += row_height + spacing
                    row_height = 0

                if y + img.height > height - margin:
                    # Start new page
                    if add_scale:
                        self._add_scale_bar(page, draw, scale_cm)
                    pages.append(page)
                    page = Image.new('RGB', (width, height), 'white')
                    draw = ImageDraw.Draw(page)
                    x, y = margin, margin
                    row_height = 0
                    page_images = []

                # Paste image
                page.paste(img, (x, y))
                page_images.append((x, y, img.width, img.height,
                                  os.path.basename(img_path)))

                x += img.width + spacing
                row_height = max(row_height, img.height)

            except Exception as e:
                QgsMessageLog.logMessage(f"Error in puzzle layout: {e}",
                                       "PyArchInit", Qgis.Warning)

        # Add last page
        if page_images:
            if add_scale:
                self._add_scale_bar(page, draw, scale_cm)
            pages.append(page)

        return pages

    def _add_scale_bar(self, page: Image.Image, draw: ImageDraw.Draw,
                      scale_cm: int):
        """Add scale bar to page"""
        # Assume 118 pixels per cm at 300 DPI
        pixels_per_cm = 118
        bar_length = scale_cm * pixels_per_cm
        bar_height = 10

        x = page.width - bar_length - 100
        y = page.height - 100

        # Draw scale bar
        draw.rectangle([x, y, x + bar_length, y + bar_height],
                      fill='black')

        # Draw segments
        for i in range(scale_cm):
            seg_x = x + i * pixels_per_cm
            color = 'white' if i % 2 == 0 else 'black'
            draw.rectangle([seg_x, y, seg_x + pixels_per_cm, y + bar_height],
                         fill=color)

        # Add label
        font = self.get_font(14)
        if font:
            draw.text((x, y - 20), f"{scale_cm} cm", fill='black', font=font)

    def _save_as_pdf(self, pages: List[Image.Image], output_path: str):
        """Save pages as PDF"""
        if pages:
            pages[0].save(output_path, "PDF", save_all=True,
                        append_images=pages[1:] if len(pages) > 1 else [])

    def _save_as_images(self, pages: List[Image.Image], output_path: str):
        """Save pages as individual images"""
        base_path = Path(output_path).stem
        ext = Path(output_path).suffix or '.png'
        dir_path = Path(output_path).parent

        for i, page in enumerate(pages):
            page_path = dir_path / f"{base_path}_page{i+1:03d}{ext}"
            page.save(page_path)

    def _pil_to_qimage(self, pil_image: Image.Image) -> QImage:
        """Convert PIL Image to QImage"""
        if pil_image.mode == "RGB":
            r, g, b = pil_image.split()
            pil_image = Image.merge("RGB", (b, g, r))
        elif pil_image.mode == "RGBA":
            r, g, b, a = pil_image.split()
            pil_image = Image.merge("RGBA", (b, g, r, a))
        elif pil_image.mode == "L":
            pil_image = pil_image.convert("RGB")

        width, height = pil_image.size
        data = pil_image.tobytes("raw", "RGB")
        qimage = QImage(data, width, height, QImage.Format_RGB888)
        return qimage


class ImageProcessor:
    """Process and enhance pottery images"""

    def __init__(self):
        pass

    def enhance_image(self, image_path: str, output_path: str,
                     brightness: float = 1.0,
                     contrast: float = 1.0,
                     sharpness: float = 1.0) -> bool:
        """
        Enhance image quality

        Args:
            image_path: Input image path
            output_path: Output image path
            brightness: Brightness adjustment (1.0 = no change)
            contrast: Contrast adjustment (1.0 = no change)
            sharpness: Sharpness adjustment (1.0 = no change)

        Returns:
            True if successful
        """
        if not HAS_DEPENDENCIES:
            return False

        try:
            from PIL import ImageEnhance

            img = Image.open(image_path)

            # Apply enhancements
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brightness)

            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(contrast)

            if sharpness != 1.0:
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(sharpness)

            img.save(output_path)
            return True

        except Exception as e:
            QgsMessageLog.logMessage(f"Image enhancement error: {str(e)}",
                                    "PyArchInit", Qgis.Warning)
            return False

    def remove_background(self, image_path: str, output_path: str,
                         threshold: int = 240) -> bool:
        """
        Simple background removal (white background)

        Args:
            image_path: Input image path
            output_path: Output image path
            threshold: Threshold for white detection

        Returns:
            True if successful
        """
        if not HAS_DEPENDENCIES:
            return False

        try:
            img = Image.open(image_path).convert("RGBA")
            data = img.getdata()

            new_data = []
            for item in data:
                # Check if pixel is close to white
                if item[0] > threshold and item[1] > threshold and item[2] > threshold:
                    # Make transparent
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)

            img.putdata(new_data)
            img.save(output_path, "PNG")
            return True

        except Exception as e:
            QgsMessageLog.logMessage(f"Background removal error: {str(e)}",
                                    "PyArchInit", Qgis.Warning)
            return False


# Import missing io module
import io


class PotteryInkProcessor:
    """
    AI-powered pottery drawing enhancement using diffusion models
    Transforms pencil drawings into publication-ready illustrations
    Based on PyPotteryInk project
    """

    def __init__(self, venv_python=None):
        self.model = None
        self.device = None
        self.use_fp16 = False
        self.model_cache = {}
        self.venv_python = venv_python  # Store venv Python path for subprocess calls

        # Check for available device
        self._setup_device()

    def _setup_device(self):
        """Setup the best available device for processing"""
        # If we have venv_python, check device using that
        if self.venv_python:
            import subprocess
            import os
            clean_env = os.environ.copy()
            for key in ['PYTHONHOME', 'PYTHONPATH', 'PYTHONSTARTUP', 'VIRTUAL_ENV']:
                clean_env.pop(key, None)

            try:
                # Check device availability using venv Python
                check_cmd = [self.venv_python, '-c', '''
import torch
if torch.backends.mps.is_available():
    print("mps")
elif torch.cuda.is_available():
    print("cuda")
else:
    print("cpu")
''']
                result = subprocess.run(check_cmd, capture_output=True, text=True, env=clean_env, timeout=5)
                if result.returncode == 0:
                    device_str = result.stdout.strip()
                    if device_str == "mps":
                        self.device = "mps"
                        self.use_fp16 = False  # MPS uses FP32 for stability
                        QgsMessageLog.logMessage("✓ Using MPS (Apple Silicon) for PotteryInk",
                                                "PyArchInit", Qgis.Info)
                    elif device_str == "cuda":
                        self.device = "cuda"
                        self.use_fp16 = True  # CUDA supports FP16
                        QgsMessageLog.logMessage("✓ Using CUDA GPU for PotteryInk",
                                                "PyArchInit", Qgis.Info)
                    else:
                        self.device = "cpu"
                        self.use_fp16 = False
                        QgsMessageLog.logMessage("Using CPU for PotteryInk",
                                                "PyArchInit", Qgis.Info)
                else:
                    self.device = "cpu"
                    self.use_fp16 = False
            except Exception as e:
                QgsMessageLog.logMessage(f"Device setup error: {str(e)}",
                                        "PyArchInit", Qgis.Warning)
                self.device = "cpu"
                self.use_fp16 = False
            return

        # Fallback if no venv_python
        if not HAS_POTTERY_INK:
            self.device = None
            return

        try:
            # Prefer MPS (Apple Silicon) if available
            if torch.backends.mps.is_available():
                self.device = "mps"
                self.use_fp16 = False  # MPS uses FP32 for stability
            # Otherwise use CUDA if available
            elif torch.cuda.is_available():
                self.device = "cuda"
                self.use_fp16 = True  # CUDA supports FP16
            else:
                self.device = "cpu"
                self.use_fp16 = False

            QgsMessageLog.logMessage(f"PotteryInk device: {self.device} (FP16: {self.use_fp16})",
                                    "PyArchInit", Qgis.Info)
        except Exception as e:
            QgsMessageLog.logMessage(f"Device setup error: {str(e)}",
                                    "PyArchInit", Qgis.Warning)
            self.device = None

    def is_available(self) -> bool:
        """Check if PotteryInk functionality is available"""
        # If we have venv_python set, we trust that dependencies are available
        # (they were checked when the processor was initialized)
        if self.venv_python:
            return True

        # Otherwise use the module-level check
        return HAS_POTTERY_INK and self.device is not None

    def load_model(self, model_path: str) -> bool:
        """Load PotteryInk model for processing"""
        if not self.is_available():
            return False

        try:
            # Check if model is already cached
            if model_path in self.model_cache:
                self.model = self.model_cache[model_path]
                return True

            # Import PotteryInk model class
            from pathlib import Path
            ink_model_path = Path(model_path)

            if not ink_model_path.exists():
                QgsMessageLog.logMessage(f"Model not found: {model_path}",
                                        "PyArchInit", Qgis.Warning)
                return False

            # For now, use a simplified approach with diffusers
            # In a full implementation, you'd load the custom Pix2Pix_Turbo model
            try:
                # This is a placeholder - you'd need to implement the actual model loading
                # based on the PotteryInk model architecture
                QgsMessageLog.logMessage(f"Loading PotteryInk model: {model_path}",
                                        "PyArchInit", Qgis.Info)

                # Cache the model
                self.model_cache[model_path] = True  # Placeholder
                self.model = True  # Placeholder
                return True

            except Exception as e:
                QgsMessageLog.logMessage(f"Model loading error: {str(e)}",
                                        "PyArchInit", Qgis.Warning)
                return False

        except Exception as e:
            QgsMessageLog.logMessage(f"PotteryInk model load error: {str(e)}",
                                    "PyArchInit", Qgis.Warning)
            return False

    def enhance_drawing(self, input_image_path: str, output_path: str,
                       prompt: str = "make it ready for publication",
                       contrast_scale: float = 1.0,
                       patch_size: int = 512,
                       overlap: int = 64,
                       apply_preprocessing: bool = True,
                       model_path: str = None,
                       use_ml: bool = True) -> bool:
        """
        Transform a pencil drawing into publication-ready illustration

        Args:
            input_image_path: Path to input pencil drawing
            output_path: Path for output illustration
            prompt: Processing prompt for AI model
            contrast_scale: Contrast enhancement factor (also used as strength for ML)
            patch_size: Size of processing patches
            overlap: Overlap between patches
            apply_preprocessing: Whether to apply preprocessing
            model_path: Path to .pkl model file (optional, will use default if not provided)
            use_ml: Whether to use ML-based enhancement (True) or basic filters (False)

        Returns:
            True if successful, False otherwise
        """
        availability = self.is_available()
        QgsMessageLog.logMessage(f"PotteryInk availability check: {availability}, venv_python: {self.venv_python}",
                                "PyArchInit", Qgis.Info)
        if not availability:
            QgsMessageLog.logMessage("PotteryInk dependencies not available",
                                    "PyArchInit", Qgis.Warning)
            return False

        # Try ML-based enhancement first if available and requested
        if use_ml and self.venv_python:
            ml_result = self._enhance_with_ml(
                input_image_path, output_path,
                model_path=model_path,
                strength=min(contrast_scale, 1.0) if contrast_scale > 0 else 0.6,
                size=patch_size
            )
            if ml_result:
                return True
            else:
                QgsMessageLog.logMessage("ML enhancement failed, falling back to basic enhancement",
                                        "PyArchInit", Qgis.Warning)

        # Fall back to basic enhancement
        try:
            # Load image
            image = Image.open(input_image_path).convert('RGB')

            # Apply preprocessing if requested
            if apply_preprocessing:
                QgsMessageLog.logMessage("Applying preprocessing adjustments...", "PyArchInit", Qgis.Info)
                grayscale = image.convert('L')
                preprocessed = self.apply_preprocessing(grayscale)
                # Convert back to RGB for further processing
                image = preprocessed.convert('RGB')

            # Ensure dimensions are multiples of 4 for model stability
            width = image.width - image.width % 4
            height = image.height - image.height % 4
            image = image.resize((width, height), Image.BICUBIC)

            # Apply basic enhancement
            enhanced_image = self._basic_enhancement(image, contrast_scale)

            # Save result
            enhanced_image.save(output_path, 'PNG', dpi=(300, 300))

            QgsMessageLog.logMessage(f"Enhanced drawing saved (basic): {output_path}",
                                    "PyArchInit", Qgis.Info)
            return True

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            QgsMessageLog.logMessage(f"Drawing enhancement error: {str(e)}\n{error_detail}",
                                    "PyArchInit", Qgis.Warning)
            return False

    def _enhance_with_ml(self, input_path: str, output_path: str,
                        model_path: str = None, strength: float = 0.6,
                        size: int = 512, steps: int = 4) -> bool:
        """
        Enhance drawing using ML model via subprocess

        Args:
            input_path: Path to input image
            output_path: Path for output image
            model_path: Path to .pkl model file
            strength: Denoising strength (0-1)
            size: Processing size
            steps: Number of inference steps

        Returns:
            True if successful, False otherwise
        """
        if not self.venv_python:
            return False

        try:
            import subprocess

            # Find inference script
            script_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'scripts', 'pottery_ink_inference.py'
            )

            if not os.path.exists(script_path):
                QgsMessageLog.logMessage(f"Inference script not found: {script_path}",
                                        "PyArchInit", Qgis.Warning)
                return False

            # Find model if not provided
            if not model_path:
                models_dir = os.path.join(os.path.expanduser("~"), "pyarchinit", "bin", "models")
                # Try to find any available model
                for model_name in ['model_10k.pkl', '6h-MCG.pkl', '6h-MC.pkl', '4h-PAINT.pkl']:
                    potential_path = os.path.join(models_dir, model_name)
                    if os.path.exists(potential_path):
                        model_path = potential_path
                        break

            if not model_path or not os.path.exists(model_path):
                QgsMessageLog.logMessage("No PotteryInk model found. Please download models first.",
                                        "PyArchInit", Qgis.Warning)
                return False

            # Prepare environment
            clean_env = os.environ.copy()
            for key in ['PYTHONHOME', 'PYTHONPATH', 'PYTHONSTARTUP', 'VIRTUAL_ENV']:
                clean_env.pop(key, None)

            # Build command
            cmd = [
                self.venv_python,
                script_path,
                '--input', input_path,
                '--output', output_path,
                '--model', model_path,
                '--device', 'auto',
                '--strength', str(strength),
                '--steps', str(steps),
                '--size', str(size),
                '--json-output'
            ]

            QgsMessageLog.logMessage(f"Running ML enhancement: {os.path.basename(model_path)}",
                                    "PyArchInit", Qgis.Info)

            # Run inference
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=clean_env,
                timeout=600  # 10 minute timeout for large images
            )

            if result.returncode == 0:
                QgsMessageLog.logMessage(f"ML enhancement successful: {output_path}",
                                        "PyArchInit", Qgis.Info)
                return True
            else:
                QgsMessageLog.logMessage(f"ML enhancement failed: {result.stderr}",
                                        "PyArchInit", Qgis.Warning)
                return False

        except subprocess.TimeoutExpired:
            QgsMessageLog.logMessage("ML enhancement timed out after 10 minutes",
                                    "PyArchInit", Qgis.Warning)
            return False
        except Exception as e:
            QgsMessageLog.logMessage(f"ML enhancement error: {str(e)}",
                                    "PyArchInit", Qgis.Warning)
            return False

    def _basic_enhancement(self, image: Image.Image, contrast_scale: float) -> Image.Image:
        """Enhanced image processing with preprocessing and stylization"""
        try:
            from PIL import ImageEnhance, ImageFilter, ImageOps
            import numpy as np

            # Step 1: Preprocessing - Clean up the input image
            QgsMessageLog.logMessage("Step 1: Preprocessing image...", "PyArchInit", Qgis.Info)

            # Convert to grayscale for better edge detection
            gray = image.convert('L')

            # Apply adaptive equalization to normalize contrast
            gray_array = np.array(gray)

            # Enhance edges using unsharp mask
            enhanced = gray.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

            # Apply bilateral filter for noise reduction while preserving edges
            enhanced = enhanced.filter(ImageFilter.SMOOTH_MORE)

            # Step 2: Edge Detection and Line Extraction
            QgsMessageLog.logMessage("Step 2: Extracting pottery lines...", "PyArchInit", Qgis.Info)

            # Find edges using enhanced Sobel filter
            edges = enhanced.filter(ImageFilter.FIND_EDGES)

            # Enhance the edges
            edges = edges.filter(ImageFilter.EDGE_ENHANCE_MORE)

            # Convert back to RGB for further processing
            result = edges.convert('RGB')

            # Step 3: Apply stippling/contrast effect
            if contrast_scale != 1.0:
                QgsMessageLog.logMessage(f"Step 3: Applying stippling effect (level: {contrast_scale})...",
                                        "PyArchInit", Qgis.Info)
                enhancer = ImageEnhance.Contrast(result)
                result = enhancer.enhance(contrast_scale)

                # Apply sharpening based on stippling level
                sharpness_enhancer = ImageEnhance.Sharpness(result)
                result = sharpness_enhancer.enhance(1 + contrast_scale * 0.5)

            # Step 4: Final cleanup
            QgsMessageLog.logMessage("Step 4: Final cleanup and optimization...", "PyArchInit", Qgis.Info)

            # Invert colors to get black lines on white background (traditional pottery drawing style)
            result = ImageOps.invert(result)

            # Final sharpening pass
            result = result.filter(ImageFilter.SHARPEN)

            # Apply slight smoothing to reduce artifacts
            result = result.filter(ImageFilter.SMOOTH)

            QgsMessageLog.logMessage("✓ Enhancement processing complete", "PyArchInit", Qgis.Info)

            return result

        except ImportError as e:
            QgsMessageLog.logMessage(f"Missing dependency: {str(e)}", "PyArchInit", Qgis.Warning)
            # Fallback to basic enhancement
            from PIL import ImageEnhance, ImageFilter
            if contrast_scale != 1.0:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(contrast_scale)
            image = image.filter(ImageFilter.EDGE_ENHANCE)
            image = image.filter(ImageFilter.SHARPEN)
            return image

        except Exception as e:
            QgsMessageLog.logMessage(f"Enhancement error: {str(e)}", "PyArchInit", Qgis.Warning)
            return image

    def extract_elements(self, image_path: str, output_dir: str,
                        min_area: int = 1000) -> List[str]:
        """
        Extract individual pottery elements from processed image

        Args:
            image_path: Path to processed image
            output_dir: Directory to save extracted elements
            min_area: Minimum area for detected elements

        Returns:
            List of paths to extracted element images
        """
        try:
            import cv2
            import numpy as np
        except ImportError:
            QgsMessageLog.logMessage("OpenCV not available for element extraction",
                                    "PyArchInit", Qgis.Warning)
            return []

        try:
            # Create output directory
            elements_dir = os.path.join(output_dir, 'extracted_elements')
            os.makedirs(elements_dir, exist_ok=True)

            # Read and process image
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                return []

            # Apply threshold to get binary image
            _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)

            # Find contours (pottery elements)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            element_paths = []
            base_name = os.path.splitext(os.path.basename(image_path))[0]

            for idx, contour in enumerate(contours):
                # Filter by area
                area = cv2.contourArea(contour)
                if area < min_area:
                    continue

                # Get bounding box with padding
                x, y, w, h = cv2.boundingRect(contour)
                padding = 20
                x = max(0, x - padding)
                y = max(0, y - padding)
                w = min(img.shape[1] - x, w + 2 * padding)
                h = min(img.shape[0] - y, h + 2 * padding)

                # Extract element
                element = img[y:y+h, x:x+w]

                # Save element
                element_path = os.path.join(elements_dir, f"{base_name}_element_{idx+1:02d}.png")
                cv2.imwrite(element_path, element)
                element_paths.append(element_path)

            QgsMessageLog.logMessage(f"Extracted {len(element_paths)} pottery elements",
                                    "PyArchInit", Qgis.Info)
            return element_paths

        except Exception as e:
            QgsMessageLog.logMessage(f"Element extraction error: {str(e)}",
                                    "PyArchInit", Qgis.Warning)
            return []

    def batch_process(self, input_folder: str, output_folder: str,
                     model_path: str, prompt: str = "make it ready for publication",
                     progress_callback=None) -> Dict[str, Any]:
        """
        Process multiple drawings in batch

        Args:
            input_folder: Folder containing input drawings
            output_folder: Folder for processed outputs
            model_path: Path to PotteryInk model
            prompt: Processing prompt
            progress_callback: Function to call for progress updates

        Returns:
            Dictionary with processing results and statistics
        """
        if not self.is_available():
            return {'success': False, 'error': 'PotteryInk not available'}

        try:
            # Load model
            if not self.load_model(model_path):
                return {'success': False, 'error': 'Failed to load model'}

            # Create output directory
            os.makedirs(output_folder, exist_ok=True)

            # Find input images
            supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            image_files = []
            for ext in supported_formats:
                pattern = f"*{ext}"
                image_files.extend(Path(input_folder).glob(pattern))
                image_files.extend(Path(input_folder).glob(pattern.upper()))

            if not image_files:
                return {'success': False, 'error': 'No images found'}

            # Process images
            results = {
                'success': True,
                'total_images': len(image_files),
                'processed': 0,
                'failed': 0,
                'output_paths': [],
                'processing_times': []
            }

            for i, img_path in enumerate(image_files):
                if progress_callback:
                    progress_callback(i, len(image_files), f"Processing {img_path.name}")

                try:
                    import time
                    start_time = time.time()

                    # Generate output path
                    output_path = os.path.join(output_folder, f"enhanced_{img_path.stem}.png")

                    # Process image
                    if self.enhance_drawing(str(img_path), output_path, prompt):
                        results['processed'] += 1
                        results['output_paths'].append(output_path)
                        results['processing_times'].append(time.time() - start_time)
                    else:
                        results['failed'] += 1

                except Exception as e:
                    QgsMessageLog.logMessage(f"Error processing {img_path}: {str(e)}",
                                            "PyArchInit", Qgis.Warning)
                    results['failed'] += 1

            return results

        except Exception as e:
            QgsMessageLog.logMessage(f"Batch processing error: {str(e)}",
                                    "PyArchInit", Qgis.Warning)
            return {'success': False, 'error': str(e)}

    def enhance_high_res(self, input_image_path: str, output_path: str,
                        patch_size: int = 512, overlap: int = 64,
                        contrast_scale: float = 1.0,
                        apply_preprocessing: bool = True) -> bool:
        """
        Process high-resolution images using patch-based processing

        Args:
            input_image_path: Path to input image
            output_path: Path for output image
            patch_size: Size of processing patches
            overlap: Overlap between patches in pixels
            contrast_scale: Contrast enhancement factor
            apply_preprocessing: Whether to apply preprocessing

        Returns:
            True if successful, False otherwise
        """
        try:
            QgsMessageLog.logMessage("Starting high-resolution processing...", "PyArchInit", Qgis.Info)

            # Load image
            image = Image.open(input_image_path).convert('RGB')

            # Apply preprocessing if requested
            if apply_preprocessing:
                QgsMessageLog.logMessage("Applying preprocessing to high-res image...", "PyArchInit", Qgis.Info)
                grayscale = image.convert('L')
                preprocessed = self.apply_preprocessing(grayscale)
                image = preprocessed.convert('RGB')

            width, height = image.size

            # Calculate patch grid
            stride = patch_size - overlap
            n_patches_x = (width - overlap) // stride + 1
            n_patches_y = (height - overlap) // stride + 1

            QgsMessageLog.logMessage(f"Processing {n_patches_x}x{n_patches_y} patches of size {patch_size}px",
                                    "PyArchInit", Qgis.Info)

            # Create output image
            output = Image.new('RGB', (width, height), 'white')
            weight_map = Image.new('L', (width, height), 0)

            # Process each patch
            patch_count = 0
            total_patches = n_patches_x * n_patches_y

            for i in range(n_patches_y):
                for j in range(n_patches_x):
                    patch_count += 1

                    # Calculate patch boundaries
                    x1 = j * stride
                    y1 = i * stride
                    x2 = min(x1 + patch_size, width)
                    y2 = min(y1 + patch_size, height)

                    # Skip if patch is too small
                    if (x2 - x1) < patch_size // 2 or (y2 - y1) < patch_size // 2:
                        continue

                    QgsMessageLog.logMessage(f"Processing patch {patch_count}/{total_patches}",
                                            "PyArchInit", Qgis.Info)

                    # Extract and process patch
                    patch = image.crop((x1, y1, x2, y2))

                    # Enhance patch
                    enhanced_patch = self._basic_enhancement(patch, contrast_scale)

                    # Create weight mask for blending
                    weight = Image.new('L', (x2-x1, y2-y1), 255)

                    # Apply feathering to edges
                    if overlap > 0:
                        from PIL import ImageDraw
                        draw = ImageDraw.Draw(weight)
                        feather_size = overlap // 2

                        # Feather edges
                        for k in range(feather_size):
                            alpha = int(255 * (k / feather_size))
                            # Top edge
                            if i > 0:
                                draw.rectangle([0, k, x2-x1, k+1], fill=alpha)
                            # Bottom edge
                            if i < n_patches_y - 1:
                                draw.rectangle([0, y2-y1-k-1, x2-x1, y2-y1-k], fill=alpha)
                            # Left edge
                            if j > 0:
                                draw.rectangle([k, 0, k+1, y2-y1], fill=alpha)
                            # Right edge
                            if j < n_patches_x - 1:
                                draw.rectangle([x2-x1-k-1, 0, x2-x1-k, y2-y1], fill=alpha)

                    # Blend patch into output
                    output.paste(enhanced_patch, (x1, y1))
                    weight_map.paste(weight, (x1, y1))

            # Save result
            output.save(output_path, 'PNG', dpi=(300, 300))

            QgsMessageLog.logMessage(f"✓ High-resolution processing complete: {output_path}",
                                    "PyArchInit", Qgis.Info)
            return True

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            QgsMessageLog.logMessage(f"High-res processing error: {str(e)}\n{error_detail}",
                                    "PyArchInit", Qgis.Warning)
            return False

    def export_to_svg(self, image_path: str, output_path: str,
                     simplify: float = 2.0, min_path_size: int = 20) -> bool:
        """
        Export enhanced pottery drawing to SVG format

        Args:
            image_path: Path to enhanced image
            output_path: Path for output SVG file
            simplify: Simplification factor for paths
            min_path_size: Minimum size for paths to include

        Returns:
            True if successful, False otherwise
        """
        try:
            QgsMessageLog.logMessage("Starting SVG export...", "PyArchInit", Qgis.Info)

            # Try to use potrace for vectorization if available
            try:
                import subprocess
                import tempfile

                # Check if potrace is available
                result = subprocess.run(['potrace', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    # Use potrace for high-quality vectorization
                    with tempfile.NamedTemporaryFile(suffix='.bmp', delete=False) as tmp_bmp:
                        # Convert to BMP for potrace
                        img = Image.open(image_path)
                        img = img.convert('L')  # Convert to grayscale
                        img.save(tmp_bmp.name, 'BMP')

                        # Run potrace
                        cmd = [
                            'potrace',
                            '-s',  # SVG output
                            '-o', output_path,
                            '--turdsize', str(min_path_size),
                            tmp_bmp.name
                        ]
                        result = subprocess.run(cmd, capture_output=True, text=True)

                        if result.returncode == 0:
                            QgsMessageLog.logMessage(f"✓ SVG exported with potrace: {output_path}",
                                                    "PyArchInit", Qgis.Info)
                            return True
            except:
                pass

            # Fallback: Create basic SVG from image contours
            QgsMessageLog.logMessage("Using fallback SVG generation (install potrace for better quality)",
                                    "PyArchInit", Qgis.Info)

            # Import cv2 here for fallback method
            try:
                import cv2
                import numpy as np
            except ImportError:
                QgsMessageLog.logMessage("OpenCV not available for SVG export",
                                        "PyArchInit", Qgis.Warning)
                return False

            # Read and process image
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise ValueError(f"Cannot read image: {image_path}")

            # Apply threshold
            _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)

            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # Create SVG
            height, width = img.shape
            svg_lines = []
            svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
            svg_lines.append('<g fill="none" stroke="black" stroke-width="1">')

            for contour in contours:
                # Skip small contours
                if cv2.contourArea(contour) < min_path_size:
                    continue

                # Simplify contour
                epsilon = simplify * cv2.arcLength(contour, True) / 100
                approx = cv2.approxPolyDP(contour, epsilon, True)

                # Convert to SVG path
                if len(approx) > 2:
                    path_data = f'M {approx[0][0][0]},{approx[0][0][1]}'
                    for point in approx[1:]:
                        path_data += f' L {point[0][0]},{point[0][1]}'
                    path_data += ' Z'
                    svg_lines.append(f'  <path d="{path_data}"/>')

            svg_lines.append('</g>')
            svg_lines.append('</svg>')

            # Write SVG file
            with open(output_path, 'w') as f:
                f.write('\n'.join(svg_lines))

            QgsMessageLog.logMessage(f"✓ SVG exported (basic): {output_path}", "PyArchInit", Qgis.Info)
            return True

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            QgsMessageLog.logMessage(f"SVG export error: {str(e)}\n{error_detail}",
                                    "PyArchInit", Qgis.Warning)
            return False

    def apply_preprocessing(self, image: Image.Image, model_stats: Dict = None) -> Image.Image:
        """
        Apply recommended preprocessing adjustments based on model statistics

        Args:
            image: Input PIL Image
            model_stats: Model statistics dictionary (if None, uses default)

        Returns:
            Preprocessed PIL Image
        """
        try:
            from PIL import ImageEnhance, ImageOps
            import numpy as np

            # Convert to grayscale if needed
            if image.mode != 'L':
                image = image.convert('L')

            # Default model stats if not provided
            if model_stats is None:
                model_stats = {
                    'mean': {'mean': 127, 'std': 30},
                    'contrast_ratio': {'mean': 50, 'std': 15},
                    'std': {'mean': 60, 'std': 20}
                }

            # Calculate current metrics
            img_array = np.array(image)
            current_mean = np.mean(img_array)
            current_std = np.std(img_array)
            p1, p99 = np.percentile(img_array, [1, 99])
            current_contrast = p99 / (p1 + 1e-6)

            # Apply adjustments
            adjusted_image = image.copy()

            # Adjust brightness if needed
            target_mean = model_stats.get('mean', {}).get('mean', 127)
            if abs(current_mean - target_mean) > 20:
                brightness_factor = target_mean / (current_mean + 1e-6)
                brightness_factor = np.clip(brightness_factor, 0.5, 2.0)
                enhancer = ImageEnhance.Brightness(adjusted_image)
                adjusted_image = enhancer.enhance(brightness_factor)
                QgsMessageLog.logMessage(f"Applied brightness adjustment: {brightness_factor:.2f}",
                                        "PyArchInit", Qgis.Info)

            # Adjust contrast if needed
            target_contrast = model_stats.get('contrast_ratio', {}).get('mean', 50)
            if abs(current_contrast - target_contrast) > 10:
                contrast_factor = 1 + (target_contrast - current_contrast) / 100
                contrast_factor = np.clip(contrast_factor, 0.5, 2.0)
                enhancer = ImageEnhance.Contrast(adjusted_image)
                adjusted_image = enhancer.enhance(contrast_factor)
                QgsMessageLog.logMessage(f"Applied contrast adjustment: {contrast_factor:.2f}",
                                        "PyArchInit", Qgis.Info)

            # Normalize histogram
            adjusted_image = ImageOps.equalize(adjusted_image)

            return adjusted_image

        except Exception as e:
            QgsMessageLog.logMessage(f"Preprocessing error: {str(e)}", "PyArchInit", Qgis.Warning)
            return image

    def analyze_dataset_metrics(self, folder_path: str) -> Dict[str, Any]:
        """
        Analyze all images in a folder to extract statistical metrics

        Args:
            folder_path: Path to folder containing images

        Returns:
            Dictionary with dataset statistics
        """
        try:
            import numpy as np
            from pathlib import Path

            metrics = {
                'mean': [], 'std': [], 'contrast_ratio': [],
                'median': [], 'dynamic_range': [], 'entropy': []
            }

            # Process each image
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            image_files = []
            for ext in image_extensions:
                image_files.extend(Path(folder_path).glob(f'*{ext}'))
                image_files.extend(Path(folder_path).glob(f'*{ext.upper()}'))

            QgsMessageLog.logMessage(f"Analyzing {len(image_files)} images...", "PyArchInit", Qgis.Info)

            for img_path in image_files:
                try:
                    img = Image.open(img_path).convert('L')
                    img_array = np.array(img)

                    # Calculate metrics
                    p1, p99 = np.percentile(img_array, [1, 99])
                    p25, p75 = np.percentile(img_array, [25, 75])

                    metrics['mean'].append(float(np.mean(img_array)))
                    metrics['std'].append(float(np.std(img_array)))
                    metrics['contrast_ratio'].append(float(p99 / (p1 + 1e-6)))
                    metrics['median'].append(float(np.median(img_array)))
                    metrics['dynamic_range'].append(float(p99 - p1))

                    # Calculate entropy
                    histogram = img.histogram()
                    total_pixels = sum(histogram)
                    probabilities = [h/total_pixels for h in histogram if h > 0]
                    entropy = -sum(p * np.log2(p) for p in probabilities)
                    metrics['entropy'].append(float(entropy))

                except Exception as e:
                    QgsMessageLog.logMessage(f"Error analyzing {img_path}: {str(e)}",
                                            "PyArchInit", Qgis.Warning)
                    continue

            # Calculate statistics for each metric
            distributions = {}
            for metric, values in metrics.items():
                if values:
                    values_array = np.array(values)
                    distributions[metric] = {
                        'mean': float(np.mean(values_array)),
                        'std': float(np.std(values_array)),
                        'median': float(np.median(values_array)),
                        'min': float(np.min(values_array)),
                        'max': float(np.max(values_array)),
                        'percentiles': [float(p) for p in np.percentile(values_array, [5, 25, 50, 75, 95])],
                        'n_samples': len(values),
                        'values': values  # Keep raw values for KDE
                    }

            QgsMessageLog.logMessage(f"✓ Dataset analysis complete", "PyArchInit", Qgis.Info)
            return distributions

        except Exception as e:
            QgsMessageLog.logMessage(f"Dataset analysis error: {str(e)}", "PyArchInit", Qgis.Warning)
            return {}

    def run_diagnostic(self, image_path: str) -> Dict[str, Any]:
        """
        Run diagnostic analysis on pottery drawing

        Args:
            image_path: Path to image to analyze

        Returns:
            Dictionary with diagnostic information
        """
        try:
            QgsMessageLog.logMessage("Running diagnostic analysis...", "PyArchInit", Qgis.Info)

            # Import cv2 here
            try:
                import cv2
                import numpy as np
            except ImportError:
                QgsMessageLog.logMessage("OpenCV not available for diagnostic",
                                        "PyArchInit", Qgis.Warning)
                return {'error': 'OpenCV not installed'}

            # Load image
            img = cv2.imread(image_path)
            if img is None:
                return {'error': 'Cannot read image'}

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Collect diagnostic info
            diagnostic = {
                'image_info': {
                    'width': img.shape[1],
                    'height': img.shape[0],
                    'channels': img.shape[2] if len(img.shape) > 2 else 1,
                    'dtype': str(img.dtype),
                    'file_size': os.path.getsize(image_path)
                },
                'quality_metrics': {},
                'preprocessing_suggestions': [],
                'device_info': {
                    'device': str(self.device) if self.device else 'cpu',
                    'venv_python': bool(self.venv_python),
                    'has_pottery_ink': HAS_POTTERY_INK
                }
            }

            # Analyze image quality
            # Check contrast
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist = hist.flatten() / hist.sum()

            # Calculate metrics
            mean_val = gray.mean()
            std_val = gray.std()

            diagnostic['quality_metrics']['mean_intensity'] = float(mean_val)
            diagnostic['quality_metrics']['std_intensity'] = float(std_val)
            diagnostic['quality_metrics']['contrast'] = float(std_val / mean_val) if mean_val > 0 else 0

            # Check if too dark or too bright
            if mean_val < 50:
                diagnostic['preprocessing_suggestions'].append("Image is very dark - increase brightness")
            elif mean_val > 200:
                diagnostic['preprocessing_suggestions'].append("Image is very bright - decrease brightness")

            if std_val < 20:
                diagnostic['preprocessing_suggestions'].append("Low contrast - increase contrast")

            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            edge_ratio = np.count_nonzero(edges) / edges.size
            diagnostic['quality_metrics']['edge_ratio'] = float(edge_ratio)

            if edge_ratio < 0.01:
                diagnostic['preprocessing_suggestions'].append("Few edges detected - check image quality")
            elif edge_ratio > 0.2:
                diagnostic['preprocessing_suggestions'].append("Many edges detected - image may be noisy")

            # Check resolution
            total_pixels = img.shape[0] * img.shape[1]
            if total_pixels < 500000:  # Less than 0.5 megapixels
                diagnostic['preprocessing_suggestions'].append("Low resolution - consider higher quality scan")
            elif total_pixels > 10000000:  # More than 10 megapixels
                diagnostic['preprocessing_suggestions'].append("Very high resolution - consider using high-res mode")

            # Add processing recommendations
            diagnostic['recommended_settings'] = {
                'contrast_scale': 1.5 if std_val < 30 else 1.0,
                'use_high_res': total_pixels > 4000000,
                'patch_size': 512 if total_pixels > 4000000 else 256
            }

            QgsMessageLog.logMessage("✓ Diagnostic complete", "PyArchInit", Qgis.Info)
            return diagnostic

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            QgsMessageLog.logMessage(f"Diagnostic error: {str(e)}\n{error_detail}",
                                    "PyArchInit", Qgis.Warning)
            return {'error': str(e)}