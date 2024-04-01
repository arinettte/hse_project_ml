import sys, os
import sqlite3
import hashlib
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl, QSize, QRect
from PyQt5.QtWidgets import (QWidget, QPushButton, QApplication, QSlider, QStyle,
                             QSizePolicy, QHBoxLayout, QLabel, QVBoxLayout,
                             QSplashScreen, QMainWindow, QFrame)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QUrl, QDir
from PyQt5.QtGui import QPixmap, QPalette, QColor, QPainter, QBitmap, QIcon
from PyQt5.QtWidgets import QApplication, QDialog, QStackedWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QMessageBox

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QUrl, QEasingCurve, QDir
from PyQt5.QtGui import QPixmap, QPalette, QColor
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton
from databases import Database
from PyQt5.QtCore import pyqtSignal

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QLineEdit, QLabel, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.uic import loadUi
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtCore import QTimer, Qt

main_user = None


class WelcomeScreen(QDialog):

    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("LYE.ui", self)

        self.login.clicked.connect(self.login_account)
        self.create.clicked.connect(self.create_account)

    # for login connection
    def login_account(self):
        open_login_widget = widget.currentIndex() + 1
        widget.setCurrentIndex(open_login_widget)
        index = widget.indexOf(self.login)
        print("Login_account", index)

    # for create connection
    def create_account(self):
        open_login_widget = widget.currentIndex() + 2
        widget.setCurrentIndex(open_login_widget)
        index = widget.indexOf(self.create)
        print("Create_account", index)


class LoginScreen(QDialog):

    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("LYElog.ui", self)
        self.passwordd.setEchoMode(QtWidgets.QLineEdit.Password)
        self.loginn.clicked.connect(self.login_function)
        self.prev.clicked.connect(self.prev_function)

    # back button
    def prev_function(self):
        self.error_message1.clear()
        current_index = widget.currentIndex()
        print("Index_prev", current_index)
        if current_index > 0:
            return_welcome_widget = current_index - 1
            widget.setCurrentIndex(return_welcome_widget)

    def login_function(self):
        user = self.name.text()
        password = self.passwordd.text()

        if len(user) == 0 or len(password) == 0:
            self.error_message1.setText("Not all fields are filled in.")
            return

        else:
            conn = sqlite3.connect("shop_data.db")
            cur = conn.cursor()
            data = 'SELECT password FROM login_info WHERE username =\'' + user + "\'"
            cur.execute(data)
            result_pass = cur.fetchone()

            if result_pass != None and result_pass[0] == password:
                print("Successfully logged in.")
                global main_user
                main_user = user
                current_index = widget.currentIndex()
                open_main_window = current_index + 2
                if current_index > 0:
                    widget.setCurrentIndex(open_main_window)
            else:
                self.error_message1.setText("Invalid filling")


class CreateAccScreen(QMainWindow):

    def __init__(self):
        super(CreateAccScreen, self).__init__()
        loadUi("LYEcreate.ui", self)

        self.passwordd.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passwordd_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.signupfunction)
        self.prev.clicked.connect(self.prevfunction)

    # back button
    def prevfunction(self):
        self.error_message.clear()
        current_index = widget.currentIndex()
        if current_index > 0:
            widget.setCurrentIndex(current_index - 2)

    def signupfunction(self):
        user = self.name.text()
        password = self.passwordd.text()
        confirmpassword = self.passwordd_2.text()

        if len(user) == 0 or len(password) == 0 or len(confirmpassword) == 0:
            self.error_message.setText("Not all fields are filled in.")

        elif password != confirmpassword:
            self.error_message.setText("Passwords mismatch.")
        else:
            conn = sqlite3.connect("shop_data.db")
            cur = conn.cursor()
            user_info = [user, password]
            print(3)
            cur.execute('INSERT INTO login_info (username, password) VALUES (?,?)', user_info)
            print("Successfully logged in.")
            self.error_message.setText("Creation is comlete. Go to LOGIN.")
            conn.commit()
            conn.close()


# profile LYE
class Profile(QDialog):

    def __init__(self):
        super(Profile, self).__init__()
        loadUi("profile.ui", self)
        self.save_ch.clicked.connect(self.save_chh())
        self.prevv.clicked.connect(self.prevfunction())
        self.user_namename.setText(main_user)

    def prevfunction(self):
        self.error_message1.clear()
        current_index = widget.currentIndex()
        if current_index > 0:
            widget.setCurrentIndex(current_index - 2)

    def save_chh(self):
        user1 = self.firstname.text()
        user2 = self.lastname.text()

        if len(user1) == 0 or len(user2) == 0:
            self.label_2.setText("Not all fields are filled in.")

        else:
            conn = sqlite3.connect("shop_data.db")
            cur = conn.cursor()
            user_info = [user1, user2]
            cur.execute('INSERT INTO login_info_app (first_name, last_name) VALUES (?,?)', user_info)
            print("Successfully save changes.")
            conn.commit()
            conn.close()
            current_index = widget.currentIndex()
            if current_index > 0:
                widget.setCurrentIndex(current_index - 2)


def emotion_to_number(emotion):
    if emotion.lower() in ['angry', 'disgust', 'fear', 'sad']:
        return 1
    elif emotion.lower() == 'neutral':
        return 2
    else:
        return 3


def choose_playlist(number_):  # for connection with other members

    global choose_em_playlist

    if number_ == 1:
        choose_em_playlist = {
            "voila.mp3": "sad.jpg",
            "sad_snow.mp3": "sad.jpg",
            "sad_pretend.mp3": "sad.jpg"
        }
    elif number_ == 2:
        choose_em_playlist = {
            "happy_love.mp3": "happy.jpg",
            "sedaja.mp3": "happy.jpg",
            "happy_ball.mp3": "happy.jpg"
        }
    elif number_ == 3:
        choose_em_playlist = {
            "aach.mp3": "neu.jpg",
            "neu_sen.mp3": "neu.jpg",
            "neu_shopen.mp3": "neu.jpg"
        }


# emotion addition
class EmotionPanel(QWidget):
    def __init__(self, light_theme=True):
        super().__init__()
        self.light_theme = light_theme
        self.initUI()

    def initUI(self):
        def_layout = QVBoxLayout()  # for inscription
        emotion_layout = QHBoxLayout()  # for emotion buttons

        # inscription
        self.label = QLabel("Listen your emotion")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if self.light_theme:
            self.label.setStyleSheet(
                "font-family: 'Snell Roundhand', cursive; font-size: 25px; font-stretch: normal; color: #222222;")
        else:
            self.label.setStyleSheet(
                "font-family: 'Snell Roundhand', cursive; font-size: 25px; font-stretch: normal; color: #FFFFFF;")

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

    def update_theme(self, light_theme):
        self.light_theme = light_theme
        if self.light_theme:
            self.label.setStyleSheet(
                "font-family: 'Snell Roundhand', cursive; font-size: 25px; font-stretch: normal; color: #222222;")
        else:
            self.label.setStyleSheet(
                "font-family: 'Snell Roundhand', cursive; font-size: 25px; font-stretch: normal; color: #FFFFFF;")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.tracks = {
            "aach.mp3": "neu.jpg",
            "sedaja.mp3": "happy.jpg",
            "voila.mp3": "sad.jpg"
        }

        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('LYE')

        self.current_index = 0  # for songs
        self.current_playlist = 3  # neutral - basic
        self.playlist_index = {}

        # color theme for now
        self.light_theme = True

        # button to save your favorite tracks
        self.heart_button = QPushButton("❤")
        self.heart_button.setFixedSize(30, 30)
        self.heart_button.setToolTip("Add to favorites")
        self.heart_button.setStyleSheet("background-color: #BA55D3; border-radius: 5px;")
        self.heart_button.clicked.connect(self.show_message)

        self.center_screen()

        # side buttons

        self.create_tag("LYE")
        self.create_profile_button("Your Lye")
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

    def create_profile_button(self, text):
        profile_button = QPushButton(text, self)
        button_size = 65
        profile_button.setGeometry(10, 60, button_size, 45)
        profile_button.setStyleSheet(
            "QPushButton {"
            "    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #AAAAAA);"
            "    border: none;"
            "    text-shadow: 2px 2px 2px rgba(0, 0, 0, 0.5);"
            "    color: #222222;"
            f"    border-radius: 15px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #87CEEB;"
            "}"
        )

        profile_button.clicked.connect(self.fill)

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

        default_image = "aaa.jpg"
        pixmap = QPixmap(default_image)
        pixmap = pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()

        # buttons
        btn5 = QPushButton('Next', clicked=self.next_m)
        btn6 = QPushButton('Prev', clicked=self.prev_m)
        btn4 = QPushButton(clicked=self.volume_st)
        btn4.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        btn1 = QPushButton(clicked=self.open_file)
        btn1.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        # slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(20)
        self.volume_slider.valueChanged.connect(self.change_volume)
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(self.volume_slider)

        # play
        self.btn_play = QPushButton()
        self.btn_play.setEnabled(False)
        self.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        # label
        self.label = QLabel()
        self.layout.addLayout(musicControl)
        self.layout.addLayout(volumeControl)
        self.layout.addLayout(button_layout)

        # add buttons
        button_layout.addWidget(btn6)
        button_layout.addWidget(btn4)
        button_layout.addWidget(btn1)
        button_layout.addWidget(btn5)
        button_layout.addWidget(self.volume_slider)
        button_layout.addWidget(self.heart_button)

        # Desired order for arrangement

        button_layout.setStretch(0, 1)
        button_layout.setStretch(1, 1)
        button_layout.setStretch(2, 1)
        button_layout.setStretch(3, 1)
        button_layout.setStretch(4, 4)
        button_layout.setStretch(5, 1)

        # emotional buttons

        self.emotion_panel = EmotionPanel()  # Define emotion_panel as an instance attribute
        self.layout.addWidget(self.emotion_panel)

        # for low panel

        button_area.setFixedSize(550, 50)
        self.layout.addWidget(button_area)

        # connect emotional

        self.emotion_panel.btn_sad.clicked.connect(self.sad_playlist)
        self.emotion_panel.btn_neutral.clicked.connect(self.happy_playlist)
        self.emotion_panel.btn_happy.clicked.connect(self.neutral_playlist)

        self.player = QMediaPlayer()
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)

    def set_theme(self, light_theme):
        self.light_theme = light_theme
        color_hex = "#AAAAAA" if self.light_theme else "#FFFFFF"
        color = QColor(color_hex)
        c = self.palette()
        c.setColor(QPalette.Window, color)
        self.setPalette(c)
        self.emotion_panel.update_theme(self.light_theme)

        # sun icon
        self.theme_button = QPushButton(self)
        self.theme_button.setIcon(QIcon("sun.jpg"))
        self.theme_button.setIconSize(QSize(30, 30))
        self.theme_button.clicked.connect(self.change_theme)
        self.theme_button.setGeometry(QRect(self.width() - 40, 10, 30, 30))
        self.theme_button.move(self.width() - 40, 10)
        self.theme_button.setStyleSheet("border-radius: 15px;")

    def change_theme(self):
        print(self.layout)
        self.set_theme(not self.light_theme)

    def fill(self):
        print(1)
        profile_dialog = Profile()
        profile_dialog.show()

    def show_message(self):
        QMessageBox.about(self, "Message", "Added to favorites ❤ ")

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
        if image_filename:
            image_path = os.path.join(os.getcwd(), image_filename)
        else:
            image_path = "lye.jpg"
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()

    def show_splash(self):
        pixmap = QPixmap("LYEE.jpg")
        pixmap = pixmap.scaled(600, 450)

        splash = QSplashScreen(pixmap)
        splash.setFixedSize(pixmap.size())
        splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        splash.move(splash.pos().x() - 20, splash.pos().y() - 35)
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


if __name__ == '__main__':
    app = QApplication(sys.argv)

    widget = QStackedWidget()
    welcome = WelcomeScreen()
    widget.addWidget(welcome)

    login = LoginScreen()
    widget.addWidget(login)
    create = CreateAccScreen()
    widget.addWidget(create)

    mainWindow = MainWindow()
    widget.addWidget(mainWindow)
    widget.setFixedHeight(450)
    widget.setFixedWidth(600)
    widget.show()

    splash = mainWindow.show_splash()
    splash.show()

    QTimer.singleShot(1500, lambda: widget.setCurrentIndex(-1))
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")
