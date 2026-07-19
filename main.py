import time
from pathlib import Path

import cv2

from vision.camera import Camera
from vision.hand_tracker import HandTracker
from vision.smoothing import PositionSmoother


MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "hand_landmarker.task"
)


def main() -> None:
    camera = Camera()
    tracker = HandTracker(MODEL_PATH)
    smoother = PositionSmoother(alpha=0.35)
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
                smoothed_fingertip = smoother.update(fingertip)

                height, width = output_frame.shape[:2]

                raw_position = (
                    int(fingertip[0] * width),
                    int(fingertip[1] * height),
                )

                smoothed_position = (
                    int(smoothed_fingertip[0] * width),
                    int(smoothed_fingertip[1] * height),
                )

                cv2.circle(
                    output_frame,
                    raw_position,
                    5,
                    (0, 255, 255),
                    -1,
                )

                cv2.circle(
                    output_frame,
                    smoothed_position,
                    10,
                    (0, 0, 255),
                    -1,
                )

                cv2.putText(
                    output_frame,
                    (
                        f"x={smoothed_fingertip[0]:.3f} "
                        f"y={smoothed_fingertip[1]:.3f}"
                    ),
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )
            else:
                smoother.reset()

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
