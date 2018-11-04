import cv2
import os
import time
import numpy as np
import matplotlib.pyplot as plt

from PIL import Image
from pyzbar.pyzbar import decode
from copy import deepcopy
from base64 import b64encode


class Scanner():
    def __init__(self, camera_port=0):
        if not os.path.isdir('./temp'):
            os.makedirs('./temp')
        self.camera = cv2.VideoCapture(camera_port)
        self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)

    def __del__(self):
        del(self.camera)

    def do_scan(self, interval):
        time.sleep(interval)
        ret_val, image = self.camera.read()
        if not ret_val:
            return []
        cv2.imwrite('./temp/opencv.png', image)
        img = Image.open('./temp/opencv.png')
        d = decode(img)
        opencvImage = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        to_crop = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        def offset_and_validate_br_tl(offset, br, tl, max_x, max_y):
            tl[0] -= offset
            tl[1] -= offset
            br[0] += offset
            br[1] += offset

            if tl[0] <= 0:
                tl[0] = 0
            if tl[1] <= 0:
                tl[1] = 0

            if br[0] > max_x:
                br[0] = max_x
            if br[1] > max_y:
                br[1] = max_y

            return br, tl

        result = []
        for x in d:
            left, top, width, height = x.rect
            tl = [left, top]
            br = [tl[0] + width, tl[1] + height]
            max_y = np.array(img).shape[0] - 1
            max_x = np.array(img).shape[1] - 1

            br, tl = offset_and_validate_br_tl(150, br, tl, max_x, max_y)

            cv2.rectangle(opencvImage, tuple(tl), tuple(br), (0, 200, 200), 3)
            t = tl[1]
            b = br[1]
            l = tl[0]
            r = br[0]

            tl = [left, top]
            br = [tl[0] + width, tl[1] + height]
            br, tl = offset_and_validate_br_tl(10, br, tl, max_x, max_y)

            cv2.rectangle(to_crop, tuple(tl), tuple(br), (0, 200, 200), 3)
            cropped_img = cv2.cvtColor(to_crop[t:b, l:r], cv2.COLOR_BGR2RGB)
            result.append((x, cropped_img))

        cv2.imshow("1", opencvImage)
        cv2.waitKey(0)
        # debug
        return result

    def merge(self, d1, d2):
        d = deepcopy(d1)
        for k in d2:
            if k in d:
                # keep bigger amount
                if len(d[k]) < len(d2[k]):
                    d[k] = d2[k]
            else:
                d[k] = d2[k]
        return d

    def to_occurence_list(self, d):
        items = []
        for k, imgs in d.items():
            if k.startswith('r:'):
                k = k[2:]

            for i, img in enumerate(imgs):
                container_id = str("%s" % k)
                item_id = i
                filename = "%s_%d.jpg" % (container_id, item_id)
                cv2.imwrite(filename, img, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
                items.append({'container_id': container_id, 'occurrence': item_id,
                              'img_filename': filename})
        return items

    def scan(self, n=5, interval=0.1, data=None):
        if interval < 0.1:
            interval = 0.1

        if data is None:
            decoded = {}
        else:
            decoded = data
        for _ in range(n):
            prev_decoded = decoded
            d = self.do_scan(interval)
            decoded = {}
            img = Image.open('./temp/opencv.png')
            for (x, img) in d:
                k = str(x.data)
                if k not in decoded:
                    decoded[k] = [img]
                else:
                    decoded[k].append(img)

            decoded = self.merge(prev_decoded, decoded)

        return decoded

    def pretty_print(self, data):
        for t in data:
            print("CONTAINER> %s | OCCURRENCE> %03d" %
                  (t['container_id'], t['occurrence']))


if __name__ == "__main__":
    scanner = Scanner(1)
    while(True):
        print("Scanning...", end='')
        result = scanner.scan(5, 0.1)
        scanner.pretty_print(result)
        print("Done!")
        time.sleep(1)
