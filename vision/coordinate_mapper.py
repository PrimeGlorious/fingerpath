class CoordinateMapper:
    def __init__(
        self,
        left: float,
        top: float,
        right: float,
        bottom: float,
    ) -> None:
        if not 0 <= left < right <= 1:
            raise ValueError("Invalid horizontal bounds")

        if not 0 <= top < bottom <= 1:
            raise ValueError("Invalid vertical bounds")

        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def map(
        self,
        position: tuple[float, float],
    ) -> tuple[float, float]:
        x, y = position

        mapped_x = (x - self.left) / (self.right - self.left)
        mapped_y = (y - self.top) / (self.bottom - self.top)

        return (
            max(0.0, min(1.0, mapped_x)),
            max(0.0, min(1.0, mapped_y)),
        )
