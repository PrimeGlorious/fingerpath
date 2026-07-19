import pygame

from game.coin import Coin
from game.hazard import MovingHazard


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

        self.hazards = [
            MovingHazard(
                x=width // 2,
                start_y=110,
                end_y=height - 110,
                radius=18,
                speed=220.0,
            ),
        ]

        self.coins = [
            Coin(
                x=240,
                y=height - 110,
            ),
            Coin(
                x=500,
                y=height - 140,
            ),
            Coin(
                x=560,
                y=120,
            ),
            Coin(
                x=730,
                y=120,
            ),
        ]

    @property
    def total_coins(self) -> int:
        return len(self.coins)

    @property
    def collected_coins(self) -> int:
        return sum(
            coin.collected
            for coin in self.coins
        )

    @property
    def finish_unlocked(self) -> bool:
        return (
            self.collected_coins
            == self.total_coins
        )

    def update(self, delta_time: float) -> None:
        for hazard in self.hazards:
            hazard.update(delta_time)

    def reset_round(self) -> None:
        for hazard in self.hazards:
            hazard.reset()

        for coin in self.coins:
            coin.reset()

    def collect_coins(
        self,
        player_rect: pygame.Rect,
    ) -> int:
        collected = 0

        for coin in self.coins:
            if not coin.collides(player_rect):
                continue

            coin.collect()
            collected += 1

        return collected

    def is_finished(self, player_rect: pygame.Rect) -> bool:
        return (
            self.finish_unlocked
            and self.finish_zone.contains(player_rect)
        )

    def player_hits_hazard(
        self,
        player_rect: pygame.Rect,
    ) -> bool:
        return any(
            hazard.collides(player_rect)
            for hazard in self.hazards
        )

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

        finish_color = (
            (245, 215, 110)
            if self.finish_unlocked
            else (175, 180, 185)
        )

        pygame.draw.rect(
            surface,
            finish_color,
            self.finish_zone,
        )

        for wall in self.walls:
            pygame.draw.rect(
                surface,
                (55, 65, 75),
                wall,
            )

        for coin in self.coins:
            coin.draw(surface)

        for hazard in self.hazards:
            hazard.draw(surface)

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
            (
                "FINISH"
                if self.finish_unlocked
                else "LOCKED"
            ),
            True,
            (
                (100, 75, 20)
                if self.finish_unlocked
                else (75, 80, 85)
            ),
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
