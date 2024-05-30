from model_pruning import *
import numpy as np
import onnx
from torch import nn
import torch.utils.model_zoo as model_zoo
import torch.onnx
import time
import onnxruntime as ort
import torch.nn as nn
import torch.nn.init as init
def to_numpy(tensor):
    return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()

if __name__ == "__main__":
    device = 'cuda'
    data_dir = './data'
    print(os.listdir(data_dir))
    classes_train = os.listdir(data_dir + "/train")
    classes_valid = os.listdir(data_dir + "/validation")
    print(f'Train Classes - {classes_train}')
    print(f'Validation Classes - {classes_valid}')

    train_tfms = tt.Compose([tt.Grayscale(num_output_channels=1),
                             tt.RandomHorizontalFlip(),
                             tt.RandomRotation(30),
                             tt.ToTensor()])

    valid_tfms = tt.Compose([tt.Grayscale(num_output_channels=1), tt.ToTensor()])

    batch_size = 200
    best_model = 0
    result_dir = './photos'

    result_tfms = tt.Compose([tt.Grayscale(num_output_channels=1), tt.ToTensor()])

    train_ds = ImageFolder(data_dir + '/train', train_tfms)
    valid_ds = ImageFolder(data_dir + '/validation', valid_tfms)
    train_dl = DataLoader(train_ds, batch_size, shuffle=True, num_workers=3, pin_memory=True)
    valid_dl = DataLoader(valid_ds, batch_size * 2, num_workers=3, pin_memory=True)

    train_dl = DeviceDataLoader(train_dl, device)
    valid_dl = DeviceDataLoader(valid_dl, device)

    num_classes = 7
    random_seed = 1
    l1_regularization_strength = 0
    l2_regularization_strength = 1e-4
    learning_rate = 1e-3
    learning_rate_decay = 1

    cuda_device = torch.device("cuda:0")
    cpu_device = torch.device("cpu:0")

    model = ResNet(1, len(classes_train))
    model.load_state_dict(torch.load('./models/emotion_detection_acc0.5452366471290588.pth'))
    model = to_device(model, device)
    for el in train_dl:
        test_batch = el[0]
        test_outs  = el[1]
        break
    x = to_device(torch.randn(batch_size, 1, 48, 48, requires_grad=True),device)
    torch.onnx.export(model,               # model being run
                      x,                         # model input (or a tuple for multiple inputs)
                      "onnx_model.onnx",   # where to save the model (can be a file or file-like object)
                      export_params=True,        # store the trained parameter weights inside the model file
                      opset_version=10,          # the ONNX version to export the model to
                      do_constant_folding=True,  # whether to execute constant folding for optimization
                      input_names = ['input'],   # the model's input names
                      output_names = ['output'], # the model's output names
                      dynamic_axes={'input' : {0 : 'batch_size'},    # variable length axes
                                    'output' : {0 : 'batch_size'}})


    onnx_model = onnx.load("onnx_model.onnx")
    onnx.checker.check_model(onnx_model)
    ort_session = ort.InferenceSession('onnx_model.onnx')
    res_acc = []
    for el in valid_dl:
        test_batch = el[0]
        test_outs = el[1]

        start_time = time.time()
        ort_inputs = {ort_session.get_inputs()[0].name: to_numpy(test_batch)}
        ort_outs = ort_session.run(None, ort_inputs)
        preds = [np.argmax(el) for el in ort_outs[0]]
        print("--- %s seconds with onnx ---" % (time.time() - start_time))

        start_time = time.time()
        no_onnx_dl = DataLoader(test_batch, batch_size, num_workers=3, pin_memory=False)
        no_onnx_dl = DeviceDataLoader(no_onnx_dl, device)
        no_onnx_outs = predict(model, no_onnx_dl)
        print("--- %s seconds without onnx ---\n" % (time.time() - start_time))

        res_acc.append(accuracy(to_device(torch.tensor(ort_outs[0]), device), to_device(test_outs, device)))
    print("Accuracy with onnx: ", sum(res_acc) / len(res_acc))