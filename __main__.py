import time
import cv2
import cloudinary.uploader as upl
import requests
import os
import numpy
import json
from sys import argv

from .scan import Scanner


# need to export the api key!
def send_image(url, data):
    put_data = {}
    for d in data:
        item_id = d['container_id']
        filename = d['img_filename']
        if item_id in put_data:
            continue
        response = upl.upload(open(filename, 'rb'))
        image_url = response['url']
        put_data[item_id] = {'image_url': image_url}
    headers = {"Content-Type": "application/json"}
    requests.put(url+"/shelves/1", json=json.dumps(put_data), headers=headers)


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
        key = cv2.waitKey(1000)
        if key == ord('c'):
            print('Door closed!')
            break
    data = scanner.to_occurence_list(result)

    if 'GELAFRIDGE_URL' in os.environ:
        print("Sending data to server")
        url = os.environ['GELAFRIDGE_URL']
        send_image(url, data)


first_run = False
while(True):
    cv2.imshow("1", numpy.array([[0, 0, 0], [0, 0, 0]]))
    print("Press 'o' to open the door")
    key = cv2.waitKey(0)
    if key == ord('o'):
        print('Door opened!')
        main()
