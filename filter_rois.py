"""define regions of interest based on cropped area and hsv color range

outputs data to be used in recolor.py
"""

import utils
from os.path import basename
import pandas as pd
import cv2
import argparse

parser = argparse.ArgumentParser(description='Define regions of interest based on cropped area and hsv color range')
parser.add_argument('-i', '--input', dest='input_path', help='Input image to be modified', required=True)
parser.add_argument('-o', '--output', dest='output_dir', help='Output directory to store results', required=True)
parser.add_argument('-l', '--labels', nargs='+', dest='labels',
                    help='Labels for each portion of the image to be recolored', required=True)

args = parser.parse_args()

image = cv2.imread(args.input_path)

results_df = None
for label in args.labels:
    # define color range of interest
    (lh, ls, lv), (uh, us, uv) = utils.gui_hsv_picker(image, label=label)
    # define area of interest
    x, y, w, h = utils.gui_cropper(image, label=label)
    dict_i = {'label': [label],
              'box_x': [x], 'box_y': [y], 'box_w': [w], 'box_h': [h],
              'low_h': [lh], 'low_s': [ls], 'low_v': [lv],
              'hi_h': [uh], 'hi_s': [us], 'hi_v': [uv]}

    df_i = pd.DataFrame.from_dict(dict_i)

    results_df = pd.concat((results_df, df_i))


results_df.to_csv('{0}/{1}.csv'.format(args.output_dir,basename(args.input_path).split(".")[0]))
