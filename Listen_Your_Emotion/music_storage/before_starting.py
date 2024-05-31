import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtGui import QPalette, QLinearGradient, QColor, QBrush
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import glob
import random
import csv
from pathlib import Path
from dotenv import load_dotenv, dotenv_values
from yandex_music import Client
import numpy as np
import pandas as pd
import os
import shutil
import librosa
from collections import Counter
import joblib
import catboost
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# Создаем временное хранилище mp3 (на основе избранной музыки пользователя
# в Яндекс.музыке), эти треки дальше будем классифицировать
def download_favorite_tracks():
    # Загружаем переменные из .env файла
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_file_path = os.path.join(current_dir, '..', '.env')
    load_dotenv(env_file_path)

    token = str(os.getenv('TOKEN'))
    all_music_path = os.path.join(current_dir, '..')
    client = Client(token).init()

    # Получение любимых треков пользователя
    liked_tracks = client.users_likes_tracks()

    folder_with_mp3_path = os.path.join(all_music_path, 'all_mp3')
    if not os.path.exists(folder_with_mp3_path):
        os.makedirs(folder_with_mp3_path)

    music_storage_for_csv = all_music_path

    csv_path = os.path.join(music_storage_for_csv, 'tracks_info.csv')

    with open(csv_path, mode='w', newline='', encoding='utf-8-sig') as csv_file:
        fieldnames = ['Number', 'Title', 'Artist', 'Genre', 'YandexMusicID']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        batch_size = 50
        for i in range(0, len(liked_tracks.tracks), batch_size):
            track_batch = liked_tracks.tracks[i:i + batch_size]
            track_ids = [track.id for track in track_batch]

            # Получение информации о треках
            tracks_info = client.tracks(track_ids)

            for j, track_info in enumerate(tracks_info, start=i + 1):
                title = track_info.title
                artists = ', '.join(artist.name for artist in track_info.artists)
                genre = track_info.albums[0].genre if track_info.albums and track_info.albums[0].genre else 'Unknown'
                yandex_music_id = track_info.id

                # Запись информации о треке в CSV файл
                writer.writerow({
                    'Number': j,
                    'Title': title,
                    'Artist': artists,
                    'Genre': genre,
                    'YandexMusicID': yandex_music_id
                })

                # Скачиваем трек и сохраняем его порядковый номер
                track_path = os.path.join(folder_with_mp3_path, f'{j}.mp3')
                track_info.download(track_path)


# Извлечение признаков с Librosa
def feature_1d(y, sr):
    features = []

    # tempo
    tempo = librosa.beat.tempo(y=y, sr=sr)[0]
    features.append(tempo)

    # RMS
    rms = librosa.feature.rms(y=y)
    rms_mean = np.mean(rms)
    rms_var = np.var(rms)
    features.append(rms_mean)
    features.append(rms_var)

    # chroma features
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma)
    chroma_var = np.var(chroma)
    features.append(chroma_mean)
    features.append(chroma_var)

    # spectral centroid
    centroid = librosa.feature.spectral_centroid(y=y)
    centroid_mean = np.mean(centroid)
    centroid_var = np.var(centroid)
    features.append(centroid_mean)
    features.append(centroid_var)

    # spectral rolloff
    rolloff = librosa.feature.spectral_rolloff(y=y + 0.01, sr=sr)
    rolloff_mean = np.mean(rolloff)
    rolloff_var = np.var(rolloff)
    features.append(rolloff_mean)
    features.append(rolloff_var)

    # zero crossing rate
    zcr = librosa.feature.zero_crossing_rate(y=y)
    zcr_mean = np.mean(zcr)
    zcr_var = np.var(zcr)
    features.append(zcr_mean)
    features.append(zcr_var)

    # tonnetz
    tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
    tonnetz_mean = np.mean(tonnetz)
    tonnetz_var = np.var(tonnetz)
    features.append(tonnetz_mean)
    features.append(tonnetz_var)

    # mel
    s = librosa.feature.melspectrogram(y=y, sr=sr)
    mel = librosa.amplitude_to_db(s, ref=np.max)
    mel_mean = np.mean(mel)
    mel_var = np.var(mel)
    features.append(mel_mean)
    features.append(mel_var)

    # mfcc
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    for i in range(len(mfcc)):
        mfcc_mean = np.mean(mfcc[i])
        mfcc_var = np.var(mfcc[i])
        features.append(mfcc_mean)
        features.append(mfcc_var)

    return features


# Разделяем трек на части по 25 секунд, предсказываем настроение для каждой
# и выбираем наиболее частое настроение
def predict_mood_for_file(file_path, model, label_encoder, segment_duration=25):
    y, sr = librosa.load(file_path)

    segment_samples = segment_duration * sr
    num_segments = len(y) // segment_samples

    moods = []

    for i in range(num_segments):
        start_sample = i * segment_samples
        end_sample = start_sample + segment_samples
        y_segment = y[start_sample:end_sample]

        features = feature_1d(y_segment, sr)
        features_array = np.array(features).reshape(1, -1)

        mood_prediction_encoded = model.predict(features_array)[0]
        mood_prediction = label_encoder.inverse_transform([mood_prediction_encoded])[0]
        moods.append(mood_prediction)

    if moods:
        most_common_mood = Counter(moods).most_common(1)[0][0]
        return most_common_mood
    else:
        return None


def classify_emotions():
    # Путь к модели
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, '..', 'models', 'music_classifier.pkl')
    label_encoder_path = os.path.join(current_dir, '..', 'models', 'le_mood.pkl')
    model = joblib.load(model_path)
    label_encoder = joblib.load(label_encoder_path)

    # Путь к директории с mp3 файлами и CSV файлу
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_file_path = os.path.join(current_dir, '..', '.env')
    load_dotenv(env_file_path)
    all_music_path = os.path.join(current_dir, '..')
    folder_with_mp3_path = os.path.join(all_music_path, 'all_mp3')
    csv_file_path = os.path.join(current_dir, '..', "tracks_info.csv")

    # Проход по всем mp3 файлам и предсказывание mood
    df = pd.read_csv(csv_file_path)
    if 'mood' not in df.columns:
        df['mood'] = None

    mp3_files = [f for f in os.listdir(folder_with_mp3_path) if f.endswith('.mp3')]

    for mp3_file in mp3_files:
        file_number = int(os.path.splitext(mp3_file)[0])
        file_path = os.path.join(folder_with_mp3_path, mp3_file)
        mood_prediction = predict_mood_for_file(file_path, model, label_encoder)
        if mood_prediction is not None:
            df.loc[df['Number'] == file_number, 'mood'] = mood_prediction

    df.to_csv(csv_file_path, index=False)


# Для разделения на кластеры используем меньше признаков
def extract_few_features(y, sr):
    features = []

    # Chromagram
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)
    features.extend(chroma_mean)

    # MFCC
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=15)
    mfcc_mean = np.mean(mfcc, axis=1)
    features.extend(mfcc_mean)

    return np.array(features)


def create_clusters():
    os.environ["LOKY_MAX_CPU_COUNT"] = str(2)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_file_path = os.path.join(current_dir, '..', '.env')
    load_dotenv(env_file_path)
    all_music_path = os.path.join(current_dir, '..')
    folder_with_mp3_path = os.path.join(all_music_path, 'all_mp3')

    csv_file_path = os.path.join(current_dir, '..', "tracks_info.csv")
    df = pd.read_csv(csv_file_path)

    file_column = 'Number'

    # Извлечение признаков для каждого файла
    features_list = []
    file_names = df[file_column].tolist()

    for mp3_file in file_names:
        file_path = os.path.join(folder_with_mp3_path, str(mp3_file) + '.mp3')
        y, sr = librosa.load(file_path)
        features = extract_few_features(y, sr)
        features_list.append(features)

    features_array = np.array(features_list)

    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features_array)

    # Кластеризация с использованием KMeans
    n_clusters = 8
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(features_scaled)

    df['cluster'] = labels

    df.to_csv(csv_file_path, index=False)


# После создания csv файла с нужной информацией mp3 больше не нужны
def delete_mp3():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_file_path = os.path.join(current_dir, '..',  '.env')
    load_dotenv(env_file_path)
    all_music_path = os.path.join(current_dir, '..')
    folder_with_mp3_path = os.path.join(all_music_path, 'all_mp3')
    if os.path.exists(folder_with_mp3_path):
        shutil.rmtree(folder_with_mp3_path)


def classify_favourite_music():
    download_favorite_tracks()
    classify_emotions()
    create_clusters()
    delete_mp3()


class Worker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, token):
        super().__init__()
        self.token = token

    def run(self):
        try:
            create_env_file(self.token)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


def create_env_file(token):
    if not token:
        raise ValueError("Токен должен быть заполнен!")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    env_file_path = os.path.join(parent_dir, '.env')

    with open(env_file_path, 'w') as file:
        file.write(f'TOKEN={token}')
    try:
        classify_favourite_music()
    except Exception as e:
        raise RuntimeError(f"Произошла ошибка при выполнении функции classify_favourite_music: {e}")


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Введите данные и подождите")

        # Установка фона
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        gradient.setColorAt(0.0, QColor(255, 255, 255))
        gradient.setColorAt(1.0, QColor(128, 128, 128))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

        self.token_label = QLabel("Введите токен Яндекс музыки")
        self.token_entry = QLineEdit()

        self.submit_button = QPushButton("Готово")
        self.submit_button.clicked.connect(self.on_submit)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.token_label)
        self.layout.addWidget(self.token_entry)
        self.layout.addWidget(self.submit_button)

        self.setLayout(self.layout)

    def on_submit(self):
        token = self.token_entry.text()
        self.token_label.hide()
        self.token_entry.hide()
        self.submit_button.hide()

        self.processing_label = QLabel("Ваша избранная музыка обрабатывается. Пожалуйста, подождите.")
        self.layout.addWidget(self.processing_label)

        self.worker = Worker(token)
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
