import pygame


class MovingHazard:
    def __init__(
        self,
        x: int,
        start_y: int,
        end_y: int,
        radius: int = 18,
        speed: float = 220.0,
    ) -> None:
        if start_y >= end_y:
            raise ValueError("Start position must be above end position")

        if radius <= 0:
            raise ValueError("Radius must be positive")

        if speed <= 0:
            raise ValueError("Speed must be positive")

        self.radius = radius
        self.speed = speed

        self._start_y = float(start_y)
        self._end_y = float(end_y)
        self._direction = 1.0

        self.position = pygame.Vector2(
            x,
            start_y,
        )

    def update(self, delta_time: float) -> None:
        self.position.y += (
            self.speed
            * self._direction
            * delta_time
        )

        if self.position.y >= self._end_y:
            self.position.y = self._end_y
            self._direction = -1.0
        elif self.position.y <= self._start_y:
            self.position.y = self._start_y
            self._direction = 1.0

    def collides(self, rect: pygame.Rect) -> bool:
        closest_x = max(
            rect.left,
            min(self.position.x, rect.right),
        )
        closest_y = max(
            rect.top,
            min(self.position.y, rect.bottom),
        )

        distance_x = self.position.x - closest_x
        distance_y = self.position.y - closest_y

        return (
            distance_x * distance_x
            + distance_y * distance_y
            <= self.radius * self.radius
        )

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(
            surface,
            (55, 95, 210),
            (
                round(self.position.x),
                round(self.position.y),
            ),
            self.radius,
        )
