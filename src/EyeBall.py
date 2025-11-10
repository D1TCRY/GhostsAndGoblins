from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Game import Game

from actor import Arena, Actor
from Weapon import Weapon
from status import Action, Direction, Sprite, SpriteCollection, State


import pathlib

# ======== SPRITES ========
EYEBALL_SPRITE_PATH = pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins.png"

EYEBALL_SPRITE_R1: Sprite = Sprite(path=EYEBALL_SPRITE_PATH, x=552, y=219, width=8, height=8)
EYEBALL_SPRITE_L1: Sprite = Sprite(path=EYEBALL_SPRITE_PATH, x=746, y=219, width=8, height=8)


class EyeBall(Weapon):
    def __init__(self,
        x: int | float,
        y: int | float,
        direction: Direction,
        speed: float = 2.0,
        damage: int | float = 10.0,
    ) -> None:
        super().__init__(
            action=Action.ATTACKING,
            direction=direction,
            sprite_cycle_speed=6,
        )

        self.x = x
        self.y = y

        self.width = EYEBALL_SPRITE_R1.width
        self.height = EYEBALL_SPRITE_R1.height

        self.speed = speed
        self.damage = damage


        self.sprites = SpriteCollection()
        self.sprites[Action.ATTACKING, Direction.RIGHT] = [
            EYEBALL_SPRITE_R1
        ]
        self.sprites[Action.ATTACKING, Direction.LEFT] = [
            EYEBALL_SPRITE_L1
        ]

    # ======== PROPERTIES ========
    @property
    def x(self) -> float:
        return self.__x
    @x.setter
    def x(self, value: int | float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("x must be int or float")
        self.__x = float(value)

    @property
    def y(self) -> float:
        return self.__y
    @y.setter
    def y(self, value: int | float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("y must be int or float")
        self.__y = float(value)

    @property
    def width(self) -> int:
        return self.__width
    @width.setter
    def width(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("width must be int")
        self.__width = int(value)

    @property
    def height(self) -> int:
        return self.__height
    @height.setter
    def height(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("height must be int")
        self.__height = int(value)

    @property
    def speed(self) -> float:
        return self.__speed
    @speed.setter
    def speed(self, value: int | float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("speed must be int or float")
        self.__speed = float(value)

    @property
    def damage(self) -> float:
        return self.__damage
    @damage.setter
    def damage(self, value: int | float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("damage must be int or float")
        self.__damage = float(value)

    # ======== INTERFACE IMPLEMENTATION ========
    def pos(self) -> tuple[float, float]:
        return self.x, self.y

    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def move(self, arena: Arena) -> None:
        if self.state.direction == Direction.RIGHT:
            self.x += self.speed
        else:
            self.x -= self.speed

        a_w, a_h = arena.size()
        if self.x + self.width < 0 or self.x > a_w or self.y + self.height < 0 or self.y > a_h:
            arena.kill(self)

    def sprite(self) -> Sprite | None:
        key = (self.state.action, self.state.direction)
        if key not in self.sprites.__iter__():
            return None
        sprites = self.sprites[key]
        return self._looping_sprite_selection(sprites)
