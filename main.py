from pathlib import Path
from time import perf_counter

import cv2

from game.levels import create_level_definitions
from game.menu import (
    MenuAction,
    MenuController,
    MenuScreen,
)
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
        level_transition_delay=1.5,
    )

    menu = MenuController(
        width=game_window.width,
        height=game_window.height,
        total_levels=len(level_definitions),
    )

    screen = MenuScreen.MAIN

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
                menu_requested,
            ) = game_window.process_events()

            if not running:
                break

            snapshot = vision_worker.snapshot()

            if menu_requested:
                if screen is MenuScreen.GAME:
                    screen = MenuScreen.MAIN
                    menu.set_screen(
                        MenuScreen.MAIN
                    )
                elif screen is MenuScreen.LEVEL_SELECT:
                    screen = MenuScreen.MAIN
                    menu.set_screen(
                        MenuScreen.MAIN
                    )
                else:
                    running = False

            if screen is MenuScreen.GAME:
                if reset_requested:
                    session.start_level(
                        session.level_index
                    )

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
            else:
                result = menu.update(
                    position=snapshot.position,
                    control_active=snapshot.control_active,
                    delta_time=delta_time,
                )

                if result.action is MenuAction.PLAY:
                    session.start_level(0)
                    screen = MenuScreen.GAME
                    menu.set_screen(
                        MenuScreen.GAME
                    )

                elif (
                    result.action
                    is MenuAction.OPEN_LEVEL_SELECT
                ):
                    screen = MenuScreen.LEVEL_SELECT
                    menu.set_screen(
                        MenuScreen.LEVEL_SELECT
                    )

                elif (
                    result.action
                    is MenuAction.START_LEVEL
                    and result.level_index is not None
                ):
                    session.start_level(
                        result.level_index
                    )
                    screen = MenuScreen.GAME
                    menu.set_screen(
                        MenuScreen.GAME
                    )

                elif result.action is MenuAction.BACK:
                    screen = MenuScreen.MAIN
                    menu.set_screen(
                        MenuScreen.MAIN
                    )

                elif result.action is MenuAction.QUIT:
                    running = False

                game_window.render_menu(
                    menu
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
