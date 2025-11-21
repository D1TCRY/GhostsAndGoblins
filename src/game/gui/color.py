from __future__ import annotations
from collections.abc import Iterable


class Color(object):
    """
    ### Handles an RGB or RGBA color.
    Allowed initialization:\n
    - Color(r, g, b) -> alpha = 255
    - Color(r, g, b, a)
    - Color((r, g, b))
    - Color((r, g, b, a))
    - Color([r, g, b]) / Color([r, g, b, a])\n
    ---
    All channels must be integers 0..255.
    """

    def __init__(self, r_or_iterable: int | Iterable[int], g: int | None = None, b: int | None = None, a: int | None = None, /) -> None:
        # parsing input
        if isinstance(r_or_iterable, Iterable):
            values = list(r_or_iterable)
            if len(values) not in (3, 4) or not all(isinstance(c, int) for c in values):
                raise TypeError("< iterable color must be a sequence of 3 or 4 integers >")
            r, g, b = values[0], values[1], values[2]
            a = values[3] if len(values) == 4 else 255
        else:
            if not isinstance(r_or_iterable, int) or g is None or b is None:
                raise TypeError("< provide either (r, g, b[, a]) as integers or an iterable of 3/4 integers >")
            r = r_or_iterable
            a = 255 if a is None else a

        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def __str__(self) -> str:
        if self.a == 255:
            return f"< {self.__class__.__name__} | r: {self.r}, g: {self.g}, b: {self.b} >"
        return f"< {self.__class__.__name__} | r: {self.r}, g: {self.g}, b: {self.b}, a: {self.a} >"

    def __repr__(self) -> str:
        if self.a == 255:
            return f"{self.__class__.__name__}(r_or_iterable=({self.r}, {self.g}, {self.b}))"
        return f"{self.__class__.__name__}(r_or_iterable=({self.r}, {self.g}, {self.b}, {self.a}))"

    def __iter__(self):
        yield self.r
        yield self.g
        yield self.b
        yield self.a

    def __len__(self):
        return 3 if self.a == 255 else 4

    def __getitem__(self, index: int) -> int:
        if index == 0:
            return self.r
        elif index == 1:
            return self.g
        elif index == 2:
            return self.b
        elif index == 3 and self.a != 255:
            return self.a
        else:
            raise IndexError

    # helpers
    @staticmethod
    def _validate_channel(name: str, value: int) -> int:
        if not isinstance(value, int):
            raise TypeError(f"< {name} channel must be integer >")
        if not (0 <= value <= 255):
            raise ValueError(f"< {name} channel must be in range 0..255 >")
        return value

    # properties
    @property
    def r(self) -> int:
        return self.__r
    @r.setter
    def r(self, new: int) -> None:
        self.__r = self._validate_channel("r", new)

    @property
    def g(self) -> int:
        return self.__g
    @g.setter
    def g(self, new: int) -> None:
        self.__g = self._validate_channel("g", new)

    @property
    def b(self) -> int:
        return self.__b
    @b.setter
    def b(self, new: int) -> None:
        self.__b = self._validate_channel("b", new)

    @property
    def a(self) -> int:
        return self.__a
    @a.setter
    def a(self, new: int) -> None:
        self.__a = self._validate_channel("a", new)

    # view
    @property
    def rgb(self) -> tuple[int, int, int]:
        return (self.r, self.g, self.b)

    @property
    def rgba(self) -> tuple[int, int, int, int]:
        return (self.r, self.g, self.b, self.a)

    def with_alpha(self, alpha: int) -> Color:
        """Restituisce una copia con alpha modificato."""
        return Color((self.r, self.g, self.b, self._validate_channel("a", alpha)))