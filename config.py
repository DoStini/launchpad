import os
import threading
import time
import cv2
import numpy as np
from datetime import datetime
import json

import tkinter as tk
from tkinter import ttk

PARAM1 = 30
PARAM2 = 70
MIN_RADIUS = 50
MAX_RADIUS = 60

NAME = "LaunchPa$"
CAM_IDX = 1
# TODO Interactive slider to change values and wirte config file
# def detect_circles():

cam = cv2.VideoCapture(CAM_IDX)
cv2.namedWindow(NAME)

done = False

def load_config():
    global PARAM1, PARAM2, MIN_RADIUS, MAX_RADIUS
    if not os.path.exists("config/latest.json"):
        return
    
    with open("config/latest.json", "r") as openfile:
        json_object = json.load(openfile)
        PARAM1 = json_object["param1"]
        PARAM2 = json_object["param2"]
        MIN_RADIUS = json_object["min_radius"]
        MAX_RADIUS = json_object["max_radius"]

def save_config():
    config = {
        "param1": PARAM1,
        "param2": PARAM2,
        "min_radius": MIN_RADIUS,
        "max_radius": MAX_RADIUS,
    }
    current_datetime = datetime.now()
    current_date_time = current_datetime.strftime("%m-%d-%Y, %H:%M:%S")

    if os.path.exists("config/latest.json"):
        os.rename("config/latest.json", f"config/{current_date_time}.json")
    json_object = json.dumps(config)
    with open("config/latest.json", "w") as outfile:
        outfile.write(json_object)

def gray_scale(img: cv2.Mat) -> cv2.Mat:
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def find_circles_positions(img: cv2.Mat):
    return cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 5, param1=PARAM1, param2=PARAM2, minRadius=MIN_RADIUS, maxRadius=MAX_RADIUS)

def gui():
    global PARAM1, PARAM2, MIN_RADIUS, MAX_RADIUS, done

    root = tk.Tk()
    frm = ttk.Frame(root, padding=10)
    frm.grid()
    # ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)

    param1 = tk.IntVar(value=PARAM1)
    param2 = tk.IntVar(value=PARAM2)
    min_radius = tk.IntVar(value=MIN_RADIUS)
    max_radius = tk.IntVar(value=MAX_RADIUS)


    def close():
        global done
        root.destroy()
        done = True


    def on_change(_):
        global PARAM1, PARAM2, MIN_RADIUS, MAX_RADIUS
        PARAM1 = param1.get()
        PARAM2 = param2.get()
        MIN_RADIUS = min_radius.get()
        MAX_RADIUS = max_radius.get()


    ttk.Label(frm, text="Param 1").grid(column=0, row=0)
    p1 = tk.Scale(frm, from_=1, to=200, variable=param1, orient=tk.HORIZONTAL, command=on_change)
    p1.grid(column=1, row=0)

    ttk.Label(frm, text="Param 2").grid(column=0, row=1)
    p2 = tk.Scale(frm, from_=1, to=200, variable=param2, orient=tk.HORIZONTAL, command=on_change)
    p2.grid(column=1, row=1)

    ttk.Label(frm, text="Min radius").grid(column=0, row=2)
    min_rad = tk.Scale(frm, from_=1, to=200, variable=min_radius, orient=tk.HORIZONTAL, command=on_change)
    min_rad.grid(column=1, row=2)

    ttk.Label(frm, text="Max radius").grid(column=0, row=3)
    max_rad = tk.Scale(frm, from_=1, to=200, variable=max_radius, orient=tk.HORIZONTAL, command=on_change)
    max_rad.grid(column=1, row=3)

    tk.Button(frm, text='Save configuration', command=save_config).grid(column=0,row=5)
    tk.Button(frm, text='Quit', command=close).grid(column=0,row=6)

    root.mainloop()

load_config()

threading.Thread(target=gui).start()

while True:
    _, img = cam.read()

    gray_img = gray_scale(img)
    # gray_img = cv2.medianBlur(gray_img, 5)
    circles = find_circles_positions(gray_img)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for [pos_x, pos_y, radius] in circles[0,:]:
            cv2.circle(gray_img, (pos_x, pos_y), radius, (0, 0, 0), thickness=cv2.FILLED)

    gray_img = cv2.resize(gray_img, (960, 540))
    cv2.imshow(NAME, gray_img)

    if cv2.waitKey(1) & 0xFF == ord('q') or done:
        break
    

cam.release()
cv2.destroyAllWindows()

