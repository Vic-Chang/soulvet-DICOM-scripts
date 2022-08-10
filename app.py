import requests


def download_dcm(img_url):
    results = requests.get(img_url)

    with open('test.dcm', 'wb') as f:
        f.write(results.content)


if __name__ == '__main__':
    url = ''
    download_dcm(url)
