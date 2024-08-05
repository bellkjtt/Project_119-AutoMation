import os
import requests
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from modules.gpt_text_processor import GPTProcessor
from modules.check_duplication import check_duplication   
import socketio
from django.shortcuts import get_object_or_404
from stt.models import CallLogs

# 네이버 클로바 스피치 API 설정
client_id = "etu7ckegx5"
client_secret = "4WtVsc9mDlMZJmsrswHcZIaOlW2Fz200DMAmEFvO"
lang = "Kor"
url = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang=" + lang

text = ''
full_text = ''
processor = GPTProcessor()
sio = socketio.Server(cors_allowed_origins='*')
                    
# 음성파일 클로바 API로 보내서 텍스트 받아옴
def recognize_speech(file):
    global text, full_text
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/octet-stream"
    }
    response = requests.post(url, data=file, headers=headers)
    rescode = response.status_code
    if rescode == 200:
        text = response.json().get('text', 'No text recognized')
        if text != '':
            full_text += text + " "
            result, context = processor.text_preprocessor(text)
            if result == '신고가 접수되었습니다.':
                prediction_response = requests.post('http://127.0.0.1:8000/api/predict/', data={"full_text": full_text})
                prediction = prediction_response.json().get('prediction', None)
                prediction2 = prediction_response.json().get('prediction2', None)
            # 중복 신고 여부 확인
                is_duplicate = check_duplication(context,prediction)
            
                # 중복이 아닌 신고
                if not is_duplicate:
                    print('신고가 접수되었습니다.')
                    log = CallLogs(

                            category=prediction,
                            location=context['사건 발생 장소'],
                            details=context['구체적인 현장 상태'],
                            address_name=context['추정 주소'],
                            place_name=context['추정 장소'],
                            phone_number=context['추정 번호'],
                            lat = context['위도'],
                            lng = context['경도'],
                            full_text=processor.record,
                            is_duplicate=False,
                            emergency_type=prediction2,
                            jurisdiction=prediction
                        )
                    log.save()

                    processor.record = ''
                    return [result, log.id]    
                    
                elif is_duplicate:
                
                    log = CallLogs(
                        category=prediction,
                        location=context['사건 발생 장소'],
                        details=context['구체적인 현장 상태'],
                        address_name=context['추정 주소'],
                        place_name=context['추정 장소'],
                        phone_number=context['추정 번호'],
                        lat = context['위도'],
                        lng = context['경도'],
                        full_text=processor.record,
                        is_duplicate=True,
                        emergency_type=prediction2,
                    )
                    log.save()

                    processor.record = ''
                    result = '이미 접수된 신고입니다.'
                    return [result, log.id]  
            elif result == 'GPT API 오작동 (다시 한번 말씀해주세요)':
                processor.record = ''
                return result
            else:
                return result
    else:
        print({"Error:" : response.text})

@method_decorator(csrf_exempt, name='dispatch')
class ProcessAudioView(View):
    def post(self, request, *args, **kwargs):
        global full_text
        audio_file = request.FILES.get('audio')
        
        if not audio_file:
            return JsonResponse({"error": "No audio file provided."}, status=400)

        result = recognize_speech(audio_file)
        if type(result) == list:
            return JsonResponse({"message" : result[0], "log_id" : result[1]}, status=200)
        return JsonResponse({"message" : result}, status=200)
    
@method_decorator(csrf_exempt, name='dispatch')
class FullAudioView(View):
    def post(self, request, *args, **kwargs):
        log_id = request.POST.get('log_id')
        file_path = request.POST.get('file_path')
        
        print(f"Received log_id: {log_id}, file_path: {file_path}")
        
        if log_id and file_path:
            # CallLogs 업데이트
            try:
                log = CallLogs.objects.get(id=log_id)
                log.audio_file = file_path
                log.save()
                print("CallLogs 업데이트 완료:", log_id)
                return JsonResponse({'message': 'CallLogs 업데이트 완료'}, status=200)
            except CallLogs.DoesNotExist:
                return JsonResponse({'error': '해당 log_id를 찾을 수 없습니다.'}, status=404)
        else:
            return JsonResponse({'error': 'log_id와 file_path가 필요합니다.'}, status=400)
