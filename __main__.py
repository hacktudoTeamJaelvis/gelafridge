import time
import cv2
import cloudinary.uploader as upl
import requests
import os

from .scan import Scanner


# need to export the api key!
def send_image(url, data):
    post_data = []
    for d in data:
        post_data.append(d)
        filename = post_data[-1].pop('filename')
        response = upl.upload(open(filename, 'rb'))
        post_data[-1]['image_url'] = response['url']
    requests.post(url, json={'data': post_data})


def main():
    scanner = Scanner(1)
    result = None
    while(True):
        print("Scanning...", end='')
        result = scanner.scan(5, 0.1, data=result)
        print("Done!")
        scanner.pretty_print(result)
        key = cv2.waitKey(0)
        if key == 'q':
            break
    data = scanner.to_occurence_list(result)

    url = os.environ['GELAFRIDGE_URL']
    send_image(url, data)


main()
