import os
from settings import MUSIC, IMAGE, FONT_AWESOME, WIDGETS
import time
from helpers import choose_playlist, seconds_to_str
from widgets.emotion_panel import EmotionPanel

from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QVBoxLayout, \
    QHBoxLayout, QSlider, QStyle, QMessageBox, QSplashScreen, QStackedWidget
from PyQt5.QtGui import QPixmap, QColor, QPalette, QIcon, QFont, QFontDatabase
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QTimer, Qt, QUrl, QRect, QSize
from PyQt5.QtMultimedia import QAudioOutput, QMediaPlayer, QMediaContent
from music_storage.queue_maker import *
from model_data import *
from face_getter import make_photo

globals()
CURRENT_EMOTION = "Calm"


def emotion_convert(emotion):
    if emotion.lower() in ['angry', 'disgust', 'fear', 'sad']:
        return 'sad'
    elif emotion.lower() == 'calm':
        return 'calm'
    else:
        return 'happy'


def model_init():
    global BATCH_SIZE
    global result_tfms
    global model
    global classes
    global device
    BATCH_SIZE = 200
    classes = ['Angry', 'Disgust', 'Fear', 'Happy', 'Calm', 'Sad', 'Surprise']
    result_tfms = tt.Compose([tt.Grayscale(num_output_channels=1), tt.ToTensor()])
    device = get_default_device()
    device = 'cpu'
    # model = ResNet(1, len(classes))
    # model.load_state_dict(torch.load('./models/emotion_detection_acc0.5452366471290588.pth'))
    model = torch.load('./models/quant_model_scripted.pt', map_location='cpu')
    model = to_device(model, device)


class MainWindow(QWidget):
    def __init__(self, stack: QStackedWidget):
        super().__init__()

        self.widget = stack

        self.tracks = {
            MUSIC + "aach.mp3": IMAGE + "neu.jpg",
            MUSIC + "sedaja.mp3": IMAGE + "happy.jpg",
            MUSIC + "voila.mp3": IMAGE + "sad.jpg"
        }

        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('LYE')

        self.current_index = 0  # for songs
        self.current_playlist = 3  # neutral - basic
        self.playlist_index = {}

        # color theme for now
        self.light_theme = True

        self.center_screen()

        # profile_button
        self.your_lye_button = QPushButton(self)
        self.your_lye_button.setStyleSheet("""
            QPushButton {
                border-radius: 50px;
                padding: 0px;
                color: white;
            }
        """)

        self.your_lye_button.clicked.connect(self.open_new_window)
        self.your_lye_button.move(30, 20)

        self.initUI()

        self.set_theme(self.light_theme)
        self.show()

    # central location
    def center_screen(self):
        app_geometry = QApplication.desktop().availableGeometry()
        wind_geometry = self.frameGeometry()
        wind_geometry.moveCenter(app_geometry.center())
        self.move(wind_geometry.topLeft())

    # tag
    def create_tag(self, text):
        button = QPushButton(text, self)
        button_size = 45
        button.setGeometry(10, 10, button_size + 20, button_size)
        button.setStyleSheet(
            "QPushButton {"
            "    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #AAAAAA);"
            "    border: none;"
            "    font-weight: bold;"
            "    text-shadow: 2px 2px 2px rgba(0, 0, 0, 0.5);"
            "    color: #222222;"
            f"    border-radius: {button_size // 2}px;"
            "}"
        )

    def open_new_window(self):
        WIDGETS['profile_info'].load_profile()
        self.widget.setCurrentWidget(WIDGETS['profile_info'])

    def initUI(self):
        self.initTracks()

        font_id = QFontDatabase.addApplicationFont(FONT_AWESOME)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        font_awesome = QFont(font_family)
        font_awesome.setPixelSize(32)
        font_awesome.setHintingPreference(QFont.HintingPreference.PreferNoHinting)

        self.layout = QVBoxLayout()
        self.player = QMediaPlayer()

        # top buttons
        self.top_buttons = QHBoxLayout()

        # add a text label
        self.treble_clef_label = QLabel("\U0001D11E LYE", self)
        self.treble_clef_label.setFont(QFont("cursive", 30))
        self.treble_clef_label.setStyleSheet("""
            QLabel {
                font-size: 25px;
                # background: transparent;
                border: 25px solid transparent;
                color: #AAAAAA; 
            }
        """)

        # add a profile button
        self.your_lye_button = QPushButton("\uf007", self)
        self.your_lye_button.setFont(font_awesome)
        self.your_lye_button.setFixedSize(24, 24)
        self.your_lye_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                background: transparent;
                border: 1px solid transparent;
                color: #AAAAAA; 
            }
        """)
        self.your_lye_button.clicked.connect(self.open_new_window)

        self.theme_button = QPushButton(self)
        self.theme_button.setIcon(QIcon(IMAGE + "sun.jpg"))
        self.theme_button.setIconSize(QSize(30, 30))
        self.theme_button.clicked.connect(self.change_theme)
        self.theme_button.setGeometry(QRect(self.width() - 40, 10, 30, 30))
        self.theme_button.move(self.width() - 40, 10)
        self.theme_button.setStyleSheet("border-radius: 15px;")

        # add all buttons
        self.top_buttons.addWidget(self.your_lye_button)
        self.top_buttons.addWidget(self.treble_clef_label)
        self.top_buttons.addStretch()
        self.top_buttons.addWidget(self.theme_button)

        self.setLayout(self.layout)
        button_area = QWidget()
        button_layout = QHBoxLayout(button_area)
        button_area.setStyleSheet("background-color: white; border-radius: 10px;")
        button_area.setFixedHeight(50)
        volumeControl = QHBoxLayout()
        musicControl = QHBoxLayout()

        self.layout.addLayout(self.top_buttons)

        # images
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.image_label)

        default_image = IMAGE + "aaa.jpg"
        pixmap = QPixmap(default_image)
        pixmap = pixmap.scaled(500, 400, Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()

        restart_btn = QPushButton('\uf0e2', clicked=self.open_file)
        restart_btn.setFont(font_awesome)
        restart_btn.setStyleSheet('font-size: 18px')

        # buttons
        play_btn = QPushButton('\uf04b')
        play_btn.clicked.connect(self.play_audio)
        play_btn.setFont(font_awesome)
        play_btn.setStyleSheet('font-size: 27px')

        next_btn = QPushButton('\uf050', clicked=self.next_m)
        next_btn.setFont(font_awesome)
        next_btn.setStyleSheet('font-size: 18px')

        prev_btn = QPushButton('\uf049', clicked=self.prev_m)
        prev_btn.setFont(font_awesome)
        prev_btn.setStyleSheet('font-size: 18px')

        stop_btn = QPushButton('\uf04c')
        stop_btn.clicked.connect(self.pause_audio)
        stop_btn.setFont(font_awesome)

        # button to save your favorite tracks
        self.heart_button = QPushButton("\uf004")
        self.heart_button.setFont(font_awesome)
        self.heart_button.setToolTip("Add to favorites")
        self.heart_button.setStyleSheet(
            "font-size: 18px; color: red; background: transparent; border: 1px solid transparent;")
        self.heart_button.clicked.connect(self.show_message)

        slider_style = """
        QSlider::groove:horizontal {
            border: 1px solid #CCCCCC;
            height: 8px;
            border-radius: 1px;
            background: #FFFFFF;
        }

        QSlider::handle:horizontal {
            background: #0078D7;
            border: none;
            width: 10px;
            height: 10px;
            margin: -1px 0
        }

        QSlider::add-page:horizontal {
            background: #E6E6E6;
        }

        QSlider::sub-page:horizontal {
            background: #0078D7;
        }
        """

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 1000)
        self.position_slider.setValue(0)
        self.position_slider.setStyleSheet(slider_style)
        self.position_slider.valueChanged.connect(self.change_position)

        # slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.setStyleSheet(slider_style)
        self.volume_slider.valueChanged.connect(self.change_volume)

        # play
        self.btn_play = QPushButton()
        self.btn_play.setEnabled(False)
        self.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        vol_icon = QLabel('\uf028')
        vol_icon.setStyleSheet('font-size: 16px')
        vol_icon.setFont(font_awesome)

        # label
        self.label = QLabel()
        self.layout.addLayout(musicControl)
        self.layout.addLayout(volumeControl)
        self.layout.addLayout(button_layout)

        # add buttons
        button_layout.setSpacing(20)
        button_layout.addWidget(self.heart_button)
        button_layout.addStretch()
        button_layout.addWidget(restart_btn)
        button_layout.addWidget(prev_btn)
        button_layout.addWidget(stop_btn)
        button_layout.addWidget(play_btn)
        button_layout.addWidget(next_btn)
        button_layout.addSpacing(40)
        button_layout.addStretch()

        self.position_label = QLabel('00:00:00')
        self.duration_label = QLabel('00:00:00')

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        # controls_layout.addStretch()

        controls_layout.addSpacing(10)
        controls_layout.addWidget(self.position_label)
        controls_layout.addWidget(self.position_slider, 2)
        controls_layout.addWidget(self.duration_label)
        controls_layout.addSpacing(20)
        controls_layout.addWidget(vol_icon)
        controls_layout.addWidget(self.volume_slider)
        controls_layout.addSpacing(10)
        # controls_layout.addStretch()

        # Desired order for arrangement

        '''
        button_layout.setStretch(0, 1)
        button_layout.setStretch(1, 1)
        button_layout.setStretch(2, 1)
        button_layout.setStretch(3, 1)
        button_layout.setStretch(4, 4)
        button_layout.setStretch(5, 1)
        '''

        # emotional buttons
        self.emotion_panel = EmotionPanel()
        self.layout.addWidget(self.emotion_panel)

        # for low panel

        button_area.setFixedSize(770, 70)
        self.layout.addLayout(controls_layout)
        self.layout.addWidget(button_area)

        # connect emotional
        self.emotion_panel.btn_sad.clicked.connect(self.sad_playlist)
        self.emotion_panel.btn_neutral.clicked.connect(self.neutral_playlist)
        self.emotion_panel.btn_happy.clicked.connect(self.happy_playlist)

        self.emotion_panel.btn_classic.clicked.connect(self.classic_playlist)
        self.emotion_panel.btn_pop.clicked.connect(self.pop_playlist)
        self.emotion_panel.btn_rock.clicked.connect(self.rock_playlist)
        self.emotion_panel.btn_films.clicked.connect(self.films_playlist)
        self.emotion_panel.btn_kids.clicked.connect(self.kids_playlist)

        self.emotion_panel.btn_work.clicked.connect(self.work_playlist)
        self.emotion_panel.btn_rest.clicked.connect(self.rest_playlist)
        self.emotion_panel.btn_sport.clicked.connect(self.sport_playlist)
        # self.player = QMediaPlayer()
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.player.positionChanged.connect(self.on_position_updated)
        self.player.durationChanged.connect(self.on_duration_updated)

    def set_theme(self, light_theme):
        self.light_theme = light_theme
        color_hex = "#AAAAAA" if not self.light_theme else "#FFFFFF"
        opposite_hex = "#AAAAAA" if self.light_theme else "#FFFFFF"
        color = QColor(color_hex)
        c = self.palette()
        c.setColor(QPalette.Window, color)
        self.setPalette(c)
        self.setAutoFillBackground(True)

        self.emotion_panel.update_theme(self.light_theme)

        self.your_lye_button.setStyleSheet(f"""
            QPushButton {{
                font-size: 20px;
                background: transparent;
                border: 1px solid transparent;
                color: {opposite_hex} 
            }}
        """)
        self.treble_clef_label.setStyleSheet(f"""
            QPushButton {{
                font-size: 20px;
                background: transparent;
                border: 1px solid transparent;
                color: {opposite_hex} 
            }}
        """)

    def change_theme(self):
        self.set_theme(not self.light_theme)

    def show_message(self):
        QMessageBox.about(self, "Message", "Added to favorites ❤ ")

    def set_playlist(self, playlist):  # for connection words and numbers
        if playlist == 1:
            self.current_playlist = 1
            self.tracks = choose_playlist(1)
        elif playlist == 2:
            self.current_playlist = 2
            self.tracks = choose_playlist(2)
        elif playlist == 3:
            self.current_playlist = 3
            self.tracks = choose_playlist(3)
        elif playlist == 4:
            self.current_playlist = 4
            self.tracks = choose_playlist(4)
        elif playlist == 5:
            self.current_playlist = 5
            self.tracks = choose_playlist(5)
        elif playlist == 6:
            self.current_playlist = 6
            self.tracks = choose_playlist(6)
        elif playlist == 7:
            self.current_playlist = 7
            self.tracks = choose_playlist(7)
        elif playlist == 8:
            self.current_playlist = 8
            self.tracks = choose_playlist(8)
        elif playlist == 9:
            self.current_playlist = 9
            self.tracks = choose_playlist(9)
        elif playlist == 10:
            self.current_playlist = 10
            self.tracks = choose_playlist(10)
        elif playlist == 11:
            self.current_playlist = 11
            self.tracks = choose_playlist(11)

        self.current_index = self.playlist_index.get(self.current_playlist,
                                                     0)  # index of the current track in this playlist
        self.open_file(track_type='genre')

    def pause_audio(self):
        self.player.pause()

    def play_audio(self):
        self.player.play()

    def sad_playlist(self):
        global CURRENT_EMOTION
        CURRENT_EMOTION = 'Sad'
        self.open_file()

    def neutral_playlist(self):
        global CURRENT_EMOTION
        CURRENT_EMOTION = 'Calm'
        self.open_file()

    def happy_playlist(self):
        global CURRENT_EMOTION
        CURRENT_EMOTION = 'Happy'
        self.open_file()

    def classic_playlist(self):
        self.set_playlist(4)

    def pop_playlist(self):
        self.set_playlist(5)

    def rock_playlist(self):
        self.set_playlist(6)

    def kids_playlist(self):
        self.set_playlist(7)

    def films_playlist(self):
        self.set_playlist(8)

    def work_playlist(self):
        self.set_playlist(9)

    def rest_playlist(self):
        self.set_playlist(10)

    def sport_playlist(self):
        self.set_playlist(11)

    def change_volume(self, value):
        self.player.setVolume(value)

    def change_position(self, value):
        self.player.setPosition(int(self.player.duration() * value / 1000))

    def on_duration_updated(self, value):
        self.duration_label.setText(seconds_to_str(value / 1000))

    def on_position_updated(self, value):
        if not self.player.duration():
            return

        time = int(value / self.player.duration() * 1000)

        self.position_slider.blockSignals(True)
        self.position_label.setText(seconds_to_str(value / 1000))
        self.position_slider.setValue(time)
        self.position_slider.blockSignals(False)

    def initTracks(self):
        self.playlist_index = {1: 0, 2: 0, 3: 0}
        self.tracks = choose_playlist(self.current_playlist)

    def volume_pl(self):
        curr = self.player.volume()
        self.player.setVolume(curr + 20)

    def volume_ms(self):
        curr = self.player.volume()
        self.player.setVolume(curr - 20)

    def volume_st(self):
        self.player.setMuted(not self.player.isMuted())

    def open_file(self, track_type='emotion'):

        if track_type == 'emotion':
            directory = os.path.join(CURRENT_EMOTION)
            fourth_track_path = get_second_latest_mp3(directory)
            media = QMediaContent(QUrl.fromLocalFile(fourth_track_path))
        else:

            current_track = list(self.tracks.keys())[self.current_index]
            track_path = os.path.join(os.getcwd(), current_track)
            media = QMediaContent(QUrl.fromLocalFile(track_path))
        self.player.stop()
        self.player.setMedia(media)
        self.player.play()
        self.update_image(track_type)

        if track_type == 'emotion':
            update_queue(CURRENT_EMOTION)

    def final_predict(self):

        global result_tfms
        global classes
        global device
        global model

        make_photo()

        def local_pred_step(batch):
            images = batch
            out = model(images)

            return out

        def local_predict(pred_loader):
            outputs = [local_pred_step(batch) for batch in pred_loader]
            return [torch.max(el, dim=1)[1] for el in outputs]

        data = [result_tfms(PIL.Image.open('./photos/' + os.listdir('./photos/')[-1]).resize((48, 48)))]
        data_dl = DataLoader(data, 200, pin_memory=True)
        data_dl = DeviceDataLoader(data_dl, device)
        start_time = time.time()

        pred = local_predict(data_dl)[0][0]
        # pred = predict(model, data_dl)[0][0]
        print("--- %s seconds to predict ---\n" % (time.time() - start_time))
        print(pred)

        # save the model and check the model size
        def print_size_of_model(model, label=""):
            torch.save(model.state_dict(), "temp.p")
            size = os.path.getsize("temp.p")
            print("model: ", label, ' \t', 'Size (KB):', size / 1e3)
            os.remove('temp.p')
            return size

        return classes[pred]

    def next_m(self):
        global CURRENT_EMOTION
        CURRENT_EMOTION = emotion_convert(
            self.final_predict()).capitalize()
        self.open_file()

    def on_media_status_changed(self, state):  # auto transition to next track
        if state == QMediaPlayer.EndOfMedia:
            self.next_m()

    def prev_m(self):
        self.current_index = (self.current_index - 1) % len(self.tracks)
        self.playlist_index[self.current_playlist] = self.current_index
        self.open_file(track_type='no_emotion')

    def update_image(self, track_type):
        if track_type == "emotion":
            if CURRENT_EMOTION == 'Calm':
                image_path = IMAGE + "neu.jpg"
                self.emotion_panel.set_neu()
            elif CURRENT_EMOTION == 'Sad':
                image_path = IMAGE + 'sad.JPG'
                self.emotion_panel.set_sad()
            elif CURRENT_EMOTION == 'Happy':
                image_path = IMAGE + 'happy.JPG'
                self.emotion_panel.set_happy()
            else:
                image_path = IMAGE + "lye.jpg"
        else:
            current_track = list(self.tracks.keys())[self.current_index]
            image_filename = self.tracks[current_track]
            if image_filename:
                image_path = os.path.join(os.getcwd(), image_filename)
            else:
                image_path = IMAGE + "lye.jpg"
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(600, 500, Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()

    def show_splash(self):
        pixmap = QPixmap(IMAGE + "LYEE.jpg")
        pixmap = pixmap.scaled(791, 600)
        splash = QSplashScreen(pixmap)
        splash.setFixedSize(pixmap.size())
        splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        screen_geometry = QApplication.desktop().screenGeometry()
        splash_geometry = splash.frameGeometry()
        splash.move(
            ((screen_geometry.width() - splash_geometry.width()) // 2),
            ((screen_geometry.height() - splash_geometry.height()) // 2)
        )

        splash.show()

        # add animation for splash-screen

        animation = QPropertyAnimation(splash, b"windowOpacity")
        animation.setDuration(3000)
        animation.setStartValue(0.96)
        animation.setEndValue(0.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()

        QTimer.singleShot(1500, splash.close)
        splash.show()

        return splash
