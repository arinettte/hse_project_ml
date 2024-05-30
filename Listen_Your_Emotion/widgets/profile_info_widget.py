import sqlite3

from PyQt5.QtWidgets import QDialog, QStackedWidget
from PyQt5.QtCore import Qt

from PyQt5.uic import loadUi

from settings import FILES_UI, USER_INFO, WIDGETS

from db.database import database


class ProfileInfoWidget(QDialog):

    def __init__(self, stack: QStackedWidget):
        super().__init__()

        self.widget = stack
        self.setWindowModality(Qt.ApplicationModal)
        loadUi(FILES_UI + 'addprofile2.ui', self)

        self.edit_profile.clicked.connect(self.on_edit_profile)
        self.prevv.clicked.connect(self.prevfunction)
        self.user_namename.setText(USER_INFO['username'])

    def load_profile(self):
        profile = database.get_profile_by_username(USER_INFO['username'])

        if profile:
            self.user_namename.setText(profile.username)

            self.firstname.setText(profile.first_name or '')
            self.lastname.setText(profile.last_name or '')
            if profile.birthday:
                self.birthday.setDate(profile.birthday)

            self.favArtist.setText(profile.fav_artist or '')

            self.favSong.setText(profile.fav_song or '')
            self.favGenre.setText(profile.fav_genre or '')

            gender = profile.gender
            self.comboBox.setCurrentIndex(0)
            if gender == 0:
                self.comboBox.setCurrentIndex(1)
            elif gender == 1:
                self.comboBox.setCurrentIndex(2)

    def prevfunction(self):
        self.widget.setCurrentWidget(WIDGETS['main_window'])

    def on_edit_profile(self):
        WIDGETS['profile_edit'].load_profile()
        self.widget.setCurrentWidget(WIDGETS['profile_edit'])

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
            current_index = self.widget.currentIndex()
            if current_index > 0:
                self.widget.setCurrentIndex(current_index - 2)
