"""define regions of interest based on cropped area and hsv color range

outputs data to be used in recolor.py
"""

import utils
from os.path import basename
import pandas as pd
import cv2

# hardcoded inputs for now
input_path = 'images/party_pink.jpg'
output_dir = 'data'
labels = ['bride', 'bridesmaids', 'groom', 'groomsmen']

image = cv2.imread(input_path)

results_df = None
for label in labels:
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


results_df.to_csv(f'{output_dir}/{basename(input_path).split(".")[0]}.csv')
