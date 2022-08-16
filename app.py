import datetime
import requests
import dicom2jpg
from urllib import parse
from pydicom import dcmread


def download_dcm(img_url: str):
    results = requests.get(img_url)
    file_name = parse.parse_qs(parse.urlparse(img_url).query)['image'][0]
    dcm_file = f'{file_name}.dcm'
    with open(dcm_file, 'wb') as f:
        f.write(results.content)

    ds = dcmread(dcm_file)

    tag_datetime = datetime.datetime.strptime((ds.ContentDate + ds.ContentTime), '%Y%m%d%H%M%S.%f')
    print(tag_datetime)

    tag_modality = ds.Modality
    print(tag_modality)

    tag_patient_name = ds.PatientName
    print(tag_patient_name)

    tag_patient_phone_number = ds.PatientID
    print(tag_patient_phone_number)

    tag_patient_sex = ds.PatientSex
    print(tag_patient_sex)

    tag_hospital = ds[0x0009, 0x1080].value
    print(tag_hospital)

    tag_body_part_examined = ds.BodyPartExamined
    print(tag_body_part_examined)

    tag_device_description = ds.AcquisitionDeviceProcessingDescription
    print(tag_device_description)

    tag_menu_name = ds[0x0019, 0x1032].value
    print(tag_menu_name)

    tag_image_type = ds[0x0019, 0x1040].value
    print(tag_image_type)

    tag_film_annotation = ds[0x0019, 0x1090].value
    print(tag_film_annotation)

    tag_rows = ds.Rows
    print(tag_rows)

    tag_columns = ds.Columns
    print(tag_columns)

    # Convert to jpg
    dicom2jpg.dicom2jpg(dcm_file)


if __name__ == '__main__':
    url = 'https://soulvet.tw/v2/public/soulvet/getShareUrlImage/TpCZGL2D?image=367f60cc-ee7a-47c5-936c-93d01fb8bdfd'
    download_dcm(url)
