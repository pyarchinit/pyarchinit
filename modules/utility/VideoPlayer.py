
import os
import numpy as np
import cv2
import pygame
from qgis.PyQt.QtCore import QTimer,Qt
from qgis.PyQt.QtGui import QImage, QPixmap,QIcon
from qgis.PyQt.QtWidgets import QTableWidgetItem, QInputDialog, QMainWindow, QListWidgetItem,  QMessageBox, QWidget, QLabel, QSizePolicy, QSlider, QPushButton, QHBoxLayout, QVBoxLayout


from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_utility import Utility

class VideoPlayerWindow(QMainWindow):
    def __init__(self, parent, db_manager=None, icon_list_widget=None, main_class=None):
        super().__init__(parent)
        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(400, 300)

        self.DB_MANAGER = db_manager
        self.iconListWidget = icon_list_widget
        self.mainclass = main_class
        self.bookmarks = []

        # Creiamo un widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principale
        main_layout = QVBoxLayout(central_widget)

        # Creazione dei widget
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_pause)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.slider_moved)
        self.slider.sliderReleased.connect(self.slider_released)

        self.time_label = QLabel()

        self.save_frame_button = QPushButton("Save Frame")
        self.save_frame_button.clicked.connect(self.save_frame_to_db)

        # Creazione dei layout
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.slider)
        control_layout.addWidget(self.time_label)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_frame_button)

        # Aggiunta dei widget e layout al layout principale
        main_layout.addWidget(self.video_label)
        main_layout.addLayout(control_layout)
        main_layout.addLayout(button_layout)

        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.is_playing = False
        self.has_audio = False

        pygame.init()
        pygame.mixer.init()
        # Imposta la finestra del video player per stare sempre sopra
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)


    def set_video(self, file_path):
        self.cap = cv2.VideoCapture(file_path)
        if not self.cap.isOpened():
            print(f"Error: Could not open video file {file_path}")
            return

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.slider.setRange(0, self.total_frames - 1)
        self.update_time_label()

        try:
            pygame.mixer.music.load(file_path)
            self.has_audio = True
        except pygame.error:
            print("Warning: Could not load audio from the video file")
            self.has_audio = False

        self.display_frame(self.get_frame(0))

    def play_pause(self):
        if self.cap is None:
            return

        if self.is_playing:
            self.timer.stop()
            if self.has_audio:
                pygame.mixer.music.pause()
            self.play_button.setText("Play")
        else:
            self.timer.start(int(1000 / self.fps))
            if self.has_audio:
                pygame.mixer.music.play(-1, self.slider.value() / self.fps)
            self.play_button.setText("Pause")
        self.is_playing = not self.is_playing

    def update_frame(self):
        current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        if current_frame < self.total_frames - 1:
            ret, frame = self.cap.read()
            if ret:
                self.display_frame(frame)
                self.slider.setValue(current_frame)
                self.update_time_label()
        else:
            self.timer.stop()
            if self.has_audio:
                pygame.mixer.music.stop()
            self.play_button.setText("Play")
            self.is_playing = False
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.slider.setValue(0)
            self.display_frame(self.get_frame(0))

    def display_frame(self, frame):
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.video_label.setPixmap(scaled_pixmap)

    def slider_moved(self, position):
        if self.cap is not None:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
            self.display_frame(self.get_frame(position))
            self.update_time_label()

    def slider_released(self):
        if self.cap is not None:
            position = self.slider.value()
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
            if self.is_playing:
                if self.has_audio:
                    pygame.mixer.music.play(-1, position / self.fps)
            else:
                self.display_frame(self.get_frame(position))
            self.update_time_label()

    def get_frame(self, position):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
        ret, frame = self.cap.read()
        return frame if ret else None

    def update_time_label(self):
        if self.cap is not None:
            current_frame = self.slider.value()
            current_time = current_frame / self.fps
            total_time = self.total_frames / self.fps
            self.time_label.setText(f'{int(current_time // 60):02d}:{int(current_time % 60):02d} / '
                                    f'{int(total_time // 60):02d}:{int(total_time % 60):02d}')

    def save_frame_to_db(self):
        # Check if required fields are set
        sito = self.mainclass.comboBox_sito.currentText()
        us = self.mainclass.lineEdit_us.text()
        area = self.mainclass.comboBox_area.currentText()

        if not sito or not area or not us:
            QMessageBox.warning(self, "Warning",
                                "Please ensure that Site, Divelog ID, and Year are set before saving the frame.")
            return

        if self.cap is None:
            return

        current_frame = self.slider.value()
        frame = self.get_frame(current_frame)
        if frame is None:
            return

        conn = Connection()
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        thumb_resize = conn.thumb_resize()
        thumb_resize_str = thumb_resize['thumb_resize']

        if thumb_path_str == '':
            QMessageBox.information(self, "Info",
                                    "You must first set the path to save the thumbnails and videos. Go to system/path setting")
            return


        # Ask user for image name
        base_filename, ok = QInputDialog.getText(self, "Save Frame", "Enter a name for the image:")
        if not ok or not base_filename:
            return

        # Verifica se il filename esiste già e, in caso affermativo, aggiunge un contatore
        counter = 0
        while True:
            filename = f"{base_filename}_{counter}" if counter > 0 else base_filename
            if not self.DB_MANAGER.query_bool({'filename': f"'{filename}'"}, 'MEDIA'):
                break
            counter += 1

        filetype = "png"
        mediatype = "image"
        # Get the max id from the media table
        media_max_num_id = self.DB_MANAGER.max_num_id('MEDIA', 'id_media')
        # Create thumbnail and resized image
        media_thumb_suffix = '_thumb.png'
        media_resize_suffix = '.png'
        filename_thumb = f"{media_max_num_id}_{filename}{media_thumb_suffix}"
        filename_resize = f"{media_max_num_id}_{filename}"
        filepath_thumb = filename_thumb
        filepath_resize = filename_resize
        # Save resized image at 300 dpi, 15x10 cm
        filepath_r = os.path.join(thumb_resize_str, f"{filename_resize}.{filetype}")

        # Calculate pixel dimensions for 15x10 cm at 300 dpi
        dpi = 300
        cm_to_inch = 0.393701  # 1 cm = 0.393701 inches
        width_inch = 15 * cm_to_inch
        height_inch = 10 * cm_to_inch
        width_pixels = int(width_inch * dpi)
        height_pixels = int(height_inch * dpi)

        # Resize the image
        resized_image = cv2.resize(frame, (width_pixels, height_pixels), interpolation=cv2.INTER_AREA)

        # Create a new image with white background
        white_background = np.ones((height_pixels, width_pixels, 3), dtype=np.uint8) * 255

        # Calculate position to paste the resized image
        y_offset = (height_pixels - resized_image.shape[0]) // 2
        x_offset = (width_pixels - resized_image.shape[1]) // 2

        # Paste the resized image onto the white background
        white_background[y_offset:y_offset + resized_image.shape[0],
        x_offset:x_offset + resized_image.shape[1]] = resized_image

        # Save the image
        cv2.imwrite(filepath_r, white_background, [cv2.IMWRITE_PNG_COMPRESSION, 0])  # Use PNG for lossless compression

        # Check if the image already exists in the database
        idunique_image_check = self.db_search_check('MEDIA', 'filepath', filepath_r)
        if bool(idunique_image_check):
            return

        # Insert record in the media table
        media_id = self.insert_record_media(mediatype, filename, filetype, filepath_r)

        if media_id:
            # Create and save thumbnail
            filepath_t = os.path.join(thumb_path_str, f"{filename_thumb}.{filetype}")
            thumb = cv2.resize(frame, (100, 100))
            cv2.imwrite(filepath_t, thumb)

            # Insert record in the media_thumb table
            self.insert_record_mediathumb(media_id, mediatype, filename, filename_thumb, filetype,
                                          filepath_thumb, filepath_resize)




            # Add item to the iconListWidget if available
            if self.iconListWidget is not None:
                item = QListWidgetItem(filename)
                item.setData(Qt.UserRole, str(media_id))
                icon = QIcon(filepath_t)  # Usa filepath_t invece di filepath_thumb
                item.setIcon(icon)
                self.iconListWidget.addItem(item)
                # Generate and assign tags
                us_list = self.generate_US()
                if us_list:
                    self.assignTags_US(item)
                    self.iconListWidget.repaint()
                else:
                    print("No tags generated for this item")
        else:
            QMessageBox.warning(self, "Error", "Failed to insert media record")
            return




    def generate_US(self):
        sito = self.mainclass.comboBox_sito.currentText()
        us = self.mainclass.lineEdit_us.text()
        area = self.mainclass.comboBox_area.currentText()


        #QMessageBox.information(self, 'test', f"Warning: Record {sito}\n{divelog}\n{years}"


        search_dict = {
            'sito': "'" + str(sito) + "'",
            'area': "'" + str(area) + "'",
            'us': "'" + str(us) + "'"
        }

        records = self.DB_MANAGER.query_bool(search_dict, 'US')

        us_list = []
        for record in records:
            if hasattr(record, 'id_us'):
                us_list.append([record.id_us, 'US', 'us_table'])
            else:
                QMessageBox.information(self,'test',f"Warning: Record {record} does not have 'gid' attribute")

        if not us_list:
            print("No matching records found in generate_US")
            #print(f"Search parameters: Site: {sito}, Divelog: {divelog}, Years: {years}")

        return us_list



    def assignTags_US(self, item):

        us_list = self.generate_US()

        # QMessageBox.information(self,'search db',str(us_list))
        if not us_list:
            return

        for us_data in us_list:
            id_orig_item = item.text()  # return the name of original file
            search_dict = {'filename': "'" + str(id_orig_item) + "'"}
            media_data = self.DB_MANAGER.query_bool(search_dict, 'MEDIA')
            self.insert_mediaToEntity_rec(us_data[0], us_data[1], us_data[2], media_data[0].id_media,
                                          media_data[0].filepath, media_data[0].filename)


    def db_search_check(self, table, field, value):
        self.table_class = table
        search_dict = {field: "'" + str(value) + "'"}
        u = Utility()
        search_dict = u.remove_empty_items_fr_dict(search_dict)
        res = self.DB_MANAGER.query_bool(search_dict, self.table_class)
        return res

    def insert_record_media(self, mediatype, filename, filetype, filepath):
        self.mediatype = mediatype
        self.filename = filename
        self.filetype = filetype
        self.filepath = filepath
        try:
            media_id = self.DB_MANAGER.max_num_id('MEDIA', 'id_media') + 1
            data = self.DB_MANAGER.insert_media_values(
                media_id,
                str(self.mediatype),  # 1 - mediatyype
                str(self.filename),  # 2 - filename
                str(self.filetype),  # 3 - filetype
                str(self.filepath),  # 4 - filepath
                str('Insert description'),  # 5 - descrizione
                str("['imagine']"))  # 6 - tags
            try:
                self.DB_MANAGER.insert_data_session(data)
                return media_id
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = self.filename + ": Image already in the database"
                else:
                    msg = e
                QMessageBox.warning(self, "Error", f"Warning 1! \n{str(msg)}", QMessageBox.Ok)
                return None
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Warning 2! \n{str(e)}", QMessageBox.Ok)
            return None

    def insert_record_mediathumb(self, media_id, mediatype, filename, filename_thumb, filetype, filepath_thumb,
                                 filepath_resize):
        self.media_id = media_id
        self.mediatype = mediatype
        self.filename = filename
        self.filename_thumb = filename_thumb
        self.filetype = filetype
        self.filepath_thumb = filepath_thumb
        self.filepath_resize = filepath_resize

        # Verifica se il record esiste già
        search_dict = {'media_thumb_filename': f"'{self.filename_thumb}'"}
        existing_record = self.DB_MANAGER.query_bool(search_dict, 'MEDIA_THUMB')

        if existing_record:
            # Il record esiste già, non è necessario inserirlo di nuovo
            print(f"Thumb record already exists for filename: {self.filename_thumb}")
            return True

        try:
            data = self.DB_MANAGER.insert_mediathumb_values(
                self.DB_MANAGER.max_num_id('MEDIA_THUMB', 'id_media_thumb') + 1,
                str(self.media_id),
                str(self.mediatype),
                str(self.filename),
                str(self.filename_thumb),
                str(self.filetype),
                str(self.filepath_thumb),
                str(self.filepath_resize))
            try:
                self.DB_MANAGER.insert_data_session(data)
                return True
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    print(f"Thumb record already exists for filename: {self.filename_thumb}")
                else:
                    print(f"Error inserting thumb record: {str(e)}")
                return False
        except Exception as e:
            print(f"Error preparing thumb record: {str(e)}")
            return False

    def insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name):
        self.id_entity = id_entity
        self.entity_type = entity_type
        self.table_name = table_name
        self.id_media = id_media
        self.filepath = filepath
        self.media_name = media_name

        # Verifica se il record esiste già
        search_dict = {
            'id_entity': self.id_entity,
            'entity_type': f"'{self.entity_type}'",
            'id_media': self.id_media
        }
        existing_record = self.DB_MANAGER.query_bool(search_dict, 'MEDIATOENTITY')

        if existing_record:
            # Il record esiste già, non è necessario inserirlo di nuovo
            print(
                f"Record already exists for id_entity={self.id_entity}, entity_type={self.entity_type}, id_media={self.id_media}")
            return 1

        try:
            data = self.DB_MANAGER.insert_media2entity_values(
                self.DB_MANAGER.max_num_id('MEDIATOENTITY', 'id_mediaToEntity') + 1,
                int(self.id_entity),
                str(self.entity_type),
                str(self.table_name),
                int(self.id_media),
                str(self.filepath),
                str(self.media_name))
            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("Integrity"):
                    msg = f"Record already exists for id_entity={self.id_entity}, entity_type={self.entity_type}, id_media={self.id_media}"
                else:
                    msg = str(e)
                print(f"Warning: {msg}")
                return 0
        except Exception as e:
            print(f"Error: {str(e)}")
            return 0

    def save_image_to_db(self, file_path, format):
        if self.db_manager is None:
            QMessageBox.warning(self, "Error", "Database manager not available")
            return

        # Leggi l'immagine
        img = cv2.imread(file_path)

        # Crea una thumbnail
        max_size = (150, 150)
        h, w = img.shape[:2]
        aspect = min(max_size[0] / w, max_size[1] / h)
        thumb = cv2.resize(img, (int(w * aspect), int(h * aspect)), interpolation=cv2.INTER_AREA)

        # Converti l'immagine e la thumbnail in bytes
        _, img_encoded = cv2.imencode(f'.{format}', img)
        _, thumb_encoded = cv2.imencode(f'.{format}', thumb)

        image_data = img_encoded.tobytes()
        thumb_data = thumb_encoded.tobytes()

        # Prepara i dati per il database
        filename = os.path.basename(file_path)
        media_data = {
            'media_filename': filename,
            'media_thumb': thumb_data,
            'media_filename_thumb': f"thumb_{filename}",
            'media_tags': 'video_frame',
            'media_type': format.lower(),
            'filepath': file_path
        }

        # Inserisci nel database
        try:
            self.db_manager.insert_media_values(media_data)
            QMessageBox.information(self, "Success", "Image saved to database")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save to database: {str(e)}")

    def closeEvent(self, event):
        if self.cap is not None:
            self.cap.release()
        if self.has_audio:
            pygame.mixer.music.stop()
        pygame.quit()

        # Nascondi la finestra invece di chiuderla
        self.hide()
        event.ignore()  # Ignora l'evento di chiusura

    def shutdown(self):
        # Chiudi effettivamente la finestra e rilascia le risorse
        if self.cap is not None:
            self.cap.release()
        if self.has_audio:
            pygame.mixer.music.stop()
        pygame.quit()
        self.close()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.cap is not None:
            current_frame = self.slider.value()
            self.display_frame(self.get_frame(current_frame))