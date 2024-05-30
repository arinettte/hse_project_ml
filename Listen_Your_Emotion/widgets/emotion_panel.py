from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy


class EmotionPanel(QWidget):
    def __init__(self, light_theme=True):
        super().__init__()
        self.light_theme = light_theme
        self.initUI()

    def initUI(self):
        self.def_layout = QVBoxLayout()  # Main layout
        self.genre_layout = QHBoxLayout()  # Genre buttons layout
        self.emotion_layout = QHBoxLayout()  # Emotion buttons layout

        # Layout for buttons to show/hide 'genre' and 'for action'
        self.buttons_layout = QHBoxLayout()

        # Inscription
        self.label = QLabel("Listen your emotion")
        self.label.setAlignment(Qt.AlignCenter)

        if self.light_theme:
            self.label.setStyleSheet(
                "font-family: 'Snell Roundhand', cursive; font-size: 30px; font-stretch: normal; color: #222222;")
        else:
            self.label.setStyleSheet(
                "font-family: 'Snell Roundhand', cursive; font-size: 30px; font-stretch: normal; color: #FFFFFF;")

        self.def_layout.addWidget(self.label)

        self.btn_show_genres = QPushButton('Genres')
        self.btn_show_genres.setCheckable(True)
        self.btn_show_genres.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                font-stretch: normal;
                font-family: cursive;                         
                border-radius: 0px;
                border: 0px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
            QPushButton:checked {
                color: black;
                border-bottom: 2px solid black;
            }
        """)
        self.btn_show_genres.clicked.connect(self.toggle_genres_genres)
        self.buttons_layout.addWidget(self.btn_show_genres)

        self.btn_for_action = QPushButton('For Action')
        self.btn_for_action.setCheckable(True)
        self.btn_for_action.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                font-stretch: normal;
                font-family: cursive;                      
                border-radius: 0px;
                border: 0px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
            QPushButton:checked {
                color: black;
                border-bottom: 2px solid black;
            }
        """)
        self.btn_for_action.clicked.connect(self.toggle_genres_actions)
        self.buttons_layout.addWidget(self.btn_for_action)

        # left corner for genre and action buttons
        self.buttons_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Add the buttons layout to the main layout
        self.def_layout.addLayout(self.buttons_layout)

        # buttons touched genre
        self.btn_classic = QPushButton('Classic')
        self.btn_films = QPushButton('Soundtracks')
        self.btn_rock = QPushButton('Rock')
        self.btn_pop = QPushButton('Pop')
        self.btn_kids = QPushButton('For kids')

        self.genre_layout.addWidget(self.btn_classic)
        self.genre_layout.addWidget(self.btn_films)
        self.genre_layout.addWidget(self.btn_rock)
        self.genre_layout.addWidget(self.btn_pop)
        self.genre_layout.addWidget(self.btn_kids)

        self.genre_widget = QWidget()
        self.genre_widget.setLayout(self.genre_layout)
        self.genre_widget.setVisible(False)

        self.def_layout.addWidget(self.genre_widget)

        # Action buttons layout
        self.action_layout = QHBoxLayout()

        # "For Action" buttons
        self.btn_work = QPushButton('Work')
        self.btn_rest = QPushButton('Rest')
        self.btn_sport = QPushButton('Sport')

        self.action_layout.addWidget(self.btn_work)
        self.action_layout.addWidget(self.btn_rest)
        self.action_layout.addWidget(self.btn_sport)
        self.action_widget = QWidget()
        self.action_widget.setLayout(self.action_layout)
        self.action_widget.setVisible(False)

        self.def_layout.addWidget(self.action_widget)

        # EMOTION PANEL
        self.btn_sad = QPushButton('Sad')
        self.btn_neutral = QPushButton('Neutral')
        self.btn_happy = QPushButton('Happy')

        self.emotion_layout.addWidget(self.btn_sad)
        self.emotion_layout.addWidget(self.btn_neutral)
        self.emotion_layout.addWidget(self.btn_happy)

        # touch response for genres
        self.btn_classic.clicked.connect(self.set_classic)
        self.btn_pop.clicked.connect(self.set_pop)
        self.btn_rock.clicked.connect(self.set_rock)
        self.btn_kids.clicked.connect(self.set_kids)
        self.btn_films.clicked.connect(self.set_films)

        # touch response for actions 
        self.btn_work.clicked.connect(self.set_work)
        self.btn_rest.clicked.connect(self.set_rest)
        self.btn_sport.clicked.connect(self.set_sport)

        # touch response for emotions
        self.btn_sad.clicked.connect(self.set_sad)
        self.btn_neutral.clicked.connect(self.set_neu)
        self.btn_happy.clicked.connect(self.set_happy)

        self.def_layout.addLayout(self.emotion_layout)  # Add emotion buttons layout and genre buttons
        self.setLayout(self.def_layout)

    def toggle_genres_genres(self):
        is_visible = self.genre_widget.isVisible()
        self.genre_widget.setVisible(not is_visible)

    def toggle_genres_actions(self):
        is_visible = self.action_widget.isVisible()
        self.action_widget.setVisible(not is_visible)

    def reset_colors(self):  # reset prev style
        self.btn_sad.setStyleSheet("")
        self.btn_neutral.setStyleSheet("")
        self.btn_happy.setStyleSheet("")

        self.btn_classic.setStyleSheet("")
        self.btn_pop.setStyleSheet("")
        self.btn_rock.setStyleSheet("")
        self.btn_films.setStyleSheet("")
        self.btn_kids.setStyleSheet("")

        self.btn_sport.setStyleSheet("")
        self.btn_work.setStyleSheet("")
        self.btn_rest.setStyleSheet("")

    def set_sad(self):
        self.reset_colors()
        self.btn_sad.setStyleSheet("background-color: #9370DB; color: white;")

    def set_neu(self):
        self.reset_colors()
        self.btn_neutral.setStyleSheet("background-color: #87CEEB; color: white;")

    def set_happy(self):
        self.reset_colors()
        self.btn_happy.setStyleSheet("background-color: #90EE90; color: white;")

    def set_classic(self):
        self.reset_colors()
        self.btn_classic.setStyleSheet("background-color: #FF4F00; color: white;")

    def set_films(self):
        self.reset_colors()
        self.btn_films.setStyleSheet("background-color: #BF5D30; color: white;")

    def set_rock(self):
        self.reset_colors()
        self.btn_rock.setStyleSheet("background-color: #A63400; color: white;")

    def set_pop(self):
        self.reset_colors()
        self.btn_pop.setStyleSheet("background-color: #FF7B40; color: white;")

    def set_kids(self):
        self.reset_colors()
        self.btn_kids.setStyleSheet("background-color: #FF9E73; color: white;")

    def set_work(self):
        self.reset_colors()
        self.btn_work.setStyleSheet("background-color: #BF8230; color: white;")

    def set_rest(self):
        self.reset_colors()
        self.btn_rest.setStyleSheet("background-color: #A65F00; color: white;")

    def set_sport(self):
        self.reset_colors()
        self.btn_sport.setStyleSheet("background-color: #FFAD40; color: white;")

    def update_theme(self, light_theme):
        self.light_theme = light_theme
        if self.light_theme:
            self.label.setStyleSheet(
                "font-family: 'Snell Roundhand', cursive; font-size: 25px; color: #222222;")
        else:
            self.label.setStyleSheet(
                "font-family: 'Snell Roundhand', cursive; font-size: 25px; color: #AD4029;")
