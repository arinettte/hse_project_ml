from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QWidget, QVBoxLayout, QLabel, QSizePolicy, QPushButton
from PyQt5.QtCore import Qt


class RatingWindow(QDialog):
    def __init__(self):
        super(RatingWindow, self).__init__()

        self.resize(400, 200)
        self.setWindowTitle("Info")
        layout = QVBoxLayout()

        hello_label = QLabel("Listen Your Emotion:", self)
        hello_label.setAlignment(Qt.AlignCenter)
        hello_label.setStyleSheet("font-size: 20px; font-family: 'Snell Roundhand'; font-weight: bold;")
        hello_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        layout.addWidget(hello_label)
        self.setWindowModality(Qt.ApplicationModal)
        content_widget = QWidget()

        self.about_text_label = QLabel("")
        self.about_text_label.setWordWrap(True)

        # adding buttons
        about_us_button = QPushButton("О нас")
        chat_support_button = QPushButton("Чат с поддержкой")
        rate_app_button = QPushButton("Оцените приложение")

        about_us_button.setAutoDefault(False)
        chat_support_button.setAutoDefault(False)
        rate_app_button.setAutoDefault(False)

        # click-connect 
        about_us_button.clicked.connect(self.show_about_us_text)
        chat_support_button.clicked.connect(self.show_chat_support_text)
        rate_app_button.clicked.connect(self.show_rate_app_text)

        # adding widgets into layout
        layout.addWidget(about_us_button)
        layout.addWidget(chat_support_button)
        layout.addWidget(rate_app_button)
        layout.addWidget(self.about_text_label)
        self.setLayout(layout)

        about_us_button.clicked.connect(lambda: self.set_button_color(about_us_button))
        chat_support_button.clicked.connect(lambda: self.set_button_color(chat_support_button))
        rate_app_button.clicked.connect(lambda: self.set_button_color(rate_app_button))
        self.current_button = None
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def set_button_color(self, button):
        if self.current_button:
            self.current_button.setStyleSheet("")
            self.current_button.setStyleSheet("color: black;")
        button.setStyleSheet("background-color: #778899; color: white;")
        # update button
        self.current_button = button

    def resizeEvent(self, event):
        if self.size().height() == 500:
            self.setGeometry(350, 273, 400, 500)
        elif self.size().height() == 100:
            self.setGeometry(350, 273, 400, 100)
        elif self.size().height() == 300:
            self.setGeometry(350, 273, 400, 300)
        event.accept()

    def show_about_us_text(self):
        self.setGeometry(350, 273, 400, 500)
        about_us_text = (
            "\"Listen Your Emotion\" - это удивительное приложение, способное чувствовать и отражать ваше настроение через музыку. "
            "Оно сканирует ваше лицо, захватывая каждое выражение и эмоцию, чтобы подобрать идеальный трек, который соответствует вашему текущему состоянию души.\n\n"
            "С помощью \"Listen Your Emotion\" вы можете погрузиться в мир музыки, созданной специально для вас. От меланхоличных мелодий до бодрящих ритмов - приложение подберет идеальный саундтрек для каждого вашего настроения.\n\n"
            "Позвольте себе окунуться в атмосферу гармонии и эмоций с \"Listen Your Emotion\" - приложением, которое делает вашу жизнь звучащей и красивой."
        )
        self.about_text_label.setText(about_us_text)

    def show_chat_support_text(self):
        self.setGeometry(350, 273, 400, 100)
        self.about_text_label.setText("<a href='https://t.me/lyesplyebot'>Связаться с нами в Telegram</a>")
        self.about_text_label.setOpenExternalLinks(True)

    def show_rate_app_text(self):
        self.setGeometry(350, 273, 400, 100)
        rate_app_text = "Оценить приложение и помочь сделать его лучше вы сможете здесь"
        self.about_text_label.setText(rate_app_text)
        self.about_text_label.setText("<a href='https://t.me/lyesplyebot'>Оценить нас</a>")
        self.about_text_label.setOpenExternalLinks(True)
