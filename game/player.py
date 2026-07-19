from math import ceil

import pygame


class Player:
    def __init__(self, size: int = 30) -> None:
        self.size = size
        self.rect = pygame.Rect(0, 0, size, size)
        self._position = pygame.Vector2()

    def reset(self, center: tuple[int, int]) -> None:
        self._position.update(center)
        self.rect.center = center

    def move_towards(
        self,
        target: tuple[int, int],
        walls: list[pygame.Rect],
        bounds: pygame.Rect,
    ) -> None:
        target_position = pygame.Vector2(target)
        delta = target_position - self._position
        distance = delta.length()

        if distance == 0:
            return

        max_step = max(1.0, self.size / 4)
        step_count = max(1, ceil(distance / max_step))
        step = delta / step_count

        for _ in range(step_count):
            self._move_axis(
                step.x,
                0,
                walls,
                bounds,
            )
            self._move_axis(
                0,
                step.y,
                walls,
                bounds,
            )

    def _move_axis(
        self,
        delta_x: float,
        delta_y: float,
        walls: list[pygame.Rect],
        bounds: pygame.Rect,
    ) -> None:
        if delta_x:
            self._position.x += delta_x
            self.rect.centerx = round(self._position.x)

            for wall in walls:
                if not self.rect.colliderect(wall):
                    continue

                if delta_x > 0:
                    self.rect.right = wall.left
                else:
                    self.rect.left = wall.right

                self._position.x = self.rect.centerx

        if delta_y:
            self._position.y += delta_y
            self.rect.centery = round(self._position.y)

            for wall in walls:
                if not self.rect.colliderect(wall):
                    continue

                if delta_y > 0:
                    self.rect.bottom = wall.top
                else:
                    self.rect.top = wall.bottom

                self._position.y = self.rect.centery

        self.rect.clamp_ip(bounds)
        self._position.update(self.rect.center)
