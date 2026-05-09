# modules/utility/VideoPlayerPottery.py

## Overview

This file contains 21 documented elements.

## Classes

### VideoPlayerWindow

*No description available.*
A `QMainWindow` subclass that provides an embedded video playback interface with integrated database persistence. It uses OpenCV for frame decoding and rendering, a horizontal slider for seeking, and pygame for audio playback, with playback controls (play/pause, seek) synchronized between the video stream and audio track. The window also supports capturing the current frame as a PNG image, saving it to the database as a media record with an associated thumbnail, and linking it to matching pottery records retrieved via the provided database manager.

**Inherits from**: QMainWindow

#### Methods

##### __init__(self, parent, db_manager, icon_list_widget, main_class)

Initializes a `VideoPlayerWindow` instance by configuring the main window properties (title, geometry, and minimum size) and storing references to the provided `db_manager`, `icon_list_widget`, and `main_class` parameters, along with an empty `bookmarks` list. Constructs the UI layout consisting of a central widget with a video display label, a play/pause button, a horizontal slider with position tracking, a time label, and a save-frame button arranged in vertical and horizontal layouts. Initializes playback state variables (`cap`, `timer`, `is_playing`, `has_audio`), sets up a `QTimer` connected to `update_frame`, initializes `pygame` and its mixer for audio support, and applies the `Qt.WindowStaysOnTopHint` flag to keep the window always on top.

##### set_video(self, file_path)

*No description available.*
Opens and initializes a video file for playback by loading it into an OpenCV `VideoCapture` object. Retrieves the total frame count and frame rate from the capture, configures the slider range accordingly, and updates the time label. Attempts to load the file's audio track via `pygame.mixer.music`; sets `has_audio` to `True` on success or `False` if a `pygame.error` is raised, then renders the first frame of the video.

##### play_pause(self)

*No description available.*
Toggles the playback state of the currently loaded video between playing and paused. When pausing, the timer is stopped and audio (if present) is suspended via `pygame.mixer.music.pause()`; when resuming, the timer is started at an interval derived from the video's frame rate and audio playback resumes from the current slider position. The play/pause button label is updated accordingly, and `is_playing` is toggled to reflect the new state.

##### update_frame(self)

*No description available.*
Advances the video playback by reading the next frame from the capture object and displaying it via `display_frame`, while synchronizing the slider position and time label. If the current frame has not yet reached the end of the video, the frame is read and the UI controls are updated accordingly. When the last frame is reached, the timer and audio are stopped, playback state is reset, the slider is returned to position zero, and the first frame is displayed.

##### display_frame(self, frame)

*No description available.*
Converts a BGR-formatted OpenCV frame to RGB and renders it on the video label widget. The frame is wrapped into a `QImage` with `Format_RGB888` encoding, converted to a `QPixmap`, and scaled to fit `self.video_label`'s current size while preserving the aspect ratio using smooth transformation. If `frame` is `None`, the method performs no action.

##### slider_moved(self, position)

*No description available.*
Handles slider movement events by seeking the video capture object to the specified frame position when a capture device is active. Sets the video capture's frame position using `cv2.CAP_PROP_POS_FRAMES`, then retrieves and displays the corresponding frame via `display_frame` and `get_frame`. The time label is subsequently updated to reflect the new playback position.

##### slider_released(self)

*No description available.*
Handles the event triggered when the user releases the video position slider. Sets the video capture position to the slider's current value and, if playback is active and audio is available, resumes audio playback via `pygame.mixer.music.play` at the corresponding timestamp derived from the position and frame rate. If playback is not active, the frame at the new position is displayed directly and the time label is updated in either case.

##### get_frame(self, position)

*No description available.*
Seeks the video capture object to the specified frame position using `cv2.CAP_PROP_POS_FRAMES` and reads the frame at that position. Returns the decoded frame if the read operation succeeds (`ret` is truthy), or `None` if the read fails.

##### update_time_label(self)

Updates the time label displayed in the UI to reflect the current playback position. If a video capture object (`self.cap`) is available, it calculates the current time and total duration in minutes and seconds by dividing the slider's current frame value and the total frame count by the frame rate (`self.fps`). The result is formatted as `MM:SS / MM:SS` and set on `self.time_label`.

##### save_frame_to_db(self)

Captures the current video frame identified by the slider position and saves it as a lossless PNG image to the configured thumbnail and resize paths, after validating that the required fields (site, area, US, and ID number) are populated and a valid capture device is available. The resized image is scaled to 15×10 cm at 300 DPI and composited onto a white background, while a 100×100 pixel thumbnail is also generated and stored separately. Corresponding records are inserted into the `MEDIA` and `MEDIA_THUMB` database tables, and if successful, the media item is added to `iconListWidget` with its icon and associated tags.

##### generate_US(self)

Queries the database for `POTTERY` records matching the current values of site (`sito`), area, US, and ID number retrieved from the main class UI controls. For each matching record, it appends a three-element list containing `id_rep`, the string `'CERAMICA'`, and the string `'pottery_table'` to a result list, logging a warning dialog if a record lacks the `id_rep` attribute. Returns the assembled list of pottery record entries, or an empty list if no matching records are found.

##### assignTags_US(self, item)

*No description available.*
Assigns US (Unità Stratigrafica) tags to a media item by first retrieving the list of US records via `generate_US()`. For each US record returned, it queries the database for the media entry matching the filename of the provided `item`, then creates a media-to-entity association record using `insert_mediaToEntity_rec()`. If no US records are found, the method returns immediately without performing any database operations.

##### db_search_check(self, table, field, value)

*No description available.*
Queries the database for records in the specified table where the given field matches the provided value. It constructs a search dictionary mapping the field to the string-formatted value, removes any empty entries using a `Utility` helper, and executes a boolean query via `DB_MANAGER`. Returns the result of the query as produced by `query_bool`.

##### insert_record_media(self, mediatype, filename, filetype, filepath)

*No description available.*
```python
def insert_record_media(self, mediatype, filename, filetype, filepath)
```

Inserts a new media record into the database with the provided media metadata. The method automatically determines the next available media ID by incrementing the current maximum, then constructs and persists a new media entry with a default description of `'Insert description'` and a default tag of `"['imagine']"`. Returns the newly assigned `media_id` on success, or `None` if the insertion fails; in the case of an integrity violation (e.g., a duplicate entry), a warning dialog is displayed indicating the image already exists in the database.

##### insert_record_mediathumb(self, media_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

*No description available.*
```python
def insert_record_mediathumb(self, media_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)
```

Inserts a new media thumbnail record into the `MEDIA_THUMB` database table using the provided media metadata. Before insertion, it queries the database to check whether a record with the given `filename_thumb` already exists; if so, it skips the insert and returns `True`. On a successful insert it returns `True`, or `False` if an error occurs during record preparation or session insertion, logging integrity conflicts and other exceptions to standard output.

##### insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name)

*No description available.*
Inserts a new media-to-entity association record into the `MEDIATOENTITY` database table, linking a media item identified by `id_media` to an entity identified by `id_entity` and `entity_type`. Before inserting, the method queries the database to check whether a matching record already exists for the given `id_entity`, `entity_type`, and `id_media` combination; if so, it skips the insertion and returns `1`. On a successful insert, the method returns `1`; on failure it returns `0`, printing a warning message that distinguishes integrity constraint violations from other errors.

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

