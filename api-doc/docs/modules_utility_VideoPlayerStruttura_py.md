# modules/utility/VideoPlayerStruttura.py

## Overview

This file contains 21 documented elements.

## Classes

### VideoPlayerWindow

`VideoPlayerWindow` is a `QMainWindow` subclass that provides a video playback interface using OpenCV for frame rendering and pygame for audio playback. It presents a central widget containing a video display label, a horizontal seek slider, a play/pause button, and a time label, with the window configured to remain always on top. The class also integrates with a database manager to support saving the current video frame as a PNG image, creating an associated thumbnail, and linking the media record to a corresponding `STRUTTURA` entity in the database.

**Inherits from**: QMainWindow

#### Methods

##### __init__(self, parent, db_manager, icon_list_widget, main_class)

Initializes a `VideoPlayerWindow` instance by configuring the main window properties (title, geometry, and minimum size) and storing references to the provided `db_manager`, `icon_list_widget`, and `main_class` parameters, along with an empty `bookmarks` list. Constructs the UI layout consisting of a central widget with a video display label, a play/pause button, a horizontal seek slider, a time label, and a save-frame button arranged in vertical and horizontal layouts. Initializes playback state variables (`cap`, `is_playing`, `has_audio`), sets up a `QTimer` connected to `update_frame`, initializes `pygame` and its mixer for audio support, and applies the `Qt.WindowStaysOnTopHint` flag to keep the window always on top.

##### set_video(self, file_path)

*No description available.*
Opens and initializes a video file for playback using the specified `file_path`. It reads the total frame count and frames-per-second from the video capture, configures the slider range accordingly, and updates the time label. Additionally, it attempts to load the file's audio track via `pygame.mixer.music`; if loading fails, `has_audio` is set to `False`. Upon successful initialization, the first frame of the video is retrieved and displayed.

##### play_pause(self)

*No description available.*
Toggles the playback state of the currently loaded video between playing and paused. When pausing, the timer is stopped and audio (if present) is paused via `pygame.mixer.music.pause()`; when resuming, the timer is started at an interval derived from the video's frame rate and audio playback resumes from the current slider position. The play/pause button label and the `is_playing` flag are updated accordingly to reflect the new state.

##### update_frame(self)

*No description available.*
Advances playback by reading the next frame from the video capture object and displaying it via `display_frame`, while synchronizing the slider position and time label. If the current frame has not yet reached the end of the video, the frame is read and the UI controls are updated accordingly. When the last frame is reached, the timer and audio are stopped, playback state is reset, and the video and slider are rewound to the beginning with the first frame displayed.

##### display_frame(self, frame)

*No description available.*
Converts a BGR-formatted OpenCV frame to RGB and renders it in the UI's video label widget. The frame is wrapped into a `QImage` with `Format_RGB888` encoding, converted to a `QPixmap`, and scaled to fit `self.video_label`'s current size while preserving the aspect ratio using smooth transformation. If `frame` is `None`, the method performs no action.

##### slider_moved(self, position)

Sets the video capture position to the specified frame `position` when the slider is moved, provided that a video capture object (`self.cap`) is currently active. It updates the displayed frame by calling `display_frame` with the result of `get_frame(position)`, then refreshes the time label via `update_time_label`.

##### slider_released(self)

*No description available.*
Handles the slider release event by synchronizing the video capture position to the current slider value. If the video is playing and audio is available, resumes audio playback from the corresponding timestamp calculated using the frame position and frame rate; otherwise, displays the frame at the selected position. Updates the time label to reflect the new position regardless of playback state.

##### get_frame(self, position)

*No description available.*
Seeks the video capture object to the specified frame position using `cv2.CAP_PROP_POS_FRAMES`, then reads and returns the frame at that position. Returns the decoded frame if the read operation succeeds (`ret` is truthy), or `None` if the read fails.

##### update_time_label(self)

*No description available.*
Updates the time display label to reflect the current playback position of the loaded video. When a video capture object (`self.cap`) is available, it calculates the current time and total duration in seconds by dividing the slider's current frame value and `self.total_frames` by `self.fps`, respectively. The result is formatted as `MM:SS / MM:SS` and set as the text of `self.time_label`.

##### save_frame_to_db(self)

*No description available.*
Captures the current video frame at the slider position and persists it as a PNG image record in the database. Before saving, the method validates that the site, structure sigla, and structure number fields are populated, retrieves configured thumbnail and resize paths via `Connection`, prompts the user for a filename (appending an auto-incremented counter if the name already exists), and writes both a full-resolution resized image (15×10 cm at 300 dpi on a white background) and a 100×100 pixel thumbnail to their respective directories. On success, it inserts corresponding records into the `MEDIA` and media thumbnail tables, adds the item to `iconListWidget` with its icon, and attempts to assign US tags; on failure or missing prerequisites, it displays an appropriate warning or informational dialog and returns early.

##### generate_US(self)

Queries the database for `STRUTTURA` records matching the site, structure abbreviation, and structure number retrieved from the main UI form controls. For each matching record, it appends a three-element list containing the record's `id_struttura`, the string `'STRUTTURA'`, and the string `'struttura_table'` to a result list. Returns the compiled list of structure entries, or an empty list if no matching records are found.

##### assignTags_US(self, item)

*No description available.*
Assigns US (Unità Stratigrafica) tags to a media item by first retrieving the US list via `generate_US()`. For each US entry in the list, it resolves the corresponding media record from the database by querying the `MEDIA` table using the filename derived from `item.text()`. It then creates a media-to-entity association for each US record by calling `insert_mediaToEntity_rec` with the US data and the resolved media record's `id_media`, `filepath`, and `filename`.

##### db_search_check(self, table, field, value)

*No description available.*
Queries the database for records in the specified table where the given field matches the provided value. It constructs a search dictionary mapping the field to the string-formatted value, removes any empty entries via `Utility.remove_empty_items_fr_dict`, and executes a boolean query through `DB_MANAGER.query_bool`. Returns the query result.

##### insert_record_media(self, mediatype, filename, filetype, filepath)

*No description available.*
Inserts a new media record into the database with the provided media type, filename, file type, and file path. The method automatically determines the next available media ID by incrementing the current maximum ID in the `MEDIA` table, then constructs and persists the record with a default description of `'Insert description'` and a default tag of `"['imagine']"`. Returns the newly assigned `media_id` on success, or `None` if the insertion fails; integrity constraint violations (e.g., duplicate entries) and other exceptions are reported to the user via a `QMessageBox` warning dialog.

##### insert_record_mediathumb(self, media_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

*No description available.*
```python
def insert_record_mediathumb(self, media_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)
```

Inserts a new thumbnail record into the `MEDIA_THUMB` database table using the provided media metadata. Before insertion, it queries the database to check whether a record with the given `filename_thumb` already exists; if so, it skips insertion and returns `True`. On successful insertion it returns `True`, or `False` if an error occurs during record preparation or the database session insert.

##### insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name)

*No description available.*
```python
def insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name)
```

Inserts a new media-to-entity association record into the `MEDIATOENTITY` database table, linking a media item identified by `id_media` to an entity identified by `id_entity` and `entity_type`. Before inserting, the method queries the database to check whether a matching record already exists for the given `id_entity`, `entity_type`, and `id_media` combination; if so, it skips the insertion and returns `1`. Returns `1` on success or if the record already exists, and `0` if an error occurs during data preparation or insertion.

##### save_image_to_db(self, file_path, format)

*No description available.*
Reads an image from the specified file path using OpenCV, generates a proportionally scaled thumbnail with a maximum size of 150×150 pixels, and encodes both the full image and thumbnail into bytes using the given format. Constructs a media data dictionary containing the filename, thumbnail bytes, thumbnail filename (prefixed with `"thumb_"`), tags set to `'video_frame'`, media type, and file path, then inserts the record into the database via `self.db_manager.insert_media_values()`. Displays a warning dialog if the database manager is unavailable or if the insert operation fails, and an information dialog upon successful insertion.

##### closeEvent(self, event)

*No description available.*
Intercepts the window close event to perform resource cleanup before suppressing the actual closure. If a video capture object (`self.cap`) is active, it is released; if audio is present (`self.has_audio`), the pygame music playback is stopped and pygame is shut down. Rather than closing the window, the method hides it and calls `event.ignore()` to cancel the close event.

##### shutdown(self)

*No description available.*
Performs a complete teardown of the window and its associated resources. If a video capture object (`cap`) is active, it is released; if audio is present (`has_audio`), the pygame music playback is stopped and pygame is fully quit. Finally, the window is closed via `self.close()`.

##### resizeEvent(self, event)

*No description available.*
Handles the widget resize event by delegating to the parent class implementation via `super().resizeEvent(event)`. If a video capture object (`self.cap`) is currently loaded, it retrieves the frame at the current slider position and redraws it to reflect the new widget dimensions.

**Parameters:**
- `event` — The resize event passed to the parent class handler.

