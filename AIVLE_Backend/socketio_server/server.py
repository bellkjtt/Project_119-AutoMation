import socketio
import eventlet
import os
from datetime import datetime
import requests

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

UPLOAD_FOLDER = 'media/uploads'
UPLOAD_FOLDER_FULL = 'media/full_audio'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_FULL, exist_ok=True)

# 모든 위치 데이터를 저장할 리스트
all_locations = []

@sio.event
def connect(sid, environ):
    print("연결됨", sid)

@sio.event
def disconnect(sid):
    print("연결 끊김", sid)

@sio.event
def audio_data(sid, data):
    print("파일 전송됨")
    
    filename = datetime.now().strftime('%Y%m%d%H%M%S') + '.wav'
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    with open(file_path, 'wb') as f:
        f.write(data)
    print("파일 저장 완료:", file_path)
    
    with open(file_path, 'rb') as fp:
        files = {'audio': fp}
        print("view 호출")
        try:
            response = requests.post('http://backend:8000/stt/process_audio/', files=files)
        except Exception as e:
            print("Django 뷰 호출 중 예외 발생:", str(e))
            return
    
        print(response.status_code)
        print(response.json())
        
        if response.status_code == 200:
            response_data = response.json()
            recognized_text = response_data.get('message', 'No text recognized')
            log_id = response_data.get('log_id', None)
            latitude = response_data.get('latitude', 0)
            longtitue = response_data.get('longtitue', 0)
            place = response_data.get('place', None)
            
            if recognized_text!=None:
                sio.emit('audio_text', {
                    'message': recognized_text,
                    'log_id': log_id
                }, to=sid)
            
            if latitude !=0 or longtitue!=0:
                # 새 위치 정보를 리스트에 추가
                all_locations.append({
                    'lat': latitude,
                    'lng': longtitue,
                    'name': 'New Report',
                    'place': place,
                    'description': recognized_text
                })
        else:
            message = 'Django 뷰 호출 실패'
            sio.emit('audio_text', {'message': message}, to=sid)
            print('Django 뷰 호출 실패')
@sio.event
def request_initial_locations(sid):
    sio.emit('locations_update', all_locations, to=sid)

@sio.event
def request_locations(sid):
    sio.emit('locations_update', all_locations, to=sid)

@sio.event
def audio_full(sid, data):
    print("파일 전송됨")
    
    # 파일과 로그 ID 추출
    if isinstance(data, dict) and 'wav' in data and 'log_id' in data:
        audio_data = data['wav']
        log_id = data['log_id']
        
        # 파일 저장
        filename = datetime.now().strftime('%Y%m%d%H%M%S') + '.wav'
        file_path = os.path.join(UPLOAD_FOLDER_FULL, filename)
        
        if isinstance(audio_data, bytes):
            with open(file_path, 'wb') as f:
                f.write(audio_data)
            print("오디오 파일 저장 완료:", file_path)
            
            # CallLogs 업데이트
            payload = {'log_id': log_id, 'file_path': file_path}
            print(f"Sending payload: {payload}")
            response = requests.post('http://127.0.0.1:8000/stt/full_audio/', data=payload)
            
            if response.status_code == 200:
                print("CallLogs 업데이트 완료:", log_id)
            else:
                try:
                    error_response = response.json()
                except ValueError:
                    error_response = response.text
                print(f"오류 발생: {response.status_code}, {error_response}")


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)