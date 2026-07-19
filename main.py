from pathlib import Path
from time import perf_counter

import cv2

from game.levels import create_level_definitions
from game.player import Player
from game.session import GameSession
from game.window import GameWindow
from vision.worker import VisionWorker


MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "hand_landmarker.task"
)


def main() -> None:
    game_window = GameWindow(
        target_fps=144
    )

    level_definitions = create_level_definitions(
        *game_window.size
    )

    player = Player()

    session = GameSession(
        level_definitions=level_definitions,
        player=player,
        surface_size=game_window.size,
        sensitivity=2.5,
        max_speed=850.0,
        input_deadzone=1.5,
        max_velocity_hold=0.075,
        death_delay=0.6,
    )

    vision_worker = VisionWorker(
        MODEL_PATH
    )

    running = True
    last_debug_sample_id = -1

    vision_worker.start()

    try:
        while running:
            delta_time = game_window.tick()

            (
                running,
                reset_requested,
                next_level_requested,
            ) = game_window.process_events()

            if not running:
                break

            if reset_requested:
                session.reset()

            if next_level_requested:
                session.next_level()

            snapshot = vision_worker.snapshot()

            session.update(
                position=snapshot.position,
                control_active=snapshot.control_active,
                sample_id=snapshot.sample_id,
                sample_time=snapshot.sample_time,
                delta_time=delta_time,
                current_time=perf_counter(),
            )

            game_window.render(
                session,
                snapshot.vision_fps,
            )

            if (
                snapshot.frame is not None
                and snapshot.sample_id
                != last_debug_sample_id
            ):
                last_debug_sample_id = (
                    snapshot.sample_id
                )

                cv2.imshow(
                    "Fingerpath Hand Tracking",
                    snapshot.frame,
                )

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    running = False
    finally:
        vision_worker.close()
        game_window.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
