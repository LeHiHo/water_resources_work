import pandas as pd

file_name = 'test.txt'

# 파일 경로 설정
file_path = f'C:/Users/wkdgh/OneDrive/바탕 화면/{file_name}'

def calculate_adjustment_factor(duration):
    if duration <= 48:
        return 0.1346 * (duration ** -1.4170) + 1.0014
    else:
        return 1  # 48시간을 초과하는 경우 환산계수를 적용하지 않고 1을 반환

# 데이터를 읽어 들임
columns = ['Year', 'Month', 'Day'] + [f'Hour_{i + 1}' for i in range(24)]
data_list = []
with open(file_path, 'r') as file:
    for line in file:
        date_part, rain_part = line[:9], line[10:]
        year = int(date_part[:4])
        month = int(date_part[4:6])
        day = int(date_part[6:])
        rain_data = list(map(float, rain_part.split()))
        data_list.append([year, month, day] + rain_data)

# 데이터 프레임 생성
df = pd.DataFrame(data_list, columns=columns)

# 강우량 데이터만 추출 및 시간별 데이터를 하나의 긴 시리즈로 변환
rain_series = pd.Series(df.filter(regex='Hour_.*').values.flatten())

# 연도 정보 확장
extended_year_series = pd.Series(df['Year'].repeat(24).values)

# 연도별 최대 지속 강우량 계산
max_durations = pd.DataFrame(index=df['Year'].unique(), columns=[f'{i}-HR' for i in range(1, 73)])

for year in df['Year'].unique():
    year_data = rain_series[extended_year_series == year]
    for duration in range(1, 73):
        adjustment_factor = calculate_adjustment_factor(duration)
        # 롤링 합계 계산
        rolling_sum = year_data.rolling(window=duration).sum()
        max_rain = rolling_sum.max()
        adjusted_rain = round(max_rain * adjustment_factor,1)
        max_durations.loc[year, f'{duration}-HR'] = adjusted_rain

# CSV 파일로 저장
output_file_path = f'C:/Users/wkdgh/OneDrive/바탕 화면/{file_name}_max_durations.csv'
max_durations.to_csv(output_file_path, index=True, header=True)

print(f"File saved as: {output_file_path}")
