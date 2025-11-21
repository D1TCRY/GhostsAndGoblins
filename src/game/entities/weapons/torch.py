from typing import TYPE_CHECKING
import pathlib

# CORE
if TYPE_CHECKING: from ...core import Game
from ...core.file_management import read_settings

# ACTOR
from ..actor import Actor

# STATE
from ...state import Action, Direction, Sprite, SpriteCollection, EntityState

# OBJECTS
from ..objects import Flame

# WEAPONS
from ..weapons import Weapon


SPR_PATH = pathlib.Path(__file__).parent.parent.parent.parent / "data" / "textures" / "ghosts-goblins.png"

TORCH_FLY_R1 = Sprite(SPR_PATH, 18, 398, 16, 16)
TORCH_FLY_R2 = Sprite(SPR_PATH, 39, 398, 16, 16)
TORCH_FLY_R3 = Sprite(SPR_PATH, 57, 399, 16, 16)
TORCH_FLY_R4 = Sprite(SPR_PATH, 77, 398, 16, 16)

TORCH_FLY_L1 = Sprite(SPR_PATH, 478, 398, 16, 16)
TORCH_FLY_L2 = Sprite(SPR_PATH, 457, 398, 16, 16)
TORCH_FLY_L3 = Sprite(SPR_PATH, 439, 399, 16, 16)
TORCH_FLY_L4 = Sprite(SPR_PATH, 419, 398, 16, 16)



class Torch(Weapon):
    def __init__(
        self,
        x: float,
        y: float,
        damage: int | float | None = None,
        speed: float | None = None,
        gravity: float | None = None,
        *,
        owner: Actor | None = None,
        action: Action | None = None,
        direction: Direction | None = None,
        sprite_cycle_speed: int | None = None,
    ) -> None:
        defaults: dict = read_settings().get("Torch", {}).get("defaults", {})

        # DEFAULTS
        self.damage = damage if damage is not None else defaults.get("damage", 50)
        self.speed = speed if speed is not None else defaults.get("speed", 7.0)
        self.gravity = gravity if gravity is not None else defaults.get("gravity", 0.7)
        self.sprite_cycle_speed = sprite_cycle_speed if sprite_cycle_speed is not None else defaults.get("sprite_cycle_speed", 4)

        action_val = action if action is not None else getattr(Action, defaults.get("action", "ATTACKING"), Action.ATTACKING)
        self.direction = direction if direction is not None else getattr(Direction, defaults.get("direction", "RIGHT"), Direction.RIGHT)

        super().__init__(owner=owner, action=action_val, direction=self.direction, sprite_cycle_speed=self.sprite_cycle_speed)

        # STATE
        self.state = EntityState(action=Action.ATTACKING, direction=self.direction)
        self.sprites = SpriteCollection()
        self.init_sprites()
        self.sprite_cycle_counter = 0

        first = self.sprites[self.state.action, self.state.direction][0]
        self.width = first.width
        self.height = first.height

        # POSITION
        self.x = float(x)
        self.y = float(y)
        self.x_step = self.speed if self.direction == Direction.RIGHT else -self.speed
        self.y_step = -5
        self.gravity = float(self.gravity)


    def init_sprites(self) -> None:
        global TORCH_FLY_R1, TORCH_FLY_R2, TORCH_FLY_R3, TORCH_FLY_R4
        global TORCH_FLY_L1, TORCH_FLY_L2, TORCH_FLY_L3, TORCH_FLY_L4

        self.sprites[Action.ATTACKING, Direction.RIGHT] = [
            TORCH_FLY_R1, TORCH_FLY_R2, TORCH_FLY_R3, TORCH_FLY_R4,
            TORCH_FLY_R3, TORCH_FLY_R2
        ]
        self.sprites[Action.ATTACKING, Direction.LEFT] = [
            TORCH_FLY_L1, TORCH_FLY_L2, TORCH_FLY_L3, TORCH_FLY_L4,
            TORCH_FLY_L3, TORCH_FLY_L2
        ]

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
        self.__x: float = float(value)

    @property
    def y(self) -> float:
        return self.__y
    @y.setter
    def y(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("y must be an int or float")
        self.__y: float = float(value)

    @property
    def x_step(self) -> float:
        return self.__vx
    @x_step.setter
    def x_step(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("x_step must be an int or float")
        self.__vx: float = float(value)

    @property
    def y_step(self) -> float:
        return self.__vy
    @y_step.setter
    def y_step(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("y_step must be an int or float")
        self.__vy: float = float(value)

    @property
    def gravity(self) -> float:
        return self.__gravity
    @gravity.setter
    def gravity(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("gravity must be an int or float")
        self.__gravity: float = float(value)

    @property
    def state(self) -> EntityState:
        return self.__state
    @state.setter
    def state(self, value: EntityState):
        if not isinstance(value, EntityState):
            raise TypeError("state must be a State")
        self.__state: EntityState = value

    @property
    def sprites(self) -> SpriteCollection:
        return self.__sprites
    @sprites.setter
    def sprites(self, value: SpriteCollection):
        if not isinstance(value, SpriteCollection):
            raise TypeError("sprites must be a SpriteCollection")
        self.__sprites: SpriteCollection = value

    @property
    def width(self) -> int:
        return self.__width
    @width.setter
    def width(self, value: int):
        if not isinstance(value, int):
            raise TypeError("width must be an int")
        self.__width: int = int(value)

    @property
    def height(self) -> int:
        return self.__height
    @height.setter
    def height(self, value: int):
        if not isinstance(value, int):
            raise TypeError("height must be an int")
        self.__height: int = int(value)

    @property
    def damage(self) -> float:
        return self.__damage
    @damage.setter
    def damage(self, value: int | float):
        if not isinstance(value, (int, float)):
            raise TypeError("damage must be an int")
        self.__damage: float = float(value)