import os
import requests
from collections import defaultdict
from datetime import datetime, timedelta

####################################################

directory = r'D:\RFAHD\지역빈도최신화(8,16)\rawdata\16'
start_date = datetime(2018, 1, 1)
obscd = '20184140'

####################################################

def query_rainfall(start_date, end_date):
    url = "http://www.wamis.go.kr:8080/wamis/openapi/wkw/rf_hrdata"
    params = {
        'obscd': obscd, # 관측소 코드
        'startdt': start_date.strftime('%Y%m%d'),  # 시작 날짜
        'enddt': end_date.strftime('%Y%m%d')  # 종료 날짜
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()  # 응답을 JSON으로 파싱
    else:
        print(f"Failed to retrieve data, status code: {response.status_code}, from {start_date} to {end_date}")
        return None

def format_rainfall(rain):
    if rain < 1:
        # 1 미만의 값에서는 소수점 앞의 0을 제거하여 포맷팅
        formatted = f"{rain:.1f}".lstrip('0')
    else:
        # 1 이상의 값은 소수점 첫째 자리까지 정상적으로 표시
        formatted = f"{rain:.1f}"
    # 생성된 문자열을 우측 정렬하여 전체 길이를 6칸으로 맞춤
    return f"{formatted:>6}"

def find_negative_rainfall(rainfall_data):
    negative_dates = []
    for date, hours in rainfall_data.items():
        for hour, rain in hours.items():
            if rain < 0:
                negative_dates.append(date)
                break  # 한 날짜에 한 번만 추가
    return negative_dates

def save_to_file(data, file_path):
    with open(file_path, 'w') as file:
        file.write(data)

# 날짜 범위 설정

current_date = datetime.now() - timedelta(days=1)
delta_six_months = timedelta(days=180)  # 대략 6개월

# 데이터 파싱 및 출력 구조
rainfall_data = defaultdict(lambda: defaultdict(float))

while start_date < current_date:
    end_date = min(start_date + delta_six_months, current_date)  # 종료 날짜 설정
    data = query_rainfall(start_date, end_date)
    if data:
        for item in data.get('list', []):
            ymdh = item['ymdh']
            rf = float(item['rf'])
            date, hour = ymdh[:8], ymdh[8:]
            rainfall_data[date][hour] = rf
    start_date = end_date + timedelta(days=1)  # 다음 기간 시작일은 이전 종료일 다음날


negative_dates = find_negative_rainfall(rainfall_data)
formatted_output = []

if negative_dates:
    print("Dates with negative rainfall values:", negative_dates)
else:
    print("No negative rainfall values found.")

# 결과 출력
for date, hours in sorted(rainfall_data.items()):
    year = date[:4]
    month = date[4:6]
    day = date[6:]
    month = month.lstrip('0') if month.startswith('0') else month
    day = day.lstrip('0') if day.startswith('0') else day
    if len(month) == 2 and len(day) == 2:
        formatted_date = f"{year}{month}{day}"
    elif len(month) == 1 and len(day) == 2:
        formatted_date = f"{year} {month}{day}"
    elif len(month) == 2 and len(day ) == 1:
        formatted_date = f"{year}{month} {day}"
    else:
        formatted_date = f"{year} {month} {day}"

    # hour_rainfalls = [hours[str(h).zfill(2)] for h in range(1, 25)]
    # print(f"{formatted_date: <8}" + ''.join(format_rainfall(rain) for rain in hour_rainfalls))

    hour_rainfalls = [format_rainfall(hours[str(h).zfill(2)]) for h in range(1, 25)]
    formatted_output.append(f"{formatted_date: <8}" + ''.join(hour_rainfalls))

file_path = os.path.join(directory, f'{obscd}.txt')
save_to_file('\n'.join(formatted_output), file_path)
print(f"Data saved to {file_path}")