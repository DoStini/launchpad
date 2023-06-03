import math
import time
import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

NAME = "LaunchPa$"
CAM_IDX = 2

# def detect_circles():

COLOR_DIST_TRESHOLD = 30
COLOR_DETECTION_TIMEOUT = 2
NUM_COLORS = 8

cam = cv2.VideoCapture(CAM_IDX)
cv2.namedWindow(NAME)

def gray_scale(img: cv2.Mat) -> cv2.Mat:
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def find_circles_positions(img: cv2.Mat):
    return cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 5, param1=15, param2=35, minRadius=5, maxRadius=20)

def find_circle_color(img, x, y, r):
    roi = img[y - r: y + r, x - r: x + r]
    width, height = roi.shape[:2]
    mask = np.zeros((width, height, 3), roi.dtype)
    cv2.circle(mask, (int(width / 2), int(height / 2)), r, (255, 255, 255), -1)

    area = cv2.bitwise_and(roi, mask)
    data = []
    for i in range(3):
        channel = area[:, :, i]
        indices = np.where(channel != 0)[0]
        color = np.mean(channel[indices])
        data.append(int(color))
    return tuple(data)

class Button:
    def __init__(self, color: tuple, position: tuple, id: int) -> None:
        self.color: tuple = color
        self.position: tuple = position
        self.id: int = id

buttons = {}


def distance(c1, c2):
    (r1,g1,b1) = c1
    (r2,g2,b2) = c2
    return math.sqrt((r1 - r2)**2 + (g1 - g2) ** 2 + (b1 - b2) **2)

def find_closest_color(color):
    if len(buttons) == 0:
        return None

    res = sorted(buttons, key=lambda target: distance(color, target))
    target = res[0]
    if distance(color, target) < COLOR_DIST_TRESHOLD or len(buttons.keys()) == NUM_COLORS:
        return target

    return None


initial_time = time.time()

while True:
    _, img = cam.read()

    gray_img = gray_scale(img)
    # gray_img = cv2.medianBlur(gray_img, 5)
    circles = find_circles_positions(gray_img)
    
    if circles is not None and time.time() > initial_time + COLOR_DETECTION_TIMEOUT:
        circles = np.uint16(np.around(circles))
        for [pos_x, pos_y, radius] in circles[0,:]:
            bounding_box = [(pos_x - radius, pos_y - radius), (pos_x + radius, pos_y + radius)]
            color = find_circle_color(img, pos_x, pos_y, radius)

            similar_color = find_closest_color(color)

            if similar_color is None:
                btn = Button(color, (pos_x, pos_y), len(buttons))
                buttons[color] = btn
            else:
                btn = buttons[similar_color]
                btn.position = (pos_x, pos_y)
            cv2.rectangle(img, bounding_box[0], bounding_box[1], color, thickness=cv2.FILLED)
            cv2.rectangle(img, bounding_box[0], bounding_box[1], (0,0,0), thickness=2)
            cv2.putText(img, str(btn.id), org=(pos_x, pos_y), fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(0,0,0), thickness=1)

    cv2.imshow(NAME, img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cam.release()
cv2.destroyAllWindows()

