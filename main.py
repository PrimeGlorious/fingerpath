import time
from pathlib import Path

import cv2

from game.player import Player
from game.window import GameWindow
from vision.camera import Camera
from vision.coordinate_mapper import CoordinateMapper
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
    mapper = CoordinateMapper(
        left=0.15,
        top=0.15,
        right=0.85,
        bottom=0.85,
    )
    game_window = GameWindow()
    player = Player()

    started_at = time.perf_counter()
    game_position: tuple[float, float] | None = None
    running = True

    try:
        while running:
            running = game_window.process_events()

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

            height, width = output_frame.shape[:2]

            working_area_start = (
                int(mapper.left * width),
                int(mapper.top * height),
            )
            working_area_end = (
                int(mapper.right * width),
                int(mapper.bottom * height),
            )

            cv2.rectangle(
                output_frame,
                working_area_start,
                working_area_end,
                (255, 0, 0),
                2,
            )

            if fingertip is not None:
                smoothed_fingertip = smoother.update(fingertip)
                game_position = mapper.map(smoothed_fingertip)

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
                        f"camera=({smoothed_fingertip[0]:.3f}, "
                        f"{smoothed_fingertip[1]:.3f})"
                    ),
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )
                cv2.putText(
                    output_frame,
                    (
                        f"game=({game_position[0]:.3f}, "
                        f"{game_position[1]:.3f})"
                    ),
                    (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )
            else:
                smoother.reset()
                game_position = None

            player.update(
                game_position,
                game_window.size,
            )
            game_window.render(player)

            cv2.imshow(
                "Fingerpath Hand Tracking",
                output_frame,
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                running = False
    finally:
        game_window.close()
        tracker.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
