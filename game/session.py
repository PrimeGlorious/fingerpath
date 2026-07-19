from enum import Enum

import pygame

from game.level import Level
from game.player import Player


class GameState(Enum):
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    WON = "won"


class GameSession:
    def __init__(
        self,
        level: Level,
        player: Player,
        surface_size: tuple[int, int],
    ) -> None:
        self.level = level
        self.player = player
        self.surface_size = surface_size
        self.cursor_position: tuple[int, int] | None = None
        self.state = GameState.READY

        self.reset()

    @property
    def status_text(self) -> str:
        if self.state is GameState.READY:
            return "Move your fingertip into START"

        if self.state is GameState.PAUSED:
            return "Move your fingertip back to the player"

        if self.state is GameState.WON:
            return "LEVEL COMPLETE - Press R to restart"

        return ""

    def reset(self) -> None:
        self.player.reset(self.level.start_zone.center)
        self.cursor_position = None
        self.state = GameState.READY

    def update(
        self,
        normalized_position: tuple[float, float] | None,
    ) -> None:
        if normalized_position is None:
            self.cursor_position = None

            if self.state is GameState.RUNNING:
                self.state = GameState.PAUSED

            return

        self.cursor_position = self._to_pixels(
            normalized_position
        )

        if self.state is GameState.READY:
            candidate = self.player.rect.copy()
            candidate.center = self.cursor_position

            if self.level.can_start(candidate):
                self.player.reset(self.cursor_position)
                self.state = GameState.RUNNING

            return

        if self.state is GameState.PAUSED:
            player_position = pygame.Vector2(
                self.player.rect.center
            )
            cursor_position = pygame.Vector2(
                self.cursor_position
            )

            if player_position.distance_to(cursor_position) <= 50:
                self.state = GameState.RUNNING

            return

        if self.state is GameState.WON:
            return

        self.player.move_towards(
            self.cursor_position,
            self.level.walls,
            self.level.bounds,
        )

        if self.level.is_finished(self.player.rect):
            self.state = GameState.WON

    def _to_pixels(
        self,
        position: tuple[float, float],
    ) -> tuple[int, int]:
        width, height = self.surface_size

        x = round(position[0] * (width - 1))
        y = round(position[1] * (height - 1))

        return x, y
