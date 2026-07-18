import cv2
import numpy as np
from numpy.typing import NDArray


class Camera:
    def __init__(self, device_index: int = 0) -> None:
        self._capture = cv2.VideoCapture(device_index)

        if not self._capture.isOpened():
            raise RuntimeError("Failed to open camera")

    def read(self) -> NDArray[np.uint8]:
        success, frame = self._capture.read()

        if not success:
            raise RuntimeError("Failed to read camera frame")

        return frame

    def release(self) -> None:
        self._capture.release()
