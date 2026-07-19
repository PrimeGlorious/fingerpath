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

            fingertip = tracker.get_index_fingertip(result)

            output_frame = tracker.draw(
                mirrored_frame,
                result,
            )

            if fingertip is not None:
                x, y = fingertip
                height, width = output_frame.shape[:2]

                pixel_position = (
                    int(x * width),
                    int(y * height),
                )

                cv2.circle(
                    output_frame,
                    pixel_position,
                    10,
                    (0, 0, 255),
                    -1,
                )

                cv2.putText(
                    output_frame,
                    f"x={x:.3f} y={y:.3f}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
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
