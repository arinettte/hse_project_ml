import sys, os
from queue_maker import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (QWidget, QPushButton, QApplication, QSlider, QStyle,
                             QSizePolicy, QHBoxLayout, QLabel, QVBoxLayout,
                             QSplashScreen, QMainWindow)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QUrl, QDir
from PyQt5.QtGui import QPixmap, QPalette, QColor, QPainter, QBitmap
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
import time
import asyncio
from model_data import *
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5.QtCore import QUrl


mood = ''


def get_fourth_track_path(directory):
    files = [os.path.join(directory, f) for f in os.listdir(directory)]
    files = [f for f in files if os.path.isfile(f)]
    files.sort(key=lambda x: os.path.getmtime(x))
    # всегда возвращаем путь к четвертому файлу; можно создать очередь как массив названий и обновлять тут
    return files[3]


def recognition():  # должна работать асинхронно и вычислять среднюю эмоцию
    result_dir = './photos'
    BATCH_SIZE = 200
    classes = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
    result_tfms = tt.Compose([tt.Grayscale(num_output_channels=1), tt.ToTensor()])
    device = get_default_device()
    model = ResNet(1, len(classes))
    model.load_state_dict(
        torch.load('./models/emotion_detection_acc05452366471290588.pth', map_location=torch.device('cpu')))
    model = to_device(model, device)

    data = [result_tfms(PIL.Image.open('./photos/' + os.listdir(result_dir)[-1]).resize((48, 48)))]
    data_dl = DataLoader(data, 200, num_workers=3, pin_memory=True)
    data_dl = DeviceDataLoader(data_dl, device)
    a = classes[predict(model, data_dl)[0][0]]
    if a == 'angry' or a == 'disgust' or a == 'fear' or a == 'neutral':
        return 'Calm'
    elif a == 'happy' or a == 'surprise':
        return 'Happy'
    else:
        return 'Sad'


class MusicPlayer(QWidget): # упрощенная реализация, чтобы посмотреть, как всё подключается
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initMediaPlayer()

    def initUI(self):
        self.setWindowTitle('Very simple player')
        self.setGeometry(300, 300, 300, 200)

        # кнопка выбора плейлиста
        self.btnChoosePlaylist = QPushButton('Выбрать Плейлист', self)
        self.btnChoosePlaylist.clicked.connect(self.choosePlaylist)

        # кнопка следующего трека
        self.btnNextTrack = QPushButton('Следующий Трек', self)
        self.btnNextTrack.clicked.connect(self.nextTrack)

        layout = QVBoxLayout()
        layout.addWidget(self.btnChoosePlaylist)
        layout.addWidget(self.btnNextTrack)

        self.setLayout(layout)

    def initMediaPlayer(self):
        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)

        # трек доиграл сам -status
        self.player.mediaStatusChanged.connect(self.onMediaStatusChanged)
        self.choosePlaylist()

    def choosePlaylist(self):
        global mood
        mood = recognition()
        print(mood)
        self.playlist.clear()
        directory = os.path.join(mood)
        fourth_track_path = get_fourth_track_path(directory)
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(fourth_track_path)))
        self.player.play()

    def nextTrack(self):
        global mood
        mood = recognition()
        print(mood)
        update_queue(mood)
        self.playlist.clear()
        directory = os.path.join(mood)
        fourth_track_path = get_fourth_track_path(directory)
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(fourth_track_path)))
        self.player.play()

    def onMediaStatusChanged(self, status):
        if status == QMediaPlayer.EndOfMedia:
            global mood
            mood = recognition()
            self.nextTrack()


if __name__ == '__main__':
    # get_users_playlists() при самом первом запуске приложения
    # run face_getter
    app = QApplication(sys.argv)
    ex = MusicPlayer()
    ex.show()
    sys.exit(app.exec_())
    # stop face_getter
