import os
import requests
import pandas as pd
from pyproj import Proj, Transformer

def is_dms_format(value):
    return '-' in value

def dms_to_dd(dms):
    parts = dms.split('-')
    dd = float(parts[0]) + float(parts[1])/60 + float(parts[2])/3600
    return dd

def latlon_to_utm(lat, lon):
    # Transformer 객체 생성: WGS 84에서 UTM(zone 52N)으로 변환
    transformer = Transformer.from_crs('epsg:4326', 'epsg:5186', always_xy=True)
    x, y = transformer.transform(lon, lat)
    return x, y

# 도-분-초 변환 함수
def decimal_to_dms(decimal):
    degrees = int(decimal)
    remainder = abs(decimal - degrees)
    minutes = int(remainder * 60)
    seconds = int((remainder * 3600) - (minutes * 60))
    return f"{degrees}-{minutes}-{seconds}"

# 지정된 경로 설정
search_directory = r'C:/Program Files (x86)/환경부/RFAHD/conf/Data_Max/'

# 지정된 경로에서 파일 목록 가져오기
files = os.listdir(search_directory)
modified_files = set(file.replace('.MAX1', '') for file in files)  # 파일 확장자 제거 후 set으로 변환

# API URL
url = "http://www.wamis.go.kr:8080/wamis/openapi/wkw/rf_dubrfobs?oper=y"

# API 요청을 보내고 응답 받기
response = requests.get(url)
data = response.json()  # 응답을 JSON 형태로 변환

# 'list' 키에 해당하는 데이터에서 'obscd' 값만 추출
obs_codes = set(item['obscd'] for item in data['list'])  # obscd 값을 set으로 변환

# modified_files에 없는 obs_codes의 값 추출
missing_obs_codes = obs_codes - modified_files

open_dates = []
columns = ['지점코드', '대유역', '지점명', '관할기관', '경도', '위도', 'X', 'Y']

# 각 관측소 코드에 대해 API를 호출하고 필요한 정보를 추출하는 부분
for obs_code in missing_obs_codes:
    url = f"http://www.wamis.go.kr:8080/wamis/openapi/wkw/rf_obsinfo?obscd={obs_code}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        list_element = data.get('list', [])
        if list_element:
            obs_item = list_element[0]
            지점코드 = obs_item.get('obscd', '')
            대유역 = obs_item.get('bbsnnm', '')
            지점명 = obs_item.get('obsnm', '')
            관할기관 = obs_item.get('mngorg', '')
            경도_raw = obs_item.get('lon', '0')
            위도_raw = obs_item.get('lat', '0')

            경도 = 경도_raw if is_dms_format(경도_raw) else decimal_to_dms(float(경도_raw))
            위도 = 위도_raw if is_dms_format(위도_raw) else decimal_to_dms(float(위도_raw))

            경도_dd = dms_to_dd(경도)
            위도_dd = dms_to_dd(위도)

            x, y = latlon_to_utm(위도_dd, 경도_dd)

            open_dates.append({
                '지점코드': 지점코드,
                '대유역': 대유역,
                '지점명': 지점명,
                '관할기관': 관할기관,
                '경도': 경도,
                '위도': 위도,
                'X': x,
                'Y': y
            })

# 데이터프레임 생성
df = pd.DataFrame(open_dates, columns=columns)

# 저장할 파일명 지정
output_filename = 'output_data.csv'

# 데이터프레임을 CSV 파일로 저장
df.to_csv(output_filename, index=False, encoding='utf-8-sig')

print(f"CSV 파일이 저장되었습니다: {output_filename}")
