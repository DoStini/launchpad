import math
import time
import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

NAME = "LaunchPa$"
CAM_IDX = 0

# def detect_circles():

COLOR_DIST_TRESHOLD = 30
COLOR_DETECTION_TIMEOUT = 3
NUM_COLORS = 8

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
aruco_params = cv2.aruco.DetectorParameters()
aruco_detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

cam = cv2.VideoCapture(CAM_IDX)
cv2.namedWindow(NAME)

def distance_3d(p1, p2):
    (r1,g1,b1) = p1
    (r2,g2,b2) = p2
    return math.sqrt((r1 - r2)**2 + (g1 - g2) ** 2 + (b1 - b2) **2)

def distance_2d(p1, p2):
    return distance_3d((p1[0], p1[1], 0), (p2[0], p2[1], 0))

def gray_scale(img: cv2.Mat) -> cv2.Mat:
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def detect_bounds(gray_img) -> list[tuple[int]]:
    markers, _, _ = aruco_detector.detectMarkers(gray_img)

    means = []

    for mark in markers:
        means.append(tuple(np.mean(mark, axis=1)[0].astype(int)))

    if len(means) < 2:
        return means

    result = [means[0]]
    means = means[1:]

    while len(result) < len(markers):
        next_pnt = sorted(means, key=lambda pt: distance_2d(pt, result[len(result)-1]))[0]
        means.remove(next_pnt)
        result.append(next_pnt)

    return result

def point_outside_bounds(bounds: list[tuple[int]], point: tuple[int]) -> bool:
    return cv2.pointPolygonTest(bounds, point, measureDist=False) < 0

def find_circles_positions(img: cv2.Mat):
    return cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 5, param1=15, param2=35, minRadius=5, maxRadius=20)

def find_circle_color(img, x, y, r) -> tuple:
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

def find_closest_color(color):
    if len(buttons) == 0:
        return None

    res = sorted(buttons, key=lambda target: distance_3d(color, target))
    target = res[0]
    if distance_3d(color, target) < COLOR_DIST_TRESHOLD or len(buttons.keys()) == NUM_COLORS:
        return target

    return None


initial_time = time.time()

while True:
    _, img = cam.read()

    gray_img = gray_scale(img)
    # gray_img = cv2.medianBlur(gray_img, 5)
    circles = find_circles_positions(gray_img)

    markers = detect_bounds(gray_img)
    markers_found = len(markers) == 4

    for mark in markers:
        cv2.circle(img, mark, 10, (0,200,0), cv2.FILLED)
    
    if not markers_found:
        print("Not all markers were found")
    else:
        for x in range(-1, 3):
            cv2.line(img, markers[x], markers[x+1], (0,200,0), 4)


    if markers_found and circles is not None and time.time() > initial_time + COLOR_DETECTION_TIMEOUT:
        circles = np.uint16(np.around(circles))
        for [pos_x, pos_y, radius] in circles[0,:]:
            if point_outside_bounds(np.array(markers), (pos_x, pos_y)):
                continue
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

