from settings import PLAYLISTS


def choose_playlist(number_):
    if number_ == 1:
        return PLAYLISTS['sad']
    elif number_ == 2:
        return PLAYLISTS['happy']
    elif number_ == 3:
        return PLAYLISTS['neutral']
    elif number_ == 4:
        return PLAYLISTS['classic']
    elif number_ == 5:
        return PLAYLISTS['pop']
    elif number_ == 6:
        return PLAYLISTS['rock']
    elif number_ == 7:
        return PLAYLISTS['kids']
    elif number_ == 8:
        return PLAYLISTS['films']
    elif number_ == 9:
        return PLAYLISTS['work']
    elif number_ == 10:
        return PLAYLISTS['rest']
    elif number_ == 11:
        return PLAYLISTS['sport']


def seconds_to_str(seconds):
    hours = seconds // (60 * 60)
    seconds %= (60 * 60)
    minutes = seconds // 60
    seconds %= 60

    return "%02i:%02i:%02i" % (hours, minutes, seconds)
