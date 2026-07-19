import pygame


class GameWindow:
    def __init__(
        self,
        width: int = 960,
        height: int = 720,
    ) -> None:
        pygame.init()

        self.width = width
        self.height = height
        self._screen = pygame.display.set_mode(
            (self.width, self.height)
        )
        self._clock = pygame.time.Clock()

        pygame.display.set_caption("Fingerpath")

    def process_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        return True

    def render(
        self,
        position: tuple[float, float] | None,
    ) -> None:
        self._screen.fill((240, 240, 240))

        if position is not None:
            x = int(position[0] * self.width)
            y = int(position[1] * self.height)

            player_rect = pygame.Rect(0, 0, 24, 24)
            player_rect.center = (x, y)

            pygame.draw.rect(
                self._screen,
                (220, 30, 30),
                player_rect,
            )

        pygame.display.flip()
        self._clock.tick(60)

    def close(self) -> None:
        pygame.quit()
