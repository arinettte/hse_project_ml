from model_onnx import *

import torch.quantization
from torch.ao.quantization import get_default_qat_qconfig_mapping
from torch.ao.quantization.quantize_fx import prepare_qat_fx, convert_fx

if __name__ == "__main__":
    device = 'cpu'  # Квантизация происзодит на платформе x86 поэтому только cpu :(
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
    qconfig_mapping = get_default_qat_qconfig_mapping("fbgemm")
    example_inputs = torch.randn(batch_size, 1, 48, 48, requires_grad=True).to(device)

    model = ResNet(1, len(classes_train))
    model.load_state_dict(torch.load('./models/emotion_detection_acc0.5452366471290588.pth'))
    model = to_device(model, device)

    prepared_model_static = prepare_qat_fx(model, qconfig_mapping, example_inputs)

    # Калибровка квантизированной модели
    for batch_idx, (data, target) in enumerate(train_dl):
        prepared_model_static(data)
        if batch_idx % 10 == 0:
            break
            print("Batch %d/%d complete, continue ..." % (batch_idx + 1, len(valid_dl)))
    quantized_model = convert_fx(prepared_model_static)
    import os


    # save the model and check the model size
    def print_size_of_model(model, label=""):
        torch.save(model.state_dict(), "temp.p")
        size = os.path.getsize("temp.p")
        print("model: ", label, ' \t', 'Size (KB):', size / 1e3)
        os.remove('temp.p')
        return size


    f = print_size_of_model(model, "fp32")
    q = print_size_of_model(quantized_model, "int8")
    print("{0:.2f} times smaller".format(f / q))


    def quant_validation_epoch_end(outputs):
        batch_losses = [x['val_loss'] for x in outputs]
        epoch_loss = torch.stack(batch_losses).mean()
        batch_accs = [x['val_acc'] for x in outputs]
        epoch_acc = torch.stack(batch_accs).mean()
        return {'val_loss': epoch_loss.item(), 'val_acc': epoch_acc.item()}


    def quant_evaluate(model, val_loader):
        outputs = [quant_validation_step(model, batch) for batch in val_loader]
        return quant_validation_epoch_end(outputs)


    def quant_validation_step(model, batch):
        images, labels = batch
        out = model(images)
        loss = F.cross_entropy(out, labels)
        acc = accuracy(out, labels)
        return {'val_loss': loss.detach(), 'val_acc': acc}


    eval_accuracy = quant_evaluate(quantized_model, valid_dl)

    print(eval_accuracy)
