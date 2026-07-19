import os
from threading import Event, Lock, Thread

import cv2
import numpy as np
from numpy.typing import NDArray


class Camera:
    def __init__(
        self,
        device_index: int = 0,
        width: int = 320,
        height: int = 240,
        target_fps: int = 60,
    ) -> None:
        backend = (
            cv2.CAP_DSHOW
            if os.name == "nt"
            else cv2.CAP_ANY
        )

        self._capture = cv2.VideoCapture(
            device_index,
            backend,
        )

        if not self._capture.isOpened():
            raise RuntimeError("Failed to open camera")

        if os.name == "nt":
            self._capture.set(
                cv2.CAP_PROP_FOURCC,
                cv2.VideoWriter_fourcc(*"MJPG"),
            )

        self._capture.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            width,
        )
        self._capture.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            height,
        )
        self._capture.set(
            cv2.CAP_PROP_FPS,
            target_fps,
        )
        self._capture.set(
            cv2.CAP_PROP_BUFFERSIZE,
            1,
        )

        self._stop_event = Event()
        self._lock = Lock()
        self._frame: NDArray[np.uint8] | None = None
        self._frame_id = 0
        self._error: Exception | None = None

        self._thread = Thread(
            target=self._capture_loop,
            name="camera-capture",
            daemon=True,
        )

        self._thread.start()

    def read_latest(
        self,
        last_frame_id: int,
    ) -> tuple[int, NDArray[np.uint8]] | None:
        with self._lock:
            error = self._error

            if error is not None:
                raise RuntimeError(
                    "Camera capture failed"
                ) from error

            if (
                self._frame is None
                or self._frame_id == last_frame_id
            ):
                return None

            return (
                self._frame_id,
                self._frame.copy(),
            )

    def close(self) -> None:
        self._stop_event.set()
        self._thread.join(timeout=2)
        self._capture.release()

    def _capture_loop(self) -> None:
        try:
            while not self._stop_event.is_set():
                success, frame = self._capture.read()

                if not success:
                    if self._stop_event.is_set():
                        return

                    raise RuntimeError(
                        "Failed to read camera frame"
                    )

                with self._lock:
                    self._frame = frame
                    self._frame_id += 1
        except Exception as error:
            with self._lock:
                self._error = error
