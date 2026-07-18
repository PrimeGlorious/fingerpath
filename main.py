import time
from pathlib import Path

import cv2

from vision.camera import Camera
from vision.hand_tracker import HandTracker


MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "hand_landmarker.task"
)


def main() -> None:
    camera = Camera()
    tracker = HandTracker(MODEL_PATH)
    started_at = time.perf_counter()

    try:
        while True:
            frame = camera.read()
            mirrored_frame = cv2.flip(frame, 1)

            timestamp_ms = int(
                (time.perf_counter() - started_at) * 1000
            )

            result = tracker.detect(
                mirrored_frame,
                timestamp_ms,
            )

            output_frame = tracker.draw(
                mirrored_frame,
                result,
            )

            cv2.imshow(
                "Fingerpath Hand Tracking",
                output_frame,
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        tracker.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
