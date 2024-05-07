import os
import requests

# 지정된 경로 설정
directory = r'D:\RFAHD\연최대강우량 산정 프로그램\01_Raw'

# # 지정된 경로에서 파일 목록 가져오기
# files = os.listdir(directory)
# modified_files = set(file.replace('.DAT', '') for file in files)  # 파일 확장자 제거 후 set으로 변환

# API URL
url = "http://www.wamis.go.kr:8080/wamis/openapi/wkw/rf_dubrfobs?oper=y"

# API 요청을 보내고 응답 받기
response = requests.get(url)
data = response.json()  # 응답을 JSON 형태로 변환

# 'list' 키에 해당하는 데이터에서 'obscd' 값만 추출
obs_codes = set(item['obscd'] for item in data['list'])  # obscd 값을 set으로 변환


# # modified_files에 없는 obs_codes의 값 추출
# missing_obs_codes = obs_codes - modified_files
#
# print(missing_obs_codes)  # 결과를 리스트로 변환하여 출력

open_dates = {}

# 각 관측소 코드에 대해 API를 호출하고 개시일을 추출
for obs_code in obs_codes:
    url = f"http://www.wamis.go.kr:8080/wamis/openapi/wkw/rf_obsinfo?obscd={obs_code}"
    response = requests.get(url)
    if response.status_code == 200:
        # JSON 응답 파싱
        data = response.json()
        # 'list' 요소 찾기
        list_element = data.get('list', [])
        if list_element:
            opendt = list_element[0].get('opendt', '자료없음')  # 첫 번째 'list' 요소에서 'opendt' 값을 가져옴
            print(opendt, obs_code)
            open_dates[obs_code] = opendt
        else:
            open_dates[obs_code] = "자료없음"
    else:
        open_dates[obs_code] = "API 요청 실패"

# 결과 출력
