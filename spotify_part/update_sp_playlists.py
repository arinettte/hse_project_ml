import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import csv
import pandas as pd
import joblib
import sklearn
from dotenv import load_dotenv
import os


def fetch_playlist_tracks_audio_features():
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=env_path)
    SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
    SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
    SPOTIPY_REDIRECT_URI = 'http://localhost:8080'
    SCOPE = 'user-library-read'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                   client_secret=SPOTIPY_CLIENT_SECRET,
                                                   redirect_uri=SPOTIPY_REDIRECT_URI,
                                                   scope=SCOPE))
    results = sp.current_user_playlists()
    tracks_info = []

    while results:
        playlists = results['items']
        for playlist_item in playlists:
            playlist_id = playlist_item['id']
            playlist_tracks_results = sp.playlist_tracks(playlist_id, limit=100)
            while playlist_tracks_results:
                track_ids = [item['track']['id'] for item in playlist_tracks_results['items'] if item['track'] and item['track']['id']]
                if track_ids:
                    # Разбиваем список ID треков на пакеты по 100 штук и запрашиваем аудио характеристики для каждого пакета, чтобы уменьшить количество запросов
                    for i in range(0, len(track_ids), 100):
                        batch = track_ids[i:i+100]
                        audio_features_list = sp.audio_features(batch)
                        for track, audio_features in zip(batch, audio_features_list):
                            if audio_features:
                                track_info = {
                                    'uri': f'spotify:track:{track}',
                                    'danceability': audio_features['danceability'],
                                    'energy': audio_features['energy'],
                                    'valence': audio_features['valence']
                                }
                                tracks_info.append(track_info)

                if playlist_tracks_results['next']:
                    playlist_tracks_results = sp.next(playlist_tracks_results)
                else:
                    playlist_tracks_results = None
                time.sleep(60)
        if results['next']:
            results = sp.next(results)
        else:
            results = None
    return tracks_info


def save_tracks_to_file(tracks_info, file_name='spotify_playlist_tracks_info.csv'):
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'danceability', 'energy', 'valence'])
        for track in tracks_info:
            writer.writerow([track['uri'], track['danceability'], track['energy'], track['valence']])


def classify_music_from_spotify():
    new_data = pd.read_csv('spotify_playlist_tracks_info.csv')
    model = joblib.load('music_classifier_model.pkl')
    label_encoder = joblib.load('label_encoder.pkl')

    X_new = new_data[['danceability', 'energy', 'valence']]
    mood_predictions_encoded = model.predict(X_new)
    mood_predictions = label_encoder.inverse_transform(mood_predictions_encoded)
    new_data['mood'] = mood_predictions
    new_data.to_csv('classified_spotify_playlist.csv', index=False)


def add_tracks_to_playlists_from_csv(csv_file):
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=env_path)
    SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
    SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
    SPOTIPY_REDIRECT_URI = 'http://localhost:8080'
    SCOPE = 'playlist-modify-public'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                   client_secret=SPOTIPY_CLIENT_SECRET,
                                                   redirect_uri=SPOTIPY_REDIRECT_URI,
                                                   scope=SCOPE))

    playlists = {
        'Happy': os.getenv('HAPPY_PLAYLIST_ID'),
        'Sad': os.getenv('SAD_PLAYLIST_ID'),
        'Calm': os.getenv('CALM_PLAYLIST_ID')
    }

    df = pd.read_csv(csv_file)
    for index, row in df.iterrows():
        mood = row['mood']
        track_id = row['id']
        if mood in playlists:
            playlist_id = playlists[mood]
            try:
                sp.playlist_add_items(playlist_id, [track_id])
            except Exception:
                continue
        time.sleep(3)  # чтобы не превысить лимит


# Извлечение аудио характеристик треков из избранных плейлистов в Spotify
# tracks_info = fetch_playlist_tracks_audio_features()

# Сохранение информации в файл
# save_tracks_to_file(tracks_info)

# Обработка сохраненных треков, распределение по классам с помощью модели
# classify_music_from_spotify()

# Добавление треков в 3 плейлиста пользователя в Spotify в соответствии с распределением
# csv_file_path = 'classified_spotify_playlist.csv'
# add_tracks_to_playlists_from_csv(csv_file_path)
