import datetime
import os.path
import requests
import dicom2jpg
from PIL import Image
from urllib import parse
from pydicom import dcmread
from pydicom.pixel_data_handlers.util import convert_color_space


def download_dcm(img_url: str):
    # Save dicom file to local
    results = requests.get(img_url)
    file_name = parse.parse_qs(parse.urlparse(img_url).query)['image'][0]
    dcm_file = f'{file_name}.dcm'
    with open(dcm_file, 'wb') as f:
        f.write(results.content)

    # Read dicom tag and write to txt
    ds = dcmread(dcm_file)

    # Check dicom type, multi frame or single picture
    if ds.SOPClassUID == '1.2.840.10008.5.1.4.1.1.3.1':
        # `Ultrasound Multi frame Image Storage`
        if not os.path.exists('temp'):
            os.mkdir('temp')
        for counter, image_pixel_array in enumerate(ds.pixel_array):
            # Convert color `YBR_FULL_422` to `RGB`, or image color will be weird
            pixel_array = convert_color_space(image_pixel_array, 'YBR_FULL_422', 'RGB')
            image = Image.fromarray(pixel_array)
            image.save(os.path.join('temp', f'img_{counter:03n}.png'))

    else:
        # A single picture
        with open(f'{file_name}.txt', 'w', encoding='utf-8') as f:
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

            # Convert dicom to jpg
            dicom2jpg.dicom2jpg(dcm_file)


if __name__ == '__main__':
    url = ''
    download_dcm(url)
