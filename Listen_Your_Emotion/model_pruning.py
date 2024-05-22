from model_data import *
import os
import copy
import torch
import torch.nn.utils.prune as prune


def compute_final_pruning_rate(pruning_rate, num_iterations):
    """A function to compute the final pruning rate for iterative pruning.
        Note that this cannot be applied for global pruning rate if the pruning rate is heterogeneous among different layers.

    Args:
        pruning_rate (float): Pruning rate.
        num_iterations (int): Number of iterations.

    Returns:
        float: Final pruning rate.
    """

    final_pruning_rate = 1 - (1 - pruning_rate) ** num_iterations

    return final_pruning_rate


def measure_module_sparsity(module, weight=True, bias=False, use_mask=False):
    num_zeros = 0
    num_elements = 0

    if use_mask == True:
        for buffer_name, buffer in module.named_buffers():
            if "weight_mask" in buffer_name and weight == True:
                num_zeros += torch.sum(buffer == 0).item()
                num_elements += buffer.nelement()
            if "bias_mask" in buffer_name and bias == True:
                num_zeros += torch.sum(buffer == 0).item()
                num_elements += buffer.nelement()
    else:
        for param_name, param in module.named_parameters():
            if "weight" in param_name and weight == True:
                num_zeros += torch.sum(param == 0).item()
                num_elements += param.nelement()
            if "bias" in param_name and bias == True:
                num_zeros += torch.sum(param == 0).item()
                num_elements += param.nelement()

    sparsity = num_zeros / num_elements

    return num_zeros, num_elements, sparsity


def measure_global_sparsity(model,
                            weight=True,
                            bias=False,
                            conv2d_use_mask=False,
                            linear_use_mask=False):
    num_zeros = 0
    num_elements = 0

    for module_name, module in model.named_modules():

        if isinstance(module, torch.nn.Conv2d):

            module_num_zeros, module_num_elements, _ = measure_module_sparsity(
                module, weight=weight, bias=bias, use_mask=conv2d_use_mask)
            num_zeros += module_num_zeros
            num_elements += module_num_elements

        elif isinstance(module, torch.nn.Linear):

            module_num_zeros, module_num_elements, _ = measure_module_sparsity(
                module, weight=weight, bias=bias, use_mask=linear_use_mask)
            num_zeros += module_num_zeros
            num_elements += module_num_elements

    sparsity = num_zeros / num_elements

    return num_zeros, num_elements, sparsity


def iterative_pruning_finetuning(model,
                                 train_loader,
                                 test_loader,
                                 device,
                                 learning_rate,
                                 l1_regularization_strength,
                                 l2_regularization_strength,
                                 learning_rate_decay=0.1,
                                 conv2d_prune_amount=0.4,
                                 linear_prune_amount=0.2,
                                 num_iterations=10,
                                 num_epochs_per_iteration=10,
                                 model_filename_prefix="pruned_model",
                                 model_dir="saved_models",
                                 grouped_pruning=False):
    print("Accuracy before pruning:", evaluate(model, valid_dl))
    param_size = 0
    for param in model.parameters():
        param_size += param.nelement() * param.element_size()
    buffer_size = 0
    for buffer in model.buffers():
        buffer_size += buffer.nelement() * buffer.element_size()

    size_all_mb = (param_size + buffer_size) / 1024 ** 2
    print('model size before pruning: {:.3f}MB'.format(size_all_mb))

    for i in range(num_iterations):

        print("Pruning and Finetuning {}/{}".format(i + 1, num_iterations))

        print("Pruning...")

        if grouped_pruning == True:
            # Global pruning
            # I would rather call it grouped pruning.
            parameters_to_prune = []
            for module_name, module in model.named_modules():
                if isinstance(module, torch.nn.Conv2d):
                    parameters_to_prune.append((module, "weight"))
            prune.global_unstructured(
                parameters_to_prune,
                pruning_method=prune.L1Unstructured,
                amount=conv2d_prune_amount,
            )
        else:
            for module_name, module in model.named_modules():
                if isinstance(module, torch.nn.Conv2d):
                    prune.l1_unstructured(module,
                                          name="weight",
                                          amount=conv2d_prune_amount)
                elif isinstance(module, torch.nn.Linear):
                    prune.l1_unstructured(module,
                                          name="weight",
                                          amount=linear_prune_amount)

        eval_accuracy = evaluate(model, test_loader)

        num_zeros, num_elements, sparsity = measure_global_sparsity(
            model,
            weight=True,
            bias=False,
            conv2d_use_mask=True,
            linear_use_mask=False)

        # print("Test Accuracy: {:.3f}".format(eval_accuracy))
        print(eval_accuracy)

        print("Global Sparsity:")
        print("{:.2f}".format(sparsity))

        # print(model.conv1._forward_pre_hooks)

        print("Fine-tuning...")
        train_model(num_epochs_per_iteration, max_lr, model, train_loader, test_loader, device=device,
                    grad_clip=grad_clip, weight_decay=l2_regularization_strength, opt_func=opt_func)
        """train_model(model=model,
                    train_loader=train_loader,
                    test_loader=test_loader,
                    device=device,
                    l1_regularization_strength=l1_regularization_strength,
                    l2_regularization_strength=l2_regularization_strength,
                    learning_rate=learning_rate * (learning_rate_decay**i),
                    num_epochs=num_epochs_per_iteration)"""

        eval_accuracy = evaluate(model, test_loader)

        num_zeros, num_elements, sparsity = measure_global_sparsity(
            model,
            weight=True,
            bias=False,
            conv2d_use_mask=True,
            linear_use_mask=False)

        # print("Test Accuracy: {:.3f}".format(eval_accuracy))
        print(eval_accuracy)
        print("Global Sparsity:")
        print("{:.2f}".format(sparsity))

        model_filename = "{}_{}.pt".format(model_filename_prefix, i + 1)
        model_filepath = os.path.join(model_dir, model_filename)

        save_model(model=model,
                   model_dir=model_dir,
                   model_filename=model_filename)
        model = load_model(model=model,
                           model_filepath=model_filepath,
                           device=device)

    return model


epochs = 130
max_lr = 0.0008
grad_clip = 0.1
weight_decay = 1e-4
opt_func = torch.optim.Adam


def remove_parameters(model):
    for module_name, module in model.named_modules():
        if isinstance(module, torch.nn.Conv2d):
            try:
                prune.remove(module, "weight")
            except:
                pass
            try:
                prune.remove(module, "bias")
            except:
                pass
        elif isinstance(module, torch.nn.Linear):
            try:
                prune.remove(module, "weight")
            except:
                pass
            try:
                prune.remove(module, "bias")
            except:
                pass

    return model


def save_model(model, model_dir, model_filename):
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    model_filepath = os.path.join(model_dir, model_filename)
    torch.save(model.state_dict(), model_filepath)


def load_model(model, model_filepath, device):
    model.load_state_dict(torch.load(model_filepath, map_location=device))

    return model


if __name__ == '__main__':
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

    model_dir = "models"
    model_filename = "emotion_detection_acc0.5452366471290588.pth"
    model_filename_prefix = "pruned_model"
    pruned_model_filename = "1.pt"
    model_filepath = os.path.join(model_dir, model_filename)
    pruned_model_filepath = os.path.join(model_dir, pruned_model_filename)

    # Create an untrained model.

    # Load a pretrained model.
    model = ResNet(1, len(classes_train))
    model.load_state_dict(torch.load('./models/emotion_detection_acc0.5452366471290588.pth'))
    model = to_device(model, device)

    eval_accuracy = evaluate(model, valid_dl)

    num_zeros, num_elements, sparsity = measure_global_sparsity(model)
    print(eval_accuracy)
    # print("Test Accuracy: {:.3f}".format(eval_accuracy))

    print("Global Sparsity:")
    print("{:.2f}".format(sparsity))

    print("Iterative Pruning + Fine-Tuning...")

    pruned_model = copy.deepcopy(model)
    iterative_pruning_finetuning(
        model=pruned_model,
        train_loader=train_dl,
        test_loader=valid_dl,
        device=cuda_device,
        learning_rate=learning_rate,
        learning_rate_decay=learning_rate_decay,
        l1_regularization_strength=l1_regularization_strength,
        l2_regularization_strength=l2_regularization_strength,
        conv2d_prune_amount=0.9,
        linear_prune_amount=0.05,
        num_iterations=1,
        num_epochs_per_iteration=5,  # Was 200
        model_filename_prefix=model_filename_prefix,
        model_dir=model_dir,
        grouped_pruning=True)
    eval_accuracy = evaluate(pruned_model, valid_dl)

    num_zeros, num_elements, sparsity = measure_global_sparsity(pruned_model)
    print(eval_accuracy)

    print("Global Sparsity:")
    print("{:.2f}".format(sparsity))
    param_size = 0
    for param in pruned_model.parameters():
        param_size += param.nelement() * param.element_size()
    buffer_size = 0
    for buffer in pruned_model.buffers():
        buffer_size += buffer.nelement() * buffer.element_size()

    size_all_mb = (param_size + buffer_size) / 1024 ** 2
    print('model size after pruning: {:.3f}MB'.format(size_all_mb))
