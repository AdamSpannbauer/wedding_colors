"""apply color transformation to an area of an image

use output data of filter_rois.py to apply color transformation
"""

import pandas as pd
import numpy as np
import cv2
import argparse

parser = argparse.ArgumentParser(description='Apply color transformations to an area of an image')
parser.add_argument('-i', '--image', dest='image_path', help='Path to input image to be modified', required=True)
parser.add_argument('-d', '--data', dest='data_path',
                    help='Path to csv specifying regions to be modified', required=True)
parser.add_argument('-c', '--colors', dest='colors',
                    help='Path to csv specifying new colors (in rgb) to apply to regions')

args = parser.parse_args()

# recolor labeled areas buy single rgb value
new_colors_rgb = pd.read_csv(args.colors).to_dict()
for k in new_colors_rgb.keys():
    new_colors_rgb[k] = list(new_colors_rgb[k].values())

# read in image and recolor data
image = cv2.imread(args.image_path)
recolor_data = pd.read_csv(args.data_path)

# copy image for safe keeping and blur
image_og = np.copy(image)
blurred = cv2.GaussianBlur(image, (3, 3), 0, 0)

# get image dims
im_h, im_w = image.shape[:2]


def scale_between(arr, a, b):
    return (b - a) * (arr - arr.min()) / (arr.max() - arr.min())


for i, row in recolor_data.iterrows():
    if row['label'] in new_colors_rgb.keys():
        new_color_patch = cv2.cvtColor(np.zeros((10, 10), dtype='uint8'), cv2.COLOR_GRAY2BGR)
        new_color_patch[:] = new_colors_rgb[row['label']][::-1]
    else:
        continue
    # mask to roi
    x, y, w, h = row['box_x'], row['box_y'], row['box_w'], row['box_h']
    mask = np.zeros((im_h, im_w), dtype="uint8")
    mask = cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
    masked = cv2.bitwise_and(blurred, blurred, mask=mask)

    # perform color filter
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    lower_thresh = (row['low_h'], row['low_s'], row['low_v'])
    upper_thresh = (row['hi_h'], row['hi_s'], row['hi_v'])
    color_mask = cv2.inRange(hsv, lower_thresh, upper_thresh)

    # clean up salt/pepper color filtering noise
    kernel = np.ones((5, 5), np.uint8)
    color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel)
    color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel)
    color_mask = cv2.dilate(color_mask, np.ones((3, 3), np.uint8))

    # mask roi to color range of interest
    color_masked = cv2.bitwise_and(masked, masked, mask=color_mask)

    # recenter image around destination color
    lab_patch = np.float32(cv2.cvtColor(new_color_patch, cv2.COLOR_BGR2LAB))
    dst_l, dst_a, dst_b = cv2.split(lab_patch)

    color_masked_lab = np.float32(cv2.cvtColor(color_masked, cv2.COLOR_BGR2LAB))
    src_l, src_a, src_b = cv2.split(color_masked_lab)

    out_l = src_l - src_l.mean() + dst_l.mean()
    out_a = src_a - src_a.mean() + dst_a.mean()
    out_b = src_b - src_b.mean() + dst_b.mean()

    # rescale if outside of 0-255 range
    if out_l.max() > 255 and out_l.min() < 0:
        out_l = scale_between(out_l, 0, 255)
    elif out_l.max() > 255:
        out_l = scale_between(out_l, out_l.min(), 255)
    elif out_l.min() < 0:
        out_l = scale_between(out_l, 0, out_l.max())

    # recombine color channels and convert to BGR for display
    recolored = cv2.merge([out_l, out_a, out_b])
    recolored = np.uint8(recolored)
    recolored = cv2.cvtColor(recolored, cv2.COLOR_LAB2BGR)

    # apply region and color filters to recolored image
    masked_recolored = cv2.bitwise_and(recolored, recolored, mask=mask)
    masked_recolored = cv2.bitwise_and(masked_recolored, masked_recolored, mask=color_mask)

    # find non zero elements from masked recolored image
    roi_y, roi_x = cv2.cvtColor(masked_recolored, cv2.COLOR_BGR2GRAY).nonzero()

    # transfer recoloring to source image
    result = image[:]
    result[roi_y, roi_x, :] = masked_recolored[roi_y, roi_x, :]

# display results
cv2.imshow('input', image_og)
cv2.imshow('recolored', result)
cv2.imshow('reference color', new_color_patch)
cv2.waitKey(0)
