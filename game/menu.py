from dataclasses import dataclass
from enum import Enum

import pygame


class MenuScreen(Enum):
    MAIN = "main"
    LEVEL_SELECT = "level_select"
    GAME = "game"


class MenuAction(Enum):
    NONE = "none"
    PLAY = "play"
    OPEN_LEVEL_SELECT = "open_level_select"
    START_LEVEL = "start_level"
    BACK = "back"
    QUIT = "quit"


@dataclass(frozen=True)
class MenuResult:
    action: MenuAction
    level_index: int | None = None


class MenuButton:
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        action: MenuAction,
        level_index: int | None = None,
    ) -> None:
        self.rect = rect
        self.text = text
        self.action = action
        self.level_index = level_index
        self.hover_progress = 0.0

    def update(
        self,
        hovered: bool,
        delta_time: float,
    ) -> None:
        direction = 1.0 if hovered else -1.0

        self.hover_progress = max(
            0.0,
            min(
                1.0,
                self.hover_progress
                + direction * delta_time * 8.0,
            ),
        )

    def draw(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
    ) -> None:
        progress = self.hover_progress

        fill_color = (
            round(248 - 42 * progress),
            round(248 - 30 * progress),
            round(252 - 5 * progress),
        )

        border_color = (
            30,
            45,
            95,
        )

        scale = 1.0 + progress * 0.04

        draw_rect = pygame.Rect(
            0,
            0,
            round(self.rect.width * scale),
            round(self.rect.height * scale),
        )
        draw_rect.center = self.rect.center

        pygame.draw.rect(
            surface,
            fill_color,
            draw_rect,
        )

        pygame.draw.rect(
            surface,
            border_color,
            draw_rect,
            4,
        )

        text_surface = font.render(
            self.text,
            True,
            border_color,
        )

        surface.blit(
            text_surface,
            text_surface.get_rect(
                center=draw_rect.center,
            ),
        )


class MenuController:
    def __init__(
        self,
        width: int,
        height: int,
        total_levels: int,
    ) -> None:
        self.width = width
        self.height = height
        self.total_levels = total_levels

        self.screen = MenuScreen.MAIN

        self._title_font = pygame.font.Font(
            None,
            86,
        )
        self._button_font = pygame.font.Font(
            None,
            42,
        )
        self._level_font = pygame.font.Font(
            None,
            38,
        )
        self._info_font = pygame.font.Font(
            None,
            28,
        )

        self._cursor: pygame.Vector2 | None = None
        self._click_armed = False

        self._main_buttons = self._create_main_buttons()
        self._level_buttons = self._create_level_buttons()
        self._back_button = MenuButton(
            pygame.Rect(
                40,
                height - 90,
                150,
                52,
            ),
            "BACK",
            MenuAction.BACK,
        )

    def set_screen(
        self,
        screen: MenuScreen,
    ) -> None:
        self.screen = screen
        self._click_armed = False

        for button in self._all_buttons:
            button.hover_progress = 0.0

    def update(
        self,
        position: tuple[float, float] | None,
        control_active: bool,
        delta_time: float,
    ) -> MenuResult:
        clicked = False

        if position is None:
            self._cursor = None
            self._click_armed = False
        else:
            self._cursor = pygame.Vector2(
                position[0] * self.width,
                position[1] * self.height,
            )

            if control_active:
                self._click_armed = True
            elif self._click_armed:
                clicked = True
                self._click_armed = False

        buttons = self._current_buttons

        hovered_button: MenuButton | None = None

        if self._cursor is not None:
            for button in buttons:
                if button.rect.collidepoint(
                    self._cursor
                ):
                    hovered_button = button
                    break

        for button in buttons:
            button.update(
                button is hovered_button,
                delta_time,
            )

        if clicked and hovered_button is not None:
            return MenuResult(
                action=hovered_button.action,
                level_index=hovered_button.level_index,
            )

        return MenuResult(
            action=MenuAction.NONE,
        )

    def draw(
        self,
        surface: pygame.Surface,
    ) -> None:
        surface.fill(
            (232, 235, 246)
        )

        self._draw_grid(surface)

        if self.screen is MenuScreen.MAIN:
            self._draw_main(surface)
        elif self.screen is MenuScreen.LEVEL_SELECT:
            self._draw_level_select(surface)

        self._draw_cursor(surface)

    @property
    def _current_buttons(
        self,
    ) -> list[MenuButton]:
        if self.screen is MenuScreen.MAIN:
            return self._main_buttons

        if self.screen is MenuScreen.LEVEL_SELECT:
            return [
                *self._level_buttons,
                self._back_button,
            ]

        return []

    @property
    def _all_buttons(
        self,
    ) -> list[MenuButton]:
        return [
            *self._main_buttons,
            *self._level_buttons,
            self._back_button,
        ]

    def _create_main_buttons(
        self,
    ) -> list[MenuButton]:
        button_width = 310
        button_height = 68
        gap = 22

        start_y = 310

        definitions = (
            (
                "PLAY",
                MenuAction.PLAY,
            ),
            (
                "LEVEL SELECT",
                MenuAction.OPEN_LEVEL_SELECT,
            ),
            (
                "QUIT",
                MenuAction.QUIT,
            ),
        )

        return [
            MenuButton(
                pygame.Rect(
                    (
                        self.width
                        - button_width
                    )
                    // 2,
                    start_y
                    + index
                    * (
                        button_height
                        + gap
                    ),
                    button_width,
                    button_height,
                ),
                text,
                action,
            )
            for index, (
                text,
                action,
            ) in enumerate(definitions)
        ]

    def _create_level_buttons(
        self,
    ) -> list[MenuButton]:
        columns = 5
        button_width = 130
        button_height = 90
        horizontal_gap = 22
        vertical_gap = 24

        total_width = (
            columns * button_width
            + (columns - 1)
            * horizontal_gap
        )

        start_x = (
            self.width - total_width
        ) // 2
        start_y = 250

        buttons = []

        for level_index in range(
            self.total_levels
        ):
            column = level_index % columns
            row = level_index // columns

            buttons.append(
                MenuButton(
                    pygame.Rect(
                        start_x
                        + column
                        * (
                            button_width
                            + horizontal_gap
                        ),
                        start_y
                        + row
                        * (
                            button_height
                            + vertical_gap
                        ),
                        button_width,
                        button_height,
                    ),
                    f"{level_index + 1:02d}",
                    MenuAction.START_LEVEL,
                    level_index=level_index,
                )
            )

        return buttons

    def _draw_main(
        self,
        surface: pygame.Surface,
    ) -> None:
        title_surface = self._title_font.render(
            "FINGERPATH",
            True,
            (30, 45, 95),
        )

        subtitle_surface = (
            self._info_font.render(
                "MOVE WITH YOUR FINGER",
                True,
                (60, 70, 105),
            )
        )

        instruction_surface = (
            self._info_font.render(
                "PINCH TO SELECT",
                True,
                (60, 70, 105),
            )
        )

        surface.blit(
            title_surface,
            title_surface.get_rect(
                center=(
                    self.width // 2,
                    140,
                ),
            ),
        )

        surface.blit(
            subtitle_surface,
            subtitle_surface.get_rect(
                center=(
                    self.width // 2,
                    205,
                ),
            ),
        )

        surface.blit(
            instruction_surface,
            instruction_surface.get_rect(
                center=(
                    self.width // 2,
                    240,
                ),
            ),
        )

        for button in self._main_buttons:
            button.draw(
                surface,
                self._button_font,
            )

    def _draw_level_select(
        self,
        surface: pygame.Surface,
    ) -> None:
        title_surface = self._title_font.render(
            "SELECT LEVEL",
            True,
            (30, 45, 95),
        )

        instruction_surface = (
            self._info_font.render(
                "ALL LEVELS ARE AVAILABLE",
                True,
                (60, 70, 105),
            )
        )

        surface.blit(
            title_surface,
            title_surface.get_rect(
                center=(
                    self.width // 2,
                    115,
                ),
            ),
        )

        surface.blit(
            instruction_surface,
            instruction_surface.get_rect(
                center=(
                    self.width // 2,
                    175,
                ),
            ),
        )

        for button in self._level_buttons:
            button.draw(
                surface,
                self._level_font,
            )

        self._back_button.draw(
            surface,
            self._info_font,
        )

    def _draw_grid(
        self,
        surface: pygame.Surface,
    ) -> None:
        grid_color = (
            215,
            220,
            238,
        )

        spacing = 40

        for x in range(
            0,
            self.width,
            spacing,
        ):
            pygame.draw.line(
                surface,
                grid_color,
                (x, 0),
                (x, self.height),
                1,
            )

        for y in range(
            0,
            self.height,
            spacing,
        ):
            pygame.draw.line(
                surface,
                grid_color,
                (0, y),
                (self.width, y),
                1,
            )

    def _draw_cursor(
        self,
        surface: pygame.Surface,
    ) -> None:
        if self._cursor is None:
            return

        center = (
            round(self._cursor.x),
            round(self._cursor.y),
        )

        pygame.draw.circle(
            surface,
            (255, 255, 255),
            center,
            15,
        )

        pygame.draw.circle(
            surface,
            (215, 35, 45),
            center,
            15,
            4,
        )

        pygame.draw.circle(
            surface,
            (215, 35, 45),
            center,
            4,
        )
