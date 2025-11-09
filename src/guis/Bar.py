from .GUIComponent import GUIComponent
from collections.abc import Callable


class Bar(GUIComponent):
    def __init__(self,
        g2d,
        name_id: str,
        x: float = 5,
        y: float = 5,
        width: float = 72,
        height: float = 14,
        text: str = "Bar",
        text_size: int = 10,
        text_color: tuple[int, int, int] = (248, 248, 248),
        background_color: tuple[int, int, int] = (116, 16, 8),
        bar_color: tuple[int, int, int] = (248, 128, 96),
        max_value: float = 1,
        value: float | Callable = 1,
        padding: float = 1
    ) -> None:
        self.g2d = g2d
        self.name_id = name_id
        self.x = x
        self.y = y
        self.padding = padding
        self.width = width
        self.height = height
        self.text = text
        self.text_size = text_size
        self.text_color = text_color
        self.background_color = background_color
        self.bar_color = bar_color
        self.max_value = max_value
        self.value = value

    @property
    def g2d(self):
        return self.__g2d
    @g2d.setter
    def g2d(self, value) -> None:
        if not hasattr(value, "draw_rect") or not hasattr(value, "draw_text") or not hasattr(value, "set_color"):
            raise TypeError("g2d must have draw_rect, draw_text and set_color methods")
        self.__g2d = value

    @property
    def name_id(self) -> str:
        return self.__name_id
    @name_id.setter
    def name_id(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("name_id must be a string")
        self.__name_id: str = str(value)

    @property
    def x(self) -> float:
        return self.__x
    @x.setter
    def x(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("x must be an int or float")
        self.__x: float = float(value)

    @property
    def y(self) -> float:
        return self.__y
    @y.setter
    def y(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("y must be an int or float")
        self.__y: float = float(value)

    @property
    def width(self) -> float:
        return self.__width
    @width.setter
    def width(self, value: int | float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("width must be an int or float")
        if value - 2*self.padding < 1:
            raise ValueError("width must be greater than 2*padding")
        self.__width: float = float(value)

    @property
    def height(self) -> float:
        return self.__height
    @height.setter
    def height(self, value: int | float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("height must be an int or float")
        if value - 2*self.padding < 1:
            raise ValueError("height must be greater than 2*padding")
        self.__height: float = float(value)

    @property
    def text(self) -> str:
        return self.__text
    @text.setter
    def text(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("text must be a string")
        self.__text: str = str(value)

    @property
    def text_size(self) -> int:
        return self.__text_size
    @text_size.setter
    def text_size(self, value: int | float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("text_size must be an int or float")
        self.__text_size: int = int(round(value))

    @property
    def text_color(self) -> tuple[int, int, int]:
        return self.__text_color
    @text_color.setter
    def text_color(self, value: tuple[int, int, int]) -> None:
        if not isinstance(value, tuple) or len(value) != 3 or not all(isinstance(_, int) for _ in value):
            raise TypeError("text_color must be a tuple of three integers")
        self.__text_color: tuple[int, int, int] = tuple(value)

    @property
    def background_color(self) -> tuple[int, int, int]:
        return self.__background_color
    @background_color.setter
    def background_color(self, value: tuple[int, int, int]) -> None:
        if not isinstance(value, tuple) or len(value) != 3 or not all(isinstance(_, int) for _ in value):
            raise TypeError("background_color must be a tuple of three integers")
        self.__background_color: tuple[int, int, int] = tuple(value)

    @property
    def bar_color(self) -> tuple[int, int, int]:
        return self.__bar_color
    @bar_color.setter
    def bar_color(self, value: tuple[int, int, int]) -> None:
        if not isinstance(value, tuple) or len(value) != 3 or not all(isinstance(_, int) for _ in value):
            raise TypeError("background_color must be a tuple of three integers")
        self.__bar_color: tuple[int, int, int] = tuple(value)

    @property
    def max_value(self) -> float:
        return self.__max_value
    @max_value.setter
    def max_value(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("max must be an int or float")
        self.__max_value: float = float(value)

    @property
    def value(self) -> float:
        if isinstance(self.__value, (float, int)):
            return self.__value
        else:
            return max(0.0, min(float(self.__value()), self.max_value))
    @value.setter
    def value(self, value: float | Callable) -> None:
        if not isinstance(value, (int, float, Callable)):
            raise TypeError("value must be an int or float or Callable")

        if isinstance(value, (float, int)):
            self.__value: float | Callable = max(0.0, min(float(value), self.max_value))
        else:
            self.__value: float | Callable = value

    @property
    def padding(self) -> float:
        return self.__padding
    @padding.setter
    def padding(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("padding must be an int or float")
        self.__padding: float = float(value)

    def render_info(self, new_value: float = None):
        self.value = new_value if new_value is not None else self.value

        x, y = self.x, self.y
        width, height = self.width, self.height

        inner_x, inner_y = x + self.padding, y + self.padding
        inner_width, inner_height = width - 2 * self.padding, height - 2 * self.padding
        inner_real_width = inner_width * self.value / self.max_value

        center_x, center_y = x + width / 2, y + height / 2

        text = self.text.replace("{value}", str(int(round(self.value))))

        return [
            {
                "type": "rect",
                "color": self.background_color,
                "pos": (x, y),
                "size": (width, height)
            },
            {
                "type": "rect",
                "color": self.bar_color,
                "pos": (inner_x, inner_y),
                "size": (inner_real_width, inner_height)
            },
            {
                "type": "text",
                "text": text,
                "center": (center_x, center_y),
                "font_size": self.text_size
            }
        ]

    def g2d_draw(self, new_value: float = None) -> None:
        self.value = new_value if new_value is not None else self.value

        x, y = self.x, self.y
        width, height = self.width, self.height

        inner_x, inner_y = x+self.padding, y+self.padding
        inner_width, inner_height = width-2*self.padding, height-2*self.padding
        inner_real_width = inner_width * self.value / self.max_value

        center_x, center_y = x + width/2, y + height/2

        text = self.text.replace("{value}", str(int(round(self.value))))

        self.g2d.set_color(self.background_color)
        self.g2d.draw_rect(pos=(x, y), size=(width, height))

        self.g2d.set_color(self.bar_color)
        self.g2d.draw_rect(pos=(inner_x, inner_y), size=(inner_real_width, inner_height))

        self.g2d.set_color(self.text_color)
        self.g2d.draw_text(text=text, center=(center_x, center_y), size=self.text_size)
