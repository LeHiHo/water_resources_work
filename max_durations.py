import os
import pandas as pd

######################################################################

directory = 'D:/RFAHD/지역빈도최신화(8,16)/rawdata/16/'

######################################################################

def calculate_adjustment_factor(duration):
    if duration <= 48:
        return 0.1346 * (duration ** -1.4170) + 1.0014
    else:
        return 1  # 48시간을 초과하는 경우 환산계수를 적용하지 않고 1을 반환


# 연도별 최대 지속 강우량 계산 함수
def process_file(file_path):
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    output_file_path = os.path.join(directory, f'{file_name}.csv')

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

    df = pd.DataFrame(data_list, columns=columns)
    rain_series = pd.Series(df.filter(regex='Hour_.*').values.flatten())
    extended_year_series = pd.Series(df['Year'].repeat(24).values)

    max_durations = pd.DataFrame(index=df['Year'].unique(), columns=[f'{i}-HR' for i in range(1, 73)])

    for year in df['Year'].unique():
        year_data = rain_series[extended_year_series == year]
        for duration in range(1, 73):
            adjustment_factor = calculate_adjustment_factor(duration)
            rolling_sum = year_data.rolling(window=duration).sum()
            max_rain = rolling_sum.max()
            adjusted_rain = round(max_rain * adjustment_factor, 1)
            max_durations.loc[year, f'{duration}-HR'] = adjusted_rain

    max_durations.to_csv(output_file_path, index=True, header=True)
    print(f"File saved as: {output_file_path}")


# 디렉토리 내의 모든 .txt 파일을 처리
for file in os.listdir(directory):
    if file.endswith('.txt'):
        file_path = os.path.join(directory, file)
        process_file(file_path)
