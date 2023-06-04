from enum import Enum
import json
import os
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
from Hand import Hand
from HandTrackingModule import HandDetector

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


import math
import time
import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import mido

midi_port = mido.open_output("Fluidsynth GM")


PARAM1 = 1
PARAM2 = 1
MIN_RADIUS = 1
MAX_RADIUS = 1

def load_config():
    global PARAM1, PARAM2, MIN_RADIUS, MAX_RADIUS
    if not os.path.exists("config/latest.json"):
        print("ERROR: Create configuration file using config.py")
        exit(1)

    with open("config/latest.json", "r") as openfile:
        json_object = json.load(openfile)
        PARAM1 = json_object["param1"]
        PARAM2 = json_object["param2"]
        MIN_RADIUS = json_object["min_radius"]
        MAX_RADIUS = json_object["max_radius"]


load_config()

BOARD_NAME = "LaunchPa$ Board"
HEIGHT_NAME = "LaunchPa$ Height"
HEIGHT_CLICK_VALUE = 180

BOARD_CAM_IDX = 1
HEIGHT_CAM_IDX = 2

detector = HandDetector(detectionCon=0.85, maxHands=2)

COLOR_DIST_TRESHOLD = 30
COLOR_DETECTION_TIMEOUT = 3
NUM_COLORS = 7

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
aruco_params = cv2.aruco.DetectorParameters()
aruco_detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

board_cam = cv2.VideoCapture(BOARD_CAM_IDX)
cv2.namedWindow(BOARD_NAME)

height_cam = cv2.VideoCapture(HEIGHT_CAM_IDX)
cv2.namedWindow(HEIGHT_NAME)



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

def point_inside_bounding_box(box, pos):
    [(x1, y1), (x2, y2)] = box
    x, y = pos
    return x > x1 and x < x2 and y > y1 and y < y2

def point_outside_bounds(bounds: list[tuple[int]], point: tuple[int]) -> bool:
    return cv2.pointPolygonTest(bounds, point, measureDist=False) < 0

def find_circles_positions(img: cv2.Mat):
    return cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 5, param1=PARAM1, param2=PARAM2, minRadius=MIN_RADIUS, maxRadius=MAX_RADIUS)

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
    def __init__(self, color: tuple, position: tuple, bounding_box: tuple, id: int) -> None:
        self.color: tuple = color
        self.position: tuple = position
        self.bounding_box: tuple = bounding_box
        self.id: int = id

buttons: dict[tuple[int], Button] = {}

def merge_hands(previous_hands: list[Hand], landmarks, fingers_up):
    new_list = []
    for idx, landmark in enumerate(landmarks):
        match = None
        best_dist = 10000
        for hand in previous_hands:
            dist = math.dist(
                (
                    int(landmark[0][1]),
                    int(landmark[0][2]),
                ),
                (hand.wrist_position[0], hand.wrist_position[1]),
            )
            # if dist > 50:
            #     continue
            if dist < best_dist:
                match = hand
                best_dist = dist

        if match:
            match.update_positions(landmark, fingers_up[idx])
        else:
            match = Hand(landmark, fingers_up[idx])

        new_list.append(match)
    return new_list

def find_button(pos):
    for button in buttons.values():
        if not point_inside_bounding_box(button.bounding_box, pos):
            continue
        return button

def find_closest_color(color):
    if len(buttons) == 0:
        return None

    res = sorted(buttons, key=lambda target: distance_3d(color, target))
    target = res[0]
    if distance_3d(color, target) < COLOR_DIST_TRESHOLD or len(buttons.keys()) == NUM_COLORS:
        return target

    return None

initial_time = time.time()

def click_position(hands: list[Hand]):
    for hand in hands:
        return hand.index_tip_position

def run_board(img, hands: list[Hand]):
    global click_state

    clicked_btn = None

    for hand in hands:
        if not hand.clicked:
            continue
        
        clicked_btn = find_button(hand.position)
        if clicked_btn is None:
            continue

        msg = mido.Message('note_on', note=clicked_btn.id + 50)
        midi_port.send(msg)

        hand.consume_click()
        

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
                btn = Button(color, (pos_x, pos_y), bounding_box, len(buttons))
                buttons[color] = btn
            else:
                btn = buttons[similar_color]
                btn.position = (pos_x, pos_y)
                btn.bounding_box = bounding_box


        for button in buttons.values():
            border_color = (256, 256, 256) if button == clicked_btn else (0,0,0)
            cv2.rectangle(img, button.bounding_box[0], button.bounding_box[1], button.color, thickness=cv2.FILLED)
            cv2.rectangle(img, button.bounding_box[0], button.bounding_box[1], border_color , thickness=5)
            cv2.putText(img, str(button.id), org=button.position, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(0,0,0), thickness=1)

    img = cv2.resize(img, (960, 540))
    cv2.imshow(BOARD_NAME, img)


def update_click_status(hands: list[Hand]):
    for hand in hands:
        hand.update_click_status()

def draw_hands(img, hands: list[Hand]):
    for hand in hands:
        cv2.circle(img, hand.position, 10, (200,0, 0), cv2.FILLED)

hands_list: list[Hand] = []


while True:
    # _, height_img = height_cam.read()
    _, board_img = board_cam.read()

    detector.find_hands(board_img, board_img, draw=False)
    landmarks = detector.find_positions(board_img, draw=False)
    hand_fingers = detector.fingers_up()

    hands_list = merge_hands(hands_list, landmarks, hand_fingers)
    update_click_status(hands_list)

    draw_hands(board_img, hands_list)

    # run_height(height_img)
    run_board(board_img, hands_list)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


board_cam.release()
height_cam.release()
cv2.destroyAllWindows()

