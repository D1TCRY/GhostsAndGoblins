from actor import Actor, Arena, check_collision, check_overlap
from Platform import Platform
from Ladder import Ladder
from Torch import Torch
from src.GraveStone import GraveStone

from status import Sprite, State, Action, Direction, SpriteCollection

import pathlib


ARTHUR_SPRITE_PATH = pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins.png"
ARTHUR_SPRITE_WIDTH = 21
ARTHUR_SPRITE_HEIGHT = 32

# IDLE
ARTHUR_SPRITE_IDLE_R: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=7, y=42, width=19, height=ARTHUR_SPRITE_HEIGHT)
ARTHUR_SPRITE_IDLE_L: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=486, y=42, width=19, height=ARTHUR_SPRITE_HEIGHT)

# WALKING
ARTHUR_SPRITE_WALKING_R1: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=41, y=42, width=22, height=ARTHUR_SPRITE_HEIGHT)
ARTHUR_SPRITE_WALKING_R2: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=67, y=42, width=18, height=ARTHUR_SPRITE_HEIGHT)
ARTHUR_SPRITE_WALKING_R3: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=89, y=42, width=18, height=ARTHUR_SPRITE_HEIGHT)
ARTHUR_SPRITE_WALKING_R4: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=110, y=42, width=23, height=ARTHUR_SPRITE_HEIGHT)

ARTHUR_SPRITE_WALKING_L1: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=449, y=42, width=22, height=ARTHUR_SPRITE_HEIGHT)
ARTHUR_SPRITE_WALKING_L2: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=427, y=42, width=18, height=ARTHUR_SPRITE_HEIGHT)
ARTHUR_SPRITE_WALKING_L3: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=405, y=42, width=18, height=ARTHUR_SPRITE_HEIGHT)
ARTHUR_SPRITE_WALKING_L4: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=379, y=42, width=23, height=ARTHUR_SPRITE_HEIGHT)

# JUMPING
ARTHUR_SPRITE_JUMPING_R1: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=144, y=29, width=32, height=ARTHUR_SPRITE_HEIGHT)
ARTHUR_SPRITE_JUMPING_R2: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=181, y=29, width=26, height=ARTHUR_SPRITE_HEIGHT)

ARTHUR_SPRITE_JUMPING_L1: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=336, y=29, width=32, height=ARTHUR_SPRITE_HEIGHT)
ARTHUR_SPRITE_JUMPING_L2: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=305, y=29, width=26, height=ARTHUR_SPRITE_HEIGHT)

# CROUCHING
ARTHUR_SPRITE_CROUCHING_R: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=224, y=52, width=21, height=22)
ARTHUR_SPRITE_CROUCHING_L: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=267, y=52, width=21, height=22)




class Arthur(Actor):
    def __init__(self, 
        name: str, 
        x: int | float, 
        y: int | float, 
        width: int = 21,
        height: int = 31,
        speed: float = 5,
        gravity: float = 0.7,
        jump_speed: float = 10.0,
        health: int | float = 100
    ) -> None:
        global ARTHUR_SPRITE_IDLE_R, ARTHUR_SPRITE_IDLE_L

        global ARTHUR_SPRITE_WALKING_R1, ARTHUR_SPRITE_WALKING_R2, ARTHUR_SPRITE_WALKING_R3, ARTHUR_SPRITE_WALKING_R4
        global ARTHUR_SPRITE_WALKING_L1, ARTHUR_SPRITE_WALKING_L2, ARTHUR_SPRITE_WALKING_L3, ARTHUR_SPRITE_WALKING_L4

        global ARTHUR_SPRITE_JUMPING_R1, ARTHUR_SPRITE_JUMPING_R2
        global ARTHUR_SPRITE_JUMPING_L1, ARTHUR_SPRITE_JUMPING_L2

        global ARTHUR_SPRITE_CROUCHING_R, ARTHUR_SPRITE_CROUCHING_L

        self.name = name
        
        self.x = x
        self.y = y
        
        self.width = width
        self.height = height
        
        self.speed = speed
        self.x_step = 0

        self.gravity = gravity
        self.jump_speed = jump_speed
        self.y_step = 0
        
        self.health = health
        
        self.state = State(action=Action.WALKING, direction=Direction.RIGHT)
        self.sprite_cycle_counter = 0
        self.sprite_cycle_speed = 4

        self.grounded = False
        self.throw_cooldown = 0  # throw torch

        # Sprites
        self.sprites = SpriteCollection()

        self.sprites[Action.IDLE, Direction.RIGHT] = [ARTHUR_SPRITE_IDLE_R]
        self.sprites[Action.IDLE, Direction.LEFT] = [ARTHUR_SPRITE_IDLE_L]

        self.sprites[Action.WALKING, Direction.RIGHT] = [ARTHUR_SPRITE_WALKING_R1, ARTHUR_SPRITE_WALKING_R2, ARTHUR_SPRITE_WALKING_R3, ARTHUR_SPRITE_WALKING_R4] + [ARTHUR_SPRITE_WALKING_R3, ARTHUR_SPRITE_WALKING_R2]
        self.sprites[Action.WALKING, Direction.LEFT] = [ARTHUR_SPRITE_WALKING_L1, ARTHUR_SPRITE_WALKING_L2, ARTHUR_SPRITE_WALKING_L3, ARTHUR_SPRITE_WALKING_L4] + [ARTHUR_SPRITE_WALKING_L3, ARTHUR_SPRITE_WALKING_L2]

        self.sprites[Action.JUMPING, Direction.RIGHT] = [ARTHUR_SPRITE_JUMPING_R1]*3 + [ARTHUR_SPRITE_JUMPING_R2]
        self.sprites[Action.JUMPING, Direction.LEFT] = [ARTHUR_SPRITE_JUMPING_L1]*3 + [ARTHUR_SPRITE_JUMPING_L2]

        self.sprites[Action.CROUCHING, Direction.RIGHT] = [ARTHUR_SPRITE_CROUCHING_R]
        self.sprites[Action.CROUCHING, Direction.LEFT] = [ARTHUR_SPRITE_CROUCHING_L]

    
    # ======== ======== ======== ========
    # PROPERTIES
    # ........ ........ ........ ........
    @property
    def name(self) -> str:
        return self.__name
    @name.setter
    def name(self, value: str):
        self.__name: str = str(value)
    
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
    def speed(self) -> float:
        return self.__speed
    @speed.setter
    def speed(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("speed must be an int or float")
        self.__speed: float = float(value)

    @property
    def x_step(self) -> float:
        return self.__x_step
    @x_step.setter
    def x_step(self, value: int | float):
        if not isinstance(value, (int, float)):
            raise TypeError("x_step must be an int or float")
        self.__x_step: float = float(value)

    @property
    def gravity(self) -> float:
        return self.__gravity
    @gravity.setter
    def gravity(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("gravity must be an int or float")
        self.__gravity: float = float(value)
    
    @property
    def jump_speed(self) -> float:
        return self.__jump_speed
    @jump_speed.setter
    def jump_speed(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("jump_speed must be an int or float")
        self.__jump_speed: float = float(value)

    @property
    def y_step(self) -> float:
        return self.__y_step
    @y_step.setter
    def y_step(self, value: int | float):
        if not isinstance(value, (int, float)):
            raise TypeError("y_step must be an int or float")
        self.__y_step: float = float(value)

    @property
    def health(self) -> float:
        return self.__health
    @health.setter
    def health(self, value: int | float):
        if not isinstance(value, (int, float)):
            raise TypeError("health must be an int or float")
        self.__health: float = max(0.0, min(float(value), 100.0))
    
    @property
    def state(self) -> State:
        return self.__state
    @state.setter
    def state(self, value: State):
        if not isinstance(value, State):
            raise TypeError("state must be an instance of State")
        self.__state: State = value
    
    @property
    def sprite_cycle_counter(self) -> int:
        return self.__sprite_cycle_counter
    @sprite_cycle_counter.setter
    def sprite_cycle_counter(self, value: int):
        if not isinstance(value, int):
            raise TypeError("sprite_cycle_counter must be an int")
        self.__sprite_cycle_counter: int = int(value)
    
    @property
    def sprite_cycle_speed(self) -> int:
        return self.__sprite_cycle_speed
    @sprite_cycle_speed.setter
    def sprite_cycle_speed(self, value: int):
        if not isinstance(value, int):
            raise TypeError("sprite_cycle_speed must be an int")
        self.__sprite_cycle_speed: int = int(value)

    @property
    def grounded(self) -> bool:
        return self.__grounded
    @grounded.setter
    def grounded(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("grounded must be a boolean")
        self.__grounded: bool = bool(value)

    @property
    def throw_cooldown(self) -> int:
        return self.__throw_cooldown
    @throw_cooldown.setter
    def throw_cooldown(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("throw_cooldown must be an int")
        self.__throw_cooldown: int = int(value)


    @property
    def reset_sprite_cycle_counter(self) -> int:
        self.sprite_cycle_counter = 0
        return self.sprite_cycle_counter

    @property
    def increment_sprite_cycle_counter(self) -> int:
        self.sprite_cycle_counter += 1
        return self.sprite_cycle_counter
    # ^^^^^^^^ ^^^^^^^^ ^^^^^^^^ ^^^^^^^^
    # PROPERTIES 
    # ======== ======== ======== ========
    
    
    
    # ======== ======== ======== ========
    # INTERFACE IMPLEMENTATION 
    # ........ ........ ........ ........
    def pos(self) -> tuple[float, float]:
        return self.x, self.y
    
    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def move(self, arena: Arena) -> None:
        keys: list[str] = arena.current_keys()
        actors: list[Actor] = arena.actors()

        if self.throw_cooldown > 0:
            self.throw_cooldown -= 1

        # --- LANCIO FIACCOLA ---
        if "1" in keys and self.throw_cooldown == 0:
            offset_x = 10 if self.state.direction == Direction.RIGHT else -10
            spawn_x = self.x + (self.width // 2) + offset_x
            spawn_y = self.y + self.height * 0.1

            torch = Torch(x=spawn_x, y=spawn_y, direction=self.state.direction)
            try:
                arena.spawn(torch)
            except Exception:
                pass

            self.throw_cooldown = 10


        # --- VERTICALE ---
        laddered: Ladder | None = self.on_ladder(arena)
        if laddered is not None:
            self.grounded = False
            self.y_step = 0.0
            if "ArrowUp" in keys:
                self.y_step = -2
            if "ArrowDown" in keys:
                self.y_step = 2

            self.y += self.y_step
        else:
            can_jump = self.grounded

            if "ArrowUp" in keys and can_jump:
                self.y_step = -self.jump_speed
                self._set_state_action(Action.JUMPING)
            elif "ArrowDown" in keys and self.grounded:
                self._set_state_action(Action.CROUCHING)
            elif self.grounded:
                self._set_state_action(Action.WALKING if self.x_step != 0.0 else Action.IDLE)
            else:
                self._set_state_action(Action.JUMPING)

            self.y_step += self.gravity
            self.y += self.y_step


        # --- ORIZZONTALE ---
        self.x_step = 0.0
        if "ArrowLeft" in keys and self.state.action not in (Action.CROUCHING,):
            self.x_step = -self.speed
            self.state.direction = Direction.LEFT
        elif "ArrowRight" in keys and self.state.action not in (Action.CROUCHING,):
            self.x_step = self.speed
            self.state.direction = Direction.RIGHT
        elif self.state.action not in (Action.JUMPING, Action.CROUCHING):
            self._set_state_action(Action.WALKING if self.x_step != 0.0 else Action.IDLE)
        self.x += self.x_step


        self.grounded = False
        for platform in [_ for _ in actors if isinstance(_, Platform)]:
            if self.apply_clamp_on_platform(platform): # if landed
                self.grounded = True


    def sprite(self) -> Sprite | None: # type: ignore
        list_sprites = self.sprites[self.state.action, self.state.direction]

        match self.state.action:
            case Action.IDLE: return self._locked_looping_sprite_selection(list_sprites)
            case Action.WALKING: return self._looping_sprite_selection(list_sprites)
            case Action.JUMPING: return self._locked_looping_sprite_selection(list_sprites)
            case Action.CROUCHING: return self._locked_looping_sprite_selection(list_sprites)
            case _: return None
    # ^^^^^^^^ ^^^^^^^^ ^^^^^^^^ ^^^^^^^^
    # INTERFACE IMPLEMENTATION 
    # ======== ======== ======== ========
    
    # ======== ======== ======== ========
    # HELPER METHODS 
    # ........ ........ ........ ........
    def on_ladder(self, arena: Arena) -> Ladder | None:
        for ladder in [_ for _ in arena.actors() if isinstance(_, Ladder)]:
            if ladder.check_collision(self): return ladder
        return None

    def on_platform(self, arena: Arena) -> Platform | None:
        for platform in [_ for _ in arena.actors() if isinstance(_, Platform) and not isinstance(_, (Ladder,))]:
            if platform.check_collision(self): return platform
        return None

    def apply_clamp_on_platform(self, platform: Platform) -> bool:
        direction, dx, dy = platform.clamp(self)
        if direction is None:
            return False

        if dx: self.x += dx
        if dy: self.y += dy

        if direction in (Direction.LEFT, Direction.RIGHT):
            self.x_step = 0.0
            return False
        else:
            self.y_step = 0.0
            return direction == Direction.UP

    def inside_arena(self, arena: Arena) -> bool:
        a_width, a_height = arena.size()
        return self.x >= 0 and self.x + self.width <= a_width and self.__y + self.height <= a_height


    def _looping_sprite_selection(self, sprites: list[Sprite]) -> Sprite:
        self.sprite_cycle_counter += 1
        return sprites[(self.sprite_cycle_counter // self.__sprite_cycle_speed) % len(sprites)]

    def _locked_looping_sprite_selection(self, sprites: list[Sprite]) -> Sprite:
        self.sprite_cycle_counter += 1
        i = self.sprite_cycle_counter // self.__sprite_cycle_speed
        return sprites[i if i < len(sprites) else -1]

    def _set_state_action(self, action: Action) -> None:
        if self.state.action != action:
            _ = self.reset_sprite_cycle_counter

        self.state.action = action

        self.y = self.y + self.height - self.sprites[self.state.action, self.state.direction][0].height

        self.width = max(self.width, min(self.sprites[self.state.action, self.state.direction][0].width, 28))
        self.height = self.sprites[self.state.action, self.state.direction][0].height

    # ^^^^^^^^ ^^^^^^^^ ^^^^^^^^ ^^^^^^^^
    # HELPER METHODS
    # ======== ======== ======== ========

    # ======== ======== ======== ========
    # GET METHODS
    # ........ ........ ........ ........
    def get_health_value(self) -> float:
        return self.health
    # ^^^^^^^^ ^^^^^^^^ ^^^^^^^^ ^^^^^^^^
    # GET METHODS
    # ======== ======== ======== ========