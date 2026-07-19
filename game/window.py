import pygame

from game.session import GameSession


class GameWindow:
    def __init__(
        self,
        width: int = 960,
        height: int = 720,
        target_fps: int = 144,
    ) -> None:
        pygame.init()

        self.width = width
        self.height = height
        self.target_fps = target_fps

        self._screen = pygame.display.set_mode(
            (self.width, self.height)
        )
        self._clock = pygame.time.Clock()
        self._zone_font = pygame.font.Font(None, 30)
        self._status_font = pygame.font.Font(None, 36)
        self._info_font = pygame.font.Font(None, 26)

        pygame.display.set_caption("Fingerpath")

    @property
    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def tick(self) -> float:
        milliseconds = self._clock.tick_busy_loop(
            self.target_fps
        )

        return max(
            milliseconds / 1000.0,
            0.001,
        )

    def process_events(
        self,
    ) -> tuple[bool, bool, bool]:
        running = True
        reset_requested = False
        next_level_requested = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_r:
                reset_requested = True

            if event.key == pygame.K_RETURN:
                next_level_requested = True

        return (
            running,
            reset_requested,
            next_level_requested,
        )

    def render(
        self,
        session: GameSession,
        vision_fps: float,
    ) -> None:
        self._screen.fill((240, 240, 240))

        session.level.draw(
            self._screen,
            self._zone_font,
        )

        pygame.draw.rect(
            self._screen,
            (220, 30, 30),
            session.player.rect,
        )

        if session.status_text:
            status_surface = self._status_font.render(
                session.status_text,
                True,
                (35, 40, 45),
            )

            status_background = status_surface.get_rect(
                center=(self.width // 2, 32)
            ).inflate(24, 14)

            pygame.draw.rect(
                self._screen,
                (255, 255, 255),
                status_background,
                border_radius=6,
            )

            self._screen.blit(
                status_surface,
                status_surface.get_rect(
                    center=status_background.center
                ),
            )

        control_text = (
            "CONTROL ACTIVE"
            if session.control_active
            else "CONTROL PAUSED"
        )

        control_color = (
            (25, 145, 65)
            if session.control_active
            else (170, 45, 45)
        )

        control_surface = self._info_font.render(
            control_text,
            True,
            control_color,
        )

        fps_surface = self._info_font.render(
            (
                f"GAME {self._clock.get_fps():.0f} FPS"
                f" | VISION {vision_fps:.0f} FPS"
            ),
            True,
            (55, 60, 65),
        )

        deaths_surface = self._info_font.render(
            f"DEATHS {session.deaths}",
            True,
            (55, 60, 65),
        )

        level_surface = self._info_font.render(
            (
                f"LEVEL {session.level_number}"
                f"/{session.total_levels}"
            ),
            True,
            (55, 60, 65),
        )

        coins_surface = self._info_font.render(
            (
                f"COINS "
                f"{session.level.collected_coins}"
                f"/{session.level.total_coins}"
            ),
            True,
            (55, 60, 65),
        )

        self._screen.blit(
            control_surface,
            (16, 16),
        )

        self._screen.blit(
            fps_surface,
            (
                self.width
                - fps_surface.get_width()
                - 16,
                16,
            ),
        )

        self._screen.blit(
            deaths_surface,
            (
                16,
                self.height
                - deaths_surface.get_height()
                - 14,
            ),
        )

        self._screen.blit(
            level_surface,
            (
                (
                    self.width
                    - level_surface.get_width()
                )
                // 2,
                self.height
                - level_surface.get_height()
                - 14,
            ),
        )

        self._screen.blit(
            coins_surface,
            (
                self.width
                - coins_surface.get_width()
                - 16,
                self.height
                - coins_surface.get_height()
                - 14,
            ),
        )

        pygame.display.flip()

    def close(self) -> None:
        pygame.quit()
