from __future__ import annotations
from typing import TYPE_CHECKING
import pathlib

# CORE
if TYPE_CHECKING: from ...core import Game

# ACTOR
from ..actor import Arena, Actor

# WEAPONS
from .weapon import Weapon

# STATE
from ...state import Action, Direction, Sprite, SpriteCollection, State



# SPRITES
EYEBALL_SPRITE_PATH = pathlib.Path(__file__).parent.parent.parent.parent / "data" / "textures" / "ghosts-goblins.png"

EYEBALL_SPRITE_R1: Sprite = Sprite(path=EYEBALL_SPRITE_PATH, x=552, y=219, width=8, height=8)
EYEBALL_SPRITE_L1: Sprite = Sprite(path=EYEBALL_SPRITE_PATH, x=746, y=219, width=8, height=8)


class EyeBall(Weapon):
    def __init__(
        self,
        x: float,
        y: float,
        direction: Direction,
        *,
        owner: Actor | None = None,
        speed: float = 2.0,
        damage: int = 10,
        max_travel_distance: float = 400.0,
        sprite_cycle_speed: int = 6,
    ) -> None:
        super().__init__(
            owner=owner,
            action=Action.ATTACKING,
            direction=direction,
            sprite_cycle_speed=sprite_cycle_speed,
        )

        # state
        self.state = State(action=Action.ATTACKING, direction=direction)
        self.sprites = SpriteCollection()
        self.sprite_cycle_counter = 0
        self.sprite_cycle_speed = sprite_cycle_speed

        self.sprites[Action.ATTACKING, Direction.RIGHT] = [EYEBALL_SPRITE_R1]
        self.sprites[Action.ATTACKING, Direction.LEFT] = [EYEBALL_SPRITE_L1]

        first = self.sprites[self.state.action, self.state.direction][0]
        self.width = first.width
        self.height = first.height

        # position
        self.x = x
        self.y = y
        self.speed = speed

        self.damage = damage

        self.travelled_distance = 0.0
        self.max_travel_distance = float(max_travel_distance)

    # ======== INTERFACE IMPLEMENTATION ========
    def pos(self) -> tuple[float, float]:
        return self.x, self.y

    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def move(self, arena: "Game") -> None:
        if self.state.action is Action.DEAD:
            return

        old_x = self.x

        # --- HORIZONTAL ---
        if self.state.direction is Direction.RIGHT:
            self.x += self.speed
        else:
            self.x -= self.speed

        self.travelled_distance += abs(self.x - old_x)

        # dies after traveling max_travel_distance
        if self.travelled_distance >= self.max_travel_distance:
            self.state.action = Action.DEAD
            return


    def sprite(self) -> Sprite | None:
        if self.state.action is Action.DEAD:
            return None

        sprites = self.sprites[self.state.action, self.state.direction]
        return self._looping_sprite_selection(sprites)

    # ======== METHODS ========
    def hit(self, damage: int | float) -> None:
        self.state.action = Action.DEAD


    # ======== PROPRIETÀ ========
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
    def width(self) -> int:
        return self.__width
    @width.setter
    def width(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("width must be an int")
        self.__width = int(value)

    @property
    def height(self) -> int:
        return self.__height
    @height.setter
    def height(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("height must be an int")
        self.__height = int(value)

    @property
    def speed(self) -> float:
        return self.__speed
    @speed.setter
    def speed(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("speed must be an int or float")
        self.__speed = float(value)

    @property
    def damage(self) -> int:
        return self.__damage
    @damage.setter
    def damage(self, value: int) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("damage must be an int or float")
        self.__damage = int(value)

    @property
    def travelled_distance(self) -> float:
        return self.__travelled_distance
    @travelled_distance.setter
    def travelled_distance(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("travelled_distance must be an int or float")
        self.__travelled_distance = float(value)

    @property
    def max_travel_distance(self) -> float:
        return self.__max_travel_distance
    @max_travel_distance.setter
    def max_travel_distance(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("max_travel_distance must be an int or float")
        self.__max_travel_distance = float(value)
