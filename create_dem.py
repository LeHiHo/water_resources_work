# -*- coding: utf-8 -*-
"""
2024-04-26 v1 Jang - 프로토타입
2024-05-02 v2 Jang - 상위폴더 생성
2024-05-03 v2 Jang - 파일명 전처리 기능 추가
"""

import arcpy
import sys
import os
import zipfile

##################################################################

directory_name = 'gs_5'# 최상위 폴더명`
directory_zip_path = 'D:/수치지도/연습2' ## 압축파일이 있는 폴더
cell_size = 5 # 레스터파일 CELLSIZE 결정

###############################################################

reload(sys)
sys.setdefaultencoding('utf8')

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_unique_directory(base_path):
    if not os.path.exists(base_path):
        os.makedirs(base_path)
        return base_path.replace('\\', '/')
    else:
        counter = 1
        while True:
            new_path = u"{}-{}".format(base_path, counter)
            if not os.path.exists(new_path):
                os.makedirs(new_path)
                return new_path.replace('\\', '/')
            counter += 1

def preprocess_file_name(file_name):
    prefix_map = {
        'F0010000': 'N3L_F0010000',
        'F0020000': 'N3P_F0020000',
        'B0010000': 'N3A_B0010000',
        'A0010000': 'N3A_A0010000'
    }
    return prefix_map.get(file_name, file_name)

def extract_files_from_zip(zip_file, data_path, target_files, index):
    extracted_files = {}
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        for raw_file in zip_ref.namelist():
            base_file_name, file_extension = os.path.splitext(os.path.basename(raw_file))
            processed_file_name = preprocess_file_name(base_file_name)
            for target_file, display_name in target_files.items():
                if processed_file_name == target_file:
                    new_filename = os.path.join(data_path, "{}_{}{}".format(index, target_file, file_extension)).replace('\\', '/')
                    with zip_ref.open(raw_file, 'r') as file_data, open(new_filename, 'wb') as new_file:
                        new_file.write(file_data.read())
                    if target_file not in extracted_files:
                        extracted_files[target_file] = []
                    extracted_files[target_file].append(new_filename)
    return extracted_files



def merge_shp(files, merge_path, pattern_name):
    merged_output = os.path.join(merge_path, "{}_merged.shp".format(pattern_name)).replace('\\', '/')
    if os.path.exists(merged_output):
        os.remove(merged_output)
    arcpy.Merge_management(inputs=files, output=merged_output)

def create_tin(tin_path, in_features, constrained_delaunay="CONSTRAINED_DELAUNAY"):
    in_features_modify = os.path.join(in_features).replace('\\', '/')
    if os.path.exists(tin_path):
        os.remove(tin_path)
    arcpy.CreateTin_3d(out_tin=tin_path, in_features=in_features_modify, constrained_delaunay=constrained_delaunay)
    print ('Tin 생성')

def raster_to_acsii(raster_path, ascii_path):
    ascii_output = os.path.join(ascii_path, 'ascii.asc').replace('\\', '/')
    if os.path.exists(ascii_output):
        os.remove(ascii_output)
    arcpy.RasterToASCII_conversion(in_raster=raster_path, out_ascii_file=ascii_output)
    print ('Ascii 생성')

def tinToRaster_AND_RasterToAscii(tin_path, raster_path, ascii_path):
    raster_output = os.path.join(raster_path, 'raster.tif').replace('\\', '/')
    if os.path.exists(raster_output):
        os.remove(raster_output)
    arcpy.TinRaster_3d(in_tin=tin_path, out_raster=raster_output, sample_distance='CELLSIZE {}'.format(cell_size))
    print ('Raster 생성')

    raster_to_acsii(raster_output, ascii_path)

def main(source_directory, target_files=None):
    arcpy.env.workspace = source_directory
    data_path = os.path.join(source_directory, 'data').replace('\\', '/')
    merge_path = os.path.join(source_directory, 'merge').replace('\\', '/')
    tin_path = os.path.join(source_directory, 'tin').replace('\\', '/')
    raster_path = os.path.join(source_directory, 'raster').replace('\\', '/')
    ascii_path = os.path.join(source_directory, 'ascii').replace('\\', '/')

    create_directory(data_path)
    create_directory(merge_path)
    create_directory(raster_path)
    create_directory(ascii_path)
    print ('폴더 생성')


    if target_files is None:
        target_files = {
            'N3L_F0010000': 'contours',
            'N3P_F0020000': 'elevation_points',
            'N3A_B0010000': 'buildings',
            'N3A_A0010000': 'roads'
        }

    pattern_files = {key: [] for key in target_files.keys()}
    zip_files = [os.path.join(directory_zip_path, f) for f in os.listdir(directory_zip_path) if f.endswith('.zip')]
    for index, zip_file in enumerate(zip_files, start=1):
        extracted_files = extract_files_from_zip(zip_file, data_path, target_files, index)
        for key, files in extracted_files.items():
            pattern_files[key].extend(files)

    for target_file, files in pattern_files.items():
        shp_files = [f for f in files if f.endswith('.shp')]
        merge_shp(shp_files, merge_path, target_files[target_file])
    print ('merge 완료')

    in_features = "{0} 등고수치 Hard_Line; {1} 수치 Mass_Points".format(
        os.path.join(merge_path, "contours_merged.shp"),
        os.path.join(merge_path, "elevation_points_merged.shp")
    )

    create_tin(tin_path, in_features)
    tinToRaster_AND_RasterToAscii(tin_path, raster_path, ascii_path)
    print ('작업완료')

if __name__ == "__main__":
    if not isinstance(directory_zip_path, unicode):
        directory_zip_path = directory_zip_path.decode('utf-8')
    if not isinstance(directory_name, unicode):
        directory_name = directory_name.decode('utf-8')

    base_path = os.path.join(directory_zip_path, directory_name)
    unique_directory_path = create_unique_directory(base_path)

    main(unique_directory_path)
