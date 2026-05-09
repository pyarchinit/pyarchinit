# gui/imageViewer.py

## Overview

This file contains 8 documented elements.

## Classes

### ImageViewer

*No description available.*
A `QDialog` subclass that provides a modal image viewing interface supporting both local file paths and remote URLs (including `http://`, `https://`, `cloudinary://`, and `unibo://` schemes). It renders images inside a `QGraphicsView`-based widget and stores the currently displayed image path for later use. An "Esporta" button is included in the dialog's button box, allowing the user to export the current image to a user-chosen local destination via `QFileDialog`.

**Inherits from**: QDialog, IMAGE_VIEWER

#### Methods

##### __init__(self, parent, origPixmap)

Initializes an `ImageViewer` dialog instance by invoking the `QDialog` constructor with the given `parent` and calling `setupUi` to configure the UI layout defined by `IMAGE_VIEWER`. Sets `current_image_path` to `None` to track the currently displayed image path for export purposes. Creates an "Esporta" (`QPushButton`), connects it to the `export_image` method, and adds it to the dialog's `buttonBox` with `ActionRole`.

##### show_image(self, path, flags)

Displays an image at the specified path in a QGraphicsView widget.
Supports local paths, HTTP/HTTPS URLs, cloudinary://, and unibo:// paths.

Args:
    path (str): The path to the image file (local or remote).
    flags (Union[Qt.AspectRatioMode, Qt.Transformations], optional): The aspect ratio mode to use when displaying the image. Defaults to Qt.AspectRatioMode.KeepAspectRatioByExpanding.

Returns:
    None

##### export_image(self)

Export the current image to a user-chosen location.
Works with both local and remote (unibo://, http://, cloudinary://) paths.

### ImageViewClass

*No description available.*
A `QGraphicsView` subclass designed to display an image scaled to the current widget size. It defines a fixed zoom factor of `1.25` and accepts an optional `origPixmap` parameter at construction to retain a reference to the original pixmap. The `wheelEvent` override implements mouse-anchored zoom functionality, scaling the view in or out based on the vertical scroll direction of the mouse wheel and translating the scene to keep the content under the cursor stable.

**Inherits from**: QGraphicsView

#### Methods

##### __init__(self, parent, origPixmap)

QGraphicsView that will show an image scaled to the current widget size

using events

##### wheelEvent(self, event)

*No description available.*
Handles mouse wheel scroll events to zoom the graphics view in or out, using `self.zoom_in` as the zoom factor for upward scrolling and its reciprocal for downward scrolling. The resize and transformation anchors are set to `AnchorUnderMouse`, and the drag mode is set to `ScrollHandDrag` before applying the scale transformation. To correct for positional drift introduced by scaling, the scene position under the cursor is sampled before and after the scale operation, and the view is translated by the resulting delta to keep the point under the mouse stationary.

