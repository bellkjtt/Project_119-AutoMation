## Kakao 지도 API 활용, 신고 위치(주소, 장소) 추정 모듈 파일 ##

import requests
import os

# Kakao 지도 API 기반 주소 및 장소 추정
def get_address(location):
    
    try:
        # 장소 추정 단어 가져옴
        url = 'https://dapi.kakao.com/v2/local/search/keyword.json'
        params = {'query': location, 'page': 1}
        headers = {"Authorization": "KakaoAK " + os.getenv('KAKAO_API_KEY')}
        
        # 장소 documents 가져옴
        places = requests.get(url, params=params, headers=headers).json()['documents']
        address = places[0]
        
        context = {
            '추정 주소' : address['address_name'], 
            '추정 장소' : address['place_name'], 
            '추정 번호' : address['phone'],
            '위도' : address['y'],
            '경도' : address['x'],
        }

        return context
    
    except IndexError:
        return "Index_Error"

# get_address('마포구 마포대교')