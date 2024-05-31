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
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    # всегда возвращаем путь ко второму файлу
    return files[1]


def update_queue(emoji):  # вызываем из плеера, когда включается следующий трек или когда пользователь переключает трек
    global cluster

    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_file_path = os.path.join(current_dir, '..', '.env')
    load_dotenv(env_file_path)
    token = str(os.getenv('TOKEN'))
    client = Client(token).init()
    if emoji == "Relaxed":
        emoji = 'Calm'

    folder_path2 = f"./music_storage/music_queues/{emoji}"
    csv_path = 'tracks_info.csv'

    with open(csv_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    if emoji == "Calm":
        emoji = "Relaxed"

    # Фильтруем строки по emoji и cluster
    filtered_rows = [row for row in rows if row['mood'].capitalize() == emoji]
    filtered_rows2 = [row for row in rows if row['mood'].capitalize() == emoji]

    if cluster and random.random() < 0.7:  # в 70% случаев учитываем cluster, чтобы
        # выбор не зацикливался на одном кластере
        filtered_rows2 = [row for row in filtered_rows if row['cluster'] == cluster]

    # Выбираем случайную строку из отфильтрованных строк, но только если их достаточно
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
