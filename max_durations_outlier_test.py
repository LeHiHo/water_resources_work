from scipy.stats import t
import pandas as pd
import numpy as np

file_path = 'C:/Users/wkdgh/OneDrive/바탕 화면/RFAHD/20181289.csv'
new_data = pd.read_csv(file_path)


# 'Unnamed: 0' 열 제거
new_data_cleaned = new_data.drop(columns=['Unnamed: 0'])

# 기초 통계량 확인
print(new_data_cleaned.describe())




# Grubbs 검정을 수행하는 함수 정의
def grubbs_test(data, alpha=0.05):
    n = len(data)
    mean_x = np.mean(data)
    std_x = np.std(data, ddof=1)
    G = max(abs(data - mean_x)) / std_x
    t_dist = t.ppf(1 - alpha / (2 * n), n - 2)
    G_critical = ((n - 1) / np.sqrt(n)) * np.sqrt(t_dist**2 / (n - 2 + t_dist**2))
    return G, G_critical

# 각 시간별 데이터에 대해 Grubbs 검정 수행
grubbs_results = {}
for col in new_data_cleaned.columns:
    G, G_critical = grubbs_test(new_data_cleaned[col])
    is_outlier = G > G_critical
    grubbs_results[col] = (G, G_critical, is_outlier)

print(grubbs_results)