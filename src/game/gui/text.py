from .gui_component import GUIComponent


class Text(GUIComponent):
    def __init__(self,
                 name_id: str = "Text",
                 x: float = 0,
                 y: float = 0,
                 text: str = "Text",
                 text_size: int = 10,
                 text_color: tuple[int, int, int] | tuple[int, int, int, int] = (248, 248, 248),
                 fixed: bool = True) -> None:
        """
        Componente GUI che gestisce solo testo.
        Le coordinate (x, y) rappresentano SEMPRE il centro del testo.
        """
        self.name_id = name_id
        self.fixed = fixed

        self.x = x
        self.y = y

        self.text = text
        self.text_size = text_size
        self.text_color = text_color

    # ========== RENDERING ==========
    def render_info(self) -> list[dict]:
        """
        Restituisce le informazioni grafiche per disegnare il testo.
        """
        return [
            {
                "type": "text",
                "color": self.text_color,
                "text": self.text,
                "center": (self.x, self.y),
                "font_size": self.text_size
            }
        ]

    # ========== PROPERTIES ==========
    @property
    def name_id(self) -> str:
        return self.__name_id
    @name_id.setter
    def name_id(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("name_id must be a string")
        self.__name_id = str(value)

    @property
    def fixed(self) -> bool:
        return self.__fixed
    @fixed.setter
    def fixed(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("fixed must be a boolean")
        self.__fixed = bool(value)

    @property
    def x(self) -> float:
        return self.__x
    @x.setter
    def x(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("x must be an int or float")
        self.__x = float(value)

    @property
    def y(self) -> float:
        return self.__y
    @y.setter
    def y(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("y must be an int or float")
        self.__y = float(value)

    @property
    def text(self) -> str:
        return self.__text
    @text.setter
    def text(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("text must be a string")
        self.__text = str(value)

    @property
    def text_size(self) -> int:
        return self.__text_size
    @text_size.setter
    def text_size(self, value: int | float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("text_size must be an int or float")
        self.__text_size = int(round(value))

    @property
    def text_color(self) -> tuple[int, int, int] | tuple[int, int, int, int]:
        return self.__text_color # type: ignore
    @text_color.setter
    def text_color(self, value: tuple[int, int, int] | tuple[int, int, int, int]) -> None:
        if (not isinstance(value, tuple)
                or len(value) > 4
                or not all(isinstance(_, int) for _ in value)):
            raise TypeError("text_color must be a tuple of three or four integers")
        self.__text_color = tuple(value)
