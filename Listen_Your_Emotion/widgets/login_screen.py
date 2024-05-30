import hashlib
from settings import FILES_UI, USER_INFO, WIDGETS

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QLineEdit, QStackedWidget

from db.database import database


class LoginScreen(QDialog):

    def __init__(self, widget: QStackedWidget):
        super(LoginScreen, self).__init__()
        loadUi(FILES_UI + "LYElog.ui", self)

        self.widget = widget

        self.passwordd.setEchoMode(QLineEdit.Password)
        self.loginn.clicked.connect(self.login_function)
        self.prev.clicked.connect(self.prev_function)

    def prev_function(self):
        self.error_message1.clear()
        self.widget.setCurrentWidget(WIDGETS['welcome'])

    def login_function(self):
        user = self.name.text()
        password = self.passwordd.text()

        if len(user) == 0 or len(password) == 0:
            self.error_message1.setText("Not all fields are filled in.")
            return

        profile = database.get_profile_by_username(user)
        if not profile:
            self.error_message1.setText('User not found!')
            return

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if profile.password != hashed_password:
            self.error_message1.setText('Wrong password!')
            return

        print("Successfully logged in.")

        USER_INFO['username'] = user
        self.widget.setCurrentWidget(WIDGETS['main_window'])
