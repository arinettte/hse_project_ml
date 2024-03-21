import sys, os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (QWidget, QPushButton, QApplication, QSlider, QStyle,
                             QSizePolicy, QHBoxLayout, QLabel, QVBoxLayout,
                             QSplashScreen, QMainWindow)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QUrl, QDir
from PyQt5.QtGui import QPixmap, QPalette, QColor, QPainter, QBitmap
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
#from model_data import *
def model_init():
    global result_dir
    global BATCH_SIZE
    global result_tfms
    global model
    global classes
    global device
    result_dir = './photos'
    BATCH_SIZE = 200
    classes = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
    result_tfms = tt.Compose([tt.Grayscale(num_output_channels=1), tt.ToTensor()])
    device = get_default_device()
    model = ResNet(1, len(classes))
    model.load_state_dict(torch.load('./models/emotion_detection_acc0.5452366471290588.pth'))
    model = to_device(model,device)
def final_predict():
    global result_tfms
    global classes
    global device
    global model
    data = [result_tfms(PIL.Image.open('./photos/'+os.listdir(result_dir)[-1]).resize((48, 48)))]
    data_dl = DataLoader(data, 200, num_workers=3, pin_memory=True)
    data_dl = DeviceDataLoader(data_dl, device)
    return classes[predict(model,data_dl)[0][0]]
def emotion_to_number(emotion):
    if emotion.lower() in ['angry', 'disgust', 'fear', 'sad']:
        return 1
    elif emotion.lower() == 'neutral':
        return 2
    else:
        return 3

PLAYER_PATH = "./player/"
def choose_playlist(number_):  # for connection with other members

    global choose_em_playlist

    if number_ == 1:
        choose_em_playlist = {
            PLAYER_PATH + "voila.mp3": PLAYER_PATH +"sad.jpg",
            PLAYER_PATH +"sad_snow.mp3": PLAYER_PATH +"sad.jpg",
            PLAYER_PATH +"sad_pretend.mp3": PLAYER_PATH +"sad.jpg"
        }
    elif number_ == 2:
        choose_em_playlist = {
            PLAYER_PATH +"happy_love.mp3": PLAYER_PATH +"happy.jpg",
            PLAYER_PATH +"sedaja.mp3": PLAYER_PATH +"happy.jpg",
            PLAYER_PATH + "happy_ball.mp3": PLAYER_PATH +"happy.jpg"
        }
    elif number_ == 3:
        choose_em_playlist = {
            PLAYER_PATH +  "aach.mp3":PLAYER_PATH + "neu.jpg",
            PLAYER_PATH + "neu_sen.mp3": PLAYER_PATH +"neu.jpg",
            PLAYER_PATH + "neu_shopen.mp3": PLAYER_PATH +"neu.jpg"
        }


# emotion addition
class EmotionPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        def_layout = QVBoxLayout()  # for inscription
        emotion_layout = QHBoxLayout()  # for emotion buttons

        # inscription
        self.label = QLabel("Listen your emotion")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(
            "font-family: 'Snell Roundhand', cursive; font-size: 25px; font-stretch: normal")
        def_layout.addWidget(self.label)

        # EMOTION PANEL
        self.btn_sad = QPushButton('Sad')
        self.btn_neutral = QPushButton('Neutral')
        self.btn_happy = QPushButton('Happy')

        emotion_layout.addWidget(self.btn_sad)
        emotion_layout.addWidget(self.btn_neutral)
        emotion_layout.addWidget(self.btn_happy)

        # touch response
        self.btn_sad.clicked.connect(self.set_sad)
        self.btn_neutral.clicked.connect(self.set_neu)
        self.btn_happy.clicked.connect(self.set_happy)

        def_layout.addLayout(emotion_layout)
        self.setLayout(def_layout)

    def reset_colors(self):  # reset prev style
        self.btn_sad.setStyleSheet("")
        self.btn_neutral.setStyleSheet("")
        self.btn_happy.setStyleSheet("")

    def set_sad(self):
        self.reset_colors()
        self.btn_sad.setStyleSheet("background-color: #9370DB;")

    def set_neu(self):
        self.reset_colors()
        self.btn_neutral.setStyleSheet("background-color: #87CEEB;")

    def set_happy(self):
        self.reset_colors()
        self.btn_happy.setStyleSheet("background-color: #90EE90;")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.tracks = {
            PLAYER_PATH +"aach.mp3": PLAYER_PATH +"neu.jpg",
            PLAYER_PATH +"sedaja.mp3": PLAYER_PATH +"happy.jpg",
            PLAYER_PATH + "voila.mp3": PLAYER_PATH +"sad.jpg"
        }

        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('LYE')

        self.current_index = 0  # for songs
        self.current_playlist = 3  # neutral - basic
        self.playlist_index = {}

        # color theme
        color_hex = "#DCDCDC"
        color = QColor(color_hex)
        c = self.palette()
        c.setColor(QPalette.Window, color)
        self.setPalette(c)
        self.center_screen()
        self.create_tag("LYE")
        self.initUI()
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
        button.setGeometry(10, 10, button_size, button_size)
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

    def initUI(self):
        self.initTracks()

        self.player = QMediaPlayer()
        self.layout = QVBoxLayout()

        self.setLayout(self.layout)
        button_area = QWidget()
        button_layout = QHBoxLayout(button_area)
        button_area.setStyleSheet("background-color: white; border-radius: 10px;")
        button_area.setFixedHeight(50)
        volumeControl = QHBoxLayout()
        musicControl = QHBoxLayout()

        # images
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.image_label)

        # buttons
        btn5 = QPushButton('Next', clicked=self.next_m)
        btn6 = QPushButton('Prev', clicked=self.prev_m)
        btn4 = QPushButton(clicked=self.volume_st)
        btn4.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        btn1 = QPushButton(clicked=self.open_file)
        btn1.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        # play
        self.btn_play = QPushButton()
        self.btn_play.setEnabled(False)
        self.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        # slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(20)
        self.volume_slider.valueChanged.connect(self.change_volume)
        musicControl.addWidget(self.volume_slider)

        # label
        self.label = QLabel()
        self.layout.addLayout(musicControl)
        self.layout.addLayout(volumeControl)

        # add buttons
        button_layout.addWidget(btn6)
        button_layout.addWidget(btn4)
        button_layout.addWidget(btn1)
        button_layout.addWidget(btn5)

        # emotional buttons

        self.emotion_panel = EmotionPanel()  # Define emotion_panel as an instance attribute
        self.layout.addWidget(self.emotion_panel)

        button_area.setFixedSize(550, 50)
        self.layout.addWidget(button_area)

        # connect emotional
        self.emotion_panel.btn_sad.clicked.connect(self.sad_playlist)
        self.emotion_panel.btn_neutral.clicked.connect(self.happy_playlist)
        self.emotion_panel.btn_happy.clicked.connect(self.neutral_playlist)

        self.player = QMediaPlayer()
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)

    def set_playlist(self, playlist):  # for connection words and numbers
        if playlist == 1:
            choose_playlist(1)
            self.current_playlist = 1
            self.tracks = choose_em_playlist
        elif playlist == 2:
            choose_playlist(2)
            self.current_playlist = 2
            self.tracks = choose_em_playlist
        elif playlist == 3:
            choose_playlist(3)
            self.current_playlist = 3
            self.tracks = choose_em_playlist
        self.current_index = self.playlist_index.get(self.current_playlist,
                                                     0)  # index of the current track in this playlist
        self.open_file()

    def sad_playlist(self):
        self.set_playlist(1)

    def neutral_playlist(self):
        self.set_playlist(2)

    def happy_playlist(self):
        self.set_playlist(3)

    def change_volume(self, value):
        self.player.setVolume(value)

    def initTracks(self):
        choose_playlist(self.current_playlist)
        self.playlist_index = {1: 0, 2: 0, 3: 0}
        self.tracks = choose_em_playlist

    def volume_pl(self):
        curr = self.player.volume()
        self.player.setVolume(curr + 20)

    def volume_ms(self):
        curr = self.player.volume()
        self.player.setVolume(curr - 20)

    def volume_st(self):
        self.player.setMuted(not self.player.isMuted())

    def open_file(self):
        current_track = list(self.tracks.keys())[self.current_index]
        track_path = os.path.join(os.getcwd(), current_track)
        media = QMediaContent(QUrl.fromLocalFile(track_path))

        self.player.stop()
        self.player.setMedia(media)
        self.player.play()
        self.update_image()

    def next_m(self):
        self.current_index = (1 + self.current_index) % len(self.tracks)
        self.playlist_index[self.current_playlist] = self.current_index
        self.open_file()

    def on_media_status_changed(self, state):  # auto transition to next track
        if state == QMediaPlayer.EndOfMedia:
            self.next_m()

    def prev_m(self):
        self.current_index = (self.current_index - 1) % len(self.tracks)
        self.playlist_index[self.current_playlist] = self.current_index
        self.open_file()

    def update_image(self):
        current_track = list(self.tracks.keys())[self.current_index]
        image_filename = self.tracks[current_track]
        image_path = os.path.join(os.getcwd(), image_filename)
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()

    def show_splash(self):
        pixmap = QPixmap(PLAYER_PATH +"LYEE.jpg")
        pixmap = pixmap.scaled(600, 400)

        splash = QSplashScreen(pixmap)
        splash.setFixedSize(pixmap.size())
        splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        splash.move(splash.pos().x(), splash.pos().y() + 6)
        splash.show()

        # add animation for splash-screen

        animation = QPropertyAnimation(splash, b"windowOpacity")
        animation.setDuration(1500)
        animation.setStartValue(0.96)
        animation.setEndValue(0.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()

        QTimer.singleShot(1500, splash.close)
        splash.show()
        return splash


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainWindow()
    splash = ex.show_splash()
    ex.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Stop music...')
