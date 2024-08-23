import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split, RandomSampler

import asyncio
import aiohttp
import numpy as np
from django.http import JsonResponse
from rest_framework.views import APIView
import io
import os
from .classify_model import Model1, Model2

# 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "finetuned_models")
checkpoint = 'checkpoint-11500'
tokenizer_name = 'KcELECTRA-base-v2022'

# 모델1 초기화
model1 = Model1(model_path=model_path, checkpoint=checkpoint, tokenizer_name=tokenizer_name)

# 모델2 초기화
model_link = 'beomi/KcELECTRA-base-v2022'
ckpt_path = os.path.join(BASE_DIR, 'model2/checkpoint_2_300.tar')
model2 = Model2(model_link=model_link, ckpt_path=ckpt_path)

padding = 'max_length'

SEED = 42
os.environ['PYTHONHASHSEED'] = str(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed(SEED)
torch.backends.cudnn.deterministic = True

async def classify_text(text, tokenizer, model, device, label_frequency=None):
    custom_labels = {0: "비구급", 1: "구급"}
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=padding, max_length=model.tokenizer.model_max_length)
    if label_frequency:
        input_ids = inputs['input_ids'].to(device)
        attention_mask = inputs['attention_mask'].to(device)
        token_type_ids = inputs['token_type_ids'].to(device)
    else:
        inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        if label_frequency:
            outputs = model.model(input_ids, attention_mask, token_type_ids)
            logits = outputs
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            predicted_class = (probabilities[0, 1] >= label_frequency).int().item()
            predicted_label = custom_labels[predicted_class]
            confidence = probabilities[0][predicted_class].item()      
        else:
            outputs = model.model(**inputs)
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            predicted_class = torch.argmax(probabilities, dim=-1).item()
            predicted_label = model.config.id2label[predicted_class]
            confidence = probabilities[0][predicted_class].item()
    
    return predicted_label, confidence

class PredictView(APIView):
    async def post(self, request, *args, **kwargs):
        audio_file = request.FILES.get("audio_file")
        if not audio_file:
            return JsonResponse({"error": "No audio file provided"}, status=400)

        try:
            text = await speech_to_text(audio_file)
        except Exception as e:
            return JsonResponse({"error": f"Failed to transcribe audio: {str(e)}"}, status=500)

        if not text:
            return JsonResponse({"error": "Failed to transcribe audio"}, status=500)

        # 두 모델의 예측을 병렬로 실행
        prediction1_task = asyncio.create_task(classify_text(text, model1.tokenizer, model1, model1.device))
        prediction2_task = asyncio.create_task(classify_text(text, model2.tokenizer, model2, model2.device, model2.inference_label_frequency))
        
        # 두 태스크가 모두 완료될 때까지 기다림
        (prediction1, confidence1), (prediction2, confidence2) = await asyncio.gather(prediction1_task, prediction2_task)

        return JsonResponse({
            "transcription": text,
            "prediction": prediction1,
            "confidence": float(confidence1),
            "prediction2": prediction2,
            "confidence2": float(confidence2),
        })
