import pygame

from game.session import GameSession, GameState


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
        self._zone_font = pygame.font.Font(None, 30)
        self._status_font = pygame.font.Font(None, 36)

        pygame.display.set_caption("Fingerpath")

    @property
    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def process_events(self) -> tuple[bool, bool]:
        running = True
        reset_requested = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_r
            ):
                reset_requested = True

        return running, reset_requested

    def render(self, session: GameSession) -> None:
        self._screen.fill((240, 240, 240))

        session.level.draw(
            self._screen,
            self._zone_font,
        )

        if session.cursor_position is not None:
            pygame.draw.circle(
                self._screen,
                (30, 130, 220),
                session.cursor_position,
                9,
                2,
            )

            if session.state is GameState.RUNNING:
                pygame.draw.line(
                    self._screen,
                    (120, 170, 220),
                    session.player.rect.center,
                    session.cursor_position,
                    1,
                )

        pygame.draw.rect(
            self._screen,
            (220, 30, 30),
            session.player.rect,
        )

        if session.status_text:
            text = self._status_font.render(
                session.status_text,
                True,
                (35, 40, 45),
            )

            background = text.get_rect(
                center=(self.width // 2, 32)
            ).inflate(24, 14)

            pygame.draw.rect(
                self._screen,
                (255, 255, 255),
                background,
                border_radius=6,
            )

            self._screen.blit(
                text,
                text.get_rect(
                    center=background.center,
                ),
            )

        pygame.display.flip()
        self._clock.tick(60)

    def close(self) -> None:
        pygame.quit()
