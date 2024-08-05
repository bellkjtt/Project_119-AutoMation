from collections import OrderedDict

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

from transformers import AutoModel

class Baseline(nn.Module):
    def __init__(self,
                 model_link='beomi/KcELECTRA-base-v2022',
                 class_num=2):
        super(Baseline, self).__init__()
        self.electra = AutoModel.from_pretrained(model_link)
        
        self.classifier = nn.Sequential(OrderedDict([
            ('dense',nn.Linear(768, 768)),
            ('dropout', nn.Dropout(0.1)),
            ('out_proj', nn.Linear(768, 2)),
        ]))
        
    def encode(self, input_ids, att_mask, token_type_ids):
        output = self.electra(input_ids, att_mask, token_type_ids)
        last_hidden_state = output.last_hidden_state
        
        # cls = torch.mean(last_hidden_state, dim=1)
        cls = last_hidden_state[:, 0, :]
        return cls
        
    def forward(self, input_ids, att_mask, token_type_ids):
        output = self.electra(input_ids, att_mask, token_type_ids)
        last_hidden_state = output.last_hidden_state
        
        # cls = torch.mean(last_hidden_state, dim=1)
        cls = last_hidden_state[:, 0, :]
        logit = self.classifier(cls)
        return logit

def get_Model(class_name):
    try:
        Myclass = eval(class_name)()
        return Myclass
    except NameError as e:
        print("Class [{}] is not defined".format(class_name))

def main():
    pass

if __name__ == "__main__":
    main()