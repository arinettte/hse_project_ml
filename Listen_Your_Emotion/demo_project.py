import time
import asyncio

from app_first import *
from model_data import *
from face_getter import make_photo

if __name__ == '__main__':
    model_init()
    widget.show()

    splash = mainWindow.show_splash()
    splash.show()

    QTimer.singleShot(1500, lambda: widget.setCurrentIndex(-1))
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")
