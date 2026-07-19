from enum import Enum

import pygame

from game.level import Level
from game.level_definition import LevelDefinition
from game.player import Player


class GameState(Enum):
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    DEAD = "dead"
    WON = "won"


class GameSession:
    def __init__(
        self,
        level_definitions: tuple[
            LevelDefinition,
            ...
        ],
        player: Player,
        surface_size: tuple[int, int],
        sensitivity: float = 2.5,
        max_speed: float = 850.0,
        input_deadzone: float = 1.5,
        max_velocity_hold: float = 0.075,
        death_delay: float = 0.6,
    ) -> None:
        if not level_definitions:
            raise ValueError(
                "At least one level is required"
            )

        self.surface_size = surface_size
        self.player = player
        self.sensitivity = sensitivity
        self.max_speed = max_speed
        self.input_deadzone = input_deadzone
        self.max_velocity_hold = max_velocity_hold
        self.death_delay = death_delay

        width, height = surface_size

        self._levels = [
            Level(
                width,
                height,
                definition,
            )
            for definition in level_definitions
        ]

        self.level_index = 0
        self.state = GameState.READY
        self.control_active = False
        self.deaths = 0

        self._velocity = pygame.Vector2()
        self._velocity_valid_until = 0.0
        self._last_input_position: pygame.Vector2 | None = None
        self._last_sample_id = -1
        self._last_sample_time = 0.0
        self._dead_until = 0.0

        self.reset()

    @property
    def level(self) -> Level:
        return self._levels[self.level_index]

    @property
    def level_number(self) -> int:
        return self.level_index + 1

    @property
    def total_levels(self) -> int:
        return len(self._levels)

    @property
    def is_last_level(self) -> bool:
        return (
            self.level_index
            == self.total_levels - 1
        )

    @property
    def status_text(self) -> str:
        if self.state is GameState.READY:
            return "Release the pinch to start"

        if self.state is GameState.PAUSED:
            return "Release the pinch to resume"

        if self.state is GameState.DEAD:
            return "HIT - Returning to START"

        if self.state is GameState.WON:
            if self.is_last_level:
                return (
                    "ALL LEVELS COMPLETE "
                    "- Press R to restart"
                )

            return (
                "LEVEL COMPLETE "
                "- Press Enter"
            )

        return ""

    def reset(self) -> None:
        self.level_index = 0
        self.deaths = 0

        for level in self._levels:
            level.reset_round()

        self._reset_player_state()

    def next_level(self) -> None:
        if self.state is not GameState.WON:
            return

        if self.is_last_level:
            return

        self.level_index += 1
        self.level.reset_round()
        self._reset_player_state()

    def update(
        self,
        position: tuple[float, float] | None,
        control_active: bool,
        sample_id: int,
        sample_time: float,
        delta_time: float,
        current_time: float,
    ) -> None:
        self.level.update(delta_time)

        if self.state is GameState.DEAD:
            if current_time >= self._dead_until:
                self._reset_round()

            return

        if sample_id != self._last_sample_id:
            self._last_sample_id = sample_id

            self._process_input_sample(
                position,
                control_active,
                sample_time,
            )

        if self.state is not GameState.RUNNING:
            return

        if current_time >= self._velocity_valid_until:
            self._velocity.update(0, 0)

        self.player.move_by(
            self._velocity * delta_time,
            self.level.walls,
            self.level.bounds,
        )

        if self.level.player_hits_hazard(
            self.player.rect
        ):
            self._kill_player(current_time)
            return

        self.level.collect_coins(
            self.player.rect
        )

        if self.level.is_finished(
            self.player.rect
        ):
            self._stop_movement()
            self.control_active = False
            self.state = GameState.WON

    def _process_input_sample(
        self,
        position: tuple[float, float] | None,
        control_active: bool,
        sample_time: float,
    ) -> None:
        self.control_active = (
            control_active
            and position is not None
        )

        if not self.control_active:
            self._stop_movement()
            self._last_input_position = None

            if self.state is GameState.RUNNING:
                self.state = GameState.PAUSED

            return

        current_position = self._to_control_pixels(
            position
        )

        if self.state in (
            GameState.READY,
            GameState.PAUSED,
        ):
            self.state = GameState.RUNNING
            self._stop_movement()
            self._last_input_position = (
                current_position
            )
            self._last_sample_time = sample_time
            return

        if self.state is GameState.WON:
            return

        if self._last_input_position is None:
            self._stop_movement()
            self._last_input_position = (
                current_position
            )
            self._last_sample_time = sample_time
            return

        sample_delta_time = (
            sample_time - self._last_sample_time
        )

        input_delta = (
            current_position
            - self._last_input_position
        )

        self._last_input_position = (
            current_position
        )
        self._last_sample_time = sample_time

        if sample_delta_time <= 0:
            self._stop_movement()
            return

        if (
            input_delta.length()
            <= self.input_deadzone
        ):
            self._stop_movement()
            return

        velocity = (
            input_delta
            * self.sensitivity
            / sample_delta_time
        )

        if velocity.length() > self.max_speed:
            velocity.scale_to_length(
                self.max_speed
            )

        velocity_hold = min(
            max(
                sample_delta_time * 1.15,
                0.035,
            ),
            self.max_velocity_hold,
        )

        self._velocity.update(velocity)
        self._velocity_valid_until = (
            sample_time + velocity_hold
        )

    def _kill_player(
        self,
        current_time: float,
    ) -> None:
        self.deaths += 1
        self.state = GameState.DEAD
        self.control_active = False
        self._dead_until = (
            current_time + self.death_delay
        )
        self._last_input_position = None
        self._stop_movement()

    def _reset_round(self) -> None:
        self.level.reset_round()
        self._reset_player_state()

    def _reset_player_state(self) -> None:
        self.player.reset(
            self.level.start_zone.center
        )

        self.state = GameState.READY
        self.control_active = False

        self._stop_movement()
        self._last_input_position = None
        self._last_sample_id = -1
        self._last_sample_time = 0.0
        self._dead_until = 0.0

    def _stop_movement(self) -> None:
        self._velocity.update(0, 0)
        self._velocity_valid_until = 0.0

    def _to_control_pixels(
        self,
        position: tuple[float, float],
    ) -> pygame.Vector2:
        width, height = self.surface_size

        return pygame.Vector2(
            position[0] * width,
            position[1] * height,
        )
