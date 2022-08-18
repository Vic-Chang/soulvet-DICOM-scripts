import datetime
import io
import os.path
import shutil
import requests
import dicom2jpg
import glob
import argparse
from pathlib import Path
from enum import Flag
from PIL import Image
from urllib import parse
from pydicom import dcmread
from pydicom.pixel_data_handlers.util import convert_color_space


class DicomType(Flag):
    """
    Dicom image type
    US: Ultrasound Image
    USM: Ultrasound Multi frame Image
    CR: Computed Radiography Image
    """
    US = '1.2.840.10008.5.1.4.1.1.6.1'
    USM = '1.2.840.10008.5.1.4.1.1.3.1'
    CR = '1.2.840.10008.5.1.4.1.1.1'


def download_dcm(img_url: str):
    """
    Download the source of dicom file and convert it to jpg or gif file ( Determined by dicom file type )
    :param img_url: Dicom file url
    :return: Save source of dicom and save as jpg or gif file
    """
    # Save dicom file to memory
    file_name = parse.parse_qs(parse.urlparse(img_url).query)['image'][0]
    dcm_file = f'{file_name}.dcm'
    results = requests.get(img_url)
    memory_dicom_file = io.BytesIO()
    memory_dicom_file.write(results.content)
    memory_dicom_file.seek(0)

    # Read dicom tag
    dicom_type = dcmread(memory_dicom_file).SOPClassUID

    export_path = 'Results'
    # Check dicom type, ultrasound or CR image
    if dicom_type == DicomType.CR.value:
        # `CR image`

        # Save dicom file to local from memory
        export_path = os.path.join(export_path, 'CR')
        source_export_path = os.path.join(export_path, 'Source')
        Path(source_export_path).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(source_export_path, dcm_file), 'wb') as f:
            f.write(memory_dicom_file.getvalue())

        # Convert dicom to jpg
        dicom2jpg.dicom2jpg(source_export_path)

        # Move jpg file to outer path and rename jpg file
        folder_name = datetime.datetime.now().strftime('%Y%m%d')
        all_jpg_files = glob.glob(f'{os.path.join(export_path, folder_name)}/**/*.jpg', recursive=True)
        for jpg_file in all_jpg_files:
            shutil.move(jpg_file, os.path.join(export_path, f'{file_name}.jpg'))

        # Remove empty folder
        shutil.rmtree(os.path.join(export_path, folder_name), ignore_errors=True)

        with open(os.path.join(export_path, f'{file_name}.txt'), 'w', encoding='utf-8') as f:
            ds = dcmread(os.path.join(source_export_path, dcm_file))
            tag_hospital = ds[0x0009, 0x1080].value
            f.write('醫院名稱: ' + str(tag_hospital) + '\n')
            print('醫院名稱: ', tag_hospital)

            tag_datetime = datetime.datetime.strptime((ds.ContentDate + ds.ContentTime), '%Y%m%d%H%M%S.%f')
            f.write('拍攝時間: ' + datetime.datetime.strftime(tag_datetime, '%Y/%m/%d %H:%M:%S') + '\n')
            print('拍攝時間: ', tag_datetime)

            tag_modality = ds.Modality
            f.write('拍攝類型: ' + str(tag_modality) + '\n')
            print('拍攝類型: ', tag_modality)

            tag_patient_name = ds.PatientName
            f.write('名稱: ' + str(tag_patient_name) + '\n')
            print('名稱: ', tag_patient_name)

            tag_patient_sex = ds.PatientSex
            f.write('性別: ' + str(tag_patient_sex) + '\n')
            print('性別: ', tag_patient_sex)

            tag_patient_phone_number = ds.PatientID
            f.write('手機: ' + str(tag_patient_phone_number) + '\n')
            print('手機: ', tag_patient_phone_number)

            tag_body_part_examined = ds.BodyPartExamined
            f.write('檢查部位: ' + str(tag_body_part_examined) + '\n')
            print('檢查部位: ', tag_body_part_examined)

            tag_device_description = ds.AcquisitionDeviceProcessingDescription
            f.write('裝置處理描述: ' + str(tag_device_description) + '\n')
            print('裝置處理描述: ', tag_device_description)

            tag_menu_name = ds[0x0019, 0x1032].value
            f.write('照片名稱: ' + str(tag_menu_name) + '\n')
            print('照片名稱: ', tag_menu_name)

            tag_image_type = ds[0x0019, 0x1040].value
            f.write('照片類型: ' + str(tag_image_type) + '\n')
            print('照片類型: ', tag_image_type)

            tag_film_annotation = ds[0x0019, 0x1090].value
            f.write('註記: ' + str(tag_film_annotation) + '\n')
            print('註記: ', tag_film_annotation)

            tag_rows = ds.Rows
            f.write('圖片高度: ' + str(tag_rows) + '\n')
            print('圖片高度: ', tag_rows)

            tag_columns = ds.Columns
            f.write('圖片寬度: ' + str(tag_columns) + '\n')
            print('圖片寬度: ', tag_columns)
    else:
        # `Ultrasound Image`

        # Save dicom file to local from memory
        export_path = os.path.join(export_path, 'US')
        source_export_path = os.path.join(export_path, 'Source')
        Path(source_export_path).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(source_export_path, dcm_file), 'wb') as f:
            f.write(memory_dicom_file.getvalue())

        ds = dcmread(os.path.join(source_export_path, dcm_file))

        # Check ultrasound type, ultrasound image or multiple frame image
        if dicom_type == DicomType.USM.value:
            # `Ultrasound Multi frame Image Storage`

            temp_frames_folder = 'temp'
            if os.path.exists(temp_frames_folder):
                shutil.rmtree(temp_frames_folder, ignore_errors=True)
            os.mkdir(temp_frames_folder)

            # Extract and save all frames from dicom
            for counter, image_pixel_array in enumerate(ds.pixel_array):
                # Convert color `YBR_FULL_422` to `RGB`, or image color will be weird
                pixel_array = convert_color_space(image_pixel_array, 'YBR_FULL_422', 'RGB')
                image = Image.fromarray(pixel_array)
                image.save(os.path.join(temp_frames_folder, f'img_{counter:03n}.png'))

            # Collect all photos ( frames )
            frames = []
            frame_photos = glob.glob(f'{temp_frames_folder}/*.png')
            for frame in frame_photos:
                new_frame = Image.open(frame)
                frames.append(new_frame)

            frame_time = ds.FrameTime

            # Convert all photos into gif, `append_images` must start from second or the first photo will be repeated
            # twice
            frames[0].save(os.path.join(export_path, f'{file_name}.gif'), format='GIF', append_images=frames[1:],
                           save_all=True, duration=frame_time, loop=0)

            # Remove temp photos
            shutil.rmtree(temp_frames_folder, ignore_errors=True)

        elif dicom_type == DicomType.US.value:
            # `Ultrasound Image Storage`

            pixel_array = convert_color_space(ds.pixel_array, 'YBR_FULL_422', 'RGB')
            image = Image.fromarray(pixel_array)
            image.save(os.path.join(export_path, f'{file_name}.png'))

        with open(os.path.join(export_path, f'{file_name}.txt'), 'w', encoding='utf-8') as f:
            tag_datetime = datetime.datetime.strptime((ds.ContentDate + ds.ContentTime), '%Y%m%d%H%M%S')
            f.write('拍攝時間: ' + datetime.datetime.strftime(tag_datetime, '%Y/%m/%d %H:%M:%S') + '\n')
            print('拍攝時間: ', tag_datetime)

            tag_modality = ds.Modality
            f.write('拍攝類型: ' + str(tag_modality) + '\n')
            print('拍攝類型: ', tag_modality)

            tag_patient_name = ds.PatientName
            f.write('名稱: ' + str(tag_patient_name) + '\n')
            print('名稱: ', tag_patient_name)

            tag_patient_sex = ds.PatientSex
            f.write('性別: ' + str(tag_patient_sex) + '\n')
            print('性別: ', tag_patient_sex)

            tag_patient_age = ds.PatientAge
            f.write('年齡: ' + str(tag_patient_age) + '\n')
            print('年齡: ', tag_patient_age)

            tag_patient_phone_number = ds.PatientID
            f.write('手機: ' + str(tag_patient_phone_number) + '\n')
            print('手機: ', tag_patient_phone_number)

            tag_processing_function = ds.ProcessingFunction
            f.write('執行方法: ' + str(tag_processing_function) + '\n')
            print('執行方法: ', tag_processing_function)

            tag_rows = ds.Rows
            f.write('影片高度: ' + str(tag_rows) + '\n')
            print('影片高度: ', tag_rows)

            tag_columns = ds.Columns
            f.write('影片寬度: ' + str(tag_columns) + '\n')
            print('影片寬度: ', tag_columns)

    memory_dicom_file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=str, help='DICOM file url')
    args = parser.parse_args()
    download_dcm(args.url)
