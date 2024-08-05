import os
import glob
import shutil
import random
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import json
import pandas as pd
import soundfile as sf
import librosa 

# root_path='/mnt/storage/projects/incheon-119/datasets/cau/'
# save_path='./'
# 경로의 끝이 '/'로 끝나게 설정 필요

def data_processing(root_path, save_path):
    json_source_pattern = root_path+'231119/2.라벨데이터/*/*/*' # 폴더 이름에 ' '(띄어쓰기) 있으면 작동하지 않으니 수정이 필요합니다.
    wav_source_pattern = root_path+'231119/1.원천데이터/*/*/*' # 폴더 이름에 ' '(띄어쓰기) 있으면 작동하지 않으니 수정이 필요합니다.

    json_destination_dir = root_path+'json'
    wav_destination_dir = root_path+'wav/original'
    #data_move/copy

    os.makedirs(json_destination_dir, exist_ok=True)
    # 원본 파일 이동
    file_list = glob.glob(json_source_pattern)
    for file_path in tqdm(file_list):
        # shutil.move(file_path, json_destination_dir)
        shutil.copy2(file_path, json_destination_dir)


    os.makedirs(wav_destination_dir, exist_ok=True)
    # 원본 파일 이동
    file_list = glob.glob(wav_source_pattern)
    for file_path in tqdm(file_list):
        # shutil.move(file_path, wav_destination_dir)
        shutil.copy2(file_path, wav_destination_dir)


    json_file_path=root_path+'json/'
    wav_file_path=root_path+'wav/'
    all_json_files = sorted(glob.glob(json_file_path+'*.json'))
    all_wav_files = sorted(glob.glob(wav_file_path+'original/*.wav'))


    df_dict = {'json_path':[],'wav_path':[], 'id':[], 'symptom':[],'label':[]}

    emergency_symptoms_list = ['흉통', '절단', '압궤손상', '의식장애', '호흡곤란', '호흡정지', '심정지', '경련/발작', '실신', '토혈', '혈변', '저체온증', '마비', '기도이물']
    emergency_symptoms_list_sub1 =['얼굴마비', '구음장애', '팔 위약/ 마비', '다리 위약/마비', '의식장애', '어지러움', '두통', '경련/발작', '실신']
    emergency_symptoms_list_sub2 = ['흉통', '가슴불편감', '실신', '호흡곤란', '심계향진']
    emergency_symptoms_list.append(emergency_symptoms_list_sub1)
    emergency_symptoms_list.append(emergency_symptoms_list_sub2)

    def check_elements(a, b):
        for sub_list in b:
            count=0 
            for elem in a:
                if elem in b:
                    return True
                if isinstance(sub_list, list):
                    if elem in sub_list:
                        count+=1
                        if count > 1:
                            return True
        return False

    for file_path in all_json_files:
        filename=file_path.split('/')[-1]
        wav_name=filename.split('.json')[0]+'.wav'
        if filename.endswith('.json') and os.path.exists(os.path.join(wav_file_path,'original',filename.split('.json')[0]+'.wav')):
            with open(file_path, 'r') as f:
                
                data = json.load(f)

                if isinstance(data['symptom'],list) and 'symptom' in data.keys():
                    # Comments #
                    utterances = data['utterances']
                    text = []
                    label = check_elements(data['symptom'],emergency_symptoms_list)
                

                    # Temporary Label 
                    df_dict['json_path'].append(file_path)
                    df_dict['wav_path'].append(os.path.join(wav_file_path,'original',filename.split('.json')[0]+'.wav'))
                    df_dict['id'].append(data['_id'])
                    df_dict['symptom'].append(data['symptom'])
                    df_dict['label'].append(label)

            
    data_df = pd.DataFrame(df_dict)

    train_list, test_list=train_test_split(data_df, test_size=0.2, stratify=data_df['label'],random_state=42)
    train_list, valid_list=train_test_split(train_list, test_size=0.2, stratify=train_list['label'],random_state=42)

    # 분할 정보를 나타내는 열 추가
    data_df['split'] = 'None'  # 초기값으로 'None' 할당

    train_indices = train_list.index
    valid_indices = valid_list.index
    test_indices = test_list.index

    data_df.loc[train_indices, 'split'] = 'train'
    data_df.loc[valid_indices, 'split'] = 'valid'
    data_df.loc[test_indices, 'split'] = 'test'

    train_df=data_df.loc[train_indices]
    valid_df=data_df.loc[valid_indices]
    test_df=data_df.loc[test_indices]

    # train_df.to_csv('train_df.csv', index=False)
    # valid_df.to_csv('valid_df.csv', index=False)
    # test_df.to_csv('test_df.csv', index=False)
    # data_df.to_csv('data_df.csv', index=False)

    def make_label(root_path, df, mode):

        path = os.path.join(root_path,'json')
        audio_path = os.path.join(root_path, 'wav', 'original')
        audio_slide_path = os.path.join(root_path, 'wav', 'original_slide')

        df_dict = {'id':[], 'json_file_path':[], 'wav_original_file_path':[] ,'text':[], 'endAt':[],'label':[]}

        emergency_symptoms_list = ['흉통', '절단', '압궤손상', '의식장애', '호흡곤란', '호흡정지', '심정지', '경련/발작', '실신', '토혈', '혈변', '저체온증', '마비', '기도이물']
        emergency_symptoms_list_sub1 =['얼굴마비', '구음장애', '팔 위약/ 마비', '다리 위약/마비', '의식장애', '어지러움', '두통', '경련/발작', '실신']
        emergency_symptoms_list_sub2 = ['흉통', '가슴불편감', '실신', '호흡곤란', '심계향진']
        emergency_symptoms_list.append(emergency_symptoms_list_sub1)
        emergency_symptoms_list.append(emergency_symptoms_list_sub2)

        def check_elements(a, b):
            for sub_list in b:
                count=0 
                for elem in a:
                    if elem in b:
                        return True
                    if isinstance(sub_list, list):
                        if elem in sub_list:
                            count+=1
                            if count > 1:
                                return True
            return False

        json_file_path=df['json_path']
        original_file_path=df['wav_path']

        for n, (filename,wav_path) in tqdm(enumerate(zip(json_file_path,original_file_path))):
            if filename.endswith('.json'):
                file_path = os.path.join(path, filename)

                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data['symptom'],list) and 'symptom' in data.keys():
                        # Comments #
                        utterances = data['utterances']
                        text = []
                        label = check_elements(data['symptom'],emergency_symptoms_list)
                        for each in utterances:
                            if mode == 'test' and each['endAt'] > 120000: 
                                break
                            text.append(each['text'])


                    df_dict['json_file_path'].append(file_path)
                    if mode == 'test':
                        df_dict['wav_original_file_path'].append(root_path+'wav/original_cut/{}'.format(os.path.splitext(os.path.basename(wav_path))[0]+'_cut.wav'))
                    else:
                        df_dict['wav_original_file_path'].append(wav_path)
                    df_dict['text']+=[' '.join(text[:len(text)])]
                    df_dict['endAt'].append(each['endAt'])
                    df_dict['id'].append(data['_id'])
                    df_dict['label'].append(label)

        data_df = pd.DataFrame(df_dict)
        return data_df
    # id,json_file_path,wav_original_file_path,text,endAt,label
    train_dataset_path=save_path+'train_json_audio_data_end_full.csv'
    valid_dataset_path=save_path+'valid_json_audio_data_end_full.csv'
    test_dataset_path=save_path+'test_json_audio_data_end_full.csv'


    print('###########make_train_label###########')
    train=make_label(root_path=root_path,df=train_df, mode='test') #mode == 'test' -> cut 120초 / mode != 'test' -> non_cut
    train.to_csv(train_dataset_path, index=False)

    print('###########make_valid_label###########')
    valid=make_label(root_path=root_path,df=valid_df, mode='test')
    valid.to_csv(valid_dataset_path, index=False)

    print('###########make_test_label###########')
    test=make_label(root_path=root_path,df=test_df, mode='test')
    test.to_csv(test_dataset_path, index=False)

    print('\ntrain/valid/test 데이터의 수')
    print((len(train),len(valid),len(test)))
    print('train/valid/test 데이터의 응급비율')
    print((sum(train['label']==True)/len(train),
    sum(valid['label']==True)/len(valid),
    sum(test['label']==True)/len(test)))


    train=pd.read_csv(train_dataset_path)
    valid=pd.read_csv(valid_dataset_path)
    test=pd.read_csv(test_dataset_path)

    os.makedirs(root_path+'wav/original_cut', exist_ok=True)

    end_time=int(120000)/1000
    sr=16000
    end_sample = int(end_time * sr)

    def audio_cut(data, target_path, sampling_rate = 16000):
        past_audio_path=''
        row_iter = tqdm(data.iterrows(), total=len(data))
        for _, row in row_iter:
            audio_path=row[target_path]

            if audio_path != past_audio_path:

                past_audio_path=audio_path

                y, sr = librosa.load(row['wav_original_file_path'].replace('_cut.wav','.wav').replace('original_cut','original'), sr=sampling_rate)
                y_cut = y[:end_sample]

                sf.write(row['wav_original_file_path'], y_cut, sr)
            

    print('-----------train_cut------------')
    audio_cut(train, target_path= 'wav_original_file_path', sampling_rate = 16000)
    print('-----------valid_cut------------')
    audio_cut(valid, target_path= 'wav_original_file_path', sampling_rate = 16000)
    print('-----------test_cut------------')
    audio_cut(test, target_path= 'wav_original_file_path', sampling_rate = 16000)




    return train_dataset_path, valid_dataset_path, test_dataset_path
