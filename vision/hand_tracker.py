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

INDEX_FINGER_TIP = 8


class HandTracker:
    def __init__(
        self,
        model_path: str | Path,
        num_hands: int = 1,
    ) -> None:
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
            mp.tasks.vision.HandLandmarker.create_from_options(options)
        )

    def detect(
        self,
        frame: NDArray[np.uint8],
        timestamp_ms: int,
    ) -> mp.tasks.vision.HandLandmarkerResult:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame,
        )

        return self._landmarker.detect_for_video(
            image,
            timestamp_ms,
        )

    def get_index_fingertip(
            self,
            result: mp.tasks.vision.HandLandmarkerResult,
    ) -> tuple[float, float] | None:
        if not result.hand_landmarks:
            return None

        landmark = result.hand_landmarks[0][INDEX_FINGER_TIP]

        return landmark.x, landmark.y

    def draw(
        self,
        frame: NDArray[np.uint8],
        result: mp.tasks.vision.HandLandmarkerResult,
    ) -> NDArray[np.uint8]:
        height, width = frame.shape[:2]

        for hand_landmarks in result.hand_landmarks:
            points = [
                (
                    int(landmark.x * width),
                    int(landmark.y * height),
                )
                for landmark in hand_landmarks
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

        return frame

    def close(self) -> None:
        self._landmarker.close()
