import cv2
import numpy as np

NAME = "LaunchPa$"
CAM_IDX = 2

# def detect_circles():

cam = cv2.VideoCapture(CAM_IDX)
cv2.namedWindow(NAME)

def gray_scale(img: cv2.Mat) -> cv2.Mat:
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def find_circles_positions(img: cv2.Mat):
    return cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 5, param1=20, param2=40, minRadius=5, maxRadius=50)


while True:
    _, img = cam.read()

    gray_img = gray_scale(img)
    # gray_img = cv2.medianBlur(gray_img, 5)
    circles = find_circles_positions(gray_img)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for [pos_x, pos_y, radius] in circles[0,:]:
            cv2.circle(gray_img, (pos_x, pos_y), radius, (0, 0, 0), thickness=cv2.FILLED)

    cv2.imshow(NAME, gray_img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cam.release()
cv2.destroyAllWindows()

