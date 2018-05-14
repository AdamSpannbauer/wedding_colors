"""
util functions for cropping/color filtering labeled regions of interest
"""
import cv2
import numpy as np
import imutils


def do_nothing(_):
    """place holder function for use in cv2.createTrackbar

    :param _:
    :return: nada
    """
    pass


def display_labeled_im(image, wait_key=300, label=''):
    """util func to write label on image then display

    :param image: image to put label on
    :param wait_key: value to pass to cv2.waitKey
    :param label: text to write on image before displaying
    :return:
    """
    cv2.putText(image, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.imshow(label, image)
    return cv2.waitKey(wait_key)


def gui_cropper(image, label=''):
    """crude gui utility using sliders to find crop coords

    :param image: input image to crop
    :param label: label for region of interest to crop (will display in gui)
    :return: box coords as tuple: (x, y, w, h)
    """
    im_h, im_w = image.shape[:2]

    cv2.namedWindow(label)
    cv2.createTrackbar('x', label, 0, im_w, do_nothing)
    cv2.createTrackbar('y', label, 0, im_h, do_nothing)
    cv2.createTrackbar('w', label, 0, im_w, do_nothing)
    cv2.createTrackbar('h', label, 0, im_h, do_nothing)

    while True:
        # get input values from sliders
        x = cv2.getTrackbarPos('x', label)
        y = cv2.getTrackbarPos('y', label)
        w = cv2.getTrackbarPos('w', label)
        h = cv2.getTrackbarPos('h', label)

        # mask areas not in crop range
        mask = np.zeros((im_h, im_w), dtype="uint8")
        mask = cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
        masked = cv2.bitwise_and(image, image, mask=mask)

        # display masked results
        result = np.hstack((image, masked))

        key = display_labeled_im(result, label=label) & 0xFF
        if key == 27:
            break

    cv2.destroyAllWindows()
    return x, y, w, h


def gui_hsv_picker(image, label=''):
    """crude gui utility using sliders to find hsv color ranges

    :param image: input image to color filter
    :param label: label for color range of interest to crop (will display in gui)
    :return: hsv color range as tuple of tuples: (h, s, v), (uh, us, uv)
    """
    resized = imutils.resize(image, width=500)
    hsv_og = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)

    # h, s, v = 100, 100, 100

    # create track bars
    cv2.namedWindow(label)
    cv2.createTrackbar('low-h', label, 0, 179, do_nothing)
    cv2.createTrackbar('low-s', label, 0, 255, do_nothing)
    cv2.createTrackbar('low-v', label, 0, 255, do_nothing)
    cv2.createTrackbar('hi-h', label, 0, 179, do_nothing)
    cv2.createTrackbar('hi-s', label, 0, 255, do_nothing)
    cv2.createTrackbar('hi-v', label, 0, 255, do_nothing)

    while True:
        hsv_i = hsv_og[:]

        # get input values from sliders
        h = cv2.getTrackbarPos('low-h', label)
        s = cv2.getTrackbarPos('low-s', label)
        v = cv2.getTrackbarPos('low-v', label)
        uh = 179 - cv2.getTrackbarPos('hi-h', label)
        us = 255 - cv2.getTrackbarPos('hi-s', label)
        uv = 255 - cv2.getTrackbarPos('hi-v', label)

        # mask areas not in color range
        lower_thresh = np.array([h, s, v])
        upper_thresh = np.array([uh, us, uv])

        mask = cv2.inRange(hsv_i, lower_thresh, upper_thresh)
        masked = cv2.bitwise_and(hsv_i, hsv_i, mask=mask)

        # write range to screen
        cv2.putText(masked,
                    'hsv({}, {}, {}) - hsv({}, {}, {})'.format(h, s, v, uh, us, uv),
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    2)

        # display masked results
        result = np.hstack((hsv_og, masked))
        result = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)

        key = display_labeled_im(result, label=label) & 0xFF
        if key == 27:
            break

    cv2.destroyAllWindows()
    return (h, s, v), (uh, us, uv)
