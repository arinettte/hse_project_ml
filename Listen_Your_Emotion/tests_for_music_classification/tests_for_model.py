import unittest
from dotenv import load_dotenv
import numpy as np
import pandas as pd
import os
import librosa
from collections import Counter
import joblib


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


def predict_mood(track):
    # Путь к модели
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, '..', 'models', 'music_classifier.pkl')
    label_encoder_path = os.path.join(current_dir, '..', 'models', 'le_mood.pkl')
    model = joblib.load(model_path)
    label_encoder = joblib.load(label_encoder_path)

    track_path = os.path.join(current_dir, track)
    mood_prediction = predict_mood_for_file(track_path, model, label_encoder)
    return mood_prediction


class TestMusicMoodModel(unittest.TestCase):

    def setUp(self):
        self.tracks = [
            {"title": "1.mp3", "expected_mood": "relaxed"},
            {"title": "2.mp3", "expected_mood": "relaxed"},
            {"title": "3.mp3", "expected_mood": "happy"},
            {"title": "4.mp3", "expected_mood": "happy"},
            {"title": "5.mp3", "expected_mood": "sad"},
        ]
        self.result_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_results.txt')
        with open(self.result_file_path, 'w') as f:
            f.write("Title - Predicted Mood - Expected Mood\n")

    def test_predict_mood_for_tracks(self):
        for track in self.tracks:
            title = track["title"]
            expected_mood = track["expected_mood"]
            mood = predict_mood(title)
            result_line = f"{title} - {mood} - {expected_mood}\n"

            # Записываем результат в файл
            with open(self.result_file_path, 'a') as f:
                f.write(result_line)


if __name__ == '__main__':
    unittest.main()
