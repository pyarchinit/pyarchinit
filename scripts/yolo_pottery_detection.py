#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO Pottery Detection Script
Runs in the pottery_venv to detect pottery drawings using YOLO model
Falls back to contour-based detection for scanned drawings

Usage:
    python yolo_pottery_detection.py --input IMAGE_PATH --output OUTPUT_DIR --model MODEL_PATH [options]
"""

import argparse
import os
import sys
import json
from pathlib import Path


def detect_pottery_contours(image_path: str, output_dir: str,
                           min_area: int = 10000, padding: int = 30) -> dict:
    """
    Detect pottery drawings using contour detection (for scanned drawings)

    Args:
        image_path: Path to input image
        output_dir: Directory to save extracted regions
        min_area: Minimum contour area to consider (filters out small noise)
        padding: Padding around detected regions

    Returns:
        Dict with detection results
    """
    import cv2
    import numpy as np

    result_info = {
        'success': False,
        'input': image_path,
        'output_dir': output_dir,
        'method': 'contour',
        'detections': [],
        'extracted_images': [],
        'error': None
    }

    try:
        print(f"Loading image: {image_path}")
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")

        img_height, img_width = img.shape[:2]
        print(f"Image size: {img_width}x{img_height}")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply adaptive thresholding (better for scanned documents with varying lighting)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 21, 10
        )

        # Morphological operations to connect nearby components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(thresh, kernel, iterations=3)
        closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel, iterations=2)

        # Find contours
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        print(f"Found {len(contours)} raw contours")

        # Calculate max area threshold (exclude regions > 5% of image - single pottery pieces are smaller)
        max_area = (img_width * img_height) * 0.05

        # Filter and sort contours by area
        valid_contours = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > min_area and area < max_area:
                x, y, w, h = cv2.boundingRect(cnt)
                # Filter out very thin or very wide rectangles (likely lines/borders)
                aspect_ratio = w / h if h > 0 else 0
                if 0.2 < aspect_ratio < 5:  # reasonable aspect ratio for pottery drawings
                    valid_contours.append((area, x, y, w, h))

        # Sort by position (top to bottom, left to right)
        valid_contours.sort(key=lambda c: (c[2] // 100, c[1]))  # Group by row, then by x

        print(f"Found {len(valid_contours)} valid pottery regions")

        os.makedirs(output_dir, exist_ok=True)
        base_name = Path(image_path).stem

        for idx, (area, x, y, w, h) in enumerate(valid_contours):
            # Add padding
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(img_width, x + w + padding)
            y2 = min(img_height, y + h + padding)

            # Extract region
            roi = img[y1:y2, x1:x2]

            # Save extracted region
            region_path = os.path.join(
                output_dir,
                f"{base_name}_pottery{idx+1:02d}.png"
            )
            cv2.imwrite(region_path, roi)

            detection = {
                'bbox': [x1, y1, x2 - x1, y2 - y1],
                'area': area,
                'output_path': region_path
            }
            result_info['detections'].append(detection)
            result_info['extracted_images'].append(region_path)

            print(f"  Region {idx+1}: area={area}, bbox=[{x1}, {y1}, {x2-x1}, {y2-y1}]")

        result_info['success'] = True
        print(f"Extracted {len(valid_contours)} pottery regions to: {output_dir}")

    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Error: {error_msg}")
        traceback.print_exc()
        result_info['error'] = error_msg

    return result_info


def detect_pottery(image_path: str, model_path: str, output_dir: str,
                   confidence: float = 0.5, padding: int = 20,
                   fallback_contours: bool = True) -> dict:
    """
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
    """
    import cv2
    import numpy as np
    from ultralytics import YOLO

    result_info = {
        'success': False,
        'input': image_path,
        'output_dir': output_dir,
        'model': model_path,
        'detections': [],
        'extracted_images': [],
        'error': None
    }

    try:
        # Load model
        print(f"Loading YOLO model from: {model_path}")
        model = YOLO(model_path)

        # Load image
        print(f"Loading image: {image_path}")
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")

        img_height, img_width = img.shape[:2]
        print(f"Image size: {img_width}x{img_height}")

        # Run detection
        print(f"Running detection with confidence={confidence}...")
        results = model(image_path, conf=confidence, verbose=False)

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Process detections
        base_name = Path(image_path).stem
        detected_regions = []

        for result in results:
            if result.boxes is not None:
                boxes = result.boxes.xyxy.cpu().numpy()  # x1, y1, x2, y2
                confidences = result.boxes.conf.cpu().numpy()
                classes = result.boxes.cls.cpu().numpy()

                print(f"Found {len(boxes)} detections")

                for idx, (box, conf, cls) in enumerate(zip(boxes, confidences, classes)):
                    x1, y1, x2, y2 = map(int, box)

                    # Add padding
                    x1 = max(0, x1 - padding)
                    y1 = max(0, y1 - padding)
                    x2 = min(img_width, x2 + padding)
                    y2 = min(img_height, y2 + padding)

                    # Extract region
                    roi = img[y1:y2, x1:x2]

                    # Save extracted region
                    region_path = os.path.join(
                        output_dir,
                        f"{base_name}_pottery{idx+1:02d}.png"
                    )
                    cv2.imwrite(region_path, roi)

                    detection = {
                        'bbox': [x1, y1, x2 - x1, y2 - y1],
                        'confidence': float(conf),
                        'class': int(cls),
                        'output_path': region_path
                    }
                    detected_regions.append(detection)
                    result_info['extracted_images'].append(region_path)

                    print(f"  Detection {idx+1}: conf={conf:.2f}, bbox=[{x1}, {y1}, {x2-x1}, {y2-y1}]")

        result_info['detections'] = detected_regions
        result_info['method'] = 'yolo'

        # If no YOLO detections and fallback enabled, try contour detection
        if len(detected_regions) == 0 and fallback_contours:
            print("No YOLO detections, falling back to contour detection...")
            return detect_pottery_contours(image_path, output_dir, padding=padding)

        result_info['success'] = True
        print(f"Extracted {len(detected_regions)} pottery regions to: {output_dir}")

    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Error: {error_msg}")
        traceback.print_exc()
        result_info['error'] = error_msg

    return result_info


def main():
    parser = argparse.ArgumentParser(description='YOLO Pottery Detection')
    parser.add_argument('--input', '-i', required=True, help='Input image path')
    parser.add_argument('--output', '-o', required=True, help='Output directory for extracted regions')
    parser.add_argument('--model', '-m', required=True, help='Path to YOLO .pt model file')
    parser.add_argument('--confidence', '-c', type=float, default=0.5,
                       help='Detection confidence threshold (0-1, default 0.5)')
    parser.add_argument('--padding', '-p', type=int, default=20,
                       help='Padding around detected regions (default 20)')
    parser.add_argument('--json-output', action='store_true',
                       help='Output results as JSON')
    parser.add_argument('--contours-only', action='store_true',
                       help='Use contour detection only (skip YOLO)')

    args = parser.parse_args()

    # Validate input
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        return 1

    if not args.contours_only and not os.path.exists(args.model):
        print(f"Error: Model file not found: {args.model}")
        return 1

    # Run detection
    if args.contours_only:
        result = detect_pottery_contours(
            args.input,
            args.output,
            padding=args.padding
        )
    else:
        result = detect_pottery(
            args.input,
            args.model,
            args.output,
            confidence=args.confidence,
            padding=args.padding
        )

    # Output JSON if requested
    if args.json_output:
        print("---JSON_OUTPUT---")
        print(json.dumps(result, indent=2))

    return 0 if result['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
