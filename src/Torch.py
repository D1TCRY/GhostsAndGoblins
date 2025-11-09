from actor import Actor, Arena
from status import Action, Direction, Sprite, SpriteCollection, State
from Platform import Platform
from Zombie import Zombie
from Flame import Flame
from Weapon import Weapon
import pathlib


SPR_PATH = pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins.png"

TORCH_FLY_R1 = Sprite(SPR_PATH, 18, 398, 16, 16)
TORCH_FLY_R2 = Sprite(SPR_PATH, 39, 398, 16, 16)
TORCH_FLY_R3 = Sprite(SPR_PATH, 57, 399, 16, 16)
TORCH_FLY_R4 = Sprite(SPR_PATH, 77, 398, 16, 16)

TORCH_FLY_L1 = Sprite(SPR_PATH, 478, 398, 16, 16)
TORCH_FLY_L2 = Sprite(SPR_PATH, 457, 398, 16, 16)
TORCH_FLY_L3 = Sprite(SPR_PATH, 439, 399, 16, 16)
TORCH_FLY_L4 = Sprite(SPR_PATH, 419, 398, 16, 16)



class Torch(Weapon):
    def __init__(self,
        x: float,
        y: float,
        direction: Direction,
        *,
        speed: float = 7,
        gravity: float = 0.7,
        sprite_cycle_speed: int = 4
    ) -> None:
        super().__init__()

        global TORCH_FLY_R1, TORCH_FLY_R2, TORCH_FLY_R3, TORCH_FLY_R4
        global TORCH_FLY_L1, TORCH_FLY_L2, TORCH_FLY_L3, TORCH_FLY_L4

        self.x = float(x)
        self.y = float(y)
        self.vx = speed if direction == Direction.RIGHT else -speed
        self.vy = -7
        self.gravity = float(gravity)

        self.state = State(action=Action.ATTACKING, direction=direction)
        self.sprites = SpriteCollection()
        self.sprite_cycle_counter = 0
        self.sprite_cycle_speed = int(sprite_cycle_speed)

        self.sprites[(Action.ATTACKING, Direction.RIGHT)] = [TORCH_FLY_R1, TORCH_FLY_R2, TORCH_FLY_R3, TORCH_FLY_R4] + [TORCH_FLY_R3, TORCH_FLY_R2]
        self.sprites[(Action.ATTACKING, Direction.LEFT)]  = [TORCH_FLY_L1, TORCH_FLY_L2, TORCH_FLY_L3, TORCH_FLY_L4] + [TORCH_FLY_L3, TORCH_FLY_L2]

        first = self.sprites[(self.state.action, self.state.direction)][0]
        self.width = first.width
        self.height = first.height

        self._alive = True

    @property
    def x(self) -> float:
        return self.__x
    @x.setter
    def x(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("x must be an int or float")
        self.__x = float(value)

    @property
    def y(self) -> float:
        return self.__y
    @y.setter
    def y(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("y must be an int or float")
        self.__y = float(value)

    @property
    def vx(self) -> float:
        return self.__vx
    @vx.setter
    def vx(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("vx must be an int or float")
        self.__vx = float(value)

    @property
    def vy(self) -> float:
        return self.__vy
    @vy.setter
    def vy(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("vy must be an int or float")
        self.__vy = float(value)

    @property
    def gravity(self) -> float:
        return self.__gravity
    @gravity.setter
    def gravity(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("gravity must be an int or float")
        self.__gravity = float(value)

    @property
    def state(self) -> State:
        return self.__state
    @state.setter
    def state(self, value: State):
        if not isinstance(value, State):
            raise TypeError("state must be a State")
        self.__state = value

    @property
    def sprites(self) -> SpriteCollection:
        return self.__sprites
    @sprites.setter
    def sprites(self, value: SpriteCollection):
        if not isinstance(value, SpriteCollection):
            raise TypeError("sprites must be a SpriteCollection")
        self.__sprites = value

    @property
    def sprite_cycle_counter(self) -> int:
        return self.__sprite_cycle_counter
    @sprite_cycle_counter.setter
    def sprite_cycle_counter(self, value: int):
        if not isinstance(value, int):
            raise TypeError("sprite_cycle_counter must be an int")
        self.__sprite_cycle_counter = int(value)

    @property
    def sprite_cycle_speed(self) -> int:
        return self.__sprite_cycle_speed
    @sprite_cycle_speed.setter
    def sprite_cycle_speed(self, value: int):
        if not isinstance(value, int):
            raise TypeError("sprite_cycle_speed must be an int")
        self.__sprite_cycle_speed = int(value)

    @property
    def width(self) -> int:
        return self.__width
    @width.setter
    def width(self, value: int):
        if not isinstance(value, int):
            raise TypeError("width must be an int")
        self.__width = int(value)

    @property
    def height(self) -> int:
        return self.__height
    @height.setter
    def height(self, value: int):
        if not isinstance(value, int):
            raise TypeError("height must be an int")
        self.__height = int(value)

    @property
    def _alive(self) -> bool:
        return self.__alive
    @_alive.setter
    def _alive(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("_alive must be a bool")
        self.__alive = bool(value)

    def pos(self) -> tuple[float, float]:
        return self.x, self.y

    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def move(self, arena: Arena) -> None:
        if not self._alive:
            return

        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

        a_w, a_h = arena.size()
        if self.x + self.width < 0 or self.x > a_w or self.y > a_h or self.y + self.height < 0:
            self._despawn(arena)
            return

        for actor in arena.actors():
            if isinstance(actor, Zombie) and self._overlap(actor):
                try:
                    arena.kill(actor)
                except Exception:
                    pass
                self._despawn(arena)
                return


        for actor in arena.actors():
            if isinstance(actor, Platform):
                direction, dx, dy = actor.clamp(self)
                if direction is None:
                    continue
                if direction == Direction.UP:
                    self.x += dx
                    self.y += dy
                    self._spawn_flame(arena)
                    self._despawn(arena)
                    return
                else:
                    self._despawn(arena)
                    return

    def sprite(self) -> Sprite | None:  # type: ignore
        sprites = self.sprites[(self.state.action, self.state.direction)]
        return self._looping_sprite_selection(sprites)

    def _overlap(self, other: Actor) -> bool:
        x, y = self.pos(); w, h = self.size()
        ox, oy = other.pos(); ow, oh = other.size()
        return not (x + w <= ox or ox + ow <= x or y + h <= oy or oy + oh <= y)

    def _spawn_flame(self, arena: Arena) -> None:
        flame_x = self.x + self.width / 2 - 10
        flame_y = self.y + self.height - 8
        arena.spawn(Flame(x=flame_x, y=flame_y))

    def _despawn(self, arena: Arena) -> None:
        self._alive = False
        try:
            arena.kill(self)
        except Exception:
            pass
