"""
HAND TRACKING MODULE USING OPENCV AND MEDIAPIPE
By Anmol Virdi (Self-Authored)
Created on 17/06/21
"""

# Importing openCV, mediapipe and time libraries
import cv2
import mediapipe as mp
import numpy as np


# Creating a Class/prototype
class HandDetector:
    # Constructor, with some default values
    def __init__(
        self, mode=False, maxHands=5, detectionCon=0.5, modelComplexity=1, trackCon=0.5
    ):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.modelComplex = modelComplexity
        self.trackCon = trackCon

        # Assigning the hand detector as well as hand landmarks(points) detector funtions to variables of the class
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            self.mode,
            self.maxHands,
            self.modelComplex,
            self.detectionCon,
            self.trackCon,
        )
        self.mpDraw = mp.solutions.drawing_utils

    # function to detect hands and place/draw landmarks on them
    def find_hands(self, img, videoCap, draw=True):
        img1 = cv2.cvtColor(videoCap, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img1)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(
                        img,
                        handLms,
                        self.mpHands.HAND_CONNECTIONS,
                        self.mpDraw.DrawingSpec(
                            color=(47, 47, 255), thickness=2, circle_radius=2
                        ),  # color of points
                        self.mpDraw.DrawingSpec(
                            color=(54, 54, 179), thickness=2, circle_radius=2
                        ),
                    )  # color of connections
        return img

    # Function to find coordinates of all the landmarks of a particular hand(default= hand number 0). Returns a list of all of them.
    def find_positions(self, img, draw=True):
        self.lmList = []
        if not self.results.multi_hand_landmarks:
            return self.lmList

        for hand in self.results.multi_hand_landmarks:
            l = []
            for id, lm in enumerate(hand.landmark):
                # To draw those handlandmarks on the video frames
                # The coordinates recieved in lm are actually relative, i.e, 0-1. So, we need to convert them as per the size of original image.

                # Getting height, width and the number of channels of the original images using the .shape function
                height, width, channels = img.shape

                # Converting the relative coordinates(x,y) from lms to original coordinates(cx,cy)
                cx, cy = int(lm.x * width), int(lm.y * height)

                l.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 10, (255, 255, 0), cv2.FILLED)

            self.lmList.append(l)

        return self.lmList

    def fingers_up(self):  # checks whether the finger are up or not
        tip_ids = [4, 8, 12, 16, 20]  # Finger tip IDs
        hands = []
        for hand in self.lmList:
            fingers = []

            # thumb
            if hand[tip_ids[0]][1] < hand[tip_ids[0] - 1][1]:
                fingers.append(0)
            else:
                fingers.append(1)

            # Other fingers
            for id in range(1, 5):
                if hand[tip_ids[id]][2] > hand[tip_ids[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            hands.append(fingers)
        return hands
