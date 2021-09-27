import colorsys
import glob
import json
import os
import re
import sys

import cv2
import numpy as np

'''
reconstruct: ffmpeg -framerate 30 -i frame%d.jpg overlayed.mp4
'''

from zlib import crc32


def bytes_to_float(b):
    return float(crc32(b) & 0xffffffff) / 2 ** 32


def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def get_bounding_box_of_polygon(polygon):
    if len(polygon) == 0:
        return {
            "min_x": 0,
            "min_y": 0,
            "max_x": 0,
            "max_y": 0,
        }

    min_x = polygon[0][0][0]
    min_y = polygon[0][0][1]
    max_x = polygon[0][0][0]
    max_y = polygon[0][0][1]
    for part in polygon:
        for point in part:
            x = point[0]
            y = point[1]

            if x < min_x:
                min_x = x
            if x > max_x:
                max_x = x
            if y < min_y:
                min_y = y
            if y > max_y:
                max_y = y

    return {
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
    }


def mapper(filename):
    anno_file = filename + '.json'
    if not os.path.exists(anno_file):
        return

    dir = os.path.dirname(filename) + '/overlays/'

    os.makedirs(dir, exist_ok=True)
    output_file = dir + os.path.basename(filename)

    img = cv2.imread(filename)

    annos = json.loads(open(anno_file, 'r').read())['Objects']

    # Initialize black image of same dimensions for drawing the rectangles
    blk = np.zeros(img.shape, np.uint8)

    for anno in annos:
        parts = []
        for part in anno['mask_vertices']:
            parts.append(np.array(part, dtype=np.int32))

        label = anno['labels']['label']
        color = colorsys.hsv_to_rgb(bytes_to_float(("fdsa3434 234 234fdsa asdf " + label).encode('utf-8')), 1, .7)
        color = (color[0] * 256, color[1] * 256, color[2] * 256)
        cv2.drawContours(img, parts, -1, color, 2, lineType=cv2.LINE_AA)
        cv2.fillPoly(blk, parts, color, 1)

        bounds = get_bounding_box_of_polygon(anno['mask_vertices'])

        textX = bounds['min_x']
        textY = bounds['min_y']

        textSize = .5
        textThickness = 1
        (w, h), _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_DUPLEX, textSize, thickness=textThickness)

        # Prints the text.
        img = cv2.rectangle(img, (textX, textY - h), (textX + w, int(textY + h * .3)), color, -1)
        cv2.putText(img, label, (textX, textY), cv2.FONT_HERSHEY_DUPLEX, textSize, (255, 255, 255),
                    thickness=textThickness, lineType=cv2.LINE_AA)

    # Generate result by blending both images (opacity of rectangle image is 0.25 = 25 %)
    img = cv2.addWeighted(img, 1.0, blk, 0.25, 1)

    cv2.imwrite(output_file, img)


if __name__ == '__main__':
    dir = sys.argv[1]

    filenames = glob.glob(dir+"/*.jpg")

    filenames = natural_sort(filenames)

    filenames = [f for f in filenames if os.path.exists(f + '.json')]
    print(filenames)

    # pool = multiprocessing.Pool(5)
    #
    # pool.map(mapper, filenames)
    #
    # # exit()

    for filename in filenames:
        mapper(filename)
