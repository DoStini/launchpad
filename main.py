import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

NAME = "LaunchPa$"
CAM_IDX = 2

# def detect_circles():

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

while True:
    _, img = cam.read()

    gray_img = gray_scale(img)
    # gray_img = cv2.medianBlur(gray_img, 5)
    circles = find_circles_positions(gray_img)
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for [pos_x, pos_y, radius] in circles[0,:]:
            color = find_circle_color(img, pos_x, pos_y, radius)
            cv2.circle(img, (pos_x, pos_y), radius, color, thickness=cv2.FILLED)
            cv2.circle(img, (pos_x, pos_y), radius, (0,0,0), thickness=2)

    cv2.imshow(NAME, img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cam.release()
cv2.destroyAllWindows()

