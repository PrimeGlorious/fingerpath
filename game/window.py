import pygame

from game.player import Player


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

    @property
    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def process_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        return True

    def render(self, player: Player) -> None:
        self._screen.fill((240, 240, 240))

        if player.visible:
            pygame.draw.rect(
                self._screen,
                (220, 30, 30),
                player.rect,
            )

        pygame.display.flip()
        self._clock.tick(60)

    def close(self) -> None:
        pygame.quit()
