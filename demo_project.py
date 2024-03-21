import time
import asyncio

from player.app_first import *
from model_data import *
from face_getter import make_photo

if __name__ == '__main__':
    #model_init()
    app = QApplication(sys.argv)
    ex = MainWindow()
    splash = ex.show_splash()
    ex.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Stop music...')