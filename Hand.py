from enum import Enum
import numpy as np
from typing import ClassVar

FingerPosition = int

UP = 0
DOWN = 1

class ClickState(Enum):
    IDLE = 1
    CLICKED = 2
    DOWN = 3

class Hand:
    THUMB: ClassVar[FingerPosition] = 0
    INDEX: ClassVar[FingerPosition] = 1
    MIDDLE: ClassVar[FingerPosition] = 2
    RING: ClassVar[FingerPosition] = 3
    PINKY: ClassVar[FingerPosition] = 4

    def __init__(
        self, finger_positions, fingers_up
    ) -> None:
        self.parse_positions(finger_positions)
        self.fingers_up = fingers_up
        self.click_state = ClickState.IDLE

    def parse_positions(self, positions, offset_ratio=(0, 0)):

        self.wrist_position = (
            positions[0][1],
            positions[0][2],
        )

        # tipIDs=[4,8,12,16,20] #Finger tip IDs
        self.finger_positions = [
            # Thumb finder tip coordinates(landmark number 4)
            (
                int(positions[4][1]),
                int(positions[4][2]),
            ),
            # Index finger tip coordinates(landmark number 8)
            (
                int(positions[8][1]),
                int(positions[8][2]),
            ),
            # Middle finger tip coordinates(landmark number 12)
            (
                int(positions[12][1]),
                int(positions[12][2]),
            ),
            # Ring finger tip coordinates(landmark number 16)
            (
                int(positions[16][1]),
                int(positions[16][2]),
            ),
            # Pinky finger tip coordinates(landmark number 20)
            (
                int(positions[20][1]),
                int(positions[20][2]),
            ),
        ]
        self.all_positions = positions
        self.offset_ratio = offset_ratio

    def update_positions(self, positions, fingers_up, offset=(1, 1)):
        self.parse_positions(positions, offset)
        self.fingers_up = fingers_up

    def update_click_status(self):
        if self.click_fingers_active():
            if self.click_state == ClickState.IDLE:
                self.click_state = ClickState.CLICKED
        elif self.click_state == ClickState.DOWN:
            self.click_state = ClickState.IDLE

    def consume_click(self):
        self.click_state = ClickState.DOWN

    @property
    def clicked(self):
        return self.click_state == ClickState.CLICKED

    @property
    def thumb_tip_position(self):
        return self.finger_positions[Hand.THUMB]

    @property
    def index_tip_position(self):
        return self.finger_positions[Hand.INDEX]

    @property
    def middle_tip_position(self):
        return self.finger_positions[Hand.MIDDLE]

    @property
    def ring_tip_position(self):
        return self.finger_positions[Hand.RING]

    @property
    def pinky_tip_position(self):
        return self.finger_positions[Hand.PINKY]

    def finger_up(self, finger: FingerPosition):
        return self.finger(finger) == UP

    def finger_down(self, finger: FingerPosition):
        return self.finger(finger) == DOWN

    def click_fingers_active(self):
        return (
            self.finger_down(Hand.INDEX)
            and self.finger_down(Hand.MIDDLE)
            and self.finger_down(Hand.RING)
            and self.finger_down(Hand.PINKY)
        )

    @property
    def position(self):
        return self.index_tip_position

    def finger(self, finger: FingerPosition):
        return self.fingers_up[finger]

    def get_bounding_box(self):
        offset_x, offset_y = self.offset_ratio

        x_coordinates = [int(x[1] * offset_x) for x in self.all_positions]
        y_coordinates = [int(x[2] * offset_y) for x in self.all_positions]
        x_min, x_max = min(x_coordinates), max(x_coordinates)
        y_min, y_max = min(y_coordinates), max(y_coordinates)

        extra = 10
        x_min -= extra
        x_max += extra
        y_min -= extra
        y_max += extra

        return x_min, x_max, y_min, y_max