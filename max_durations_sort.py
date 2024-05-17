import os

directory_path = r'C:\Program Files (x86)\환경부\RFAHD\conf\Data_Max'


def adjust_spacing(line, is_header=False):
    if is_header:
        return line

    parts = line.split()
    year = parts[0]
    hours = parts[1:]

    adjusted_hours = []
    for hour in hours:
        if '.' in hour:
            num = float(hour)
        else:
            num = int(hour)

        if num < 100:
            adjusted_hours.append(f"{' ' * 5}{hour}")
        else:
            adjusted_hours.append(f"{' ' * 4}{hour}")

    return f"{year} " + " ".join(adjusted_hours) + '\n'


def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    adjusted_lines = [adjust_spacing(lines[0], is_header=True)] + [adjust_spacing(line) for line in lines[1:]]

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(adjusted_lines)

    print(f"Adjusted file saved to: {file_path}")


# Process all .MAX1 files in the specified directory
for filename in os.listdir(directory_path):
    if filename.endswith('.MAX1'):
        file_path = os.path.join(directory_path, filename)
        process_file(file_path)
