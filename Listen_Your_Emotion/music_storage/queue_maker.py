import os
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

# Глобальная переменная cluster
cluster = 1





def get_second_latest_mp3(emoji):
    temp_directory = f"./music_storage/music_queues/{emoji}"

    files = [os.path.join(temp_directory, f) for f in os.listdir(temp_directory)]
    files = [f for f in files if os.path.isfile(f)]
    files.sort(key=lambda x: os.path.getmtime(x),reverse=True)
    # всегда возвращаем путь к четвертому файлу; можно создать очередь как массив названий и обновлять тут

    return files[1]

def update_queue(emoji):  # вызываем из плеера, когда включается следующий трек или когда пользователь переключает трек
    global cluster

    load_dotenv()
    token = 'y0_AgAAAAB0wgrKAAG8XgAAAAD97myUAACxssYMeJxLFa9EoF4vawM5Kyb2Uw'
    client = Client(token).init()
    if emoji == "Relaxed":
        emoji = 'Calm'
    # Создаем папки, если они не существуют
    folder_path2 = f"./music_storage/music_queues/{emoji}"


    # Считываем CSV файл
    csv_path = 'tracks_info.csv'

    with open(csv_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    if emoji == "Calm":
        emoji = "Relaxed"

    # Фильтруем строки по emoji и cluster
    filtered_rows = [row for row in rows if row['mood'].capitalize() == emoji]
    filtered_rows2 = [row for row in rows if row['mood'].capitalize()  == emoji]

    #print('num of track: ',len(filtered_rows))

    if cluster and random.random() < 0.7:  # 70% случаев учитываем cluster
        filtered_rows2 = [row for row in filtered_rows if row['cluster'] == cluster]

    # Выбираем случайную строку из отфильтрованных строк
    if len(filtered_rows2) < 2:
        filtered_rows2 = filtered_rows

    random_row = random.choice(filtered_rows2)
    track_id = random_row['YandexMusicID']
    # Попробуем скачать трек, если не удается, повторим попытку
    try:
        track = client.tracks(track_id)[0]
        track_path = os.path.join(folder_path2, f"{random_row['Number']}.mp3")
        track.download(track_path)
        cluster = random_row['cluster']
    except Exception as e:
        update_queue(emoji)

    # Удаление самого старого файла, чтобы очередь оставалась фиксированного размера
    search_pattern = os.path.join(folder_path2, "*.mp3")
    mp3_files = glob.glob(search_pattern)
    while len(mp3_files) >= 8:
        oldest_file = min(mp3_files, key=os.path.getctime)
        os.remove(oldest_file)
        mp3_files.remove(oldest_file)


def download_favorite_tracks():
    # Загружаем переменные из .env файла
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_file_path = os.path.join(current_dir, '..', '.env')
    load_dotenv(env_file_path)

    token = os.getenv('TOKEN')
    all_music_path = os.getenv('DIRECTORY')
    print(token)
    client = Client(token).init()

    # Получение любимых треков пользователя
    liked_tracks = client.users_likes_tracks()

    folder_with_mp3_path = os.path.join(all_music_path, 'all_mp3')
    if not os.path.exists(folder_with_mp3_path):
        os.makedirs(folder_with_mp3_path)

    music_storage_for_csv = current_dir

    csv_path = os.path.join(music_storage_for_csv, '..', 'tracks_info.csv')

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
    all_music_path = os.getenv('DIRECTORY')
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
    all_music_path = os.getenv('DIRECTORY')
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


def delete_mp3():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_file_path = os.path.join(current_dir, '..',  '.env')
    load_dotenv(env_file_path)
    all_music_path = os.getenv('DIRECTORY')
    folder_with_mp3_path = os.path.join(all_music_path, 'all_mp3')
    if os.path.exists(folder_with_mp3_path):
        shutil.rmtree(folder_with_mp3_path)


def classify_favoutite_music():
    download_favorite_tracks()
    classify_emotions()
    create_clusters()
    delete_mp3()
