from actor import Actor, Arena
from status import Sprite, Direction


class Platform(Actor):
    def __init__(self,
        x: int | float,
        y: int | float,
        width: int,
        height: int,
        contact_surfaces: list[Direction] | tuple[Direction] | None = (Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT),
        damage: int | float = 0.0,
        *,
        name: str = "Platform"
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.contact_surfaces = contact_surfaces
        self.damage = damage

        self.name = name


    # ======== PROPERTIES ========
    @property
    def x(self) -> float:
        return self.__x
    @x.setter
    def x(self, value: int | float):
        if not isinstance(value, (int, float)):
            raise TypeError("x must be an int or float")
        self.__x: float = float(value)

    @property
    def y(self) -> float:
        return self.__y
    @y.setter
    def y(self, value: int | float):
        if not isinstance(value, (int, float)):
            raise TypeError("y must be an int or float")
        self.__y: float = float(value)

    @property
    def width(self) -> int:
        return self.__width
    @width.setter
    def width(self, value: int):
        if not isinstance(value, int):
            raise TypeError("width must be an int or float")
        self.__width: int = int(value)

    @property
    def height(self) -> int:
        return self.__height
    @height.setter
    def height(self, value: int):
        if not isinstance(value, int):
            raise TypeError("height must be an int or float")
        self.__height: int = int(value)

    @property
    def contact_surfaces(self) -> list[Direction] | None:
        return self.__contact_surfaces
    @contact_surfaces.setter
    def contact_surfaces(self, value: list[Direction] | tuple[Direction] | None):
        if not (isinstance(value, (list, tuple)) or value is None):
            raise TypeError("contact_surfaces must be a list or tuple or None")
        self.__contact_surfaces: list[Direction] | None = list(value) if isinstance(value, (list, tuple)) else None

    @property
    def damage(self) -> float:
        return self.__damage
    @damage.setter
    def damage(self, value: int | float):
        if not isinstance(value, (int, float)):
            raise TypeError("damage must be an int")
        self.__damage: float = float(value)


    @property
    def name(self) -> str:
        return self.__name
    @name.setter
    def name(self, value: str):
        if not isinstance(value, str):
            raise TypeError("name must be a string")
        self.__name: str = value


    # ======== INTERFACE IMPLEMENTATION ========
    def pos(self) -> tuple[float, float]:
        return self.x, self.y

    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def move(self, arena: Arena) -> None:
        return

    def sprite(self) -> Sprite | None:
        return


    # ======== METHODS ========
    def check_collision(self, obj: Actor) -> bool:
        ox, oy = obj.pos()
        ow, oh = obj.size()

        o_left = ox
        o_top = oy
        o_right = ox + ow
        o_bottom = oy + oh

        if o_right <= self.x or o_left >= self.x + self.width or o_bottom <= self.y or o_top >= self.y + self.height:
            return False

        return True

    def clamp(self, obj: Actor) -> tuple[Direction | None, float, float]:
        ox, oy = obj.pos()
        ow, oh = obj.size()

        o_left = ox
        o_top = oy
        o_right = ox + ow
        o_bottom = oy + oh

        p_left = self.x
        p_top = self.y
        p_right = self.x + self.width
        p_bottom = self.y + self.height


        if o_right <= p_left or o_left >= p_right or o_bottom <= p_top or o_top >= p_bottom:
            return None, 0.0, 0.0


        overlap_x = min(o_right, p_right) - max(o_left, p_left)
        overlap_y = min(o_bottom, p_bottom) - max(o_top, p_top)


        o_cx = (o_left + o_right) / 2
        o_cy = (o_top + o_bottom) / 2
        p_cx = (p_left + p_right) / 2
        p_cy = (p_top + p_bottom) / 2


        if overlap_x < overlap_y:
            # orizzontale
            if o_cx < p_cx:
                direction = Direction.LEFT
                dx = -overlap_x
                dy = 0.0
            else:
                direction = Direction.RIGHT
                dx = overlap_x
                dy = 0.0
        else:
            # verticale
            if o_cy < p_cy:
                direction = Direction.UP
                dx = 0.0
                dy = -overlap_y
            else:
                direction = Direction.DOWN
                dx = 0.0
                dy = overlap_y


        if self.contact_surfaces is None or direction not in self.contact_surfaces:
            return None, 0.0, 0.0

        return direction, dx, dy