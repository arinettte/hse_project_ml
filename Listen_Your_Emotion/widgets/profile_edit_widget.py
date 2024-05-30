from PyQt5.QtWidgets import QPushButton, QDialog, QLabel, QVBoxLayout, QMessageBox, \
    QLineEdit, QCalendarWidget, QRadioButton, QHBoxLayout, QStackedWidget
from PyQt5.QtCore import Qt

from db.database import database
from settings import USER_INFO, WIDGETS


class ProfileEditWidget(QDialog):

    def __init__(self, stack: QStackedWidget):
        super().__init__()
        self.setWindowTitle("Profile")
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(791, 300)

        self.widget = stack

        # profile information
        self.name_edit = QLineEdit(self)
        self.name_edit.setPlaceholderText("Name")
        self.surname_edit = QLineEdit(self)
        self.surname_edit.setPlaceholderText("Surname")

        # hb
        self.calendar = QCalendarWidget(self)

        # profile adding
        self.artist_edit = QLineEdit(self)
        self.artist_edit.setPlaceholderText("Favorite performer")
        self.song_edit = QLineEdit(self)
        self.song_edit.setPlaceholderText("Favorite song")
        self.genre_edit = QLineEdit(self)
        self.genre_edit.setPlaceholderText("Favorite genre")

        # Sex choose
        self.gender_label = QLabel("Sex:", self)
        self.female_radio = QRadioButton("female", self)
        self.male_radio = QRadioButton("male", self)
        self.gender_group = QHBoxLayout()
        self.gender_group.addWidget(self.female_radio)
        self.gender_group.addWidget(self.male_radio)

        # Save changes
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_profile)

        self.back_button = QPushButton('Back', self)
        self.back_button.clicked.connect(self.get_back)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(self.back_button)
        buttons.addWidget(self.save_button)

        # vertical layout
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Name:", self))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("Surname:", self))
        layout.addWidget(self.surname_edit)
        layout.addWidget(QLabel("HB:", self))
        layout.addWidget(self.calendar)
        layout.addWidget(QLabel("Singer:", self))
        layout.addWidget(self.artist_edit)
        layout.addWidget(QLabel("Song:", self))
        layout.addWidget(self.song_edit)
        layout.addWidget(QLabel("Genre:", self))
        layout.addWidget(self.genre_edit)
        layout.addWidget(self.gender_label)
        layout.addLayout(self.gender_group)

        layout.addLayout(buttons)

        # connection
        self.load_profile()

    def load_profile(self):
        profile = database.get_profile_by_username(USER_INFO['username'])

        if profile:

            self.name_edit.setText(profile.first_name or '')
            self.surname_edit.setText(profile.last_name or '')
            if profile.birthday:
                self.calendar.setSelectedDate(profile.birthday)

            self.artist_edit.setText(profile.fav_artist or '')

            self.song_edit.setText(profile.fav_song or '')
            self.genre_edit.setText(profile.fav_genre or '')
            gender = profile.gender
            if gender == 0:
                self.female_radio.setChecked(True)
            elif gender == 1:
                self.male_radio.setChecked(True)

    def save_profile(self):
        profile = database.get_profile_by_username(USER_INFO['username'])

        name = self.name_edit.text()
        surname = self.surname_edit.text()
        birthday = self.calendar.selectedDate().toString("yyyy-MM-dd")
        favorite_artist = self.artist_edit.text()
        favorite_song = self.song_edit.text()
        favorite_genre = self.genre_edit.text()

        gender = 0 if self.female_radio.isChecked() else 1

        profile.first_name = name
        profile.last_name = surname
        profile.birthday = birthday
        profile.fav_artist = favorite_artist
        profile.fav_song = favorite_song
        profile.fav_genre = favorite_genre
        profile.gender = gender

        database.edit_profile(profile.id, profile)

        QMessageBox.information(self, 'Saved', 'Profile saved successfully!')

    def get_back(self):
        reply = QMessageBox.question(self, 'Message',
                                     "Do you want to leave without saving unsaved data?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            WIDGETS['profile_info'].load_profile()
            self.widget.setCurrentWidget(WIDGETS['profile_info'])
