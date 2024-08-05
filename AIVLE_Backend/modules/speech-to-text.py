# ETRI의 STT API 활용 신고 음성 Text 변환 모듈 파일 ##

import urllib3
import json
import base64
    
# STT API를 활용해 신고 전화 음성 -> Text로 변환
def voice_stt():

    openApiURL = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"        # 음성 인식 API 주소
    apiKey = "d6dec6aa-41bf-48c4-9b3a-acbd97a70b3e"                         # API 키
    language = "korean"                                                     # 언어

    audioPath = "t.wav"                                                 # 음성 파일

    # 음성 파일 압축 (인코딩)
    file = open(audioPath, "rb")
    audioContents = base64.b64encode(file.read()).decode("utf8")
    file.close()

    # 요청 형식 (언어, 음성)
    requestJson = {    
        "argument": {
            "language_code": language,
            "audio": audioContents
        }
    }

    # HttpRequest 요청 (응답)
    http = urllib3.PoolManager()
    response = http.request(
        "POST",
        openApiURL,
        headers={"Content-Type": "application/json; charset=UTF-8","Authorization": apiKey},
        body=json.dumps(requestJson)
    )

    # Text 파일 복호화
    data = json.loads(response.data.decode("utf-8", errors='ignore'))
    
    # 복호화된 Text 파일 Return
    return data['return_object']['recognized']