import requests
import dicom2jpg
from urllib import parse


def download_dcm(img_url: str):
    results = requests.get(img_url)
    file_name = parse.parse_qs(parse.urlparse(img_url).query)['image'][0]
    dcm_file = f'{file_name}.dcm'
    with open(dcm_file, 'wb') as f:
        f.write(results.content)

    # Convert to jpg
    dicom2jpg.dicom2jpg(dcm_file)


if __name__ == '__main__':
    url = ''
    download_dcm(url)
