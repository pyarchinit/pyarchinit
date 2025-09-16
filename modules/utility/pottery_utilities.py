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
    """Extract images from PDF files - Step 1 of PyPotteryLens workflow"""

    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
        self.yolo_model = None
        self.model_loaded = False
        self.mask_outputs = {}  # Store masks for later extraction

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