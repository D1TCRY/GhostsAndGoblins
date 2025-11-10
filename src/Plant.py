from __future__ import annotations

from typing import TYPE_CHECKING
import random
import pathlib

from actor import Actor, Arena
from status import Action, Direction, Sprite, SpriteCollection, State
from guis import GUIComponent, Bar
from EyeBall import EyeBall
from Platform import Platform

if TYPE_CHECKING:
    from Game import Game
    from Arthur import Arthur



PLANT_SPRITE_PATH = pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins.png"

# IDLE
PLANT_IDLE_R1: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=726,  y=207, width=16, height=32)
PLANT_IDLE_L1: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=564, y=207, width=16, height=32)

# ATTACKING
PLANT_ATTACK_R1: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=708, y=207, width=16, height=32)
PLANT_ATTACK_R2: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=690, y=207, width=16, height=32)
PLANT_ATTACK_R3: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=672, y=207, width=16, height=32)
PLANT_ATTACK_R4: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=654, y=207, width=16, height=32)

PLANT_ATTACK_L1: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=582, y=207, width=16, height=32)
PLANT_ATTACK_L2: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=600, y=207, width=16, height=32)
PLANT_ATTACK_L3: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=618, y=207, width=16, height=32)
PLANT_ATTACK_L4: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=636, y=207, width=16, height=32)

# SPAWNING
PLANT_SPAWN_R1: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=726, y=207, width=16, height=8)
PLANT_SPAWN_R2: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=726, y=207, width=16, height=16)
PLANT_SPAWN_R3: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=726, y=207, width=16, height=24)
PLANT_SPAWN_R4: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=726, y=207, width=16, height=32)

PLANT_SPAWN_L1: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=564, y=207, width=16, height=8)
PLANT_SPAWN_L2: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=564, y=207, width=16, height=16)
PLANT_SPAWN_L3: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=564, y=207, width=16, height=24)
PLANT_SPAWN_L4: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=564, y=207, width=16, height=32)

class Plant(Actor):
    def __init__(self,
        x: int | float,
        y: int | float,
        *,
        health: int = 40.0,
        direction: Direction = Direction.RIGHT,
        attack_interval: int = 180,
        projectile_speed: float = 2.0,
        projectile_damage: int | float = 10.0,
        sprite_cycle_speed: int = 6,
    ) -> None:

        self.x = x
        self.y = y

        self.health = health

        self.width = PLANT_IDLE_R1.width
        self.height = PLANT_IDLE_R1.height

        self.state = State(action=Action.SPAWNING, direction=direction)
        self.sprite_cycle_counter = 0
        self.sprite_cycle_speed = int(sprite_cycle_speed)

        self.attack_interval = attack_interval
        self.attack_cooldown = attack_interval

        self.projectile_speed = projectile_speed
        self.projectile_damage = projectile_damage

        self.sprites = SpriteCollection()
        self._init_sprites()

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
    def health(self) -> float:
        if self.__health > 0: return self.__health
        else: self.state.action = Action.DEAD; return 0
    @health.setter
    def health(self, value: int | float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("health must be int or float")
        self.__health = max(0, min(round(value), 40))

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
    def state(self) -> State:
        return self.__state
    @state.setter
    def state(self, value: State) -> None:
        if not isinstance(value, State):
            raise TypeError("state must be a State")
        self.__state = value

    @property
    def sprite_cycle_counter(self) -> int:
        return self.__sprite_cycle_counter
    @sprite_cycle_counter.setter
    def sprite_cycle_counter(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("sprite_cycle_counter must be int")
        self.__sprite_cycle_counter = int(value)

    @property
    def sprite_cycle_speed(self) -> int:
        return self.__sprite_cycle_speed
    @sprite_cycle_speed.setter
    def sprite_cycle_speed(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("sprite_cycle_speed must be int")
        self.__sprite_cycle_speed = int(value)

    @property
    def attack_interval(self) -> int:
        return self.__attack_interval
    @attack_interval.setter
    def attack_interval(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("attack_interval must be int")
        self.__attack_interval = int(value)

    @property
    def attack_cooldown(self) -> int:
        return self.__attack_cooldown
    @attack_cooldown.setter
    def attack_cooldown(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("attack_cooldown must be int")
        self.__attack_cooldown = int(value)

    @property
    def projectile_speed(self) -> float:
        return self.__projectile_speed
    @projectile_speed.setter
    def projectile_speed(self, value: int | float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("projectile_speed must be int or float")
        self.__projectile_speed = float(value)

    @property
    def projectile_damage(self) -> float:
        return self.__projectile_damage
    @projectile_damage.setter
    def projectile_damage(self, value: int | float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("projectile_damage must be int or float")
        self.__projectile_damage = float(value)

    # utility
    @property
    def reset_sprite_cycle_counter(self) -> int:
        self.sprite_cycle_counter = 0
        return self.sprite_cycle_counter

    @property
    def increment_sprite_cycle_counter(self) -> int:
        self.sprite_cycle_counter += 1
        return self.sprite_cycle_counter

    # === SPRITES SETUP ===
    def _init_sprites(self) -> None:
        if self.state.action == Action.DEAD: return

        # IDLE
        self.sprites[Action.IDLE, Direction.RIGHT] = [PLANT_IDLE_R1]
        self.sprites[Action.IDLE, Direction.LEFT]  = [PLANT_IDLE_L1]

        # ATTACKING
        self.sprites[Action.ATTACKING, Direction.RIGHT] = [
            PLANT_ATTACK_R1,
            PLANT_ATTACK_R2,
            PLANT_ATTACK_R3,
            PLANT_ATTACK_R4
        ]
        self.sprites[Action.ATTACKING, Direction.LEFT] = [
            PLANT_ATTACK_L1,
            PLANT_ATTACK_L2,
            PLANT_ATTACK_L3,
            PLANT_ATTACK_L4
        ]

        # SPAWNING
        self.sprites[Action.SPAWNING, Direction.RIGHT] = [
            PLANT_SPAWN_R1,
            PLANT_SPAWN_R2,
            PLANT_SPAWN_R3,
            PLANT_SPAWN_R4
        ]
        self.sprites[Action.SPAWNING, Direction.LEFT] = [
            PLANT_SPAWN_L1,
            PLANT_SPAWN_L2,
            PLANT_SPAWN_L3,
            PLANT_SPAWN_L4
        ]

    # === INTERFACE IMPLEMENTATION ===
    def pos(self) -> tuple[float, float]:
        return self.x, self.y

    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def move(self, arena: "Game") -> None:

        if self.state.action == Action.SPAWNING:
            sprites = self.sprites[Action.SPAWNING, self.state.direction]
            max_index = len(sprites)
            frame_index = self.sprite_cycle_counter // self.sprite_cycle_speed

            if frame_index >= max_index:
                self._set_state_action(Action.IDLE)

        elif self.state.action == Action.IDLE:
            if self.attack_cooldown > 0:
                self.attack_cooldown -= 1

            if self.attack_cooldown <= 0 and arena.player is not None:
                player = arena.player
                if player.x + player.width / 2 >= self.x + self.width / 2:
                    self.state.direction = Direction.RIGHT
                else:
                    self.state.direction = Direction.LEFT

                self._set_state_action(Action.ATTACKING)
                self.attack_cooldown = self.attack_interval

        elif self.state.action == Action.ATTACKING:
            if self._locked_anim_finished():
                self._shoot_eyeball(arena)
                self._set_state_action(Action.IDLE)

            sprites = self.sprites[Action.ATTACKING, self.state.direction]
            max_index = len(sprites)
            frame_index = self.sprite_cycle_counter // self.sprite_cycle_speed
            if frame_index >= max_index:
                self._set_state_action(Action.IDLE)

    def sprite(self) -> Sprite | None:
        key = (self.state.action, self.state.direction)
        if key not in self.sprites.__iter__():
            return None

        sprites = self.sprites[key]

        match self.state.action:
            case Action.IDLE:
                return self._looping_sprite_selection(sprites)
            case Action.ATTACKING:
                return self._locked_looping_sprite_selection(sprites)
            case Action.SPAWNING:
                return self._locked_looping_sprite_selection(sprites)
            case _:
                return None

    def hit(self, damage: int | float) -> None:
        self.health -= damage
        if self.health <= 0:
            self.state.action = Action.DEAD

    @property
    def gui(self) -> list[GUIComponent]:
        bar_w, bar_h = self.width, 3
        return [Bar(
            name_id=self.__class__.__name__,
            x=self.x,
            y=self.y - bar_h - 1,
            width=bar_w,
            height=bar_h,
            text="",
            text_size=1,
            text_color=(0, 0, 0, 0),
            background_color=(116, 16, 8),
            bar_color=(128, 248, 96),
            max_value=40,
            value=self.health,
            padding=0,
            fixed=False
        )]

    # ======== HELPER METHODS ========
    def _locked_anim_finished(self) -> bool:
        sprites = self.sprites[(self.state.action, self.state.direction)]
        i = self.sprite_cycle_counter // self.sprite_cycle_speed
        return i >= len(sprites) - 1

    def _looping_sprite_selection(self, sprites: list[Sprite]) -> Sprite:
        self.sprite_cycle_counter += 1
        return sprites[(self.sprite_cycle_counter // self.sprite_cycle_speed) % len(sprites)]

    def _locked_looping_sprite_selection(self, sprites: list[Sprite]) -> Sprite:
        self.sprite_cycle_counter += 1
        i = self.sprite_cycle_counter // self.sprite_cycle_speed
        return sprites[i if i < len(sprites) else -1]

    def _set_state_action(self, action: Action) -> None:
        if self.state.action != action:
            _ = self.reset_sprite_cycle_counter

        old_height = self.height

        self.state.action = action

        key = (self.state.action, self.state.direction)
        if key in self.sprites.__iter__():
            new_sprite = self.sprites[key][0]
            self.y = self.y + old_height - new_sprite.height
            self.width = new_sprite.width
            self.height = new_sprite.height

    def _shoot_eyeball(self, arena: "Game") -> None:
        if self.state.direction == Direction.RIGHT:
            offset_x = self.width
        else:
            offset_x = -12

        spawn_x = self.x + offset_x
        spawn_y = self.y + self.height * 0.3

        eyeball = EyeBall(
            x=spawn_x,
            y=spawn_y,
            direction=self.state.direction,
            speed=self.projectile_speed,
            damage=self.projectile_damage,
        )

        try:
            arena.spawn(eyeball)
        except Exception:
            pass

    @classmethod
    def auto_init(cls, player: "Arthur", arena: "Arena") -> "Plant":
        player_cx = player.x + player.width // 2
        player_cy = player.y + player.height // 2

        platforms: list[Platform] = [
            a for a in arena.actors()
            if isinstance(a, Platform) and round(a.damage) == 0
        ]

        distances: dict[tuple[float, float], Platform] = {}
        for platform in platforms:
            d_y = abs(player_cy - platform.y)

            if platform.x < player_cx < platform.x + platform.width:
                d_x = 0
            else:
                d_x = max(
                    player.x - platform.x + platform.width,
                    platform.x - player.x + player.width,
                )

            distances[(d_x, d_y)] = platform

        plant_x = player.x + random.choice([-1, 1]) * random.uniform(25, 200)

        base_height = PLANT_IDLE_R1.height
        base_width = PLANT_IDLE_R1.width

        if distances:
            keys = list(distances.keys())
            keys.sort(key=lambda p: (p[0] ** 2 + p[1] ** 2) ** 0.5)

            nearest_platform: Platform = distances[
                keys[random.randint(0, min(2, len(keys) - 1))]
            ]

            px, py = nearest_platform.pos()
            pwidth, _ = nearest_platform.size()

            plant_y = py - base_height

            plant_x = max(px, min(plant_x, px + pwidth - base_width))
        else:
            arena_w, arena_h = arena.size()
            plant_y = arena_h - base_height

        plant_direction = Direction.LEFT if plant_x > player.x else Direction.RIGHT

        return cls(
            x=plant_x,
            y=plant_y,
            direction=plant_direction,
        )
