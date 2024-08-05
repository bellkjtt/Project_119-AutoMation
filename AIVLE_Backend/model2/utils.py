import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm, notebook

import torch

from sklearn.metrics import (roc_auc_score, 
                             average_precision_score,
                             accuracy_score,  
                             recall_score,
                             precision_score,
                             f1_score,
                             brier_score_loss, # https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html
                             confusion_matrix,)

def calc_metric(predicted_probas, labels):
    result = {
        'THRESHOLD' : [],
        
        'TH_ACC' : [],
        'AUROC' : [],
        'AUPRC' : [],
        'RECALL' : [],
        'PRECISION' : [],
        'F1': [],
    }
    
    for threshold in np.linspace(0, 1, 384):
        result['THRESHOLD'].append(round(threshold, 5))
        
        predicted_label = np.where(predicted_probas >= threshold , 1, 0)
        
        # result['ACC'].append(round(accuracy_score(labels, np.where(predicted_probas >= 0.5 , 1, 0)), 5))
        result['TH_ACC'].append(round(accuracy_score(labels, predicted_label), 5))
        result['AUROC'].append(round(roc_auc_score(labels, predicted_probas), 5))
        result['AUPRC'].append(round(average_precision_score(labels, predicted_probas), 5))
        result['RECALL'].append(round(recall_score(labels, predicted_label), 5))
        result['PRECISION'].append(round(precision_score(labels, predicted_label), 5))
        result['F1'].append(round(f1_score(labels, predicted_label), 5))
        
    result_df = pd.DataFrame(result)
    return result_df

def set_last_sequence(df, end_time=120000, cut=False):
    columns = ['id', 'json_file_path', 'wav_original_file_path',
               'text', 'endAt', 'label']
    result = {
        'id' : [], 
        'json_file_path' : [], 
        'wav_original_file_path' : [],
        'text' : [], 
        'endAt' : [], 
        'label' : []
    }
    id_list = df.id.unique()
    if cut:        
        for i in tqdm(range(len(id_list))):
            temp = df[df.id == id_list[i]]
            temp = temp[temp.endAt <= end_time].iloc[-1:, :]
            id, json_file_path, wav_original_file_path, text, endAt, label = temp.values[0]
            result['id'].append(id)
            result['json_file_path'].append(json_file_path)
            result['wav_original_file_path'].append(wav_original_file_path)
            result['text'].append(text)
            result['endAt'].append(endAt)
            result['label'].append(label)
    else:   
        for i in tqdm(range(len(id_list))):
            temp = df[df.id == id_list[i]].iloc[-1:, :]
            id, json_file_path, wav_original_file_path, text, endAt, label = temp.values[0]
            result['id'].append(id)
            result['json_file_path'].append(json_file_path)
            result['wav_original_file_path'].append(wav_original_file_path)
            result['text'].append(text)
            result['endAt'].append(endAt)
            result['label'].append(label)
    
    one_seq_df = pd.DataFrame(result)
    return one_seq_df.sample(frac=1).reset_index(drop=True)

def set_label_frequency(df, rate=0.35, target_label=1, by_file=True):
    if rate == 0:
        label_frequency = (df.label == 1).sum() / len(df)
        return df, label_frequency
    
    columns = ['file_path', 'id', 'text', 'endAt', 'label']
    if by_file:
        upsampling_file_list = df[df.label == target_label].id.unique()
        np.random.shuffle(upsampling_file_list)
        N = int(len(upsampling_file_list) * rate)
        file_list = upsampling_file_list[:N]
        upsampling_df = df[df.id.isin(file_list)]
        target_label_df = df[df.label == target_label]
        non_target_label_df = df[df.label != target_label]
    else:
        upsampling_df = df[df.label == target_label].sample(frac=rate)
        target_label_df = df[df.label == target_label]
        non_target_label_df = df[df.label != target_label]
    result_df = pd.concat([target_label_df, non_target_label_df, upsampling_df], axis=0).sample(frac=1).reset_index(drop=True)
    label_frequency = (result_df.label == 1).sum() / len(result_df)
    return result_df, label_frequency


def get_each_output(output):
    if type(output) is not list:
        return output
    else:
        return list(map(list, zip(*output)))

def calc_acc(output, label):
    if type(output) is list:  # if multi-gpu settings
        # copy to cpu from gpu
        output = [o.detach().cpu() for o in output]
        output = torch.cat(output, dim=0)
        label = label.detach().cpu()

    o_val, o_idx = torch.max(output, dim=-1)
    return (o_idx == label).sum().item()


def draw_history(history, save_path=None):
    train_loss = history["train_loss"]
    train_acc = history["train_acc"]
    valid_loss = history["valid_loss"]
    valid_acc = history["valid_acc"]

    plt.subplot(2, 1, 1)
    plt.plot(train_loss, label="train")
    plt.plot(valid_loss, label="valid")
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(train_acc, label="train")
    plt.plot(valid_acc, label="valid")
    plt.legend()

    if save_path is None:
        plt.show()
    else:
        plt.savefig(os.path.join(save_path, 'train_plot.png'), dpi=300)


def set_device(main_device_num=0, using_device_num=4):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    device_ids = list(range(main_device_num, main_device_num + using_device_num))
    if device == 'cuda':
        device += ':{}'.format(main_device_num)
    return device, device_ids


def set_save_path(model_name, epochs, batch_size):
    directory = os.path.join('models', f'{model_name}_e{epochs}_bs{batch_size}')
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)
    return directory

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

##++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
## Created by: Hang Zhang
## ECE Department, Rutgers University
## Email: zhang.hang@rutgers.edu
## Copyright (c) 2017
##
## This source code is licensed under the MIT-style license found in the
## LICENSE file in the root directory of this source tree
## https://github.com/zhanghang1989/PyTorch-Encoding/blob/master/encoding/parallel.py
##++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""Encoding Data Parallel"""
import threading
import functools
import torch
from torch.autograd import Variable, Function
import torch.cuda.comm as comm
from torch.nn.parallel.data_parallel import DataParallel
from torch.nn.parallel.parallel_apply import get_a_var
from torch.nn.parallel._functions import ReduceAddCoalesced, Broadcast

torch_ver = torch.__version__[:3]

__all__ = ['allreduce', 'DataParallelModel', 'DataParallelCriterion',
           'patch_replication_callback']


def allreduce(*inputs):
    """Cross GPU all reduce autograd operation for calculate mean and
    variance in SyncBN.
    """
    return AllReduce.apply(*inputs)


class AllReduce(Function):
    @staticmethod
    def forward(ctx, num_inputs, *inputs):
        ctx.num_inputs = num_inputs
        ctx.target_gpus = [inputs[i].get_device() for i in range(0, len(inputs), num_inputs)]
        inputs = [inputs[i:i + num_inputs]
                  for i in range(0, len(inputs), num_inputs)]
        # sort before reduce sum
        inputs = sorted(inputs, key=lambda i: i[0].get_device())
        results = comm.reduce_add_coalesced(inputs, ctx.target_gpus[0])
        outputs = comm.broadcast_coalesced(results, ctx.target_gpus)
        return tuple([t for tensors in outputs for t in tensors])

    @staticmethod
    def backward(ctx, *inputs):
        inputs = [i.data for i in inputs]
        inputs = [inputs[i:i + ctx.num_inputs]
                  for i in range(0, len(inputs), ctx.num_inputs)]
        results = comm.reduce_add_coalesced(inputs, ctx.target_gpus[0])
        outputs = comm.broadcast_coalesced(results, ctx.target_gpus)
        return (None,) + tuple([Variable(t) for tensors in outputs for t in tensors])


class Reduce(Function):
    @staticmethod
    def forward(ctx, *inputs):
        ctx.target_gpus = [inputs[i].get_device() for i in range(len(inputs))]
        inputs = sorted(inputs, key=lambda i: i.get_device())
        return comm.reduce_add(inputs)

    @staticmethod
    def backward(ctx, gradOutput):
        return Broadcast.apply(ctx.target_gpus, gradOutput)


class DataParallelModel(DataParallel):
    """Implements data parallelism at the module level.

    This container parallelizes the application of the given module by
    splitting the input across the specified devices by chunking in the
    batch dimension.
    In the forward pass, the module is replicated on each device,
    and each replica handles a portion of the input. During the backwards pass, gradients from each replica are summed into the original module.
    Note that the outputs are not gathered, please use compatible
    :class:`encoding.parallel.DataParallelCriterion`.

    The batch size should be larger than the number of GPUs used. It should
    also be an integer multiple of the number of GPUs so that each chunk is
    the same size (so that each GPU processes the same number of samples).

    Args:
        module: module to be parallelized
        device_ids: CUDA devices (default: all devices)

    Reference:
        Hang Zhang, Kristin Dana, Jianping Shi, Zhongyue Zhang, Xiaogang Wang, Ambrish Tyagi,
        Amit Agrawal. “Context Encoding for Semantic Segmentation.
        *The IEEE Conference on Computer Vision and Pattern Recognition (CVPR) 2018*

    Example::

        >>> net = encoding.nn.DataParallelModel(model, device_ids=[0, 1, 2])
        >>> y = net(x)
    """

    def gather(self, outputs, output_device):
        return outputs

    def replicate(self, module, device_ids):
        modules = super(DataParallelModel, self).replicate(module, device_ids)
        return modules


class DataParallelCriterion(DataParallel):
    """
    Calculate loss in multiple-GPUs, which balance the memory usage for
    Semantic Segmentation.

    The targets are splitted across the specified devices by chunking in
    the batch dimension. Please use together with :class:`encoding.parallel.DataParallelModel`.

    Reference:
        Hang Zhang, Kristin Dana, Jianping Shi, Zhongyue Zhang, Xiaogang Wang, Ambrish Tyagi,
        Amit Agrawal. “Context Encoding for Semantic Segmentation.
        *The IEEE Conference on Computer Vision and Pattern Recognition (CVPR) 2018*

    Example::

        >>> net = encoding.nn.DataParallelModel(model, device_ids=[0, 1, 2])
        >>> criterion = encoding.nn.DataParallelCriterion(criterion, device_ids=[0, 1, 2])
        >>> y = net(x)
        >>> loss = criterion(y, target)
    """

    def forward(self, inputs, *targets, **kwargs):
        # input should be already scatterd
        # scattering the targets instead
        if not self.device_ids:
            return self.module(inputs, *targets, **kwargs)
        targets, kwargs = self.scatter(targets, kwargs, self.device_ids)

        if len(self.device_ids) == 1:
            return self.module(inputs, *targets[0], **kwargs[0])
        replicas = self.replicate(self.module, self.device_ids[:len(inputs)])
        outputs = _criterion_parallel_apply(replicas, inputs, targets, kwargs)
        return Reduce.apply(*outputs) / len(outputs)


import sys
import pdb


class ForkedPdb(pdb.Pdb):
    def interaction(self, *args, **kwargs):
        _stdin = sys.stdin
        try:
            sys.stdin = open('/dev/stdin')
            pdb.Pdb.interaction(self, *args, **kwargs)
        finally:
            sys.stdin = _stdin


def _criterion_parallel_apply(modules, inputs, targets, kwargs_tup=None, devices=None):
    assert len(modules) == len(inputs)
    assert len(targets) == len(inputs)
    if kwargs_tup:
        assert len(modules) == len(kwargs_tup)
    else:
        kwargs_tup = ({},) * len(modules)
    if devices is not None:
        assert len(modules) == len(devices)
    else:
        devices = [None] * len(modules)

    lock = threading.Lock()
    results = {}
    if torch_ver != "0.3":
        grad_enabled = torch.is_grad_enabled()

    def _worker(i, module, input, target, kwargs, device=None):
        if torch_ver != "0.3":
            torch.set_grad_enabled(grad_enabled)
            device = get_a_var(input).get_device()
        try:
            with torch.cuda.device(device):
                output = module(*(input + target), **kwargs)
            with lock:
                results[i] = output
        except Exception as e:
            with lock:
                results[i] = e

    if len(modules) > 1:
        threads = [threading.Thread(target=_worker,
                                    args=(i, module, (input,), target,
                                          kwargs, device), )
                   for i, (module, input, target, kwargs, device) in
                   enumerate(zip(modules, inputs, targets, kwargs_tup, devices))]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    else:
        _worker(0, modules[0], inputs[0], kwargs_tup[0], devices[0])
    outputs = []
    for i in range(len(inputs)):
        output = results[i]
        if isinstance(output, Exception):
            raise output
        outputs.append(output)
    return outputs


if __name__ == '__main__':
    # Datasets
    # train_path = "train_data.csv"
    # valid_path = "valid_data.csv"
    # test_path = "test_data.csv"
    data_path = os.path.join('train_json_audio_data_stack.csv')
    # data_path = os.path.join('valid_json_audio_data_stack.csv')
    # data_path = os.path.join('test_json_audio_data_stack.csv')

    data_data = pd.read_csv(data_path)

    ## your Data Pre-Processing
    print('init Data >>>')
    print('\tdata :', data_data.shape)

    data_data = data_data.dropna(axis=0)
    data_data = data_data.reset_index(drop=True)

    print('Drop nan >>>')
    print('\ttrain data :', data_data.shape)
    
    print('Only One Sequence >>>')
    data_data = set_last_sequence(data_data, end_time=120000, cut=False)
    
    data_data.to_csv('train_json_audio_data_one_seq.csv', index=False)
