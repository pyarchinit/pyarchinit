# modules/utility/VideoPlayerArtefact.py

## Overview

This file contains 21 documented elements.

## Classes

### VideoPlayerWindow

`VideoPlayerWindow` is a `QMainWindow` subclass that provides a video playback interface using OpenCV for frame rendering and pygame for audio playback, displayed within a Qt widget layout containing a video label, play/pause button, seek slider, and time label. The window remains always on top and supports loading video files via `set_video`, with synchronized audio and frame-accurate seeking through the slider controls. It also provides functionality to capture the current video frame, save it as a PNG image to a configured thumbnail directory, insert the resulting media records into a database, and associate them with inventory material records via tag assignment.

**Inherits from**: QMainWindow

#### Methods

##### __init__(self, parent, db_manager, icon_list_widget, main_class)

Initializes a `VideoPlayerWindow` instance by configuring the main window properties (title, geometry, and minimum size) and storing references to the provided `db_manager`, `icon_list_widget`, and `main_class` parameters, along with an empty `bookmarks` list. Constructs the UI layout consisting of a central widget with a video display label, a play/pause button, a horizontal seek slider, a time label, and a save-frame button arranged in vertical and horizontal layouts. Initializes playback state variables (`cap`, `is_playing`, `has_audio`), sets up a `QTimer` connected to `update_frame`, initializes `pygame` and its mixer for audio support, and applies the `Qt.WindowStaysOnTopHint` flag to keep the window always on top.

##### set_video(self, file_path)

*No description available.*
Opens and initializes a video file for playback using the specified `file_path`. It reads the total frame count and frames-per-second from the video capture, configures the slider range accordingly, and updates the time label. Additionally, it attempts to load the file's audio track via `pygame.mixer.music`; if loading fails, `has_audio` is set to `False`. Upon successful initialization, the first frame of the video is retrieved and displayed.

##### play_pause(self)

*No description available.*
Toggles the playback state of the currently loaded video between playing and paused. When pausing, the timer is stopped and audio (if present) is paused via `pygame.mixer.music.pause()`; when resuming, the timer is started at the interval derived from `self.fps` and audio playback restarts from the current slider position. The play/pause button label is updated accordingly, and `self.is_playing` is toggled to reflect the new state.

##### update_frame(self)

*No description available.*
Advances playback by reading the next frame from the video capture object and displaying it via `display_frame`, while synchronizing the slider position and time label. If the current frame has not yet reached the end of the video, the frame is read and the UI controls are updated accordingly. When the last frame is reached, the timer and audio are stopped, playback state is reset, and the video and slider are rewound to the beginning with the first frame displayed.

##### display_frame(self, frame)

*No description available.*
Converts a BGR-formatted OpenCV frame to RGB and renders it in the UI's video label widget. The frame is wrapped into a `QImage` with `Format_RGB888` encoding, converted to a `QPixmap`, and scaled to fit `self.video_label`'s current size while preserving the aspect ratio using smooth transformation. If `frame` is `None`, the method performs no action.

##### slider_moved(self, position)

*No description available.*
Handles slider movement events by seeking the video capture object to the specified frame position. If a video capture (`self.cap`) is active, it sets the capture's frame position using `cv2.CAP_PROP_POS_FRAMES`, retrieves and displays the corresponding frame, and updates the time label to reflect the new position.

**Parameters:**
- `position` — The target frame number to seek to within the video.

##### slider_released(self)

*No description available.*
Handles the event triggered when the user releases the video position slider. Sets the video capture position to the slider's current value and, if playback is active and audio is available, resumes audio playback via `pygame.mixer.music.play` at the corresponding timestamp derived from the position and frame rate. If playback is not active, the frame at the new position is displayed directly and the time label is updated in either case.

##### get_frame(self, position)

*No description available.*
Seeks the video capture object to the specified frame position using `cv2.CAP_PROP_POS_FRAMES` and reads the frame at that position. Returns the decoded frame if the read operation succeeds, or `None` if it fails.

##### update_time_label(self)

Updates the time label displayed in the UI to reflect the current playback position. When a video capture object is available, it calculates the current time from the slider's value and the total duration from the total frame count, both divided by the frame rate. The label is formatted as `MM:SS / MM:SS`, showing elapsed time alongside total video duration.

##### save_frame_to_db(self)

Extracts the current video frame indicated by the slider position and saves it as a lossless PNG image to the configured thumbnail and resize paths, after validating that the required site and inventory number fields are populated and that a valid thumbnail path is configured. The method prompts the user for a base filename, automatically appending an incrementing counter suffix if the filename already exists in the database, then inserts corresponding records into the `MEDIA` and `MEDIA_THUMB` database tables. If the media record is successfully created, a 100×100 pixel thumbnail is saved, and the image is added as an icon item to `iconListWidget` with associated tags generated via `generate_US` and assigned via `assignTags_US`.

##### generate_US(self)

*No description available.*
Queries the database for inventory material records (`INVENTARIO_MATERIALI`) matching the current site (`comboBox_sito`) and inventory number (`lineEdit_num_inv`) values retrieved from the main UI. For each matching record, it constructs a list of three-element entries containing the record's `id_invmat`, the string `'REPERTO'`, and the table name `'inventario_materiali_table'`; records lacking the `id_invmat` attribute trigger an informational `QMessageBox` warning. Returns the assembled list, which will be empty if no matching records are found.

##### assignTags_US(self, item)

*No description available.*
Assigns US (Unità Stratigrafica) tags to a media item by first retrieving the list of US records via `generate_US()`. For each US record found, it queries the database for the media entry matching the filename of the provided `item`, then creates a media-to-entity association record using `insert_mediaToEntity_rec()`. If no US records are returned by `generate_US()`, the method exits without performing any database operations.

##### db_search_check(self, table, field, value)

*No description available.*
Queries the database for records in the specified table where the given field matches the provided value. It constructs a search dictionary mapping the field to the string-formatted value, removes any empty entries via `Utility.remove_empty_items_fr_dict`, and executes a boolean query through `DB_MANAGER.query_bool` against the resolved table class. Returns the query result.

##### insert_record_media(self, mediatype, filename, filetype, filepath)

*No description available.*
Inserts a new media record into the database by assigning the next available media ID and constructing a media entry with the provided type, filename, file type, and file path, along with a default description of `'Insert description'` and a default tag of `"['imagine']"`.

On successful insertion, the method returns the newly assigned `media_id`. If the insertion fails due to an integrity constraint (e.g., a duplicate entry), a warning dialog is displayed indicating the image already exists in the database; any other exception also triggers a warning dialog, and `None` is returned in both failure cases.

##### insert_record_mediathumb(self, media_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

*No description available.*
```python
def insert_record_mediathumb(self, media_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)
```

Inserts a new media thumbnail record into the `MEDIA_THUMB` database table using the provided media metadata. Before insertion, it queries the database to check whether a record with the given `filename_thumb` already exists; if so, it skips insertion and returns `True`. On successful insertion it returns `True`; on failure it returns `False`, printing an error message to the console — with specific handling for integrity constraint violations.

##### insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name)

*No description available.*
```python
def insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name)
```

Inserts a new media-to-entity association record into the `MEDIATOENTITY` table, linking a media item identified by `id_media` to an entity identified by `id_entity` and `entity_type`. Before inserting, the method queries the database to check whether a matching record already exists; if so, it skips the insertion and returns `1`. On a successful insert it returns `1`, and on failure returns `0`, printing a warning or error message accordingly.

##### save_image_to_db(self, file_path, format)

*No description available.*
Reads an image from the specified file path using OpenCV, generates a proportionally scaled thumbnail with a maximum size of 150×150 pixels, and encodes both the full image and thumbnail into bytes using the given format. Constructs a media data dictionary containing the filename, thumbnail data, tags (`'video_frame'`), media type, and file path, then inserts the record into the database via `db_manager.insert_media_values()`. Displays a warning dialog if the database manager is unavailable or if the insertion fails, and an informational dialog upon success.

##### closeEvent(self, event)

*No description available.*
Intercepts the window close event to perform resource cleanup before suppressing the actual closure. If a video capture object (`self.cap`) is active, it is released; if audio is present (`self.has_audio`), the pygame music playback is stopped and pygame is shut down. Rather than closing the window, the method hides it and calls `event.ignore()` to cancel the close event.

##### shutdown(self)

*No description available.*
Performs a complete teardown of the window and its associated resources. If a video capture object (`cap`) is active, it is released; if audio is present (`has_audio`), the pygame music playback is stopped and pygame is fully quit. Finally, the window itself is closed via `self.close()`.

##### resizeEvent(self, event)

*No description available.*
Handles the widget resize event by delegating to the parent class implementation via `super().resizeEvent(event)`. If a video capture object (`self.cap`) is currently loaded, it retrieves the frame at the current slider position and redraws it to reflect the new widget dimensions.

**Parameters:**
- `event` — The resize event passed to the parent class handler.

