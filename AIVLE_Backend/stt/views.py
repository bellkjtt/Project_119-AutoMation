import asyncio
from asgiref.sync import sync_to_async
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from modules.gpt_text_processor import GPTProcessor
from modules.check_duplication import check_duplication   
from stt.models import CallLogs
import aiohttp
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session

processor = GPTProcessor()

# Clova Speech API 설정
client_id = os.environ.get('CLOVA_CLIENT_ID')
client_secret = os.environ.get('CLOVA_CLIENT_SECRET')
lang = "Kor"
url = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang=" + lang

async def async_recognize_speech(file):
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/octet-stream"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=file, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                text = result.get('text', 'No text recognized')
                if text:
                    processor.record += text + " "
                    result, context = await sync_to_async(processor.text_preprocessor)(text)
                    return [result, context]
            else:
                error_text = await response.text()
                print(f"Error: {error_text}")
                return "음성 인식 중 오류가 발생했습니다."

async def get_or_create_session(request):
    session_key = request.COOKIES.get('sessionid')
    if not session_key:
        session = await sync_to_async(SessionStore)()
        await sync_to_async(session.create)()
    else:
        session = await sync_to_async(SessionStore)(session_key)
    return session

@sync_to_async
def save_call_log(data):
    log = CallLogs(**data)
    log.save()
    return log.id

@method_decorator(csrf_exempt, name='dispatch')
class ProcessAudioView(View):
    async def post(self, request, *args, **kwargs):
        session = await get_or_create_session(request)
        audio_file = request.FILES.get('audio')
        
        if not audio_file:
            return JsonResponse({"error": "No audio file provided."}, status=400)

        result = await async_recognize_speech(audio_file)
        if isinstance(result, list):
            text, context = result
            if text == '신고가 접수되었습니다.':
                # 세션에서 이전 대화 내용 가져오기
                previous_conversation = await sync_to_async(session.get)('conversation', '')
                full_conversation = previous_conversation + processor.record

                # 예측 API 호출 (비동기로 변경)
                async with aiohttp.ClientSession() as aio_session:
                    async with aio_session.post('http://127.0.0.1:8000/api/predict/', data={"full_text": full_conversation}) as resp:
                        prediction_data = await resp.json()
                        prediction = prediction_data.get('prediction')
                        prediction2 = prediction_data.get('prediction2')

                is_duplicate = await sync_to_async(check_duplication)(context, prediction)

                log_data = {
                    'category': prediction,
                    'location': context['사건 발생 장소'],
                    'details': context['구체적인 현장 상태'],
                    'address_name': context['추정 주소'],
                    'place_name': context['추정 장소'],
                    'phone_number': context['추정 번호'],
                    'lat': context['위도'],
                    'lng': context['경도'],
                    'full_text': full_conversation,
                    'is_duplicate': is_duplicate,
                    'emergency_type': prediction2,
                    'jurisdiction': prediction
                }

                log_id = await save_call_log(log_data)

                # 세션에 대화 내용 저장
                await sync_to_async(session.__setitem__)('conversation', full_conversation)
                await sync_to_async(session.save)()

                processor.record = ''
                response = JsonResponse({"message": "신고가 접수되었습니다." if not is_duplicate else "이미 접수된 신고입니다.", "log_id": log_id}, status=200)
                response.set_cookie('sessionid', session.session_key)
                return response
            
            # 세션에 대화 내용 추가
            previous_conversation = await sync_to_async(session.get)('conversation', '')
            await sync_to_async(session.__setitem__)('conversation', previous_conversation + processor.record)
            await sync_to_async(session.save)()

            response = JsonResponse({"message": text}, status=200)
            response.set_cookie('sessionid', session.session_key)
            return response
        
        response = JsonResponse({"message": result}, status=200)
        response.set_cookie('sessionid', session.session_key)
        return response

@method_decorator(csrf_exempt, name='dispatch')
class FullAudioView(View):
    async def post(self, request, *args, **kwargs):
        session = await get_or_create_session(request)
        log_id = request.POST.get('log_id')
        file_path = request.POST.get('file_path')
        
        if log_id and file_path:
            try:
                log = await sync_to_async(CallLogs.objects.get)(id=log_id)
                log.audio_file = file_path
                await sync_to_async(log.save)()

                # 세션에서 대화 내용 초기화
                await sync_to_async(session.__setitem__)('conversation', '')
                await sync_to_async(session.save)()

                response = JsonResponse({'message': 'CallLogs 업데이트 완료'}, status=200)
                response.set_cookie('sessionid', session.session_key)
                return response
            except CallLogs.DoesNotExist:
                return JsonResponse({'error': '해당 log_id를 찾을 수 없습니다.'}, status=404)
        else:
            return JsonResponse({'error': 'log_id와 file_path가 필요합니다.'}, status=400)
