from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QStackedWidget

from settings import FILES_UI
from widgets.rating_window import RatingWindow

from settings import WIDGETS


class WelcomeScreen(QDialog):
    def __init__(self, stack: QStackedWidget):
        super(WelcomeScreen, self).__init__()

        loadUi(FILES_UI + "LYE.ui", self)
        self.widget = stack

        self.login.clicked.connect(self.login_account)
        self.create.clicked.connect(self.create_account)
        self.about_us.clicked.connect(self.about_us_function)

    # for login connection
    def login_account(self):
        self.widget.setCurrentWidget(WIDGETS['login'])

    # for create connection
    def create_account(self):
        self.widget.setCurrentWidget(WIDGETS['create_acc'])

    # for rating connection
    def about_us_function(self):
        self.rating_window = RatingWindow()
        self.rating_window.show()
