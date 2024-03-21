import cv2
import time
import os


def make_photo():  # должна работать постоянно
    face_cascade_path = 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + face_cascade_path)

    if not os.path.exists('photos'):
        os.makedirs('photos')

    cap = cv2.VideoCapture(0)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Не удалось получить изображение с камеры.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0:
                x, y, w, h = faces[0]
                face = frame[y:y+h, x:x+w]
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                photo_path = f'photos/face_{timestamp}.png'
                cv2.imwrite(photo_path, face)
                print(f"Фото сохранено: {photo_path}")

                # удаление старых фото, если их количество превышает 30
                photos_list = sorted([f for f in os.listdir('photos') if os.path.isfile(os.path.join('photos', f))])
                while len(photos_list) > 30:
                    oldest_photo = photos_list.pop(0)
                    os.remove(os.path.join('photos', oldest_photo))
                    print(f"Удалено старое фото: {oldest_photo}")

            time.sleep(10)

    finally:
        cap.release()
        cv2.destroyAllWindows()
