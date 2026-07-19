import pygame


class Level:
    def __init__(
        self,
        width: int,
        height: int,
    ) -> None:
        self.bounds = pygame.Rect(
            4,
            4,
            width - 8,
            height - 8,
        )

        self.start_zone = pygame.Rect(
            50,
            height // 2 - 60,
            120,
            120,
        )

        self.finish_zone = pygame.Rect(
            width - 170,
            height // 2 - 60,
            120,
            120,
        )

        wall_width = 40

        self.walls = [
            pygame.Rect(
                width // 3,
                self.bounds.top,
                wall_width,
                int(height * 0.72),
            ),
            pygame.Rect(
                width * 2 // 3,
                int(height * 0.28),
                wall_width,
                self.bounds.bottom - int(height * 0.28),
            ),
        ]

    def can_start(self, player_rect: pygame.Rect) -> bool:
        return self.start_zone.contains(player_rect)

    def is_finished(self, player_rect: pygame.Rect) -> bool:
        return self.finish_zone.contains(player_rect)

    def draw(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
    ) -> None:
        pygame.draw.rect(
            surface,
            (180, 230, 180),
            self.start_zone,
        )

        pygame.draw.rect(
            surface,
            (245, 215, 110),
            self.finish_zone,
        )

        for wall in self.walls:
            pygame.draw.rect(
                surface,
                (55, 65, 75),
                wall,
            )

        pygame.draw.rect(
            surface,
            (55, 65, 75),
            self.bounds,
            4,
        )

        start_text = font.render(
            "START",
            True,
            (30, 80, 30),
        )
        finish_text = font.render(
            "FINISH",
            True,
            (100, 75, 20),
        )

        surface.blit(
            start_text,
            start_text.get_rect(
                center=self.start_zone.center,
            ),
        )

        surface.blit(
            finish_text,
            finish_text.get_rect(
                center=self.finish_zone.center,
            ),
        )
