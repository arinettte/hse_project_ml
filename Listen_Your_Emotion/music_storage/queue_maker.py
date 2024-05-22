import os
import glob
import random
import csv
from pathlib import Path
from dotenv import load_dotenv
from yandex_music import Client


def update_queue(emoji):
    load_dotenv()
    token = os.getenv('TOKEN')
    client = Client(token).init()
    # скачиваем новый трек и добавляем его в соответствующую очередь
    csv_filename = f"./music_storage/{emoji}.csv"
    folder_path = Path(f"./music_storage/music_queues/{emoji}")
    with open(csv_filename, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    random_row_num = random.randint(1, len(rows))
    random_row = rows[random_row_num - 1]
    track_id = random_row['id']
    # если с текущим треком проблемы, мы обработаем другой
    try:
        track = client.tracks(track_id)[0]
        track_name = random_row['title'] + ' -- ' + random_row['artists']
        track.download(f"{folder_path}/{track_name}.mp3")
    except Exception:
        update_queue(emoji)
    # удаление самого старого файла, чтобы очередь оставалась фиксированногоо размера
    search_pattern = os.path.join(folder_path, "*.mp3")
    mp3_files = glob.glob(search_pattern)
    while len(mp3_files) >= 8:
        oldest_file = min(mp3_files, key=os.path.getctime)
        os.remove(oldest_file)
        mp3_files.remove(oldest_file)


def get_users_playlists():  # вызываем при запуске приложения
    load_dotenv()
    token = os.getenv('TOKEN')
    client = Client(token).init()

    playlists = client.users_playlists_list()
    for playlist in playlists:
        if playlist.title != 'Happy' and playlist.title != 'Sad' and playlist.title != 'Calm':
            continue
        csv_filename = f"{playlist.title}.csv"
        print(f"{playlist.title}.csv")
        with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'title', 'artists'])
            counter = 0
            for track_short in playlist.fetch_tracks():
                track = client.tracks(track_short.id)[0]
                if not track.id or not track.title or not track.artists:
                    continue
                track_title = track.title.replace(':', '').replace("'", '').replace('"', '')
                artists = ', '.join(
                    artist.name.replace(':', '').replace("'", '').replace('"', '') for artist in track.artists)
                writer.writerow([track.id, track_title, artists])
                if counter == 70:  # оптимизируем время работы
                    break
                counter += 1

    # инициализируем очередь при запуске приложения
    for i in range(7): update_queue('Calm')
    for i in range(7): update_queue('Happy')
    for i in range(7): update_queue('Sad')