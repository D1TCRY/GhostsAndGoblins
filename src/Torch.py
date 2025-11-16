from typing import TYPE_CHECKING
if TYPE_CHECKING: from Game import Game
from actor import Actor
from status import Action, Direction, Sprite, SpriteCollection, State
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
        damage: int = 50,
        speed: float = 7,
        gravity: float = 0.7,
        *,
        owner: Actor = None,
        action: Action = Action.ATTACKING,
        direction: Direction,
        sprite_cycle_speed: int = 4
    ) -> None:
        super().__init__(owner=owner, action=action, direction=direction, sprite_cycle_speed=sprite_cycle_speed)

        global TORCH_FLY_R1, TORCH_FLY_R2, TORCH_FLY_R3, TORCH_FLY_R4
        global TORCH_FLY_L1, TORCH_FLY_L2, TORCH_FLY_L3, TORCH_FLY_L4

        # stato e sprite
        self.state = State(action=Action.ATTACKING, direction=direction)
        self.sprites = SpriteCollection()
        self.sprite_cycle_counter = 0
        self.sprite_cycle_speed = int(sprite_cycle_speed)

        self.sprites[Action.ATTACKING, Direction.RIGHT] = [TORCH_FLY_R1, TORCH_FLY_R2, TORCH_FLY_R3, TORCH_FLY_R4] + [
            TORCH_FLY_R3, TORCH_FLY_R2]
        self.sprites[Action.ATTACKING, Direction.LEFT] = [TORCH_FLY_L1, TORCH_FLY_L2, TORCH_FLY_L3, TORCH_FLY_L4] + [
            TORCH_FLY_L3, TORCH_FLY_L2]

        first = self.sprites[self.state.action, self.state.direction][0]
        self.width = first.width
        self.height = first.height

        # posizione e parametri di moto
        self.x = float(x)
        self.y = float(y)
        self.x_step = speed if direction == Direction.RIGHT else -speed
        self.y_step = -5
        self.gravity = float(gravity)

        # danno
        self.damage = damage


    # ======== INTERFACE IMPLEMENTATION ========
    def pos(self) -> tuple[float, float]:
        return self.x, self.y

    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def move(self, arena: "Game") -> None:
        if self.state.action is Action.DEAD:
            return

        # --- VERTICAL ---
        self.y_step += self.gravity
        self.y += self.y_step

        # --- HORIZONTAL ---
        self.x += self.x_step

    def sprite(self) -> Sprite | None:
        if self.state.action == Action.DEAD:
            return None

        sprites = self.sprites[(self.state.action, self.state.direction)]
        return self._looping_sprite_selection(sprites)


    # ======== HELPER METHODS ========
    def on_platform_collision(self, direction: Direction | None, dx: float, dy: float, game: "Game") -> None: # -> chiamato da "Game"
        if direction is Direction.UP:
            self.x += dx
            self.y += dy
            self._spawn_flame(game)
            self.state.action = Action.DEAD
            return
        else:
            self.state.action = Action.DEAD
            return

    def _spawn_flame(self, game: "Game") -> None:
        flame_x = self.x + self.width / 2
        flame_y = self.y + self.height
        game.spawn(Flame(x=flame_x, ground_y=flame_y))

    def hit(self, damage: int | float) -> None:
        self.state.action = Action.DEAD


    # ======== PROPERTIES ========
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
    def x_step(self) -> float:
        return self.__vx
    @x_step.setter
    def x_step(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("x_step must be an int or float")
        self.__vx = float(value)

    @property
    def y_step(self) -> float:
        return self.__vy
    @y_step.setter
    def y_step(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("y_step must be an int or float")
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
    def damage(self) -> int:
        return self.__damage
    @damage.setter
    def damage(self, value: int):
        if not isinstance(value, int):
            raise TypeError("damage must be an int")
        self.__damage = int(value)