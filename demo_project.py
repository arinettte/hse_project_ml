import time
import asyncio
from player.app_first import *
from model_data import *
from face_getter import make_photo

if __name__ == '__main__':


    result_dir = './photos'
    BATCH_SIZE = 200
    classes = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
    result_tfms = tt.Compose([tt.Grayscale(num_output_channels=1), tt.ToTensor()])
    device = get_default_device()
    model = ResNet(1, len(classes))
    model.load_state_dict(torch.load('./models/emotion_detection_acc0.5452366471290588.pth'))
    model = to_device(model,device)

    choose_em_playlist = {}
    choose_playlist(2)

    app = QApplication(sys.argv)
    ex = MainWindow()
    splash = ex.show_splash()
    ex.show()
    def final_predict():
        data = [result_tfms(PIL.Image.open('./photos/'+os.listdir(result_dir)[-1]).resize((48, 48)))]
        data_dl = DataLoader(data, 200, num_workers=3, pin_memory=True)
        data_dl = DeviceDataLoader(data_dl, device)
        return classes[predict(model,data_dl)[0][0]]



