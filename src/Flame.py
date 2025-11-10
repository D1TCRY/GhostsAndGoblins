from actor import Actor, Arena
from status import Action, Direction, Sprite, SpriteCollection, State
from Zombie import Zombie
from Platform import Platform
import pathlib


SPR_PATH = pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins.png"
FLAME_BIG_R1 = Sprite(SPR_PATH, 116, 427, 34, 33)
FLAME_BIG_R2 = Sprite(SPR_PATH, 152, 427, 26, 33)

FLAME_SMALL_R3 = Sprite(SPR_PATH, 209, 442, 18, 18)
FLAME_SMALL_R4 = Sprite(SPR_PATH, 228, 442, 12, 18)

FLAME_BIG_L1 = Sprite(SPR_PATH, 362, 427, 34, 33)
FLAME_BIG_L2 = Sprite(SPR_PATH, 334, 427, 26, 33)

FLAME_SMALL_L3 = Sprite(SPR_PATH, 285, 442, 18, 18)
FLAME_SMALL_L4 = Sprite(SPR_PATH, 272, 442, 12, 18)


class Flame(Actor):
    def __init__(self,
         x: float,
         y: float,
         *,
         damage: int = 1,
         life_frames: int = 60,
         sprite_cycle_speed: int = 6
    ) -> None:
        self.x = float(x)
        self._ground_y = float(y)
        self._age = 0
        self.life_frames = int(life_frames)

        self.damage = damage

        self.state = State(action=Action.IDLE, direction=Direction.RIGHT)
        self.sprites = SpriteCollection()
        self.sprite_cycle_counter = 0
        self.sprite_cycle_speed = int(sprite_cycle_speed)

        self._big_R = [FLAME_BIG_R1, FLAME_BIG_R2, FLAME_BIG_R1, FLAME_BIG_R2]
        self._big_L = [FLAME_BIG_L1, FLAME_BIG_L2, FLAME_BIG_L1, FLAME_BIG_L2]
        self._small_R = [FLAME_SMALL_R3, FLAME_SMALL_R4, FLAME_SMALL_R3, FLAME_SMALL_R4]
        self._small_L = [FLAME_SMALL_L3, FLAME_SMALL_L4, FLAME_SMALL_L3, FLAME_SMALL_L4]

        self.sprites[(Action.IDLE, Direction.RIGHT)] = self._big_R
        self.sprites[(Action.IDLE, Direction.LEFT)]  = self._big_L

        first = self.sprites[(self.state.action, self.state.direction)][0]
        self.width = first.width
        self.height = first.height

        self.y = self._ground_y - self.height

        self._switched_to_small = False
        self._ground_snapped = False

    @property
    def x(self) -> float:
        return self.__x
    @x.setter
    def x(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("x must be a number")
        self.__x = float(value)

    @property
    def y(self) -> float:
        return self.__y
    @y.setter
    def y(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("y must be a number")
        self.__y = float(value)

    @property
    def width(self) -> int:
        return self.__width
    @width.setter
    def width(self, value: int) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("width must be a number")
        self.__width = int(value)

    @property
    def height(self) -> int:
        return self.__height
    @height.setter
    def height(self, value: int) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("height must be a number")
        self.__height = int(value)

    @property
    def life_frames(self) -> int:
        return self.__life_frames
    @life_frames.setter
    def life_frames(self, value: int) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("life_frames must be a number")
        self.__life_frames = int(value)

    @property
    def state(self) -> State:
        return self.__state
    @state.setter
    def state(self, value: State) -> None:
        if not isinstance(value, State):
            raise TypeError("state must be a State")
        self.__state = value

    @property
    def sprites(self) -> SpriteCollection:
        return self.__sprites
    @sprites.setter
    def sprites(self, value: SpriteCollection) -> None:
        if not isinstance(value, SpriteCollection):
            raise TypeError("sprites must be a SpriteCollection")
        self.__sprites = value

    @property
    def sprite_cycle_counter(self) -> int:
        return self.__sprite_cycle_counter
    @sprite_cycle_counter.setter
    def sprite_cycle_counter(self, value: int) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("sprite_cycle_counter must be a number")
        self.__sprite_cycle_counter = int(value)

    @property
    def sprite_cycle_speed(self) -> int:
        return self.__sprite_cycle_speed
    @sprite_cycle_speed.setter
    def sprite_cycle_speed(self, value: int) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("sprite_cycle_speed must be a number")
        self.__sprite_cycle_speed = int(value)

    @property
    def damage(self) -> int:
        return self.__damage
    @damage.setter
    def damage(self, value: int) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("damage must be a number")
        self.__damage = int(value)

    @property
    def _ground_y(self) -> float:
        return self.__ground_y
    @_ground_y.setter
    def _ground_y(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("_ground_y must be a number")
        self.__ground_y = float(value)

    @property
    def _age(self) -> int:
        return self.__age
    @_age.setter
    def _age(self, value: int) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("_age must be a number")
        self.__age = int(value)

    @property
    def _big_R(self) -> list[Sprite]:
        return self.__big_R
    @_big_R.setter
    def _big_R(self, value: list[Sprite]) -> None:
        self.__big_R = list(value)

    @property
    def _big_L(self) -> list[Sprite]:
        return self.__big_L
    @_big_L.setter
    def _big_L(self, value: list[Sprite]) -> None:
        self.__big_L = list(value)

    @property
    def _small_R(self) -> list[Sprite]:
        return self.__small_R
    @_small_R.setter
    def _small_R(self, value: list[Sprite]) -> None:
        self.__small_R = list(value)

    @property
    def _small_L(self) -> list[Sprite]:
        return self.__small_L
    @_small_L.setter
    def _small_L(self, value: list[Sprite]) -> None:
        self.__small_L = list(value)

    @property
    def _switched_to_small(self) -> bool:
        return self.__switched_to_small
    @_switched_to_small.setter
    def _switched_to_small(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("_switched_to_small must be a bool")
        self.__switched_to_small = bool(value)

    @property
    def _ground_snapped(self) -> bool:
        return self.__ground_snapped
    @_ground_snapped.setter
    def _ground_snapped(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("_ground_snapped must be a bool")
        self.__ground_snapped = bool(value)

    @property
    def reset_sprite_cycle_counter(self) -> int:
        self.sprite_cycle_counter = 0
        return self.sprite_cycle_counter

    @property
    def increment_sprite_cycle_counter(self) -> int:
        self.sprite_cycle_counter += 1
        return self.sprite_cycle_counter

    def pos(self) -> tuple[float, float]:
        return self.x, self.y

    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def move(self, arena: Arena) -> None:
        if not self._ground_snapped:
            best_p: Platform | None = None
            best_dist = float("inf")
            left, right = self.x, self.x + self.width

            for actor in arena.actors():
                if isinstance(actor, Platform):
                    pL, pR = actor.x, actor.x + actor.width

                    h_overlap = min(right, pR) - max(left, pL)
                    if h_overlap <= 0:
                        continue

                    bottom = self.y + self.height
                    dist = abs(bottom - actor.y)
                    if dist < best_dist:
                        best_dist = dist
                        best_p = actor

            if best_p is not None:
                self._ground_y = best_p.y
                self.y = self._ground_y - self.height
            self._ground_snapped = True

        if (not self._switched_to_small) and self._age >= self.life_frames // 2:
            self._switched_to_small = True
            self.sprites[(Action.IDLE, Direction.RIGHT)] = self._small_R
            self.sprites[(Action.IDLE, Direction.LEFT)]  = self._small_L

            first = self.sprites[(self.state.action, self.state.direction)][0]
            self.width = first.width
            self.height = first.height
            self.y = self._ground_y - self.height

            self.sprite_cycle_counter = 0

        self._age += 1
        if self._age >= self.life_frames:
            try:
                arena.kill(self)
            except Exception:
                pass

    def sprite(self) -> Sprite | None:  # type: ignore
        sprites = self.sprites[(self.state.action, self.state.direction)]
        return self._looping_sprite_selection(sprites)

    def _looping_sprite_selection(self, sprites: list[Sprite]) -> Sprite:
        self.sprite_cycle_counter += 1
        return sprites[(self.sprite_cycle_counter // self.sprite_cycle_speed) % len(sprites)]

    def _overlap(self, other: Actor) -> bool:
        x, y = self.pos(); w, h = self.size()
        ox, oy = other.pos(); ow, oh = other.size()
        return not (x + w <= ox or ox + ow <= x or y + h <= oy or oy + oh <= y)
