import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

class MyDataset(Dataset):
    def __init__(self, 
                 data, 
                 tokenizer, 
                 max_length=512, 
                 padding='max_length',
                 class_num=2, ):
        super(MyDataset, self).__init__()
        self.data = data
        # self.label_tag = {'하':0, '중':0, '상':1, '최상':1}
        
        self.tokenizer = tokenizer

        self.max_length = max_length
        self.padding = padding
        self.return_tensors = 'pt'
        self.return_token_type_ids = True
        self.return_attention_mask = True
        
        self.class_num = class_num

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        ## sentence ##
        x = self.data.text[idx]
        tokenizer_output = self.tokenizer.encode_plus(x, max_length=self.max_length, padding=self.padding,
                                          return_tensors=self.return_tensors, truncation=True,
                                          return_token_type_ids=self.return_token_type_ids,
                                          return_attention_mask=self.return_attention_mask)

        input_ids = tokenizer_output['input_ids'][0]
        att_mask = tokenizer_output['attention_mask'][0]
        type_ids = tokenizer_output['token_type_ids'][0]

        ## label ##
        # y = self.label_tag[self.data.label[idx]]
        # y = torch.tensor(y).long()
        y = self.data.label[idx]
        y = torch.tensor(y).long()
        # y = F.one_hot(y, num_classes=self.class_num).float()
        
        return (input_ids, att_mask, type_ids), y

    def shape(self):
        return self.data.shape
    
class Triplet_Dataset(Dataset):
    def __init__(self, 
                 data, 
                 tokenizer, 
                 max_length=512, 
                 padding='max_length',
                 class_num=2, ):
        super(Triplet_Dataset, self).__init__()
        self.data = data
        self.index = np.array(range(len(self.data)))  # [0, 1, ,,, , n-1, n]
        # self.label_tag = {'하':0, '중':0, '상':1, '최상':1}
        
        self.tokenizer = tokenizer

        self.max_length = max_length
        self.padding = padding
        self.return_tensors = 'pt'
        self.return_token_type_ids = True
        self.return_attention_mask = True
        
        self.class_num = class_num

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        base_query = self.index != idx
        
        ## label ##
        # y = self.label_tag[self.data.label[idx]]
        # y = torch.tensor(y).long()
        label = self.data.label[idx]
        y = torch.tensor(label).long()
        # y = F.one_hot(y, num_classes=self.class_num).float()
        
        ## anchor sentence ##
        x = self.data.text[idx]
        tokenizer_output = self.tokenizer.encode_plus(x, max_length=self.max_length, padding=self.padding,
                                          return_tensors=self.return_tensors, truncation=True,
                                          return_token_type_ids=self.return_token_type_ids,
                                          return_attention_mask=self.return_attention_mask)

        anc_input_ids = tokenizer_output['input_ids'][0]
        anc_att_mask = tokenizer_output['attention_mask'][0]
        anc_type_ids = tokenizer_output['token_type_ids'][0]
        
        ## positive sentence ##
        pos_query = (self.data['label'] == label).to_numpy().reshape(-1)
        pos_index = self.index[base_query & pos_query]
        pos_idx = np.random.choice(pos_index)
        
        x = self.data.text[pos_idx]
        tokenizer_output = self.tokenizer.encode_plus(x, max_length=self.max_length, padding=self.padding,
                                          return_tensors=self.return_tensors, truncation=True,
                                          return_token_type_ids=self.return_token_type_ids,
                                          return_attention_mask=self.return_attention_mask)

        pos_input_ids = tokenizer_output['input_ids'][0]
        pos_att_mask = tokenizer_output['attention_mask'][0]
        pos_type_ids = tokenizer_output['token_type_ids'][0]
        
        ## negative sentence ##
        neg_query = (self.data['label'] != label).to_numpy().reshape(-1)
        neg_index = self.index[base_query & neg_query]
        neg_idx = np.random.choice(neg_index)
        
        x = self.data.text[neg_idx]
        tokenizer_output = self.tokenizer.encode_plus(x, max_length=self.max_length, padding=self.padding,
                                          return_tensors=self.return_tensors, truncation=True,
                                          return_token_type_ids=self.return_token_type_ids,
                                          return_attention_mask=self.return_attention_mask)

        neg_input_ids = tokenizer_output['input_ids'][0]
        neg_att_mask = tokenizer_output['attention_mask'][0]
        neg_type_ids = tokenizer_output['token_type_ids'][0]
        
        return (anc_input_ids, anc_att_mask, anc_type_ids), (pos_input_ids, pos_att_mask, pos_type_ids), (neg_input_ids, neg_att_mask, neg_type_ids), y

class Sample_Metric_Dataset(Dataset):
    def __init__(self, 
                 data, 
                 tokenizer,
                 max_length=512, 
                 padding='max_length',
                 class_num=2, ):
        super(Sample_Metric_Dataset, self).__init__()
        self.data = data
        self.files = data.id.unique()

        self.tokenizer = tokenizer
        
        self.max_length = max_length
        self.padding = padding
        self.return_tensors = 'pt'
        self.return_token_type_ids = True
        self.return_attention_mask = True
        
        self.class_num = class_num
        
    def __len__(self):
        return len(self.files)
        
    def __getitem__(self, idx):
        file = self.files[idx]
        
        samples = self.data[self.data['id'] == file]
        file_path = samples.json_file_path.tolist()[0] # id, json_file_path, wav_original_file_path, text, startAt, endAt, label
        # samples = {s:(l,t) for _,_,s,t,l in samples.values}
        # samples = sorted(samples.items(), key = lambda item: item[1][1])
        # id,json_file_path,wav_original_file_path,wav_slide_file_path,text,startAt,endAt,label 8
        # id,json_file_path,wav_original_file_path,wav_slide_file_path,text,startAt,endAt,label 8
        # id,json_file_path,wav_accompaniment_file_path,wav_slide_file_path,text,startAt,endAt,label 8
        samples = {e:(t,a,l) for _,_,_,a,t,_,e,l in samples.values}
        samples = sorted(samples.items(), key = lambda item: item[0])
        
        sample_data = [[], [], [], []] # input_ids, att_mask, token_type, y
        # for sent, (label, _) in samples:
        for end_time, (text, audio_path, label) in samples:
            tokenizer_output = self.tokenizer.encode_plus(text, max_length=self.max_length, padding=self.padding,
                                                          return_tensors=self.return_tensors, truncation=True,
                                                          return_token_type_ids=self.return_token_type_ids,
                                                          return_attention_mask=self.return_attention_mask)
            input_ids = tokenizer_output['input_ids'][0]
            att_mask = tokenizer_output['attention_mask'][0]
            type_ids = tokenizer_output['token_type_ids'][0]

            ## label ##
            y = torch.tensor(label).long()
            
            sample_data[0].append(input_ids)
            sample_data[1].append(att_mask)
            sample_data[2].append(type_ids)
            sample_data[3].append(y)
            
        return file_path, sample_data

def main():
    pass

if __name__ == "__main__":
    main()