import sys, os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (QWidget, QPushButton, QApplication, QSlider, QStyle,
                             QSizePolicy, QHBoxLayout, QLabel, QVBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPalette, QColor
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('L.Y.E')

        # color theme
        color_hex = "#A7B3F0"
        color = QColor(color_hex)
        c = self.palette()
        c.setColor(QPalette.Window, color)
        self.setPalette(c)

        self.initUI()
        self.show()

    def initUI(self):

        # media player
        self.player = QMediaPlayer()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        volumeControl = QHBoxLayout()
        musicControl = QHBoxLayout()
        self.layout.addLayout(volumeControl)
        self.layout.addLayout(musicControl)

        # buttons
        image_above_buttons = QLabel(self)
        image_above_buttons.setPixmap( QPixmap("lake.jpg").scaled(500, 500, Qt.AspectRatioMode.KeepAspectRatio))
        image_above_buttons.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_above_buttons.setFixedSize(500, 200)
        self.layout.addWidget(image_above_buttons)


        btn5 = QPushButton('Next', clicked=self.next_m)
        btn6 = QPushButton('Prev', clicked=self.prev_m)
        musicControl.addWidget(btn5)
        musicControl.addWidget(btn6)

        btn2 = QPushButton('Value+', clicked=self.volume_pl)
        btn3 = QPushButton('Value-', clicked=self.volume_ms)
        btn4 = QPushButton('Stop', clicked=self.volume_st)
        volumeControl.addWidget(btn3)
        volumeControl.addWidget(btn4)
        volumeControl.addWidget(btn2)


        btn1 = QPushButton('Listen', clicked=self.open_file)
        btn1.setGeometry(200, 150, 100, 100)
        btn1.setStyleSheet('QPushButton { border-radius: 20px; border: 2px solid black}')
        self.layout.addWidget(btn1)


        # play
        self.btn_play = QPushButton()
        self.btn_play.setEnabled(False)
        self.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        # slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)

        # label
        self.label = QLabel()
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

    def volume_pl(self):
        curr = self.player.volume()
        self.player.setVolume(curr + 10)

    def volume_ms(self):
        curr = self.player.volume()
        self.player.setVolume(curr - 10)

    def volume_st(self):
        self.player.setMuted(not self.player.isMuted())

    def next_m(self):
        self.player.setMuted(not self.player.isMuted())

    def prev_m(self):
        self.player.setMuted(not self.player.isMuted())
    def open_file(self):
        file_path = os.path.join(os.getcwd(), 'aa.mp3')
        url = QUrl.fromLocalFile(file_path)
        media = QMediaContent(url)

        self.player.setMedia(media)
        self.player.play()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Stop music...')

