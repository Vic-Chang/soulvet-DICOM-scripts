import requests


def download_img(img_url):
    results = requests.get(img_url)

    with open('test.jpg', 'wb') as f:
        f.write(results.content)


if __name__ == '__main__':
    url = ''
    download_img(url)
