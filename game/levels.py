from game.level_definition import (
    CoinDefinition,
    HazardDefinition,
    LevelDefinition,
)


def create_level_definitions(
    width: int,
    height: int,
) -> tuple[LevelDefinition, ...]:
    first_level = LevelDefinition(
        start_zone=(
            50,
            height // 2 - 60,
            120,
            120,
        ),
        finish_zone=(
            width - 170,
            height // 2 - 60,
            120,
            120,
        ),
        walls=(
            (
                width // 3,
                4,
                40,
                int(height * 0.72),
            ),
            (
                width * 2 // 3,
                int(height * 0.28),
                40,
                height - int(height * 0.28) - 4,
            ),
        ),
        hazards=(
            HazardDefinition(
                x=width // 2,
                start_y=110,
                end_y=height - 110,
                radius=18,
                speed=220.0,
            ),
        ),
        coins=(
            CoinDefinition(
                x=240,
                y=height - 110,
            ),
            CoinDefinition(
                x=500,
                y=height - 140,
            ),
            CoinDefinition(
                x=560,
                y=120,
            ),
            CoinDefinition(
                x=730,
                y=120,
            ),
        ),
    )

    second_level = LevelDefinition(
        start_zone=(
            50,
            40,
            120,
            100,
        ),
        finish_zone=(
            width - 170,
            height - 140,
            120,
            100,
        ),
        walls=(
            (
                180,
                170,
                width - 184,
                36,
            ),
            (
                4,
                350,
                width - 184,
                36,
            ),
            (
                180,
                530,
                width - 184,
                36,
            ),
        ),
        hazards=(
            HazardDefinition(
                x=width // 2,
                start_y=225,
                end_y=315,
                radius=18,
                speed=260.0,
            ),
            HazardDefinition(
                x=width // 2,
                start_y=405,
                end_y=495,
                radius=18,
                speed=280.0,
            ),
        ),
        coins=(
            CoinDefinition(
                x=110,
                y=270,
            ),
            CoinDefinition(
                x=width - 110,
                y=270,
            ),
            CoinDefinition(
                x=width - 110,
                y=450,
            ),
            CoinDefinition(
                x=110,
                y=450,
            ),
            CoinDefinition(
                x=width // 2,
                y=height - 70,
            ),
        ),
    )

    return first_level, second_level
