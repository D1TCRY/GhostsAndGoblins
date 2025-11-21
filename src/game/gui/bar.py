from .gui_component import GUIComponent
from collections.abc import Callable


class Bar(GUIComponent):
    def __init__(self,
        name_id: str,
        x: float = 5,
        y: float = 5,
        width: float = 72,
        height: float = 14,
        text: str = "Bar",
        text_size: int = 10,
        text_color: tuple[int, int, int] | tuple[int, int, int, int] = (248, 248, 248),
        background_color: tuple[int, int, int] = (116, 16, 8),
        bar_color: tuple[int, int, int] = (248, 128, 96),
        max_value: float = 1,
        value: float | Callable = 1,
        padding: float = 1,
        fixed: bool = True    # if True the position will be considered on canvas, else on arena
    ) -> None:
        """
        Semplice barra orizzontale con testo opzionale.
        Può rappresentare valori come vita, mana, energia o progressi.
        Il valore corrente può essere un numero fisso o una funzione che viene valutata ad ogni frame.
        """
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
        self.fixed = fixed


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
        if not isinstance(value, tuple) or len(value) > 4 or not all(isinstance(_, int) for _ in value):
            raise TypeError("text_color must be a tuple of three integers")
        self.__text_color: tuple[int, int, int] = tuple(value)

    @property
    def background_color(self) -> tuple[int, int, int]:
        return self.__background_color
    @background_color.setter
    def background_color(self, value: tuple[int, int, int]) -> None:
        if not isinstance(value, tuple) or len(value) > 4 or not all(isinstance(_, int) for _ in value):
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

    @property
    def fixed(self) -> bool:
        return self.__fixed
    @fixed.setter
    def fixed(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("fixed must be a boolean")
        self.__fixed: bool = bool(value)

    def render_info(self, new_value: float = None):
        """
        Restituisce le informazioni grafiche per disegnare la Bar.

        Aggiorna il valore corrente (se new_value è fornito), calcola la larghezza
        della parte riempita in base a value e max_value e genera:
        - un rettangolo di sfondo
        - un rettangolo interno che rappresenta il valore attuale
        - un testo centrato con il valore formattato dentro la stringa text
        """

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
                "color": self.text_color,
                "text": text,
                "center": (center_x, center_y),
                "font_size": self.text_size
            }
        ]