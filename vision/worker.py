from dataclasses import dataclass
from pathlib import Path
from threading import Event, Lock, Thread
from time import perf_counter, sleep

import cv2
import numpy as np
from numpy.typing import NDArray

from vision.camera import Camera
from vision.hand_tracker import HandTracker


@dataclass(frozen=True)
class VisionSnapshot:
    position: tuple[float, float] | None
    control_active: bool
    frame: NDArray[np.uint8] | None
    sample_id: int
    sample_time: float
    vision_fps: float


class VisionWorker:
    def __init__(
        self,
        model_path: str | Path,
    ) -> None:
        self._model_path = model_path

        self._stop_event = Event()
        self._lock = Lock()
        self._thread = Thread(
            target=self._run,
            name="vision-worker",
            daemon=True,
        )

        self._position: tuple[float, float] | None = None
        self._control_active = False
        self._frame: NDArray[np.uint8] | None = None
        self._sample_id = 0
        self._sample_time = perf_counter()
        self._vision_fps = 0.0
        self._error: Exception | None = None

    def start(self) -> None:
        self._thread.start()

    def snapshot(self) -> VisionSnapshot:
        with self._lock:
            error = self._error

            snapshot = VisionSnapshot(
                position=self._position,
                control_active=self._control_active,
                frame=self._frame,
                sample_id=self._sample_id,
                sample_time=self._sample_time,
                vision_fps=self._vision_fps,
            )

        if error is not None:
            raise RuntimeError(
                "Vision worker failed"
            ) from error

        return snapshot

    def close(self) -> None:
        self._stop_event.set()
        self._thread.join(timeout=3)

    def _run(self) -> None:
        camera: Camera | None = None
        tracker: HandTracker | None = None

        try:
            camera = Camera(
                width=320,
                height=240,
                target_fps=60,
            )

            tracker = HandTracker(
                self._model_path,
                pinch_on_distance=32.0,
                pinch_off_distance=44.0,
            )

            started_at = perf_counter()
            previous_result_time = started_at
            previous_timestamp_ms = -1
            last_frame_id = -1
            vision_fps = 0.0

            while not self._stop_event.is_set():
                latest_frame = camera.read_latest(
                    last_frame_id
                )

                if latest_frame is None:
                    sleep(0.001)
                    continue

                last_frame_id, frame = latest_frame

                mirrored_frame = cv2.flip(
                    frame,
                    1,
                )

                timestamp_ms = max(
                    int(
                        (
                            perf_counter()
                            - started_at
                        )
                        * 1000
                    ),
                    previous_timestamp_ms + 1,
                )
                previous_timestamp_ms = timestamp_ms

                result = tracker.detect(
                    mirrored_frame,
                    timestamp_ms,
                )

                (
                    fingertip,
                    control_active,
                    tip_distance,
                ) = tracker.get_control_input(
                    result,
                    measurement_size=(640, 480),
                )

                sample_time = perf_counter()

                result_delta = max(
                    sample_time - previous_result_time,
                    0.000001,
                )
                previous_result_time = sample_time

                instant_fps = 1.0 / result_delta

                vision_fps = (
                    instant_fps
                    if vision_fps == 0.0
                    else vision_fps * 0.9
                    + instant_fps * 0.1
                )

                output_frame = tracker.draw(
                    mirrored_frame,
                    result,
                    control_active,
                )

                status_text = (
                    "CONTROL ACTIVE"
                    if control_active
                    else "CONTROL PAUSED"
                )

                status_color = (
                    (0, 255, 0)
                    if control_active
                    else (0, 0, 255)
                )

                cv2.putText(
                    output_frame,
                    status_text,
                    (12, 28),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    status_color,
                    2,
                )

                if tip_distance is not None:
                    cv2.putText(
                        output_frame,
                        f"TIP DISTANCE {tip_distance:.1f}",
                        (12, 54),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        (255, 255, 255),
                        2,
                    )

                cv2.putText(
                    output_frame,
                    f"VISION FPS {vision_fps:.0f}",
                    (12, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2,
                )

                with self._lock:
                    self._position = fingertip
                    self._control_active = control_active
                    self._frame = output_frame
                    self._sample_id += 1
                    self._sample_time = sample_time
                    self._vision_fps = vision_fps
        except Exception as error:
            with self._lock:
                self._error = error
        finally:
            if tracker is not None:
                tracker.close()

            if camera is not None:
                camera.close()
