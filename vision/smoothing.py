class PositionSmoother:
    def __init__(self, alpha: float = 0.35) -> None:
        if not 0 < alpha <= 1:
            raise ValueError("Alpha must be between 0 and 1")

        self._alpha = alpha
        self._position: tuple[float, float] | None = None

    def update(
        self,
        position: tuple[float, float],
    ) -> tuple[float, float]:
        if self._position is None:
            self._position = position
            return position

        previous_x, previous_y = self._position
        current_x, current_y = position

        smoothed_x = (
            self._alpha * current_x
            + (1 - self._alpha) * previous_x
        )
        smoothed_y = (
            self._alpha * current_y
            + (1 - self._alpha) * previous_y
        )

        self._position = smoothed_x, smoothed_y

        return self._position

    def reset(self) -> None:
        self._position = None
