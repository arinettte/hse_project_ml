import sys, os
import sqlite3
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (QWidget, QPushButton, QApplication, QSlider, QStyle,
                             QSizePolicy, QHBoxLayout, QLabel, QVBoxLayout,
                             QSplashScreen, QMainWindow)
from PyQt5.QtWidgets import QDialog,QStackedWidget
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QUrl, QDir
from PyQt5.QtGui import QPixmap, QPalette, QColor, QPainter, QBitmap
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from music_storage import *
from music_storage.queue_maker import update_queue
from model_data import *
from face_getter import make_photo


class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("LYE.ui", self)
        self.login.clicked.connect(self.gotologin)
        self.create.clicked.connect(self.gotocreate)

    def gotologin(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 2)

    def gotocreate(self):
        create = CreateAccScreen()
        widget.addWidget(create)
        widget.setCurrentIndex(widget.currentIndex() )


class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("LYElog.ui", self)
        self.passwordd.setEchoMode(QtWidgets.QLineEdit.Password)
        self.loginn.clicked.connect(self.loginfunction)
        self.prev.clicked.connect(self.prevfunction)

    def prevfunction(self):
        current_index = widget.currentIndex()
        if current_index > 0:
            widget.setCurrentIndex(current_index - 2)

    def loginfunction(self):
        user = self.name.text()
        password = self.passwordd.text()

        if len(user) == 0 or len(password) == 0:
            self.error_message1.setText("Please input all fields.")

        else:
            conn = sqlite3.connect("shop_data.db")
            cur = conn.cursor()
            query = 'SELECT password FROM login_info WHERE username =\'' + user + "\'"
            cur.execute(query)
            result_pass = cur.fetchone()

            if result_pass[0] == password:
                print("Successfully logged in.")
                self.error_message2.setText("Successfully logged in. TAP LYE to open.")
            else:
                self.error_message1.setText("Invalid username or password")

    # def mainapp(self):
    #     main_window = MainWindow()
    #     main_window.show()
    #     self.close()


class CreateAccScreen(QDialog):
    def __init__(self):
        super(CreateAccScreen, self).__init__()
        loadUi("LYEcreate.ui", self)
        print(2)
        self.passwordd.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_2.setEchoMode(QtWidgets.QLineEdit.Password)
        # self.signup.clicked.connect(self.signupfunction)
        # self.prev.clicked.connect(self.prevfunction)
