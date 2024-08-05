import wandb
import os
import sys

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm, notebook

from sklearn.metrics import (roc_auc_score, 
                             average_precision_score,
                             accuracy_score,  
                             recall_score,
                             precision_score,
                             f1_score,
                             brier_score_loss, # https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html
                             confusion_matrix,)

from utils import get_each_output, calc_acc

def train(label_frequency, scheduler, model, device, optimizer, 
          criterion, epochs, save_path, train_loader, valid_loader=None, save_term=256):
    """
    :param model: your model
    :param device: your device(cuda or cpu)
    :param optimizer: your optimizer
    :param criterion: loss function
    :param epochs: train epochs
    :param save_path : checkpoint path
    :param train_loader: train dataset
    :param valid_loader: valid dataset
    """
    model.to(device)
    for epoch in range(1, epochs + 1):
        model.train()
        sum_loss = sum_acc = 0
        valid_loss = valid_acc = 0
        bs = train_loader.batch_size

        # in notebook
        # pabr = notebook.tqdm(enumerate(train_loader), file=sys.stdout)

        # in interpreter
        pbar = tqdm(train_loader, file=sys.stdout)
        for batch_idx, ((input_ids, att_mask, type_ids), target) in enumerate(pbar):
            input_ids, att_mask, type_ids = input_ids.to(device), att_mask.to(device), type_ids.to(device)
            target = target.to(device)
            mb_len = len(target)

            optimizer.zero_grad()
            output = model(input_ids, att_mask, type_ids)
            # output = get_each_output(output)
            loss = criterion(output, target)
            acc = calc_acc(output, target)
            loss.backward()
            optimizer.step()
            scheduler.step()

            sum_loss += loss.item()
            sum_acc += acc

            loss = sum_loss / (batch_idx + 1)
            acc = sum_acc / (batch_idx * bs + mb_len)
            pbar.set_postfix(epoch=f'{epoch}/{epochs}', loss='{:.4f}, acc={:.4f}'.format(loss, acc))
            
            if batch_idx != 0 and batch_idx % save_term == 0:
                torch.save({
                    'model_state_dict': model.module.state_dict(),
                    'epoch': epoch,
                    'batch_idx': batch_idx
                }, os.path.join(save_path, f'checkpoint_{epoch}_{batch_idx}.tar'))
        pbar.close()

        train_loss = sum_loss / (batch_idx + 1)
        train_acc = sum_acc / (batch_idx * bs + mb_len)

        wandb.log({'train_loss': train_loss,
                   'train_acc': train_acc},
                  step=epoch)

        if valid_loader is not None:
            valid_loss, valid_acc, (AUROC, AUPRC, TH_ACC, RECALL, PRECISION, F1, BRIER) = evaluate(model, 
                                                                                                   device, 
                                                                                                   criterion, 
                                                                                                   label_frequency, 
                                                                                                   valid_loader)

            wandb.log({'valid_loss': valid_loss,
                       'valid_acc': valid_acc,
                       'valid_thacc': TH_ACC,
                       'valid_auroc': AUROC,
                       'valid_auprc': AUPRC,
                       'valid_recall': RECALL,
                       'valid_precision': PRECISION,
                       'valid_f1_score': F1,
                       'valid_brier': BRIER},
                      step=epoch)
        print()

        if epoch % 1 == 0:
            torch.save({
                'model_state_dict': model.module.state_dict(),
                'epoch': epoch,
                'batch_idx': batch_idx
            }, os.path.join(save_path, f'checkpoint_{epoch}_{batch_idx}.tar'))
    return model

def evaluate(model, device, criterion, label_frequency, data_loader):
    """
    :param model: your model
    :param device: your device(cuda or cpu)
    :param criterion: loss function
    :param data_loader: valid or test Datasets
    :return: (valid or test) loss and acc
    """
    model.eval()
    sum_loss = sum_acc = 0
    bs = data_loader.batch_size
    
    predicted = torch.tensor([])
    labels = torch.tensor([])

    with torch.no_grad():
        # in notebook
        # pabr = notebook.tqdm(enumerate(valid_loader), file=sys.stdout)

        # in interpreter
        pbar = tqdm(data_loader, file=sys.stdout)
        for batch_idx, ((input_ids, att_mask, type_ids), target) in enumerate(pbar):
            input_ids, att_mask, type_ids = input_ids.to(device), att_mask.to(device), type_ids.to(device)
            target = target.to(device)
            mb_len = len(target)

            output = model(input_ids, att_mask, type_ids)
            # output = get_each_output(output)
            loss = criterion(output, target)
            acc = calc_acc(output, target)

            sum_loss += loss.item()
            sum_acc += acc

            loss = sum_loss / (batch_idx + 1)
            acc = sum_acc / (batch_idx * bs + mb_len)
            pbar.set_postfix(loss='{:.4f}, acc={:.4f}'.format(loss, acc))
            
            if type(output) is list:
                logits = [o.detach().cpu() for o in output]
                logits = torch.cat(logits, dim=0)
            else:
                logits = output.detach().cpu()
            true_label = target.detach().cpu()
            predicted = torch.concat([predicted, logits], dim=0)
            labels = torch.concat([labels, true_label], dim=0)
        pbar.close()

    total_loss = sum_loss / (batch_idx + 1)
    total_acc = sum_acc / (batch_idx * bs + mb_len)
    
    # predicted_probas = torch.sigmoid(predicted)[:, 1]
    predicted_probas = torch.softmax(predicted, dim=-1)[:, 1]
    predicted_labels = torch.where(predicted_probas >= label_frequency , 1, 0)
    
    predicted_probas = predicted_probas.numpy()
    predicted_labels = predicted_labels.numpy()
    labels = labels.numpy()
    
    AUROC = roc_auc_score(labels, predicted_probas)
    AUPRC = average_precision_score(labels, predicted_probas)
    TH_ACC = accuracy_score(labels, predicted_labels)
    RECALL = recall_score(labels, predicted_labels)
    PRECISION = precision_score(labels, predicted_labels)
    F1 = f1_score(labels, predicted_labels)
    BRIER = brier_score_loss(labels, predicted_probas)
    # CM = confusion_matrix(labels, predicted_labels)
    return total_loss, total_acc, (AUROC, AUPRC, TH_ACC, RECALL, PRECISION, F1, BRIER)


def inference_evaluate(model, device, criterion, label_frequency, data_loader):
    """
    :param model: your model
    :param device: your device(cuda or cpu)
    :param criterion: loss function
    :param data_loader: valid or test Datasets
    :return: (valid or test) loss and acc
    """
    model.eval()
    sum_loss = sum_acc = 0
    bs = data_loader.batch_size
    
    predicted = torch.tensor([])
    labels = torch.tensor([])

    with torch.no_grad():
        # in notebook
        # pabr = notebook.tqdm(enumerate(valid_loader), file=sys.stdout)

        # in interpreter
        pbar = tqdm(data_loader, file=sys.stdout)
        for batch_idx, ((input_ids, att_mask, type_ids), target) in enumerate(pbar):
            input_ids, att_mask, type_ids = input_ids.to(device), att_mask.to(device), type_ids.to(device)
            target = target.to(device)
            mb_len = len(target)

            output = model(input_ids, att_mask, type_ids)
            # output = get_each_output(output)
            loss = criterion(output, target)
            acc = calc_acc(output, target)

            sum_loss += loss.item()
            sum_acc += acc

            loss = sum_loss / (batch_idx + 1)
            acc = sum_acc / (batch_idx * bs + mb_len)
            pbar.set_postfix(loss='{:.4f}, acc={:.4f}'.format(loss, acc))
            
            
            if type(output) is list:
                logits = [o.detach().cpu() for o in output]
                logits = torch.cat(logits, dim=0)
            else:
                logits = output.detach().cpu()
            true_label = target.detach().cpu()
            predicted = torch.concat([predicted, logits], dim=0)
            labels = torch.concat([labels, true_label], dim=0)
        pbar.close()

    total_loss = sum_loss / (batch_idx + 1)
    total_acc = sum_acc / (batch_idx * bs + mb_len)
    
    # predicted_probas = torch.sigmoid(predicted)[:, 1]
    predicted_probas = torch.softmax(predicted, dim=-1)[:, 1]
    predicted_labels = torch.where(predicted_probas >= label_frequency , 1, 0)
    
    predicted_probas = predicted_probas.numpy()
    predicted_labels = predicted_labels.numpy()
    labels = labels.numpy()
    
    AUROC = roc_auc_score(labels, predicted_probas)
    AUPRC = average_precision_score(labels, predicted_probas)
    TH_ACC = accuracy_score(labels, predicted_labels)
    RECALL = recall_score(labels, predicted_labels)
    PRECISION = precision_score(labels, predicted_labels)
    F1 = f1_score(labels, predicted_labels)
    BRIER = brier_score_loss(labels, predicted_probas)
    CM = confusion_matrix(labels, predicted_labels)
    return total_loss, total_acc, (AUROC, AUPRC, TH_ACC, RECALL, PRECISION, F1, BRIER, CM), (predicted_probas, labels)


def main():
    pass


if __name__ == "__main__":
    main()
