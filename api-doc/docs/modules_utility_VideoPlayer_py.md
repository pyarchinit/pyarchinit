# modules/utility/VideoPlayer.py

## Overview

This file contains 21 documented elements.

## Classes

### VideoPlayerWindow

`VideoPlayerWindow` is a `QMainWindow` subclass that provides a video playback interface using OpenCV for frame rendering and pygame for audio playback. It presents a central widget containing a video display label, a horizontal seek slider, a play/pause button, and a time label, with the window configured to remain always on top. The class also integrates with a database manager to capture and persist the current video frame as a media record — including a resized image, a thumbnail, and associated entity tag assignments — using contextual metadata sourced from a parent main class.

**Inherits from**: QMainWindow

#### Methods

##### __init__(self, parent, db_manager, icon_list_widget, main_class)

Initializes a `VideoPlayerWindow` instance by configuring the main window properties (title, geometry, and minimum size) and storing references to the provided `db_manager`, `icon_list_widget`, and `main_class` parameters, along with an empty `bookmarks` list. Constructs the UI layout consisting of a central widget with a video display label, a play/pause button, a horizontal seek slider, a time label, and a save-frame button arranged in vertical and horizontal layouts. Initializes playback state variables (`cap`, `is_playing`, `has_audio`), sets up a `QTimer` connected to `update_frame`, initializes `pygame` and its mixer for audio support, and applies the `Qt.WindowStaysOnTopHint` flag to keep the window always on top.

##### set_video(self, file_path)

*No description available.*
Opens and initializes a video file for playback using the specified `file_path`. It reads the total frame count and frames-per-second from the video capture, configures the slider range accordingly, and updates the time label. Additionally, it attempts to load the file's audio track via `pygame.mixer.music`; if loading fails, `has_audio` is set to `False` and a warning is printed. Finally, the first frame of the video is retrieved and displayed.

##### play_pause(self)

*No description available.*
Toggles the playback state of the currently loaded video between playing and paused. When pausing, the timer is stopped and audio (if present) is paused via `pygame.mixer.music.pause()`; when resuming, the timer is started at the interval derived from `self.fps` and audio playback restarts from the current slider position. The play/pause button label and the `is_playing` flag are updated accordingly to reflect the new state.

##### update_frame(self)

*No description available.*
Advances playback by reading the next frame from the video capture object and displaying it via `display_frame`, while synchronizing the slider position and time label. If the current frame has not yet reached the end of the video, the frame is read and the UI controls are updated accordingly. When the last frame is reached, the timer and audio are stopped, playback state is reset, and the video and slider are rewound to the beginning with the first frame displayed.

##### display_frame(self, frame)

*No description available.*
Converts a BGR-formatted OpenCV frame to RGB and renders it in the UI's video label widget. The frame is wrapped into a `QImage` with `Format_RGB888` encoding, converted to a `QPixmap`, and scaled to fit `self.video_label`'s current size while preserving the aspect ratio using smooth transformation. If `frame` is `None`, the method performs no action.

##### slider_moved(self, position)

*No description available.*
Handles slider movement events by seeking the video capture object to the specified frame position when a capture device is active. Sets the video capture's frame position using `cv2.CAP_PROP_POS_FRAMES`, then retrieves and displays the corresponding frame via `display_frame` and `get_frame`. The time label is subsequently updated to reflect the new playback position.

##### slider_released(self)

*No description available.*
Handles the event triggered when the user releases the video position slider. Sets the video capture position to the slider's current value and, if playback is active and audio is available, resumes audio playback via `pygame.mixer.music.play` at the corresponding timestamp derived from the position and frame rate. If the video is not playing, the frame at the new position is displayed directly, and the time label is updated in either case.

##### get_frame(self, position)

*No description available.*
Seeks the video capture object to the specified frame position using `cv2.CAP_PROP_POS_FRAMES` and reads the frame at that position. Returns the decoded frame if the read operation succeeds (`ret` is truthy), or `None` if the read fails.

##### update_time_label(self)

*No description available.*
Updates the time display label to reflect the current playback position relative to the total video duration. When a video capture object is available, it reads the current frame position from the slider value, converts both the current frame and total frame count to `MM:SS` formatted timestamps using the video's frame rate (`self.fps`), and sets the resulting string on `self.time_label` in the format `MM:SS / MM:SS`. No action is taken if `self.cap` is `None`.

##### save_frame_to_db(self)

*No description available.*
Captures the current video frame at the slider position and persists it as a PNG image record in the database, provided that the required fields (Site, Area, and US) are populated and a valid thumbnail path is configured. The frame is resized to 15×10 cm at 300 DPI and saved with a lossless PNG compression onto a white background, while a 100×100 pixel thumbnail is separately written to the configured thumbnail directory. If the media record is successfully inserted, the method also adds the image as an icon item to `iconListWidget` and assigns associated US tags; duplicate filenames are resolved automatically by appending an incrementing counter.

##### generate_US(self)

Queries the database for US (Stratigraphic Unit) records matching the current values of `sito`, `area`, and `us` fields retrieved from the main UI controls. For each matching record, it appends a three-element list containing the record's `id_us`, the string `'US'`, and the string `'us_table'` to a result list, logging a warning message if a record lacks the `id_us` attribute. Returns the assembled list of US record entries, or an empty list if no matching records are found.

##### assignTags_US(self, item)

*No description available.*
Assigns US (Unità Stratigrafica) tags to a media item by retrieving the list of US records via `generate_US()` and linking each one to the corresponding media entry in the database. For each US record, the method queries the `MEDIA` table using the filename derived from `item.text()`, then calls `insert_mediaToEntity_rec` to create the association between the US entity and the media record. If `generate_US()` returns an empty result, the method exits without performing any database operations.

##### db_search_check(self, table, field, value)

*No description available.*
Queries the database for records in the specified table where the given field matches the provided value. It constructs a search dictionary mapping the field to the string-formatted value, removes any empty entries using a `Utility` helper, and executes a boolean query via `DB_MANAGER`. Returns the result of the query as produced by `query_bool`.

##### insert_record_media(self, mediatype, filename, filetype, filepath)

*No description available.*
```python
def insert_record_media(self, mediatype, filename, filetype, filepath)
```

Inserts a new media record into the database with the provided media metadata. The method automatically determines the next available media ID by incrementing the current maximum, then constructs and persists a new record with a default description of `'Insert description'` and a default tag of `"['imagine']"`. Returns the newly assigned `media_id` on success, or `None` if the insertion fails, displaying a warning dialog for integrity violations (e.g., duplicate entries) or other exceptions.

##### insert_record_mediathumb(self, media_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

*No description available.*
```python
def insert_record_mediathumb(self, media_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)
```

Inserts a new media thumbnail record into the `MEDIA_THUMB` database table using the provided media metadata. Before insertion, it queries the database to check whether a record with the given `filename_thumb` already exists; if so, it skips the insert and returns `True`. On a successful insert it returns `True`, or `False` if an error occurs during record preparation or session insertion, with integrity constraint violations and other exceptions handled and reported via print output.

##### insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name)

*No description available.*
Inserts a new media-to-entity association record into the `MEDIATOENTITY` table, linking a media item identified by `id_media` to an entity identified by `id_entity` and `entity_type`. Before inserting, the method queries the database to check whether a matching record already exists; if so, it skips the insertion and returns `1`. On a successful insert it returns `1`, and on failure returns `0`, logging a warning message that distinguishes integrity constraint violations from other exceptions.

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

