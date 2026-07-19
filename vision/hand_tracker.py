from math import hypot
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from numpy.typing import NDArray


HAND_CONNECTIONS = (
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),
    (5, 9),
    (9, 10),
    (10, 11),
    (11, 12),
    (9, 13),
    (13, 14),
    (14, 15),
    (15, 16),
    (13, 17),
    (17, 18),
    (18, 19),
    (19, 20),
    (0, 17),
)

THUMB_TIP = 4
INDEX_FINGER_TIP = 8


class HandTracker:
    def __init__(
        self,
        model_path: str | Path,
        num_hands: int = 1,
        pinch_on_distance: float = 32.0,
        pinch_off_distance: float = 44.0,
    ) -> None:
        if pinch_on_distance >= pinch_off_distance:
            raise ValueError(
                "Pinch on distance must be lower than pinch off distance"
            )

        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=str(model_path),
            ),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=num_hands,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self._landmarker = (
            mp.tasks.vision.HandLandmarker.create_from_options(
                options
            )
        )

        self._pinch_on_distance = pinch_on_distance
        self._pinch_off_distance = pinch_off_distance
        self._pinched = False

    def detect(
        self,
        frame: NDArray[np.uint8],
        timestamp_ms: int,
    ) -> mp.tasks.vision.HandLandmarkerResult:
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame,
        )

        return self._landmarker.detect_for_video(
            image,
            timestamp_ms,
        )

    def get_control_input(
        self,
        result: mp.tasks.vision.HandLandmarkerResult,
        measurement_size: tuple[int, int],
    ) -> tuple[
        tuple[float, float] | None,
        bool,
        float | None,
    ]:
        if not result.hand_landmarks:
            self._pinched = False
            return None, False, None

        width, height = measurement_size
        landmarks = result.hand_landmarks[0]

        thumb_tip = landmarks[THUMB_TIP]
        index_tip = landmarks[INDEX_FINGER_TIP]

        thumb_position = (
            thumb_tip.x * width,
            thumb_tip.y * height,
        )
        index_position = (
            index_tip.x * width,
            index_tip.y * height,
        )

        tip_distance = hypot(
            thumb_position[0] - index_position[0],
            thumb_position[1] - index_position[1],
        )

        if self._pinched:
            if tip_distance >= self._pinch_off_distance:
                self._pinched = False
        elif tip_distance <= self._pinch_on_distance:
            self._pinched = True

        return (
            (index_tip.x, index_tip.y),
            not self._pinched,
            tip_distance,
        )

    def draw(
        self,
        frame: NDArray[np.uint8],
        result: mp.tasks.vision.HandLandmarkerResult,
        control_active: bool,
    ) -> NDArray[np.uint8]:
        height, width = frame.shape[:2]

        for landmarks in result.hand_landmarks:
            points = [
                (
                    round(landmark.x * width),
                    round(landmark.y * height),
                )
                for landmark in landmarks
            ]

            for start_index, end_index in HAND_CONNECTIONS:
                cv2.line(
                    frame,
                    points[start_index],
                    points[end_index],
                    (255, 255, 255),
                    2,
                )

            for point in points:
                cv2.circle(
                    frame,
                    point,
                    4,
                    (0, 255, 0),
                    -1,
                )

            thumb_point = points[THUMB_TIP]
            index_point = points[INDEX_FINGER_TIP]

            cv2.line(
                frame,
                thumb_point,
                index_point,
                (255, 200, 0),
                2,
            )

            cv2.circle(
                frame,
                thumb_point,
                9,
                (255, 200, 0),
                2,
            )

            cv2.circle(
                frame,
                index_point,
                12,
                (
                    (0, 255, 0)
                    if control_active
                    else (0, 0, 255)
                ),
                -1,
            )

        return frame

    def close(self) -> None:
        self._landmarker.close()
