import time
import cv2
import cloudinary.uploader as upl
import requests
import os
from sys import argv

from .scan import Scanner


# need to export the api key!
def send_image(url, data):
    post_data = {}
    for d in data:
        item_id = d['container_id']
        filename = d['filename']
        if item_id in post_data:
            continue
        response = upl.upload(open(filename, 'rb'))
        image_url = response['url']
        post_data[item_id] = {'image_url': image_url}
    requests.post(url, json=post_data)


def main():
    if len(argv) == 1:
        port = 0
    else:
        port = int(argv[1])
    scanner = Scanner(port)
    result = None
    while(True):
        print("Scanning...")
        result = scanner.scan(10, 0.05, data=result)
        scanner.pretty_print(result)
        print("Done! Press 'c' to close the door")
        key = cv2.waitKey(0)
        if key == ord('c'):
            print('Door closed!')
            break
    data = scanner.to_occurence_list(result)

    if 'GELAFRIDGE_URL' in os.environ:
        url = os.environ['GELAFRIDGE_URL']
        send_image(url, data)


while(True):
    main()
