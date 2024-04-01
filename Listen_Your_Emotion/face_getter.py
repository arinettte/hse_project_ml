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

        ret, frame = cap.read()
        if not ret:
            print("Не удалось получить изображение с камеры.")
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            x, y, w, h = faces[0]
            face = frame[y:y + h, x:x + w]
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            cv2.imwrite(f'photos/face_{timestamp}.png', face)


    finally:
        cap.release()
        cv2.destroyAllWindows()