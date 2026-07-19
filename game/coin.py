import pygame


class Coin:
    def __init__(
        self,
        x: int,
        y: int,
        radius: int = 10,
    ) -> None:
        if radius <= 0:
            raise ValueError("Radius must be positive")

        self.position = pygame.Vector2(x, y)
        self.radius = radius
        self.collected = False

    def collides(self, rect: pygame.Rect) -> bool:
        if self.collected:
            return False

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

    def collect(self) -> None:
        self.collected = True

    def reset(self) -> None:
        self.collected = False

    def draw(self, surface: pygame.Surface) -> None:
        if self.collected:
            return

        center = (
            round(self.position.x),
            round(self.position.y),
        )

        pygame.draw.circle(
            surface,
            (155, 120, 20),
            center,
            self.radius + 2,
        )

        pygame.draw.circle(
            surface,
            (250, 220, 45),
            center,
            self.radius,
        )
