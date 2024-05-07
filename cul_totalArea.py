# -*- coding: utf-8 -*-

import arcpy
import os

# Shapefile이 저장된 디렉토리 설정
input_directory = r"D:\GIS\pohang\pohang_e_JHJ"

# 디렉토리에서 모든 .shp 파일을 찾음
shapefiles = [os.path.join(input_directory, f) for f in os.listdir(input_directory) if f.endswith('.shp')]

for shp in shapefiles:
    # 'AREA' 필드가 이미 존재하는지 확인하고, 없으면 추가
    if len(arcpy.ListFields(shp, "AREA")) == 0:
        arcpy.AddField_management(shp, "AREA", "DOUBLE")

    # 각 파일의 총 면적을 저장할 변수
    file_total_area = 0

    # 각 피처의 면적을 계산하여 'AREA' 필드에 저장하고 총 면적 합산
    with arcpy.da.UpdateCursor(shp, ["SHAPE@AREA", "AREA"]) as cursor:
        for row in cursor:
            # SHAPE@AREA는 피처의 면적을 반환하는 토큰입니다.
            row[1] = row[0]
            file_total_area += row[0]  # 각 피처의 면적을 file_total_area에 합산
            cursor.updateRow(row)
    
    # m^2에서 km^2로 환산 (1 km^2 = 10^6 m^2)
    file_total_area_km2 = file_total_area / 10**6

    # 각 파일당 총 면적을 km^2 단위로 소수점 둘째자리까지 출력
    print("{} : {:.2f} km2".format(os.path.basename(shp), file_total_area_km2))

# N3L_F0010000 # 등고선
# N3P_F0020000 # 표고점
# N3A_B0010000 # 건물
# N3A_A0010000 # 도로
# N3A_B0010000 # 농경지

