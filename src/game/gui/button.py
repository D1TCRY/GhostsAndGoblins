from collections.abc import Callable
from .gui_component import GUIComponent
from .color import Color

from ..core.file_management import read_settings

SCALE = read_settings().get("scale", 1)

class Button(GUIComponent):
    def __init__(self,
                 name_id: str = "Button",
                 x: float = 0,
                 y: float = 0,
                 width: float = 80,
                 height: float = 24,
                 text: str = "Button",
                 text_size: int = 10,
                 text_color: Color = (248, 248, 248),
                 background_color: Color = (48, 48, 48),
                 hover_color: Color | None = (48, 48, 108),
                 pressed_color: Color | None = (48, 64, 208),
                 fixed: bool = True,
                 enabled: bool = True,
                 command: Callable[[], None] | None = None,
                 activate_keys: list[str] | None = None) -> None:
        """
        Semplice bottone rettangolare con testo centrato.
        L'aspetto dipende da enabled/hovered/pressed.
        Se command è impostato, viene eseguito quando il bottone è attivato.
        """
        self.name_id = name_id
        self.fixed = fixed

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.text = text
        self.text_size = text_size
        self.text_color = text_color

        self.background_color = background_color
        self.hover_color = hover_color if hover_color is not None else background_color
        self.pressed_color = pressed_color if pressed_color is not None else background_color

        self.enabled = enabled
        self.hovered = False
        self.pressed = False

        self.command = command
        self.activate_keys = activate_keys

    # ========== METHODS ==========
    def contains(self, cursor_pos: tuple[float, float]) -> bool:
        """Ritorna True se il cursore è sopra il bottone."""
        cx, cy = cursor_pos
        cx /= SCALE
        cy /= SCALE
        return (self.x <= cx <= self.x + self.width
                and self.y <= cy <= self.y + self.height)

    def update_hover(self, cursor_pos: tuple[float, float]) -> None:
        """
        Aggiorna solo lo stato di hover in base alla posizione del cursore.
        """
        if not self.enabled:
            self.hovered = False
            return
        self.hovered = self.contains(cursor_pos)

    def tick(self, keys: list[str], cursor_pos: tuple[float, float]) -> None:
        """
        Gestione completa del cursore e della tastiera per il bottone.
        Consente di aggiornare lo stato di hover e di eseguire il comando associato, tutto in un unico metodo.
        """
        self.update_hover(cursor_pos)
        self.handle_keys(keys)

    def invoke(self) -> None:
        """
        Esegue il comando associato, se presente e se il bottone è abilitato.
        """
        if self.enabled and self.command is not None:
            self.command()

    def handle_keys(self, keys: list[str]) -> bool:
        """
        Gestisce l'interazione da tastiera.
        Ritorna True se il bottone viene "attivato" premendo un tasto in activate_keys mentre il bottone è hovered ed enabled e chiama invoke.
        """
        if not self.enabled or not self.hovered:
            self.pressed = False
            return False

        if any(k in keys for k in self.activate_keys):
            self.pressed = True
            self.invoke()
            return True

        self.pressed = False
        return False


    # ========== RENDERING ==========
    def render_info(self) -> list[dict]:
        """
        Restituisce le informazioni grafiche per disegnare Button.
        Il colore di sfondo dipende da enabled/hovered/pressed.
        """
        x, y = self.x, self.y
        width, height = self.width, self.height

        center_x = x + width / 2
        center_y = y + height / 2

        # Determina colore di background in base allo stato
        if not self.enabled:
            base = self.background_color
            bg_color = tuple(int(c * 0.5) for c in base)
        elif self.pressed:
            bg_color = self.pressed_color
        elif self.hovered:
            bg_color = self.hover_color
        else:
            bg_color = self.background_color

        return [
            {
                "type": "rect",
                "color": bg_color.rgba,
                "pos": (x, y),
                "size": (width, height)
            },
            {
                "type": "text",
                "color": self.text_color.rgba,
                "text": self.text,
                "center": (center_x, center_y),
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
        self.__name_id: str = str(value)

    @property
    def fixed(self) -> bool:
        return self.__fixed
    @fixed.setter
    def fixed(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("fixed must be a boolean")
        self.__fixed: bool = bool(value)

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
    def width(self) -> float:
        return self.__width
    @width.setter
    def width(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("width must be an int or float")
        if value <= 0:
            raise ValueError("width must be greater than 0")
        self.__width = float(value)

    @property
    def height(self) -> float:
        return self.__height
    @height.setter
    def height(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("height must be an int or float")
        if value <= 0:
            raise ValueError("height must be greater than 0")
        self.__height = float(value)

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
    def text_color(self) -> Color:
        return self.__text_color
    @text_color.setter
    def text_color(self, value: Color | tuple[int, int, int] | tuple[int, int, int, int]) -> None:
        if not (
                isinstance(value, Color)
                or (isinstance(value, tuple) and len(value) in (3, 4) and all(isinstance(_, int) for _ in value))
        ):
            raise TypeError("text_color must be a Color or tuple of three or four integers")
        self.__text_color: Color = value if isinstance(value, Color) else Color(value)

    @property
    def background_color(self) -> Color:
        return self.__background_color
    @background_color.setter
    def background_color(self, value: tuple[int, int, int]) -> None:
        if not (
                isinstance(value, Color)
                or (isinstance(value, tuple) and len(value) in (3, 4) and all(isinstance(_, int) for _ in value))
        ):
            raise TypeError("text_color must be a Color or tuple of three or four integers")
        self.__background_color: Color = value if isinstance(value, Color) else Color(value)

    @property
    def hover_color(self) -> Color:
        return self.__hover_color
    @hover_color.setter
    def hover_color(self, value: tuple[int, int, int]) -> None:
        if not (
                isinstance(value, Color)
                or (isinstance(value, tuple) and len(value) in (3, 4) and all(isinstance(_, int) for _ in value))
        ):
            raise TypeError("text_color must be a Color or tuple of three or four integers")
        self.__hover_color = value if isinstance(value, Color) else Color(value)

    @property
    def pressed_color(self) -> Color:
        return self.__pressed_color
    @pressed_color.setter
    def pressed_color(self, value: tuple[int, int, int]) -> None:
        if not (
                isinstance(value, Color)
                or (isinstance(value, tuple) and len(value) in (3, 4) and all(isinstance(_, int) for _ in value))
        ):
            raise TypeError("text_color must be a Color or tuple of three or four integers")
        self.__pressed_color: Color = value if isinstance(value, Color) else Color(value)

    @property
    def enabled(self) -> bool:
        return self.__enabled
    @enabled.setter
    def enabled(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("enabled must be a boolean")
        self.__enabled = bool(value)

    @property
    def hovered(self) -> bool:
        return self.__hovered
    @hovered.setter
    def hovered(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("hovered must be a boolean")
        self.__hovered = bool(value)

    @property
    def pressed(self) -> bool:
        return self.__pressed
    @pressed.setter
    def pressed(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("pressed must be a boolean")
        self.__pressed = bool(value)

    @property
    def command(self) -> Callable[[], None] | None:
        return self.__command
    @command.setter
    def command(self, value: Callable[[], None] | None) -> None:
        if value is not None and not isinstance(value, Callable):
            raise TypeError("command must be a Callable or None")
        self.__command = value

    @property
    def activate_keys(self) -> list[str] | None:
        return self.__activate_keys
    @activate_keys.setter
    def activate_keys(self, value: list[str] | None) -> None:
        if value is not None and not isinstance(value, list):
            raise TypeError("activate_keys must be a list or None")
        self.__activate_keys = value if value is not None else []
