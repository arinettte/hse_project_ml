import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtGui import QPalette, QLinearGradient, QColor, QBrush
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import warnings


warnings.filterwarnings('ignore')


class Worker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, token, directory):
        super().__init__()
        self.token = token
        self.directory = directory

    def run(self):
        try:
            create_env_file(self.token, self.directory)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

def create_env_file(token, directory):
    if not token or not directory:
        raise ValueError("Все поля должны быть заполнены!")

    # Приведение разделителей к одному типу
    directory = directory.replace('/', '\\\\')
    #directory = directory.replace('\\', '\\\\')

    # Создание .env файла
    with open('../.env', 'w') as file:
        file.write(f'TOKEN="{token}"\n')
        file.write(f'DIRECTORY="{directory}"\n')

    # Вызов функции a() из файла update_music
    try:
        from queue_maker import classify_favoutite_music
        classify_favoutite_music()
    except Exception as e:
        print(123)
        raise RuntimeError(f"Произошла ошибка при выполнении функции a: {e}")

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Введите данные и подождите")

        # Установка градиентного фона (белый к серому)
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        gradient.setColorAt(0.0, QColor(255, 255, 255))
        gradient.setColorAt(1.0, QColor(128, 128, 128))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

        self.token_label = QLabel("Введите токен Яндекс музыки")
        self.token_entry = QLineEdit()

        self.directory_label = QLabel("Введите абсолютный путь к директории, где временно будет храниться музыка")
        self.directory_entry = QLineEdit()

        self.submit_button = QPushButton("Готово")
        self.submit_button.clicked.connect(self.on_submit)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.token_label)
        self.layout.addWidget(self.token_entry)
        self.layout.addWidget(self.directory_label)
        self.layout.addWidget(self.directory_entry)
        self.layout.addWidget(self.submit_button)

        self.setLayout(self.layout)

    def on_submit(self):
        token = self.token_entry.text()
        directory = self.directory_entry.text()
        self.token_label.hide()
        self.token_entry.hide()
        self.directory_label.hide()
        self.directory_entry.hide()
        self.submit_button.hide()

        self.processing_label = QLabel("Ваша избранная музыка обрабатывается. Пожалуйста, подождите.")
        self.layout.addWidget(self.processing_label)

        self.worker = Worker(token, directory)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_finished(self):
        self.layout.removeWidget(self.processing_label)
        self.processing_label.deleteLater()

        self.finished_label = QLabel("Всё готово, приятного прослушивания :)")
        self.layout.addWidget(self.finished_label)

    def on_error(self, error_message):
        QMessageBox.critical(None, "Ошибка", error_message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())