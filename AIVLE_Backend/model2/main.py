# https://github.com/HideOnHouse/TorchBase

import os
import glob
import wandb
import pickle
import argparse
import pandas as pd
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split, RandomSampler

from transformers import AutoTokenizer
from transformers import get_cosine_schedule_with_warmup
from transformers import get_linear_schedule_with_warmup

from dataset import *
from learning import *
from model import *
from data_processing import *
# from inference import *
# from inference_switching_recall import *
from utils import DataParallelModel, DataParallelCriterion
from utils import set_device, set_save_path, set_label_frequency, str2bool, calc_metric

import warnings
warnings.filterwarnings(action='ignore')

SEED = 42 # 17
# random.seed(SEED) #  Python의 random 라이브러리가 제공하는 랜덤 연산이 항상 동일한 결과를 출력하게끔
os.environ['PYTHONHASHSEED'] = str(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed(SEED)
torch.backends.cudnn.deterministic = True

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--is_scratch", type=str2bool, default=True)
    
    args = parser.parse_args()
    is_scratch = args.is_scratch
    
    # Define project
    WANDB_AUTH_KEY = 'df1bca81589e9de3f6b797bf9af026b4d175e284'
    project_name = 'NIA_119_찐막'
    model_name = 'Only_Text_{}'.format('scratch' if is_scratch else 'ckpt')
    model_link = 'beomi/KcELECTRA-base-v2022' #'beomi/kcbert-base'

    wandb.login(key=WANDB_AUTH_KEY)
    wandb.init(project=project_name)
    wandb.run.name = model_name

    # args
    epochs = 7
    batch_size = 256 # 128 + 64 + 32
    electra_lr = 2e-5
    cls_lr = 2e-3
    
    class_num = 2
    max_length = 256 # 384
    padding = 'max_length'
    upsampling_rate = 0.0
    by_file = True
    save_term = 100
    
    main_device, device_ids = set_device(main_device_num=0, using_device_num=7)
    save_path = set_save_path(model_name, epochs, batch_size)

    # Datasets
    # train_path, valid_path, test_path = data_processing(root_path=os.path.join('파일 path 입력'), 
    #                                                     save_path=os.path.join('파일 저장 경로 입력'))
    # data_propressing 함수에 문제가 발생할 경우, 해당 line 주석처리 후 아래 주석의 코드를 실행
    train_path = os.path.join('train_json_audio_data.csv')
    valid_path = os.path.join('valid_json_audio_data.csv')
    test_path = os.path.join('test_json_audio_data.csv')

    train_data = pd.read_csv(train_path)
    valid_data = pd.read_csv(valid_path)
    test_data = pd.read_csv(test_path)
    valid_file_ids = valid_data.id
    test_file_ids = test_data.id

    ## your Data Pre-Processing
    print('init Data >>>')
    print('\ttrain data :', train_data.shape)
    print('\tvalid data :', valid_data.shape)
    print('\tinit test data :', test_data.shape)

    train_data = train_data.dropna(axis=0)
    train_data = train_data.reset_index(drop=True)
    valid_data = valid_data.dropna(axis=0)
    valid_data = valid_data.reset_index(drop=True)
    test_data = test_data.dropna(axis=0)
    test_data = test_data.reset_index(drop=True)

    print('Drop nan >>>')
    print('\ttrain data :', train_data.shape)
    print('\tvalid data :', valid_data.shape)
    print('\ttest data :', test_data.shape)
    
    # print('Only One Sequence >>>')
    # train_data = set_last_sequence(train_data, end_time=120000, cut=False)
    # valid_data = set_last_sequence(valid_data, end_time=120000, cut=False)
    # test_data = set_last_sequence(test_data, end_time=120000, cut=True)
    # print('\ttrain data :', train_data.shape)
    # print('\tvalid data :', valid_data.shape)
    # print('\ttest data :', test_data.shape)

    print(f'Up-Sampling Label 0 >>> rate : {upsampling_rate}')
    train_data, train_label_frequency = set_label_frequency(train_data, rate=upsampling_rate, target_label=1, by_file=by_file)
    valid_data, valid_label_frequency = set_label_frequency(valid_data, rate=0.0, target_label=1, by_file=by_file)
    test_data, test_label_frequency = set_label_frequency(test_data, rate=0.0, target_label=1, by_file=by_file)
    print('\ttrain data :', train_data.shape)
    print('\tvalid data :', valid_data.shape)
    print('\ttest data :', test_data.shape)
    
    ## Create Dataset and DataLoader
    tokenizer = AutoTokenizer.from_pretrained(model_link)
    train_dataset = MyDataset(train_data, 
                              tokenizer, 
                              max_length=max_length, 
                              padding=padding,
                              class_num=class_num)
    valid_dataset = MyDataset(valid_data,
                              tokenizer,
                              max_length=max_length,
                              padding=padding,
                              class_num=class_num)
    test_dataset = MyDataset(test_data,
                             tokenizer,
                             max_length=max_length,
                             padding=padding,
                             class_num=class_num)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, sampler=RandomSampler(train_dataset), num_workers=4)
    valid_loader = DataLoader(valid_dataset, batch_size=batch_size, num_workers=4)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, num_workers=4)

    ## label_frequency
    train_label_frequency = (train_data.label == 1).sum() / len(train_data)
    valid_label_frequency = (valid_data.label == 1).sum() / len(valid_data)
    test_label_frequency = (test_data.label == 1).sum() / len(test_data)
    print("Label frequency of Train Data: {:6f}".format(train_label_frequency))
    print("Label frequency of Valid Data: {:6f}".format(valid_label_frequency))
    print("Label frequency of Test Data: {:6f}".format(test_label_frequency))
    
    # modeling
    if is_scratch:
        model = Baseline(model_link=model_link, class_num=2)
        model = DataParallelModel(model, device_ids=device_ids)#; model.to(device)
    else:
        check_path = os.path.join('models', 'One_Sequence_2m_O_72%_max_seq_256_e20_bs192', 'checkpoint_2_200.tar')
        model = Baseline(model_link=model_link, class_num=2)
        ckpt = torch.load(check_path, map_location=main_device)
        model.load_state_dict(ckpt['model_state_dict']); model.to(main_device)
        model = DataParallelModel(model, device_ids=device_ids)

    optimizer = optim.AdamW([{'params': model.module.electra.parameters(),'lr': electra_lr},
                             {'params': model.module.classifier.parameters(),'lr': cls_lr}],
                            eps=1e-8)
    criterion = torch.nn.CrossEntropyLoss()
    criterion = DataParallelCriterion(criterion, device_ids=device_ids)
    
    iter_len = len(train_loader)
    num_training_steps = iter_len * epochs
    num_warmup_steps = int(0.15 * num_training_steps)
    scheduler = get_linear_schedule_with_warmup(optimizer,
                                                num_warmup_steps=num_warmup_steps,
                                                num_training_steps=num_training_steps)

    config = {
        'electra_lr': electra_lr,
        'cls_lr': cls_lr,
        'batch_size': batch_size,
        'epochs': epochs,
        'max_length': max_length,
        'train_label_frequency': train_label_frequency,
        'valid_label_frequency': valid_label_frequency,
        'test_label_frequency': test_label_frequency,
        'upsampling_rate': upsampling_rate,
        'by_file':by_file
    }
    wandb.config.update(config)

    # Train
    print("============================= Train =============================")
    _ = train(train_label_frequency, scheduler, model, main_device, optimizer, criterion, epochs, save_path, train_loader, valid_loader, save_term)

    # Test
    print("============================= Test & Inference =============================")
    ckpt_path = sorted(glob.glob(os.path.join(save_path, '*.tar')))
    # print(ckpt_path)
    for model_path in ckpt_path:
        print(f"{model_path} >>> ")
        file_name = os.path.basename(model_path).split('.')[0]
        model = Baseline(model_link=model_link, class_num=2)
        ckpt = torch.load(model_path, map_location=main_device)
        model.load_state_dict(ckpt['model_state_dict']); model.to(main_device)
        model = DataParallelModel(model, device_ids=device_ids)
        
        test_loss, test_acc, (AUROC, AUPRC, TH_ACC, RECALL, PRECISION, F1, BRIER, _), (predicted_probas, labels)= inference_evaluate(model, 
                                                                                                                                  main_device, 
                                                                                                                                  criterion, 
                                                                                                                                  train_label_frequency, 
                                                                                                                                  valid_loader)
        print("test loss : {:.6f}".format(test_loss))
        print("test acc : {:.3f}".format(test_acc))
        print("test acc(th) : {:4f}".format(TH_ACC))
        print("test AUROC : {:.4f}".format(AUROC))
        print("test AUPRC : {:.4f}".format(AUPRC))
        print("test Recall : {:4f}".format(RECALL))    
        print("test Precision : {:.4f}".format(PRECISION))
        print("test F1_score : {:.4f}".format(F1))
        print("test Brier : {:4f}".format(BRIER))
        prediction_values = pd.DataFrame({'id':valid_file_ids,'predicted_probas':predicted_probas, 'labels':labels})
        prediction_values.to_csv(os.path.join(save_path, f'value_valid_{file_name}.csv'), index=False)
        
        test_loss, test_acc, (AUROC, AUPRC, TH_ACC, RECALL, PRECISION, F1, BRIER, _), (predicted_probas, labels)= inference_evaluate(model, 
                                                                                                                                  main_device, 
                                                                                                                                  criterion, 
                                                                                                                                  train_label_frequency, 
                                                                                                                                  test_loader)
        print("test loss : {:.6f}".format(test_loss))
        print("test acc : {:.3f}".format(test_acc))
        print("test acc(th) : {:4f}".format(TH_ACC))
        print("test AUROC : {:.4f}".format(AUROC))
        print("test AUPRC : {:.4f}".format(AUPRC))
        print("test Recall : {:4f}".format(RECALL))    
        print("test Precision : {:.4f}".format(PRECISION))
        print("test F1_score : {:.4f}".format(F1))
        print("test Brier : {:4f}".format(BRIER))
        prediction_values = pd.DataFrame({'id':test_file_ids,'predicted_probas':predicted_probas, 'labels':labels})
        prediction_values.to_csv(os.path.join(save_path, f'value_test_{file_name}.csv'), index=False)
        result_df = calc_metric(predicted_probas, labels)
        result_df.to_csv(os.path.join(save_path, f'TEST_{file_name}.csv'), index=False)
        print()


if __name__ == '__main__':
    main()
    # CUDA_VISIBLE_DEVICES=0,1,2,3 python main.py
    # CUDA_VISIBLE_DEVICES=1,2,3,4 python main.py
    # CUDA_VISIBLE_DEVICES= python main.py
