from math import pi
from time import perf_counter


class LowPassFilter:
    def __init__(self) -> None:
        self._value: float | None = None

    def update(
        self,
        value: float,
        alpha: float,
    ) -> float:
        if self._value is None:
            self._value = value
            return value

        self._value = (
            alpha * value
            + (1.0 - alpha) * self._value
        )

        return self._value

    def reset(self) -> None:
        self._value = None


class OneEuroFilter:
    def __init__(
        self,
        min_cutoff: float,
        beta: float,
        derivative_cutoff: float,
    ) -> None:
        if min_cutoff <= 0:
            raise ValueError("Minimum cutoff must be positive")

        if beta < 0:
            raise ValueError("Beta cannot be negative")

        if derivative_cutoff <= 0:
            raise ValueError(
                "Derivative cutoff must be positive"
            )

        self._min_cutoff = min_cutoff
        self._beta = beta
        self._derivative_cutoff = derivative_cutoff

        self._signal_filter = LowPassFilter()
        self._derivative_filter = LowPassFilter()

        self._last_raw_value: float | None = None
        self._last_timestamp: float | None = None

    def update(
        self,
        value: float,
        timestamp: float | None = None,
    ) -> float:
        current_time = (
            perf_counter()
            if timestamp is None
            else timestamp
        )

        if (
            self._last_raw_value is None
            or self._last_timestamp is None
        ):
            self._last_raw_value = value
            self._last_timestamp = current_time

            return self._signal_filter.update(
                value,
                1.0,
            )

        delta_time = max(
            current_time - self._last_timestamp,
            0.000001,
        )

        raw_derivative = (
            value - self._last_raw_value
        ) / delta_time

        filtered_derivative = (
            self._derivative_filter.update(
                raw_derivative,
                self._alpha(
                    delta_time,
                    self._derivative_cutoff,
                ),
            )
        )

        cutoff = (
            self._min_cutoff
            + self._beta * abs(filtered_derivative)
        )

        filtered_value = self._signal_filter.update(
            value,
            self._alpha(
                delta_time,
                cutoff,
            ),
        )

        self._last_raw_value = value
        self._last_timestamp = current_time

        return filtered_value

    def reset(self) -> None:
        self._signal_filter.reset()
        self._derivative_filter.reset()
        self._last_raw_value = None
        self._last_timestamp = None

    def _alpha(
        self,
        delta_time: float,
        cutoff: float,
    ) -> float:
        time_constant = 1.0 / (2.0 * pi * cutoff)

        return 1.0 / (
            1.0 + time_constant / delta_time
        )


class OneEuroFilter2D:
    def __init__(
        self,
        min_cutoff: float = 2.5,
        beta: float = 2.0,
        derivative_cutoff: float = 1.0,
    ) -> None:
        self._x_filter = OneEuroFilter(
            min_cutoff,
            beta,
            derivative_cutoff,
        )

        self._y_filter = OneEuroFilter(
            min_cutoff,
            beta,
            derivative_cutoff,
        )

    def update(
        self,
        position: tuple[float, float],
        timestamp: float | None = None,
    ) -> tuple[float, float]:
        current_time = (
            perf_counter()
            if timestamp is None
            else timestamp
        )

        return (
            self._x_filter.update(
                position[0],
                current_time,
            ),
            self._y_filter.update(
                position[1],
                current_time,
            ),
        )

    def reset(self) -> None:
        self._x_filter.reset()
        self._y_filter.reset()
