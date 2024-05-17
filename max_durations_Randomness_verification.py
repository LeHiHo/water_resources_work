import numpy as np
import pandas as pd
from scipy.stats import norm

# Load the uploaded file
file_path = 'C:/Program Files (x86)/환경부/RFAHD/conf/Data_Max/10074010.MAX1'

# Reading the data from the file with proper column names
data = pd.read_csv(file_path, delim_whitespace=True)


# Extracting all hourly data into a single series for analysis
data_values = data.iloc[:, 1:].values.flatten()


# Run Test
def run_test(data):
    median = np.median(data)
    runs, n1, n2 = 0, 0, 0
    # Determine the runs above and below the median
    for i in range(len(data)):
        if (data[i] >= median and i == 0) or (data[i] >= median and data[i-1] < median):
            runs += 1
            n1 += 1
        elif (data[i] < median and i == 0) or (data[i] < median and data[i-1] >= median):
            runs += 1
            n2 += 1
        elif data[i] >= median:
            n1 += 1
        else:
            n2 += 1

    runs_exp = ((2 * n1 * n2) / (n1 + n2)) + 1
    std_dev = np.sqrt((2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / (((n1 + n2) ** 2) * (n1 + n2 - 1)))

    z = (runs - runs_exp) / std_dev
    p_value = 2 * (1 - norm.cdf(abs(z)))

    return z, p_value

# Turning Point Test
def turning_point_test(data):
    n = len(data)
    t = 0
    for i in range(1, n-1):
        if (data[i] > data[i-1] and data[i] > data[i+1]) or (data[i] < data[i-1] and data[i] < data[i+1]):
            t += 1

    mean_t = 2 * (n - 2) / 3
    var_t = (16 * n - 29) / 90
    z = (t - mean_t) / np.sqrt(var_t)
    p_value = 2 * (1 - norm.cdf(abs(z)))

    return z, p_value

# Correlogram Test
def correlogram_test(data, lags=20):
    n = len(data)
    mean = np.mean(data)
    acf = np.correlate(data - mean, data - mean, mode='full') / np.var(data) / n
    acf = acf[n-1:]

    conf_interval = 1.96 / np.sqrt(n)

    significant_lags = np.where(np.abs(acf[1:lags+1]) > conf_interval)[0] + 1

    return acf, significant_lags

# Apply the tests
z_run, p_run = run_test(data_values)
z_turning, p_turning = turning_point_test(data_values)
acf, significant_lags = correlogram_test(data_values)

# Determine if the data is random based on the test results
run_test_is_random = (-1.96 <= z_run <= 1.96) and (p_run > 0.05)
turning_point_test_is_random = (-1.96 <= z_turning <= 1.96) and (p_turning > 0.05)
correlogram_test_is_random = len(significant_lags) == 0

# Print the results
run_test_result = f"Run Test: Z-value = {z_run}, P-value = {p_run}, Random if Z-value in [-1.96, 1.96] and P-value > 0.05"
turning_point_test_result = f"Turning Point Test: Z-value = {z_turning}, P-value = {p_turning}, Random if Z-value in [-1.96, 1.96] and P-value > 0.05"
correlogram_test_result = f"Correlogram Test: Significant lags = {significant_lags}, Random if no significant lags"

print(run_test_result)
print("Run Test - Random:", "Yes" if run_test_is_random else "No")

print(turning_point_test_result)
print("Turning Point Test - Random:", "Yes" if turning_point_test_is_random else "No")

print(correlogram_test_result)
print("Correlogram Test - Random:", "Yes" if correlogram_test_is_random else "No")