from dataclasses import dataclass


RectDefinition = tuple[int, int, int, int]


@dataclass(frozen=True)
class HazardDefinition:
    x: int
    start_y: int
    end_y: int
    radius: int = 18
    speed: float = 220.0


@dataclass(frozen=True)
class CoinDefinition:
    x: int
    y: int
    radius: int = 10


@dataclass(frozen=True)
class LevelDefinition:
    start_zone: RectDefinition
    finish_zone: RectDefinition
    walls: tuple[RectDefinition, ...]
    hazards: tuple[HazardDefinition, ...]
    coins: tuple[CoinDefinition, ...]
