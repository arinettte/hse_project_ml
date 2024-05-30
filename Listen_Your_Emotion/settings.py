import os

# ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = "."
RESOURCE_DIR = f"resources"

MUSIC = f"{RESOURCE_DIR}/music_files/"
FILES_UI = f"{RESOURCE_DIR}/ui_files/"

IMAGE = f"{RESOURCE_DIR}/image_files/"
FONTS_DIR = f"{RESOURCE_DIR}/font_files/"

FONT_AWESOME = f'{FONTS_DIR}/Font Awesome 6 Free-Solid-900.otf'

DB_FILE = f"{ROOT_DIR}/app_data.db"

PLAYLISTS = {
    'sad': {
        MUSIC + "voila.mp3": IMAGE + "sad.jpg",
        MUSIC + "sad_snow.mp3": IMAGE + "sad.jpg",
        MUSIC + "sad_pretend.mp3": IMAGE + "sad.jpg"
    },
    'neutral': {
        MUSIC + "aach.mp3": IMAGE + "neu.jpg",
        MUSIC + "neu_sen.mp3": IMAGE + "neu.jpg",
        MUSIC + "neu_shopen.mp3": IMAGE + "neu.jpg"
    },
    'happy': {
        MUSIC + "happy_love.mp3": IMAGE + "happy.jpg",
        MUSIC + "sedaja.mp3": IMAGE + "happy.jpg",
        MUSIC + "happy_ball.mp3": IMAGE + "happy.jpg"
    },
    'classic': {
        MUSIC + "classic_1.mp3": IMAGE + "classic_11.jpg",
        MUSIC + "classic_2.mp3": IMAGE + "classic_11.jpg",
        MUSIC + "classic_3.mp3": IMAGE + "classic_11.jpg"
    },
    'pop': {
        MUSIC + "pop_1.mp3": IMAGE + "pop.jpg",
        MUSIC + "pop_2.mp3": IMAGE + "pop.jpg",
        MUSIC + "pop_2.mp3": IMAGE + "pop.jpg"
    },
    'rock': {
        MUSIC + "rock_1.mp3": IMAGE + "rock.jpg",
        MUSIC + "rock_2.mp3": IMAGE + "rock.jpg",
        MUSIC + "rock_3.mp3": IMAGE + "rock.jpg"
    },
    'kids': {
        MUSIC + "kids1.mp3": IMAGE + "kids.jpg",
        MUSIC + "kids2.mp3": IMAGE + "kids.jpg",
    },

    'films': {
        MUSIC + "films1.mp3": IMAGE + "classic.jpg",
        MUSIC + "films2.mp3": IMAGE + "classic.jpg",
    },

    'work': {
        MUSIC + "work1.mp3": IMAGE + "work.jpg",
        MUSIC + "work2.mp3": IMAGE + "work.jpg",
    },
    'rest': {
        MUSIC + "classic_3.mp3": IMAGE + "rest.jpg",
        MUSIC + "neu_shopen.mp3": IMAGE + "rest.jpg",

    },
    'sport': {
        MUSIC + "sport1.mp3": IMAGE + "sport.jpg",
        MUSIC + "sport2.mp3": IMAGE + "sport.jpg",
    }
}

USER_INFO = {
    'username': ''
}

WIDGETS = {}
