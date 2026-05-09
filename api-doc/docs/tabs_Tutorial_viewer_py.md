# tabs/Tutorial_viewer.py

## Overview

This file contains 25 documented elements.

## Classes

### TutorialViewerDialog

Dialog for viewing PyArchInit tutorials with multilingual support

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent)

Initializes a `TutorialDialog` (or equivalent) dialog instance by calling the parent constructor and configuring the window title and minimum/default size based on the detected QGIS interface language. It resolves the plugin's tutorials directory path, then calls `setup_ui()` and `load_tutorial_list()` to build the interface and populate the tutorial list. Finally, it integrates theme support via `ThemeManager`, connects the theme toggle button to `_on_theme_toggled`, applies the current theme, and selects the first tutorial entry by default if any are present.

##### detect_language(self)

Detect QGIS locale and return language code

##### get_tutorials_path(self, lang)

Get the tutorials path for a specific language

##### setup_ui(self)

Setup the dialog UI

##### eventFilter(self, obj, event)

Handle mouse events for image hover popup

##### get_figure_at_position(self, pos)

Check if position is over a figure thumbnail and return image path

##### handle_mouse_move(self, event)

Check if mouse is over a figure and show popup with debounce

##### show_hover_popup(self, img_path)

Show hover popup with full-size image centered in dialog

##### hide_hover_popup(self)

Hide the hover popup

##### show_image_dialog(self, img_path)

Show image in a dialog with close button

##### on_language_changed(self, index)

Handle language change

##### update_ui_labels(self)

Update UI labels after language change

##### load_tutorial_list(self)

Load the list of available tutorials for current language

##### filter_tutorials(self, text)

Filter tutorials based on search text

##### on_tutorial_selected(self, current, previous)

Handle tutorial selection

##### load_tutorial_content(self, filepath)

Load and display tutorial content

##### markdown_to_html(self, markdown_text)

Convert markdown to HTML using basic regex patterns.
This is a simple converter that handles common markdown elements.

##### convert_tables(self, html)

Convert markdown tables to HTML

##### convert_lists(self, html)

Convert markdown lists to HTML

## Functions

### replace_code_block(match)

*No description available.*
A regex match handler that converts a fenced Markdown code block (` ``` `) into an HTML `<pre><code>` element. It extracts the optional language identifier from the first capture group and the code content from the second, escaping HTML special characters (`&`, `<`, `>`) in the code body before rendering. The resulting HTML element includes a `language-{lang}` class on the `<code>` tag to support syntax highlighting conventions.

**Parameters:**
- `match`

### replace_inline_code(match)

*No description available.*
A regex match callback that converts a single backtick-delimited inline code span into an HTML `<code>` element. The captured code content is HTML-escaped by replacing `&`, `<`, and `>` with their corresponding HTML entities (`&amp;`, `&lt;`, `&gt;`) before being wrapped in `<code>` tags. This function is intended for use as the replacement callable in `re.sub(r'`([^`]+)`', ...)`, and must be applied after fenced code block substitution to avoid conflicts.

**Parameters:**
- `match`

### replace_image(match)

Processes a regex match object representing a Markdown image token (`![alt](path)`) and converts it to an HTML representation. If `self.current_tutorial_dir` is set and the resolved absolute path exists, the function reads the image file, encodes it in Base64, generates an 80-pixel-maximum thumbnail using `PIL`, caches both the full image data in `self._image_cache` and the thumbnail-to-full-path mapping in `self._thumb_to_full`, and returns an HTML `<p>` element containing the thumbnail as a data URI alongside the alt text and a click-to-enlarge label. If the file does not exist, an error span is returned; if `current_tutorial_dir` is not set, a plain `<img>` tag with the original path and alt text is returned instead.

**Parameters:**
- `match`

### convert_blockquote(match)

*No description available.*
A regex match callback that converts Markdown-style blockquote syntax into an HTML `<blockquote>` element. It processes the full matched block by splitting it into individual lines, stripping the leading `>` character and surrounding whitespace from each qualifying line, and joining the resulting lines with `<br>` tags. The assembled content is wrapped in `<blockquote>...</blockquote>` tags and returned as a string for substitution by `re.sub`.

**Parameters:**
- `match`

