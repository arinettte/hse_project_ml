import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtCore import Qt, QTimer

from widgets.welcome_screen import WelcomeScreen

from widgets.login_screen import LoginScreen
from widgets.create_acc_screen import CreateAccScreen
from widgets.profile_info_widget import ProfileInfoWidget
from widgets.profile_edit_widget import ProfileEditWidget
from widgets.main_window import *
from settings import WIDGETS
from db.database import database

import tracemalloc

if __name__ == '__main__':
    model_init()

    app = QApplication(sys.argv)

    widget = QStackedWidget()

    welcome = WelcomeScreen(widget)
    login = LoginScreen(widget)
    create_acc = CreateAccScreen(widget)
    main_window = MainWindow(widget)
    profile_info = ProfileInfoWidget(widget)
    profile_edit = ProfileEditWidget(widget)

    WIDGETS['welcome'] = welcome
    WIDGETS['login'] = login
    WIDGETS['create_acc'] = create_acc
    WIDGETS['main_window'] = main_window
    WIDGETS['profile_info'] = profile_info
    WIDGETS['profile_edit'] = profile_edit

    widget.addWidget(welcome)
    widget.addWidget(login)
    widget.addWidget(create_acc)
    widget.addWidget(main_window)
    widget.addWidget(profile_info)
    widget.addWidget(profile_edit)

    screen_geometry = QApplication.desktop().screenGeometry()
    widget.setWindowFlags(Qt.WindowStaysOnTopHint)
    widget.setFixedWidth(791)
    widget.setFixedHeight(600)

    widget_geometry_computer = widget.frameGeometry()

    widget.move(
        (screen_geometry.width() - widget_geometry_computer.width()) // 2,
        (screen_geometry.height() - widget_geometry_computer.height()) // 2
    )
    widget.show()

    splash = main_window.show_splash()
    splash.show()

    QTimer.singleShot(1500, lambda: widget.setCurrentIndex(-1))
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")

    database.close()
