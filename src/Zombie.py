from actor import Actor, Arena
from Platform import Platform

from guis import GUIComponent, Bar
from status import Action, Direction, Sprite, SpriteCollection, State

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Arthur import Arthur

import random
import pathlib


# EMERGING
ZOMBIE_EMERGING_L1: Sprite = Sprite(path=pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins.png", x=512, y=65, width=16, height=32)
ZOMBIE_EMERGING_L2: Sprite = Sprite(path=pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins.png", x=533, y=65, width=25, height=32)
ZOMBIE_EMERGING_L3: Sprite = Sprite(path=pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins.png", x=562, y=65, width=18, height=32)
ZOMBIE_EMERGING_L4: Sprite = Sprite(path=pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins.png", x=610, y=65, width=18, height=32)

ZOMBIE_EMERGING_R1: Sprite = Sprite(path=pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins.png", x=778, y=65, width=16, height=32)
ZOMBIE_EMERGING_R2: Sprite = Sprite(path=pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins.png", x=748, y=65, width=25, height=32)
ZOMBIE_EMERGING_R3: Sprite = Sprite(path=pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins.png", x=726, y=65, width=18, height=32)
ZOMBIE_EMERGING_R4: Sprite = Sprite(path=pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins.png", x=678, y=65, width=18, height=32)

# WALK
ZOMBIE_WALK_L1: Sprite = Sprite(path=pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins.png", x=585, y=65, width=21, height=32)
ZOMBIE_WALK_L2: Sprite = Sprite(path=pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins.png", x=610, y=65, width=18, height=32)
ZOMBIE_WALK_L3: Sprite = Sprite(path=pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins.png", x=631, y=65, width=20, height=32)

ZOMBIE_WALK_R1: Sprite = Sprite(path=pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins.png", x=700, y=65, width=21, height=32)
ZOMBIE_WALK_R2: Sprite = Sprite(path=pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins.png", x=678, y=65, width=18, height=32)
ZOMBIE_WALK_R3: Sprite = Sprite(path=pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins.png", x=655, y=65, width=20, height=32)




class Zombie(Actor):
    def __init__(
        self,
        name: str,
        x: int | float,
        y: int | float,
        *,
        health: float = 70.0,
        width: int = 21,
        height: int = 32,
        speed: float = 1.0,
        min_walk_distance: float = 150.0,
        max_walk_distance: float = 300.0,
        sprite_cycle_speed: int = 6,
        direction: Direction = Direction.LEFT,
    ) -> None:
        global ZOMBIE_EMERGING_L1, ZOMBIE_EMERGING_L2, ZOMBIE_EMERGING_L3, ZOMBIE_EMERGING_L4
        global ZOMBIE_EMERGING_R1, ZOMBIE_EMERGING_R2, ZOMBIE_EMERGING_R3, ZOMBIE_EMERGING_R4
        global ZOMBIE_WALK_L1, ZOMBIE_WALK_L2, ZOMBIE_WALK_L3
        global ZOMBIE_WALK_R1, ZOMBIE_WALK_R2, ZOMBIE_WALK_R3

        self.name = name
        self.health = health

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.speed = speed
        self.x_step = 0.0

        self.min_walk_distance = float(min_walk_distance)
        self.max_walk_distance = float(max_walk_distance)
        self.distance_to_walk = random.uniform(self.min_walk_distance, self.max_walk_distance)
        self.walked_distance = 0.0

        self.state = State(action=Action.EMERGING, direction=direction)

        self.sprite_cycle_counter = 0
        self.sprite_cycle_speed = int(sprite_cycle_speed)


        # default properties
        self.sprites = SpriteCollection()

        self.sprites[(Action.EMERGING, Direction.LEFT)] = [
            ZOMBIE_EMERGING_L1, ZOMBIE_EMERGING_L2, ZOMBIE_EMERGING_L3, ZOMBIE_EMERGING_L4
        ]
        self.sprites[(Action.EMERGING, Direction.RIGHT)] = [
            ZOMBIE_EMERGING_R1, ZOMBIE_EMERGING_R2, ZOMBIE_EMERGING_R3, ZOMBIE_EMERGING_R4
        ]

        self.sprites[(Action.IMMERSING, Direction.LEFT)] = list(reversed(self.sprites[(Action.EMERGING, Direction.LEFT)]))
        self.sprites[(Action.IMMERSING, Direction.RIGHT)] = list(reversed(self.sprites[(Action.EMERGING, Direction.RIGHT)]))

        self.sprites[(Action.WALKING, Direction.LEFT)] = [ZOMBIE_WALK_L1, ZOMBIE_WALK_L2, ZOMBIE_WALK_L3]
        self.sprites[(Action.WALKING, Direction.RIGHT)] = [ZOMBIE_WALK_R1, ZOMBIE_WALK_R2, ZOMBIE_WALK_R3]

        self.sprites[(Action.DEAD, Direction.LEFT)] = []
        self.sprites[(Action.DEAD, Direction.RIGHT)] = []

        first = self.sprites[(self.state.action, self.state.direction)][0]
        self.width = first.width
        self.height = first.height

    # ======== PROPERTIES ========
    @property
    def name(self) -> str:
        return self.__name
    @name.setter
    def name(self, value: str):
        self.__name = str(value)

    @property
    def x(self) -> float:
        return self.__x
    @x.setter
    def x(self, value: int | float):
        if not isinstance(value, (int, float)):
            raise TypeError("x must be an int or float")
        self.__x = float(value)

    @property
    def y(self) -> float:
        return self.__y
    @y.setter
    def y(self, value: int | float):
        if not isinstance(value, (int, float)):
            raise TypeError("y must be an int or float")
        self.__y = float(value)

    @property
    def health(self) -> float:
        return self.__health
    @health.setter
    def health(self, value: int | float):
        if not isinstance(value, (int, float)):
            raise TypeError("health must be an int or float")
        self.__health = float(value)
        if self.__health <= 0:
            self._set_state_action(Action.DEAD)
            self.walked_distance = 0.0
            self.distance_to_walk = random.uniform(self.min_walk_distance, self.max_walk_distance)

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
    def speed(self) -> float:
        return self.__speed
    @speed.setter
    def speed(self, value: int | float):
        if not isinstance(value, (int, float)):
            raise TypeError("speed must be an int or float")
        self.__speed = float(value)

    @property
    def x_step(self) -> float:
        return self.__x_step
    @x_step.setter
    def x_step(self, value: int | float):
        if not isinstance(value, (int, float)):
            raise TypeError("x_step must be an int or float")
        self.__x_step = float(value)

    @property
    def state(self) -> "State":
        return self.__state
    @state.setter
    def state(self, value: "State"):
        # State(action: Action, direction: Direction)
        self.__state = value

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
    def reset_sprite_cycle_counter(self) -> int:
        self.sprite_cycle_counter = 0
        return self.sprite_cycle_counter

    @property
    def increment_sprite_cycle_counter(self) -> int:
        self.sprite_cycle_counter += 1
        return self.sprite_cycle_counter

    @property
    def gui(self) -> list[GUIComponent]:
        bar_w, bar_h = self.width, 3
        return [Bar(
            name_id=self.name,
            x=self.x,
            y=self.y - bar_h - 1,
            width=bar_w,
            height=bar_h,
            text="",
            text_size=1,
            text_color=(0,0,0,0),
            background_color=(116, 16, 8),
            bar_color=(128, 248, 96),
            max_value=70,
            value=self.health,
            padding=0,
            fixed=False
        )]

    # ======== INTERFACE ========
    def pos(self) -> tuple[float, float]:
        return self.x, self.y

    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def move(self, arena: "Arena") -> None:
        if self.state.action == Action.DEAD:
            return

        borders = self._clamp_in_arena(arena)
        if borders["at_left"] and self.state.direction == Direction.LEFT:
            self.state.direction = Direction.RIGHT
        elif borders["at_right"] and self.state.direction == Direction.RIGHT:
            self.state.direction = Direction.LEFT

        if self.state.action == Action.EMERGING:
            if self._locked_anim_finished():
                self._set_state_action(Action.WALKING)

        elif self.state.action == Action.WALKING:
            self.x_step = self.speed if self.state.direction == Direction.RIGHT else -self.speed
            self.x += self.x_step

            self.walked_distance += abs(self.x_step)
            if self.walked_distance >= self.distance_to_walk:
                self._set_state_action(Action.IMMERSING)

        elif self.state.action == Action.IMMERSING:
            if self._locked_anim_finished():
                self._set_state_action(Action.DEAD)

        self._clamp_in_arena(arena)

    def sprite(self) -> "Sprite | None":  # type: ignore
        sprites = self.sprites[(self.state.action, self.state.direction)]
        match self.state.action:
            case Action.WALKING:
                return self._looping_sprite_selection(sprites)
            case Action.EMERGING | Action.IMMERSING:
                return self._locked_looping_sprite_selection(sprites)
            case Action.DEAD:
                return None
            case _:
                return None

    def hit(self, damage: float) -> None:
        self.health -= damage

    # ======== HELPERS ========
    def _set_state_action(self, action: Action) -> None:
        if self.state.action != action:
            _ = self.reset_sprite_cycle_counter
            # update width, height, y based on the first sprite
            if action not in (Action.DEAD,):
                first = self.sprites[(action, self.state.direction)][0]
                self.y = self.y + self.height - first.height  # keep on ground
                self.width = first.width
                self.height = first.height
            self.state.action = action

    def _looping_sprite_selection(self, sprites: list["Sprite"]) -> "Sprite":
        self.sprite_cycle_counter += 1
        return sprites[(self.sprite_cycle_counter // self.sprite_cycle_speed) % len(sprites)]

    def _locked_looping_sprite_selection(self, sprites: list["Sprite"]) -> "Sprite":
        self.sprite_cycle_counter += 1
        i = self.sprite_cycle_counter // self.sprite_cycle_speed
        return sprites[i if i < len(sprites) else -1]

    def _locked_anim_finished(self) -> bool:
        sprites = self.sprites[(self.state.action, self.state.direction)]
        i = self.sprite_cycle_counter // self.sprite_cycle_speed
        return i >= len(sprites) - 1

    def _clamp_in_arena(self, arena: "Arena") -> dict[str, bool]:
        A_WIDTH, A_HEIGHT = arena.size()

        on_ground = False
        at_left = False
        at_right = False

        # suolo
        if self.y + self.height >= A_HEIGHT:
            self.y = A_HEIGHT - self.height
            on_ground = True

        # pareti
        if self.x <= 0:
            self.x = 0
            at_left = True
        if self.x + self.width >= A_WIDTH:
            self.x = A_WIDTH - self.width
            at_right = True

        return {"on_ground": on_ground, "at_left": at_left, "at_right": at_right}

    def inside_arena(self, arena: "Arena") -> bool:
        a_width, a_height = arena.size()
        return 0 <= self.x <= a_width - self.width and 0 <= self.y <= a_height - self.height

    # ======== AUTO CONSTRUCTOR ========
    @classmethod
    def auto_init(cls, player: "Arthur", arena: "Arena") -> "Zombie":
        player_cx, player_cy = player.x+player.width//2, player.y+player.height//2

        # search nearest platform
        platforms: list[Platform] = [_ for _ in arena.actors() if isinstance(_, Platform) and round(_.damage) == round(0)]
        distances: dict[tuple[float, float], Platform] = {}
        for platform in platforms:
            d_y = ( abs(player_cy - platform.y) )
            d_x = ( 0 if platform.x < player_cx < platform.x+platform.width else max(player.x - platform.x + platform.width, platform.x - player.x+player.width) )
            distances[(d_x, d_y)] = platform

        zombie_x = player.x + random.choice([-1, 1]) * random.uniform(25, 200)

        if distances:
            keys = list(distances.keys())
            keys.sort(key=lambda x: (x[0]**2+x[1]**2)**0.5)

            nearest_platform: Platform = distances[keys[random.randint(0, min(2, len(keys) - 1))]]
            zombie_y = nearest_platform.pos()[1] - 32
            zombie_x = max(nearest_platform.pos()[0], min(zombie_x, nearest_platform.pos()[0] + nearest_platform.width - 18))
        else:
            zombie_y = 202-10


        zombie_direction = Direction.LEFT if zombie_x > player.x else Direction.RIGHT

        return cls(name="Zombie", x=zombie_x, y=zombie_y, direction=zombie_direction)

