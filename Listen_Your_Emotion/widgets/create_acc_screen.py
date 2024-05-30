import hashlib
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QLineEdit, QStackedWidget, QMainWindow

from settings import FILES_UI, WIDGETS

from db.database import database
from db.models import Profile


class CreateAccScreen(QMainWindow):

    def __init__(self, stack: QStackedWidget):
        super(CreateAccScreen, self).__init__()
        loadUi(FILES_UI + "LYEcreate.ui", self)

        self.widget = stack

        self.passwordd.setEchoMode(QLineEdit.Password)
        self.passwordd_2.setEchoMode(QLineEdit.Password)
        self.signup.clicked.connect(self.signupfunction)
        self.prev.clicked.connect(self.prevfunction)

    def prevfunction(self):
        self.error_message.clear()
        self.widget.setCurrentWidget(WIDGETS['welcome'])

    def signupfunction(self):
        user = self.name.text()
        password = self.passwordd.text()
        confirmpassword = self.passwordd_2.text()

        if len(user) == 0 or len(password) == 0 or len(confirmpassword) == 0:
            self.error_message.setText("Please fill in all inputs.")
            return

        if password != confirmpassword:
            self.error_message.setText("Passwords do not match.")
            return

        if database.is_username_taken(user):
            self.error_message.setText("Username is already taken.")
            return

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        new_profile = Profile(
            username=user,
            password=hashed_password,
        )

        database.add_profile(
            new_profile
        )

        self.widget.setCurrentWidget(WIDGETS['login'])
