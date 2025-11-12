# modules/utility/pyarchinit_tma_label_pdf.py

## Overview

This file contains 52 documented elements.

## Classes

### TMALabelPDF

Class to generate printable labels for TMA records.

#### Methods

##### __init__(self, label_format, page_size)

Initialize the label PDF generator.

Args:
    label_format: One of the predefined label formats
    page_size: Page size (default A4)

##### calculate_label_positions(self)

Calculate label positions on page.

##### get_color_for_site(self, site_name)

Get a consistent color for a site name.

##### draw_area_symbol(self, c, center_x, center_y, area, size)

Draw a distinctive symbol based on area code.

##### generate_qr_code(self, data, size, color)

Generate QR code image.

##### format_tma_data(self, tma_record)

Format TMA record data for label.

##### draw_label(self, c, x, y, tma_data, qr_data, label_style)

Draw a single label on the canvas.

##### extract_box_number(self, cassetta)

Extract numeric portion from cassetta field.

##### group_records_by_box(self, tma_records)

Group TMA records by box numeric portion.

##### generate_labels(self, tma_records, output_path, label_style, group_by_box)

Generate PDF with labels for TMA records.

Args:
    tma_records: List of TMA record objects
    output_path: Path for output PDF file
    label_style: Style of labels ('standard', 'minimal', 'detailed')
    group_by_box: Whether to group records by box number

##### generate_single_label(self, tma_record, output_path, label_style)

Generate a single label PDF.

### TMALabelPDF

Class to generate printable labels for TMA records.

#### Methods

##### __init__(self, label_format, page_size)

Initialize the label PDF generator.

Args:
    label_format: One of the predefined label formats
    page_size: Page size (default A4)

##### calculate_label_positions(self)

Calculate label positions on page.

##### get_color_for_site(self, site_name)

Get a consistent color for a site name.

##### draw_area_symbol(self, c, center_x, center_y, area, size)

Draw a distinctive symbol based on area code.

##### generate_qr_code(self, data, size, color)

Generate QR code image.

##### format_tma_data(self, tma_record)

Format TMA record data for label.

##### draw_label(self, c, x, y, tma_data, qr_data, label_style)

Draw a single label on the canvas.

##### extract_box_number(self, cassetta)

Extract numeric portion from cassetta field.

##### group_records_by_box(self, tma_records)

Group TMA records by box numeric portion.

##### generate_labels(self, tma_records, output_path, label_style, group_by_box)

Generate PDF with labels for TMA records.

Args:
    tma_records: List of TMA record objects
    output_path: Path for output PDF file
    label_style: Style of labels ('standard', 'minimal', 'detailed')
    group_by_box: Whether to group records by box number

##### generate_single_label(self, tma_record, output_path, label_style)

Generate a single label PDF.

### TMALabelPDF

Class to generate printable labels for TMA records.

#### Methods

##### __init__(self, label_format, page_size)

Initialize the label PDF generator.

Args:
    label_format: One of the predefined label formats
    page_size: Page size (default A4)

##### calculate_label_positions(self)

Calculate label positions on page.

##### get_color_for_site(self, site_name)

Get a consistent color for a site name.

##### draw_area_symbol(self, c, center_x, center_y, area, size)

Draw a distinctive symbol based on area code.

##### generate_qr_code(self, data, size, color)

Generate QR code image.

##### format_tma_data(self, tma_record)

Format TMA record data for label.

##### draw_label(self, c, x, y, tma_data, qr_data, label_style)

Draw a single label on the canvas.

##### extract_box_number(self, cassetta)

Extract numeric portion from cassetta field.

##### group_records_by_box(self, tma_records)

Group TMA records by box numeric portion.

##### generate_labels(self, tma_records, output_path, label_style, group_by_box)

Generate PDF with labels for TMA records.

Args:
    tma_records: List of TMA record objects
    output_path: Path for output PDF file
    label_style: Style of labels ('standard', 'minimal', 'detailed')
    group_by_box: Whether to group records by box number

##### generate_single_label(self, tma_record, output_path, label_style)

Generate a single label PDF.

### TMALabelPDF

Class to generate printable labels for TMA records.

#### Methods

##### __init__(self, label_format, page_size)

Initialize the label PDF generator.

Args:
    label_format: One of the predefined label formats
    page_size: Page size (default A4)

##### calculate_label_positions(self)

Calculate label positions on page.

##### get_color_for_site(self, site_name)

Get a consistent color for a site name.

##### draw_area_symbol(self, c, center_x, center_y, area, size)

Draw a distinctive symbol based on area code.

##### generate_qr_code(self, data, size, color)

Generate QR code image.

##### format_tma_data(self, tma_record)

Format TMA record data for label.

##### draw_label(self, c, x, y, tma_data, qr_data, label_style)

Draw a single label on the canvas.

##### extract_box_number(self, cassetta)

Extract numeric portion from cassetta field.

##### group_records_by_box(self, tma_records)

Group TMA records by box numeric portion.

##### generate_labels(self, tma_records, output_path, label_style, group_by_box)

Generate PDF with labels for TMA records.

Args:
    tma_records: List of TMA record objects
    output_path: Path for output PDF file
    label_style: Style of labels ('standard', 'minimal', 'detailed')
    group_by_box: Whether to group records by box number

##### generate_single_label(self, tma_record, output_path, label_style)

Generate a single label PDF.

