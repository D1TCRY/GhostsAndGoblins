from typing import Any


class Camera(object):
    def __init__(self, view_x: float, view_y: float, width: float, height: float, target: Any | None = None) -> None:
        self.view_x = view_x
        self.view_y = view_y
        
        self.width = width
        self.height = height
        
        self.target = target
        

    @property
    def view_x(self) -> float:
        return self.__view_x
    @view_x.setter
    def view_x(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("view_x must be an int or float")
        self.__view_x: float = float(value)

    @property
    def view_y(self) -> float:
        return self.__view_y
    @view_y.setter
    def view_y(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("view_y must be an int or float")
        self.__view_y: float = float(value)

    @property
    def width(self) -> float:
        return self.__width
    @width.setter
    def width(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("width must be an int or float")
        self.__width: float = float(value)

    @property
    def height(self) -> float:
        return self.__height
    @height.setter
    def height(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("height must be an int or float")
        self.__height: float = float(value)

    @property
    def target(self) -> Any:
        return self.__target
    @target.setter
    def target(self, value: Any):
        self.__target = value

    @property
    def pos(self) -> tuple[float, float]:
        return self.view_x, self.view_y

    @property
    def size(self) -> tuple[float, float]:
        return self.width, self.height

    def tick(self, arena):
        """Aggiorna la posizione della camera in base al bersaglio e ai limiti dell arena.

        Se esiste un target:
        - calcola la posizione desiderata della camera in modo che il bersaglio
          sia approssimativamente verso il centro dello schermo (leggermente
          spostato a sinistra in orizzontale)
        - recupera la dimensione della arena per conoscere i limiti massimi di
          scorrimento
        - limita view_x e view_y in modo che la camera non esca mai fuori dai
          bordi della arena

        Se non esiste alcun target, la posizione della camera rimane invariata.
        """

        if self.target:
            desired_x = self.target.x - self.width / 3.5
            desired_y = self.target.y - self.height / 2

            arena_w, arena_h = arena.size()

            max_x = max(0.0, arena_w - self.width)
            max_y = max(0.0, arena_h - self.height)

            self.view_x = max(0.0, min(desired_x, max_x))
            self.view_y = max(0.0, min(desired_y, max_y))
