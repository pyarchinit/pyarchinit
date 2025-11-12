# modules/utility/pottery_utilities.py

## Overview

This file contains 108 documented elements.

## Classes

### PDFExtractor

Extract images from PDF files - Step 1 of PyPotteryLens workflow

#### Methods

##### __init__(self)

##### load_yolo_model(self)

Load YOLO model for pottery detection if available

##### detect_and_extract_pottery(self, image_path, confidence, kernel_size, iterations)

Detect pottery in image and extract with morphological operations

Args:
    image_path: Path to image
    confidence: Detection confidence threshold
    kernel_size: Size of morphological kernel
    iterations: Number of dilation iterations

Returns:
    List of detected pottery regions with masks

##### extract(self, pdf_path, output_dir, split_pages, auto_detect, confidence, kernel_size, iterations)

Extract images from PDF

Args:
    pdf_path: Path to PDF file
    output_dir: Output directory for images
    split_pages: Split pages into left/right
    auto_detect: Auto-detect pottery images using YOLO
    confidence: Detection confidence threshold

Returns:
    List of extracted image paths

### LayoutGenerator

Generate image layouts for pottery documentation

#### Methods

##### __init__(self)

##### get_font(self, size)

Get font for text rendering

##### create_preview(self, images, mode, page_size, rows, cols)

Create a preview of the layout

##### generate(self, images, output_path, mode, page_size, rows, cols, add_captions, add_scale, scale_cm)

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

### ImageProcessor

Process and enhance pottery images

#### Methods

##### __init__(self)

##### enhance_image(self, image_path, output_path, brightness, contrast, sharpness)

Enhance image quality

Args:
    image_path: Input image path
    output_path: Output image path
    brightness: Brightness adjustment (1.0 = no change)
    contrast: Contrast adjustment (1.0 = no change)
    sharpness: Sharpness adjustment (1.0 = no change)

Returns:
    True if successful

##### remove_background(self, image_path, output_path, threshold)

Simple background removal (white background)

Args:
    image_path: Input image path
    output_path: Output image path
    threshold: Threshold for white detection

Returns:
    True if successful

### PotteryInkProcessor

AI-powered pottery drawing enhancement using diffusion models
Transforms pencil drawings into publication-ready illustrations
Based on PyPotteryInk project

#### Methods

##### __init__(self, venv_python)

##### is_available(self)

Check if PotteryInk functionality is available

##### load_model(self, model_path)

Load PotteryInk model for processing

##### enhance_drawing(self, input_image_path, output_path, prompt, contrast_scale, patch_size, overlap, apply_preprocessing)

Transform a pencil drawing into publication-ready illustration

Args:
    input_image_path: Path to input pencil drawing
    output_path: Path for output illustration
    prompt: Processing prompt for AI model
    contrast_scale: Contrast enhancement factor
    patch_size: Size of processing patches
    overlap: Overlap between patches
    apply_preprocessing: Whether to apply preprocessing

Returns:
    True if successful, False otherwise

##### extract_elements(self, image_path, output_dir, min_area)

Extract individual pottery elements from processed image

Args:
    image_path: Path to processed image
    output_dir: Directory to save extracted elements
    min_area: Minimum area for detected elements

Returns:
    List of paths to extracted element images

##### batch_process(self, input_folder, output_folder, model_path, prompt, progress_callback)

Process multiple drawings in batch

Args:
    input_folder: Folder containing input drawings
    output_folder: Folder for processed outputs
    model_path: Path to PotteryInk model
    prompt: Processing prompt
    progress_callback: Function to call for progress updates

Returns:
    Dictionary with processing results and statistics

##### enhance_high_res(self, input_image_path, output_path, patch_size, overlap, contrast_scale, apply_preprocessing)

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

##### export_to_svg(self, image_path, output_path, simplify, min_path_size)

Export enhanced pottery drawing to SVG format

Args:
    image_path: Path to enhanced image
    output_path: Path for output SVG file
    simplify: Simplification factor for paths
    min_path_size: Minimum size for paths to include

Returns:
    True if successful, False otherwise

##### apply_preprocessing(self, image, model_stats)

Apply recommended preprocessing adjustments based on model statistics

Args:
    image: Input PIL Image
    model_stats: Model statistics dictionary (if None, uses default)

Returns:
    Preprocessed PIL Image

##### analyze_dataset_metrics(self, folder_path)

Analyze all images in a folder to extract statistical metrics

Args:
    folder_path: Path to folder containing images

Returns:
    Dictionary with dataset statistics

##### run_diagnostic(self, image_path)

Run diagnostic analysis on pottery drawing

Args:
    image_path: Path to image to analyze

Returns:
    Dictionary with diagnostic information

### PDFExtractor

Extract images from PDF files - Step 1 of PyPotteryLens workflow

#### Methods

##### __init__(self)

##### load_yolo_model(self)

Load YOLO model for pottery detection if available

##### detect_and_extract_pottery(self, image_path, confidence, kernel_size, iterations)

Detect pottery in image and extract with morphological operations

Args:
    image_path: Path to image
    confidence: Detection confidence threshold
    kernel_size: Size of morphological kernel
    iterations: Number of dilation iterations

Returns:
    List of detected pottery regions with masks

##### extract(self, pdf_path, output_dir, split_pages, auto_detect, confidence, kernel_size, iterations)

Extract images from PDF

Args:
    pdf_path: Path to PDF file
    output_dir: Output directory for images
    split_pages: Split pages into left/right
    auto_detect: Auto-detect pottery images using YOLO
    confidence: Detection confidence threshold

Returns:
    List of extracted image paths

### LayoutGenerator

Generate image layouts for pottery documentation

#### Methods

##### __init__(self)

##### get_font(self, size)

Get font for text rendering

##### create_preview(self, images, mode, page_size, rows, cols)

Create a preview of the layout

##### generate(self, images, output_path, mode, page_size, rows, cols, add_captions, add_scale, scale_cm)

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

### ImageProcessor

Process and enhance pottery images

#### Methods

##### __init__(self)

##### enhance_image(self, image_path, output_path, brightness, contrast, sharpness)

Enhance image quality

Args:
    image_path: Input image path
    output_path: Output image path
    brightness: Brightness adjustment (1.0 = no change)
    contrast: Contrast adjustment (1.0 = no change)
    sharpness: Sharpness adjustment (1.0 = no change)

Returns:
    True if successful

##### remove_background(self, image_path, output_path, threshold)

Simple background removal (white background)

Args:
    image_path: Input image path
    output_path: Output image path
    threshold: Threshold for white detection

Returns:
    True if successful

### PotteryInkProcessor

AI-powered pottery drawing enhancement using diffusion models
Transforms pencil drawings into publication-ready illustrations
Based on PyPotteryInk project

#### Methods

##### __init__(self, venv_python)

##### is_available(self)

Check if PotteryInk functionality is available

##### load_model(self, model_path)

Load PotteryInk model for processing

##### enhance_drawing(self, input_image_path, output_path, prompt, contrast_scale, patch_size, overlap, apply_preprocessing)

Transform a pencil drawing into publication-ready illustration

Args:
    input_image_path: Path to input pencil drawing
    output_path: Path for output illustration
    prompt: Processing prompt for AI model
    contrast_scale: Contrast enhancement factor
    patch_size: Size of processing patches
    overlap: Overlap between patches
    apply_preprocessing: Whether to apply preprocessing

Returns:
    True if successful, False otherwise

##### extract_elements(self, image_path, output_dir, min_area)

Extract individual pottery elements from processed image

Args:
    image_path: Path to processed image
    output_dir: Directory to save extracted elements
    min_area: Minimum area for detected elements

Returns:
    List of paths to extracted element images

##### batch_process(self, input_folder, output_folder, model_path, prompt, progress_callback)

Process multiple drawings in batch

Args:
    input_folder: Folder containing input drawings
    output_folder: Folder for processed outputs
    model_path: Path to PotteryInk model
    prompt: Processing prompt
    progress_callback: Function to call for progress updates

Returns:
    Dictionary with processing results and statistics

##### enhance_high_res(self, input_image_path, output_path, patch_size, overlap, contrast_scale, apply_preprocessing)

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

##### export_to_svg(self, image_path, output_path, simplify, min_path_size)

Export enhanced pottery drawing to SVG format

Args:
    image_path: Path to enhanced image
    output_path: Path for output SVG file
    simplify: Simplification factor for paths
    min_path_size: Minimum size for paths to include

Returns:
    True if successful, False otherwise

##### apply_preprocessing(self, image, model_stats)

Apply recommended preprocessing adjustments based on model statistics

Args:
    image: Input PIL Image
    model_stats: Model statistics dictionary (if None, uses default)

Returns:
    Preprocessed PIL Image

##### analyze_dataset_metrics(self, folder_path)

Analyze all images in a folder to extract statistical metrics

Args:
    folder_path: Path to folder containing images

Returns:
    Dictionary with dataset statistics

##### run_diagnostic(self, image_path)

Run diagnostic analysis on pottery drawing

Args:
    image_path: Path to image to analyze

Returns:
    Dictionary with diagnostic information

### PDFExtractor

Extract images from PDF files - Step 1 of PyPotteryLens workflow

#### Methods

##### __init__(self)

##### load_yolo_model(self)

Load YOLO model for pottery detection if available

##### detect_and_extract_pottery(self, image_path, confidence, kernel_size, iterations)

Detect pottery in image and extract with morphological operations

Args:
    image_path: Path to image
    confidence: Detection confidence threshold
    kernel_size: Size of morphological kernel
    iterations: Number of dilation iterations

Returns:
    List of detected pottery regions with masks

##### extract(self, pdf_path, output_dir, split_pages, auto_detect, confidence, kernel_size, iterations)

Extract images from PDF

Args:
    pdf_path: Path to PDF file
    output_dir: Output directory for images
    split_pages: Split pages into left/right
    auto_detect: Auto-detect pottery images using YOLO
    confidence: Detection confidence threshold

Returns:
    List of extracted image paths

### LayoutGenerator

Generate image layouts for pottery documentation

#### Methods

##### __init__(self)

##### get_font(self, size)

Get font for text rendering

##### create_preview(self, images, mode, page_size, rows, cols)

Create a preview of the layout

##### generate(self, images, output_path, mode, page_size, rows, cols, add_captions, add_scale, scale_cm)

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

### ImageProcessor

Process and enhance pottery images

#### Methods

##### __init__(self)

##### enhance_image(self, image_path, output_path, brightness, contrast, sharpness)

Enhance image quality

Args:
    image_path: Input image path
    output_path: Output image path
    brightness: Brightness adjustment (1.0 = no change)
    contrast: Contrast adjustment (1.0 = no change)
    sharpness: Sharpness adjustment (1.0 = no change)

Returns:
    True if successful

##### remove_background(self, image_path, output_path, threshold)

Simple background removal (white background)

Args:
    image_path: Input image path
    output_path: Output image path
    threshold: Threshold for white detection

Returns:
    True if successful

### PotteryInkProcessor

AI-powered pottery drawing enhancement using diffusion models
Transforms pencil drawings into publication-ready illustrations
Based on PyPotteryInk project

#### Methods

##### __init__(self, venv_python)

##### is_available(self)

Check if PotteryInk functionality is available

##### load_model(self, model_path)

Load PotteryInk model for processing

##### enhance_drawing(self, input_image_path, output_path, prompt, contrast_scale, patch_size, overlap, apply_preprocessing)

Transform a pencil drawing into publication-ready illustration

Args:
    input_image_path: Path to input pencil drawing
    output_path: Path for output illustration
    prompt: Processing prompt for AI model
    contrast_scale: Contrast enhancement factor
    patch_size: Size of processing patches
    overlap: Overlap between patches
    apply_preprocessing: Whether to apply preprocessing

Returns:
    True if successful, False otherwise

##### extract_elements(self, image_path, output_dir, min_area)

Extract individual pottery elements from processed image

Args:
    image_path: Path to processed image
    output_dir: Directory to save extracted elements
    min_area: Minimum area for detected elements

Returns:
    List of paths to extracted element images

##### batch_process(self, input_folder, output_folder, model_path, prompt, progress_callback)

Process multiple drawings in batch

Args:
    input_folder: Folder containing input drawings
    output_folder: Folder for processed outputs
    model_path: Path to PotteryInk model
    prompt: Processing prompt
    progress_callback: Function to call for progress updates

Returns:
    Dictionary with processing results and statistics

##### enhance_high_res(self, input_image_path, output_path, patch_size, overlap, contrast_scale, apply_preprocessing)

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

##### export_to_svg(self, image_path, output_path, simplify, min_path_size)

Export enhanced pottery drawing to SVG format

Args:
    image_path: Path to enhanced image
    output_path: Path for output SVG file
    simplify: Simplification factor for paths
    min_path_size: Minimum size for paths to include

Returns:
    True if successful, False otherwise

##### apply_preprocessing(self, image, model_stats)

Apply recommended preprocessing adjustments based on model statistics

Args:
    image: Input PIL Image
    model_stats: Model statistics dictionary (if None, uses default)

Returns:
    Preprocessed PIL Image

##### analyze_dataset_metrics(self, folder_path)

Analyze all images in a folder to extract statistical metrics

Args:
    folder_path: Path to folder containing images

Returns:
    Dictionary with dataset statistics

##### run_diagnostic(self, image_path)

Run diagnostic analysis on pottery drawing

Args:
    image_path: Path to image to analyze

Returns:
    Dictionary with diagnostic information

### PDFExtractor

Extract images from PDF files - Step 1 of PyPotteryLens workflow

#### Methods

##### __init__(self)

##### load_yolo_model(self)

Load YOLO model for pottery detection if available

##### detect_and_extract_pottery(self, image_path, confidence, kernel_size, iterations)

Detect pottery in image and extract with morphological operations

Args:
    image_path: Path to image
    confidence: Detection confidence threshold
    kernel_size: Size of morphological kernel
    iterations: Number of dilation iterations

Returns:
    List of detected pottery regions with masks

##### extract(self, pdf_path, output_dir, split_pages, auto_detect, confidence, kernel_size, iterations)

Extract images from PDF

Args:
    pdf_path: Path to PDF file
    output_dir: Output directory for images
    split_pages: Split pages into left/right
    auto_detect: Auto-detect pottery images using YOLO
    confidence: Detection confidence threshold

Returns:
    List of extracted image paths

### LayoutGenerator

Generate image layouts for pottery documentation

#### Methods

##### __init__(self)

##### get_font(self, size)

Get font for text rendering

##### create_preview(self, images, mode, page_size, rows, cols)

Create a preview of the layout

##### generate(self, images, output_path, mode, page_size, rows, cols, add_captions, add_scale, scale_cm)

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

### ImageProcessor

Process and enhance pottery images

#### Methods

##### __init__(self)

##### enhance_image(self, image_path, output_path, brightness, contrast, sharpness)

Enhance image quality

Args:
    image_path: Input image path
    output_path: Output image path
    brightness: Brightness adjustment (1.0 = no change)
    contrast: Contrast adjustment (1.0 = no change)
    sharpness: Sharpness adjustment (1.0 = no change)

Returns:
    True if successful

##### remove_background(self, image_path, output_path, threshold)

Simple background removal (white background)

Args:
    image_path: Input image path
    output_path: Output image path
    threshold: Threshold for white detection

Returns:
    True if successful

### PotteryInkProcessor

AI-powered pottery drawing enhancement using diffusion models
Transforms pencil drawings into publication-ready illustrations
Based on PyPotteryInk project

#### Methods

##### __init__(self, venv_python)

##### is_available(self)

Check if PotteryInk functionality is available

##### load_model(self, model_path)

Load PotteryInk model for processing

##### enhance_drawing(self, input_image_path, output_path, prompt, contrast_scale, patch_size, overlap, apply_preprocessing)

Transform a pencil drawing into publication-ready illustration

Args:
    input_image_path: Path to input pencil drawing
    output_path: Path for output illustration
    prompt: Processing prompt for AI model
    contrast_scale: Contrast enhancement factor
    patch_size: Size of processing patches
    overlap: Overlap between patches
    apply_preprocessing: Whether to apply preprocessing

Returns:
    True if successful, False otherwise

##### extract_elements(self, image_path, output_dir, min_area)

Extract individual pottery elements from processed image

Args:
    image_path: Path to processed image
    output_dir: Directory to save extracted elements
    min_area: Minimum area for detected elements

Returns:
    List of paths to extracted element images

##### batch_process(self, input_folder, output_folder, model_path, prompt, progress_callback)

Process multiple drawings in batch

Args:
    input_folder: Folder containing input drawings
    output_folder: Folder for processed outputs
    model_path: Path to PotteryInk model
    prompt: Processing prompt
    progress_callback: Function to call for progress updates

Returns:
    Dictionary with processing results and statistics

##### enhance_high_res(self, input_image_path, output_path, patch_size, overlap, contrast_scale, apply_preprocessing)

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

##### export_to_svg(self, image_path, output_path, simplify, min_path_size)

Export enhanced pottery drawing to SVG format

Args:
    image_path: Path to enhanced image
    output_path: Path for output SVG file
    simplify: Simplification factor for paths
    min_path_size: Minimum size for paths to include

Returns:
    True if successful, False otherwise

##### apply_preprocessing(self, image, model_stats)

Apply recommended preprocessing adjustments based on model statistics

Args:
    image: Input PIL Image
    model_stats: Model statistics dictionary (if None, uses default)

Returns:
    Preprocessed PIL Image

##### analyze_dataset_metrics(self, folder_path)

Analyze all images in a folder to extract statistical metrics

Args:
    folder_path: Path to folder containing images

Returns:
    Dictionary with dataset statistics

##### run_diagnostic(self, image_path)

Run diagnostic analysis on pottery drawing

Args:
    image_path: Path to image to analyze

Returns:
    Dictionary with diagnostic information

