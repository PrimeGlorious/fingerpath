import pygame


class Player:
    def __init__(self, size: int = 24) -> None:
        self.rect = pygame.Rect(0, 0, size, size)
        self.visible = False

    def update(
        self,
        position: tuple[float, float] | None,
        surface_size: tuple[int, int],
    ) -> None:
        if position is None:
            self.visible = False
            return

        width, height = surface_size

        x = int(position[0] * (width - 1))
        y = int(position[1] * (height - 1))

        self.rect.center = x, y
        self.rect.clamp_ip(
            pygame.Rect(0, 0, width, height)
        )

        self.visible = True
