from __future__ import annotations
from typing import Self
import g2d_lib.g2d as g2d
import random
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

    def __init__(self, r_or_iterable: int | Iterable[int], g: int | None = None, b: int | None = None, a: int | None = None) -> None:
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

    @property
    def g2d(self) -> tuple[int, int, int, int]:
        return self.rgba

    def with_alpha(self, alpha: int) -> Color:
        """Restituisce una copia con alpha modificato."""
        return Color((self.r, self.g, self.b, self._validate_channel("a", alpha)))
    


class Position(object):
    def __init__(self, x: float | int, y: float | int) -> None:
        self.x = x
        self.y = y
    
    def __str__(self) -> str:
        return f"< {self.__class__.__name__} | x: {self.x}, y: {self.y} >"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(x={self.x}, y={self.y})"
    
    def __iter__(self):
        yield self.x
        yield self.y
    
    def __len__(self):
        return 2
    
    def __getitem__(self, index: int) -> float:
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError

    @property
    def x(self) -> float:
        return self.__x
    @x.setter
    def x(self, new: float | int) -> None:
        if not isinstance(new, (int, float)):
            raise TypeError("< x coordinate must be int or float >")
        self.__x = float(new)
    
    @property
    def y(self) -> float:
        return self.__y
    @y.setter
    def y(self, new: float | int) -> None:
        if not isinstance(new, (int, float)):
            raise TypeError("< y coordinate must be int or float >")
        self.__y = float(new)

    @property
    def coords(self) -> tuple[float, float]:
        return (self.x, self.y)
    
    @property
    def size(self) -> tuple[int, int]:
        size: g2d.Point = g2d.canvas_size()
        return int(size[0]), int(size[1])
    
    @property
    def fix_position(self) -> Position:
        return Position(x=self.x, y=self.y)
    
    
    
class CenterPosition(Position):
    def __init__(self, *args, **kwargs) -> None:
        pass
    
    @property
    def x(self) -> float:
        self.__x = self.size[0] // 2
        return float(self.__x)
    @x.setter
    def x(self, new: float | int) -> None:
        if not isinstance(new, (int, float)):
            raise TypeError("< x coordinate must be int or float >")
        self.__x = float(new)
    
    @property
    def y(self) -> float:
        self.__y = self.size[1] // 2
        return float(self.__y)
    @y.setter
    def y(self, new: float | int) -> None:
        if not isinstance(new, (int, float)):
            raise TypeError("< y coordinate must be int or float >")
        self.__y = float(new)
    



class RandomPosition(Position):
    def __init__(self, *args, **kwargs) -> None:
        pass
    
    @property
    def x(self) -> float:
        self.__x = random.uniform(0, self.size[0] - 1)
        return float(self.__x)
    @x.setter
    def x(self, new: float | int) -> None:
        if not isinstance(new, (int, float)):
            raise TypeError("< x coordinate must be int or float >")
        self.__x = float(new)
    
    @property
    def y(self) -> float:
        self.__y = random.uniform(0, self.size[1] - 1)
        return float(self.__y)
    @y.setter
    def y(self, new: float | int) -> None:
        if not isinstance(new, (int, float)):
            raise TypeError("< y coordinate must be int or float >")
        self.__y = float(new)
        




class RatioPosition(Position):
    def __init__(self, x_ratio: float, y_ratio: float) -> None:
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio
        
    def __str__(self) -> str:
        return f"< {self.__class__.__name__} | x: {self.x}, y: {self.y}, x_ratio: {self.x_ratio}, y_ratio: {self.y_ratio} >"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(x_ratio={self.x_ratio}, y_ratio={self.y_ratio})"
        
        
    @property
    def x_ratio(self) -> float:
        return self.__x_ratio
    @x_ratio.setter
    def x_ratio(self, new: float | int) -> None:
        if not isinstance(new, (float, int)):
            raise TypeError("< x_ratio must be of type float or int >")
        self.__x_ratio = float(new)
        
    @property
    def y_ratio(self) -> float:
        return self.__y_ratio
    @y_ratio.setter
    def y_ratio(self, new: float | int) -> None:
        if not isinstance(new, (float, int)):
            raise TypeError("< y_ratio must be of type float or int >")
        self.__y_ratio = float(new)
        
        
    @property
    def x(self) -> float:
        self.__x = float(round(self.size[0] * self.x_ratio, 0))
        return self.__x
    @x.setter
    def x(self, new: float | int) -> None:
        if not isinstance(new, (int, float)):
            raise TypeError("< x coordinate must be int or float >")
        self.__x = float(new)
    
    @property
    def y(self) -> float:
        self.__y = float(round(self.size[1] * self.y_ratio, 0))
        return self.__y
    @y.setter
    def y(self, new: float | int) -> None:
        if not isinstance(new, (int, float)):
            raise TypeError("< y coordinate must be int or float >")
        self.__y = float(new)
    





class Pivot(object):
    __MAP: dict[str, tuple[float, float]] = {
        "nw": (0.0, 0.0),
        "n":  (0.5, 0.0),
        "ne": (1.0, 0.0),
        "w":  (0.0, 0.5),
        "center": (0.5, 0.5),
        "e":  (1.0, 0.5),
        "sw": (0.0, 1.0),
        "s":  (0.5, 1.0),
        "se": (1.0, 1.0),
    }

    def __repr__(self) -> str:
        return f"Pivot('{self.value}')"

    def __init__(self, value: str = "center") -> None:
        self.value = value

    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, new: str) -> None:
        if not isinstance(new, str) or new not in self.__MAP:
            raise ValueError('< pivot must be one of "nw","n","ne","w","center","e","sw","s","se" >')
        self.__value = new

    @property
    def fractions(self) -> tuple[float, float]:
        return self.__MAP[self.__value]




class Figure(object):
    def __init__(
        self, 
        color: Color | Iterable[int] | None = None, 
        position: tuple[float | int, float | int] | Position | CenterPosition | RandomPosition | RatioPosition | None = None, 
        collide: bool = True, 
        pivot: Pivot | str = "center",
    ) -> None:
        self.color = color
        self.position = position
        self.collide = collide
        self.pivot = pivot
    
    
    def __str__(self) -> str:
        return f"< {self.__class__.__name__} >"
    
    
    @property
    def color(self) -> Color:
        return self.__color
    @color.setter
    def color(self, new: Color | Iterable[int] | None) -> None:
        if isinstance(new, Color):
            self.__color: Color = new
            return

        if isinstance(new, Iterable):
            self.__color: Color = Color(new)
            return 

        if isinstance(new, type(None)):
            self.__color: Color = Color(
                random.randrange(256),
                random.randrange(256),
                random.randrange(256),
            )
            return

        raise TypeError("< color proprety must be Color, Iterable[int] or NoneType >")
    
    
    @property
    def position(self) -> Position | CenterPosition | RandomPosition | RatioPosition:
        return self.__position
    @position.setter
    def position(self, new: tuple[float | int, float | int] | Position | CenterPosition | RandomPosition | RatioPosition | None) -> None:
        if new is None:
            self.__position = CenterPosition()
            return
        
        if not (
            isinstance(new, (Position, CenterPosition, RandomPosition, RatioPosition)) or
            (isinstance(new, tuple) and len(new) == 2 and all(isinstance(cord, (int, float)) for cord in new))
            ):
            raise TypeError("< position proprety must be of type tuple[float|int, float|int], Position, CenterPosition, RandomPosition or RatioPosition >")
        
        if isinstance(new, tuple):
            self.__position: Position | CenterPosition | RandomPosition | RatioPosition = Position(new[0], new[1])
        else:
            self.__position: Position | CenterPosition | RandomPosition | RatioPosition = new
    
    
    @property
    def collide(self) -> bool:
        return self.__collide
    @collide.setter
    def collide(self, new: bool) -> None:
        if not isinstance(new, bool):
            raise TypeError("< collide proprety must be boolean >")
        
        self.__collide: bool = new
        
    
    @property
    def pivot(self) -> Pivot:
        return self.__pivot
    @pivot.setter
    def pivot(self, new: Pivot | str) -> None:
        if isinstance(new, str):
            self.__pivot = Pivot(new)
        elif isinstance(new, Pivot):
            self.__pivot = new
        else:
            raise TypeError('< pivot must be Pivot or str in {"nw","n","ne","w","center","e","sw","s","se"} >')





class Circle(Figure):
    def __init__(self, radius: float | int, **kwargs):
        super().__init__(**kwargs)
        
        self.radius = radius


    # dundermethods
    def __str__(self) -> str:
        return f"<{self.__class__.__name__} | radius: {self.radius} >"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    
    # propreties
    @property
    def radius(self) -> float:
        return self.__radius
    @radius.setter
    def radius(self, new: float | int) -> None:
        if not isinstance(new, (int, float)):
            raise TypeError("< radius must be int or float >")
        self.__radius = float(new)
    
    
    # BBOX, COLLIDE_POSITION, DRAW, DIMENSIONS
    @property
    def _bbox_size(self) -> tuple[int, int]:
        d = max(1, int(self.radius * 2))
        return d, d


    def collide_position(self):
        pos_x, pos_y = self.position.coords
        canvas_w, canvas_h = self.position.size
        anchor_x, anchor_y = self.pivot.fractions

        w, h = self._bbox_size

        if self.collide and w <= canvas_w and h <= canvas_h:
            min_pos_x = anchor_x * w
            max_pos_x = canvas_w - (1.0 - anchor_x) * w
            min_pos_y = anchor_y * h
            max_pos_y = canvas_h - (1.0 - anchor_y) * h

            pos_x = int(max(min_pos_x, min(pos_x, max_pos_x)))
            pos_y = int(max(min_pos_y, min(pos_y, max_pos_y)))

        return pos_x, pos_y


    @property
    def draw(self) -> Circle:
        pos_x, pos_y = self.collide_position()
        anchor_x, anchor_y = self.pivot.fractions

        w, h = self._bbox_size
        # w == h == diameter
        center_x = int(round(pos_x + (0.5 - anchor_x) * w))
        center_y = int(round(pos_y + (0.5 - anchor_y) * h))

        g2d.set_color(self.color.g2d)  # type: ignore
        g2d.draw_circle((center_x, center_y), int(round(self.radius)))
        return self


    @property
    def dimensions(self) -> dict[str, int | Position]:
        pos_x, pos_y = self.collide_position()
        anchor_x, anchor_y = self.pivot.fractions

        w, h = self._bbox_size

        left   = pos_x - anchor_x * w
        right  = pos_x + (1 - anchor_x) * w
        top    = pos_y - anchor_y * h
        bottom = pos_y + (1 - anchor_y) * h

        cx = (left + right) / 2.0
        cy = (top + bottom) / 2.0

        return {
            "width":  int(w),
            "height": int(h),

            "nw": Position(int(round(left)),  int(round(top))),
            "n":  Position(int(round(cx)),    int(round(top))),
            "ne": Position(int(round(right)), int(round(top))),

            "w":  Position(int(round(left)),  int(round(cy))),
            "center": Position(int(round(cx)), int(round(cy))),
            "e":  Position(int(round(right)), int(round(cy))),

            "sw": Position(int(round(left)),  int(round(bottom))),
            "s":  Position(int(round(cx)),    int(round(bottom))),
            "se": Position(int(round(right)), int(round(bottom))),
        }






class Rectangle(Figure):
    def __init__(
        self,
        width: float | int,
        height: float | int,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        
        self.width = width
        self.height = height

    
    # dundermethods
    def __str__(self) -> str:
        return f"< {self.__class__.__name__} | width: {self.width}, height: {self.height} >"
    
    def __repr__(self) -> str:
        return self.__str__()
    

    # propreties
    @property
    def width(self) -> float:
        return self.__width
    @width.setter
    def width(self, new: float | int) -> None:
        if not isinstance(new, (int, float)):
            raise TypeError("< width must be int or float >")
        self.__width = float(new)


    @property
    def height(self) -> float:
        return self.__height
    @height.setter
    def height(self, new: float | int) -> None:
        if not isinstance(new, (int, float)):
            raise TypeError("< height must be int or float >")
        self.__height = float(new)

    
    # BBOX, COLLIDE_POSITION, DRAW, DIMENSIONS
    @property
    def _bbox_size(self) -> tuple[int, int]:
        return max(1, int(self.width)), max(1, int(self.height))


    def collide_position(self):
        pos_x, pos_y = self.position.coords
        canvas_w, canvas_h = self.position.size
        anchor_x, anchor_y = self.pivot.fractions

        w, h = self._bbox_size

        if self.collide and w <= canvas_w and h <= canvas_h:
            min_pos_x = anchor_x * w
            max_pos_x = canvas_w - (1.0 - anchor_x) * w
            min_pos_y = anchor_y * h
            max_pos_y = canvas_h - (1.0 - anchor_y) * h

            pos_x = int(max(min_pos_x, min(pos_x, max_pos_x)))
            pos_y = int(max(min_pos_y, min(pos_y, max_pos_y)))

        return pos_x, pos_y


    @property
    def draw(self) -> Self:
        pos_x, pos_y = self.collide_position()
        anchor_x, anchor_y = self.pivot.fractions

        w, h = self._bbox_size

        top_left_x = int(round(pos_x - anchor_x * w))
        top_left_y = int(round(pos_y - anchor_y * h))

        g2d.set_color(self.color.g2d)  # type: ignore
        g2d.draw_rect((top_left_x, top_left_y), (w, h))
        return self


    @property
    def dimensions(self) -> dict[str, int | Position]:
        pos_x, pos_y = self.collide_position()
        anchor_x, anchor_y = self.pivot.fractions

        w, h = self._bbox_size

        left   = pos_x - anchor_x * w
        right  = pos_x + (1 - anchor_x) * w
        top    = pos_y - anchor_y * h
        bottom = pos_y + (1 - anchor_y) * h

        cx = (left + right) / 2.0
        cy = (top + bottom) / 2.0

        return {
            "width":  int(w),
            "height": int(h),

            "nw": Position(int(round(left)),  int(round(top))),
            "n":  Position(int(round(cx)),    int(round(top))),
            "ne": Position(int(round(right)), int(round(top))),

            "w":  Position(int(round(left)),  int(round(cy))),
            "center": Position(round(cx), round(cy)),
            "e":  Position(int(round(right)), int(round(cy))),

            "sw": Position(int(round(left)),  int(round(bottom))),
            "s":  Position(int(round(cx)),    int(round(bottom))),
            "se": Position(int(round(right)), int(round(bottom))),
        }




class Polygon(Figure):
    def __init__(
        self,
        vertices: list[Position],
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.vertices = vertices

    # dundermethods
    def __str__(self) -> str:
        return f"< {self.__class__.__name__} | vertices: {len(self.vertices)} >"

    def __repr__(self) -> str:
        return self.__str__()

    # properties
    @property
    def vertices(self) -> list[Position]:
        return self.__vertices

    @vertices.setter
    def vertices(self, new: list[Position]) -> None:
        if not isinstance(new, list) or len(new) < 3 or not all(isinstance(v, Position) for v in new):
            raise TypeError("< vertices must be a list[Position] with length >= 3 >")
        self.__vertices: list[Position] = new


    # BBOX, COLLIDE_POSITION, DRAW, DIMENSIONS
    @property
    def _bbox(self) -> tuple[int, int, int, int]:
        xs = [v.coords[0] for v in self.vertices]
        ys = [v.coords[1] for v in self.vertices]
        min_x = min(xs)
        min_y = min(ys)
        max_x = max(xs)
        max_y = max(ys)
        width = int(max_x - min_x)
        height = int(max_y - min_y)
        return int(min_x), int(min_y), width, height


    @property
    def _bbox_size(self) -> tuple[int, int]:
        _, _, w, h = self._bbox
        return max(1, int(w)), max(1, int(h))


    def collide_position(self):
        pos_x, pos_y = self.position.coords
        canvas_w, canvas_h = self.position.size
        anchor_x, anchor_y = self.pivot.fractions

        w, h = self._bbox_size

        if self.collide and w <= canvas_w and h <= canvas_h:
            min_pos_x = anchor_x * w
            max_pos_x = canvas_w - (1.0 - anchor_x) * w
            min_pos_y = anchor_y * h
            max_pos_y = canvas_h - (1.0 - anchor_y) * h

            pos_x = int(max(min_pos_x, min(pos_x, max_pos_x)))
            pos_y = int(max(min_pos_y, min(pos_y, max_pos_y)))

        return pos_x, pos_y


    @property
    def draw(self) -> Polygon:
        pos_x, pos_y = self.collide_position()
        anchor_x, anchor_y = self.pivot.fractions

        min_x, min_y, poly_w, poly_h = self._bbox

        top_left_x = int(round(pos_x - anchor_x * poly_w))
        top_left_y = int(round(pos_y - anchor_y * poly_h))

        points = [
            (int((v.coords[0] - min_x) + top_left_x), int((v.coords[1] - min_y) + top_left_y))
            for v in self.vertices
        ]

        g2d.set_color(self.color.g2d)  # type: ignore
        g2d.draw_polygon(points)       # type: ignore
        return self


    @property
    def dimensions(self) -> dict[str, int | Position]:
        pos_x, pos_y = self.collide_position()
        anchor_x, anchor_y = self.pivot.fractions

        w, h = self._bbox_size

        left   = pos_x - anchor_x * w
        right  = pos_x + (1 - anchor_x) * w
        top    = pos_y - anchor_y * h
        bottom = pos_y + (1 - anchor_y) * h

        cx = (left + right) / 2.0
        cy = (top + bottom) / 2.0

        return {
            "width":  int(w),
            "height": int(h),

            "nw": Position(int(round(left)),  int(round(top))),
            "n":  Position(int(round(cx)),    int(round(top))),
            "ne": Position(int(round(right)), int(round(top))),

            "w":  Position(int(round(left)),  int(round(cy))),
            "center": Position(int(round(cx)), int(round(cy))),
            "e":  Position(int(round(right)), int(round(cy))),

            "sw": Position(int(round(left)),  int(round(bottom))),
            "s":  Position(int(round(cx)),    int(round(bottom))),
            "se": Position(int(round(right)), int(round(bottom))),
        }





class Text(Figure):
    __W_FACTOR: float = 0.60   # larghezza media per carattere
    __H_FACTOR: float = 1.20   # altezza linea

    def __init__(self, text: str, size: float | int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.text = text
        self.size = size

    # dundermethods
    def __str__(self) -> str:
        return f"< {self.__class__.__name__} | size: {self.size}, text: '{self.text}' >"

    def __repr__(self) -> str:
        return self.__str__()

    # properties
    @property
    def text(self) -> str:
        return self.__text
    @text.setter
    def text(self, new: str) -> None:
        if not isinstance(new, str):
            raise TypeError("< text must be string >")
        if len(new) == 0:
            raise ValueError("< text must be non-empty >")
        self.__text: str = new

    @property
    def size(self) -> float:
        return self.__size
    @size.setter
    def size(self, new: float | int) -> None:
        if not isinstance(new, (int, float)):
            raise TypeError("< size must be int or float >")
        if float(new) <= 0:
            raise ValueError("< size must be > 0 >")
        self.__size = float(new)


    # BBOX - COLLIDE_POSITION - DRAW - DIMENSIONS
    # bbox stimato
    @property
    def _bbox_size(self) -> tuple[int, int]:
        w = int(round(self.__class__.__W_FACTOR * self.size * len(self.text)))
        h = int(round(self.__class__.__H_FACTOR * self.size))
        return max(w, 1), max(h, 1)


    def collide_position(self):
        pos_x, pos_y = self.position.coords
        canvas_w, canvas_h = self.position.size
        anchor_x, anchor_y = self.pivot.fractions
        
        text_w, text_h = self._bbox_size
        
        # collisione stimata
        if self.collide and text_w <= canvas_w and text_h <= canvas_h:
            min_pos_x = anchor_x * text_w
            max_pos_x = canvas_w - (1.0 - anchor_x) * text_w
            min_pos_y = anchor_y * text_h
            max_pos_y = canvas_h - (1.0 - anchor_y) * text_h

            pos_x = int(max(min_pos_x, min(pos_x, max_pos_x)))
            pos_y = int(max(min_pos_y, min(pos_y, max_pos_y)))
        
        return pos_x, pos_y


    @property
    def draw(self) -> Text:
        pos_x, pos_y = self.collide_position()
        anchor_x, anchor_y = self.pivot.fractions

        text_w, text_h = self._bbox_size

        center_x = int(round(pos_x + (0.5 - anchor_x) * text_w))
        center_y = int(round(pos_y + (0.5 - anchor_y) * text_h))

        g2d.set_color(self.color.g2d)  # type: ignore
        g2d.draw_text(self.text, (center_x, center_y), int(round(self.size)))
        
        return self


    @property
    def dimensions(self) -> dict[str, int | Position]:
        pos_x, pos_y = self.collide_position()
        anchor_x, anchor_y = self.pivot.fractions
        
        text_w, text_h = self._bbox_size
        
        left = pos_x - anchor_x*text_w
        right = pos_x + (1-anchor_x)*text_w
        
        top = pos_y - anchor_y*text_h
        bottom = pos_y + (1-anchor_y)*text_h
        
        cx = (left + right) / 2.0
        cy = (top + bottom) / 2.0
        
        
        dimensions = {
            "width":  int(text_w),
            "height": int(text_h),

            "nw": Position(int(round(left)),  int(round(top))),
            "n":  Position(int(round(cx)),    int(round(top))),
            "ne": Position(int(round(right)), int(round(top))),

            "w":  Position(int(round(left)),  int(round(cy))),
            "center": Position(int(round(cx)), int(round(cy))),
            "e":  Position(int(round(right)), int(round(cy))),

            "sw": Position(int(round(left)),  int(round(bottom))),
            "s":  Position(int(round(cx)),    int(round(bottom))),
            "se": Position(int(round(right)), int(round(bottom))),
        }
        
        return dimensions





class Segment(Figure):
    def __init__(
        self,
        p1: Position,
        p2: Position,
        thickness: float | int = 1,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.p1 = p1
        self.p2 = p2
        self.thickness = thickness

    # dunder
    def __str__(self) -> str:
        return f"< {self.__class__.__name__} | p1: {self.p1.coords}, p2: {self.p2.coords}, thickness: {self.thickness} >"

    __repr__ = __str__

    # properties
    @property
    def p1(self) -> Position:
        return self.__p1
    @p1.setter
    def p1(self, new: Position) -> None:
        if not isinstance(new, Position):
            raise TypeError("< p1 must be Position >")
        self.__p1 = new

    @property
    def p2(self) -> Position:
        return self.__p2
    @p2.setter
    def p2(self, new: Position) -> None:
        if not isinstance(new, Position):
            raise TypeError("< p2 must be Position >")
        self.__p2 = new

    @property
    def thickness(self) -> float:
        return self.__thickness
    @thickness.setter
    def thickness(self, new: float | int) -> None:
        if not isinstance(new, (int, float)):
            raise TypeError("< thickness must be int or float >")
        if float(new) <= 0:
            raise ValueError("< thickness must be > 0 >")
        self.__thickness = float(new)

    # bbox helpers
    @property
    def _bbox(self) -> tuple[int, int, int, int]:
        xs = [self.p1.coords[0], self.p2.coords[0]]
        ys = [self.p1.coords[1], self.p2.coords[1]]
        min_x = min(xs)
        min_y = min(ys)
        max_x = max(xs)
        max_y = max(ys)
        width = int(max_x - min_x) or 1
        height = int(max_y - min_y) or 1
        return int(min_x), int(min_y), width, height

    @property
    def _bbox_size(self) -> tuple[int, int]:
        _, _, w, h = self._bbox
        return max(1, int(w)), max(1, int(h))

    def collide_position(self):
        pos_x, pos_y = self.position.coords
        canvas_w, canvas_h = self.position.size
        anchor_x, anchor_y = self.pivot.fractions

        w, h = self._bbox_size
        if self.collide and w <= canvas_w and h <= canvas_h:
            min_pos_x = anchor_x * w
            max_pos_x = canvas_w - (1.0 - anchor_x) * w
            min_pos_y = anchor_y * h
            max_pos_y = canvas_h - (1.0 - anchor_y) * h

            pos_x = int(max(min_pos_x, min(pos_x, max_pos_x)))
            pos_y = int(max(min_pos_y, min(pos_y, max_pos_y)))

        return pos_x, pos_y

    @property
    def draw(self) -> Segment:
        pos_x, pos_y = self.collide_position()
        anchor_x, anchor_y = self.pivot.fractions

        min_x, min_y, w, h = self._bbox
        top_left_x = int(round(pos_x - anchor_x * w))
        top_left_y = int(round(pos_y - anchor_y * h))

        # shift dei punti nel bbox riallineato
        q1 = (int((self.p1.coords[0] - min_x) + top_left_x),
                int((self.p1.coords[1] - min_y) + top_left_y))
        q2 = (int((self.p2.coords[0] - min_x) + top_left_x),
                int((self.p2.coords[1] - min_y) + top_left_y))

        g2d.set_color(self.color.g2d, self.thickness) # type: ignore
        g2d.draw_line(q1, q2, width=self.thickness)
        return self

    @property
    def dimensions(self) -> dict[str, int | Position]:
        pos_x, pos_y = self.collide_position()
        anchor_x, anchor_y = self.pivot.fractions

        w, h = self._bbox_size
        left   = pos_x - anchor_x * w
        right  = pos_x + (1 - anchor_x) * w
        top    = pos_y - anchor_y * h
        bottom = pos_y + (1 - anchor_y) * h
        cx = (left + right) / 2.0
        cy = (top + bottom) / 2.0

        return {
            "width":  int(w),
            "height": int(h),
            "nw": Position(left, top),
            "n":  Position(cx, top),
            "ne": Position(right, top),
            "w":  Position(left, cy),
            "center": Position(cx, cy),
            "e":  Position(right, cy),
            "sw": Position(left, bottom),
            "s":  Position(cx, bottom),
            "se": Position(right, bottom),
        }






class BrokenSegment(Figure):
    def __init__(
        self,
        points: list[Position],
        thickness: float | int = 1,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.points = points
        self.thickness = thickness

    # dunder
    def __str__(self) -> str:
        return f"< {self.__class__.__name__} | points: {len(self.points)}, thickness: {self.thickness} >"

    __repr__ = __str__

    # properties
    @property
    def points(self) -> list[Position]:
        return self.__points
    @points.setter
    def points(self, new: list[Position]) -> None:
        if not isinstance(new, list) or len(new) < 2 or not all(isinstance(v, Position) for v in new):
            raise TypeError("< points must be a list[Position] with length >= 2 >")
        self.__points = new

    @property
    def thickness(self) -> float:
        return self.__thickness
    @thickness.setter
    def thickness(self, new: float | int) -> None:
        if not isinstance(new, (int, float)):
            raise TypeError("< thickness must be int or float >")
        if float(new) <= 0:
            raise ValueError("< thickness must be > 0 >")
        self.__thickness = float(new)

    # bbox helpers
    @property
    def _bbox(self) -> tuple[int, int, int, int]:
        xs = [v.coords[0] for v in self.points]
        ys = [v.coords[1] for v in self.points]
        min_x = min(xs)
        min_y = min(ys)
        max_x = max(xs)
        max_y = max(ys)
        width = int(max_x - min_x) or 1
        height = int(max_y - min_y) or 1
        return int(min_x), int(min_y), width, height

    @property
    def _bbox_size(self) -> tuple[int, int]:
        _, _, w, h = self._bbox
        return max(1, int(w)), max(1, int(h))

    def collide_position(self):
        pos_x, pos_y = self.position.coords
        canvas_w, canvas_h = self.position.size
        anchor_x, anchor_y = self.pivot.fractions

        w, h = self._bbox_size
        if self.collide and w <= canvas_w and h <= canvas_h:
            min_pos_x = anchor_x * w
            max_pos_x = canvas_w - (1.0 - anchor_x) * w
            min_pos_y = anchor_y * h
            max_pos_y = canvas_h - (1.0 - anchor_y) * h

            pos_x = int(max(min_pos_x, min(pos_x, max_pos_x)))
            pos_y = int(max(min_pos_y, min(pos_y, max_pos_y)))

        return pos_x, pos_y

    @property
    def draw(self) -> BrokenSegment:
        pos_x, pos_y = self.collide_position()
        anchor_x, anchor_y = self.pivot.fractions

        min_x, min_y, w, h = self._bbox
        top_left_x = int(round(pos_x - anchor_x * w))
        top_left_y = int(round(pos_y - anchor_y * h))

        # punti traslati nel bbox riallineato
        q = [
            (int((v.coords[0] - min_x) + top_left_x),
            int((v.coords[1] - min_y) + top_left_y))
            for v in self.points
        ]

        g2d.set_color(self.color.g2d, int(round(self.thickness)))   # type: ignore
        
        for i in range(len(q) - 1):
            g2d.draw_line(q[i], q[i+1], width=int(round(self.thickness)))
        return self

    @property
    def dimensions(self) -> dict[str, int | Position]:
        pos_x, pos_y = self.collide_position()
        anchor_x, anchor_y = self.pivot.fractions

        w, h = self._bbox_size
        left   = pos_x - anchor_x * w
        right  = pos_x + (1 - anchor_x) * w
        top    = pos_y - anchor_y * h
        bottom = pos_y + (1 - anchor_y) * h
        cx = (left + right) / 2.0
        cy = (top + bottom) / 2.0

        return {
            "width":  int(w),
            "height": int(h),
            "nw": Position(left,  top),
            "n":  Position(cx,    top),
            "ne": Position(right, top),
            "w":  Position(left,  cy),
            "center": Position(cx, cy),
            "e":  Position(right, cy),
            "sw": Position(left,  bottom),
            "s":  Position(cx,    bottom),
            "se": Position(right, bottom),
        }





if __name__ == "__main__":
    g2d.init_canvas((500, 500))
    
    c = Circle(radius=100, position=CenterPosition(), pivot="e", collide=False)
    c.draw
    
    Circle(radius=5).draw
    g2d.main_loop()
