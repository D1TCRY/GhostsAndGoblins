from __future__ import annotations
from typing import TYPE_CHECKING
import random
import pathlib
from dataclasses import dataclass

if TYPE_CHECKING:
    # CORE
    from ...core import Game
    # PLAYER
    from ..player import Arthur

# ACTOR
from ..actor import Actor

# OBJECTS
from ..objects import Platform
from ..objects import GraveStone
from ..objects import Ladder

# WEAPONS
from ..weapons import EyeBall

# STATE
from ...state import Action, Direction, Sprite, SpriteCollection, State

# GUI
from ...gui import GUIComponent, Bar




# HELPER CLASSES
@dataclass
class Range:
    min: float
    max: float

    def __str__(self) -> str:
        return f"<{self.min} -> {self.max}>"

    def __repr__(self) -> str:
        return f"Range({self.min}, {self.max})"


@dataclass
class Candidate:
    distance: float
    height: float
    range: Range
    direction: Direction

    def __str__(self) -> str:
        return f"< Candidate | {self.distance}, {self.height}, {self.range}, {self.direction} >"

    def __repr__(self) -> str:
        return f"Candidate({repr(self.distance)}, {repr(self.height)}, {repr(self.range)}, {repr(self.direction)})"


PLANT_SPRITE_PATH = pathlib.Path(__file__).parent.parent.parent.parent / "data" / "textures" / "ghosts-goblins.png"

# IDLE
PLANT_IDLE_R1: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=726, y=207, width=16, height=32)
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

# SPAWNING (emerging dal terreno)
PLANT_SPAWN_R1: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=726, y=207, width=16, height=8)
PLANT_SPAWN_R2: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=726, y=207, width=16, height=16)
PLANT_SPAWN_R3: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=726, y=207, width=16, height=24)
PLANT_SPAWN_R4: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=726, y=207, width=16, height=32)

PLANT_SPAWN_L1: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=564, y=207, width=16, height=8)
PLANT_SPAWN_L2: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=564, y=207, width=16, height=16)
PLANT_SPAWN_L3: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=564, y=207, width=16, height=24)
PLANT_SPAWN_L4: Sprite = Sprite(path=PLANT_SPRITE_PATH, x=564, y=207, width=16, height=32)


class Plant(Actor):
    def __init__(
        self,
        x: int | float,
        y: int | float,
        *,
        health: int = 40.0,
        damage: float = 10.0,
        direction: Direction = Direction.RIGHT,
        attack_interval: int = 180,
        projectile_speed: float = 2.0,
        projectile_damage: int | float = 20.0,
        sprite_cycle_speed: int = 6,
    ) -> None:
        self.x = x
        self.y = y

        self.health = health
        self.damage = damage
        self.damage_interval = 60
        self.damage_cooldown = 0

        self.width = PLANT_IDLE_R1.width
        self.height = PLANT_IDLE_R1.height

        self.state = State(action=Action.SPAWNING, direction=direction)

        # animation
        self.sprite_cycle_counter = 0
        self.sprite_cycle_speed = int(sprite_cycle_speed)

        # attack
        self.attack_interval = attack_interval
        self.attack_cooldown = attack_interval

        self.projectile_speed = projectile_speed
        self.projectile_damage = projectile_damage

        # sprites
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
        if self.__health > 0:
            return self.__health
        else:
            self.state.action = Action.DEAD
            return 0
    @health.setter
    def health(self, value: int | float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("health must be int or float")
        # clamp tra 0 e 40
        self.__health = max(0, min(round(value), 40))

    @property
    def damage(self) -> float:
        return self.__damage
    @damage.setter
    def damage(self, value: int | float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("damage must be int or float")
        self.__damage = float(value)

    @property
    def damage_interval(self) -> int:
        return self.__damage_interval
    @damage_interval.setter
    def damage_interval(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("damage_interval must be int")
        self.__damage_interval = int(value)

    @property
    def damage_cooldown(self) -> int:
        return self.__damage_counter
    @damage_cooldown.setter
    def damage_cooldown(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("damage_cooldown must be int")
        self.__damage_counter = value if value >= 0 else 0

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
        global PLANT_IDLE_R1, PLANT_IDLE_L1
        global PLANT_ATTACK_R1, PLANT_ATTACK_R2, PLANT_ATTACK_R3, PLANT_ATTACK_R4
        global PLANT_ATTACK_L1, PLANT_ATTACK_L2, PLANT_ATTACK_L3, PLANT_ATTACK_L4
        global PLANT_SPAWN_R1, PLANT_SPAWN_R2, PLANT_SPAWN_R3, PLANT_SPAWN_R4
        global PLANT_SPAWN_L1, PLANT_SPAWN_L2, PLANT_SPAWN_L3, PLANT_SPAWN_L4

        if self.state.action == Action.DEAD:
            return

        # IDLE
        self.sprites[Action.IDLE, Direction.RIGHT] = [PLANT_IDLE_R1]
        self.sprites[Action.IDLE, Direction.LEFT] = [PLANT_IDLE_L1]

        # ATTACKING
        self.sprites[Action.ATTACKING, Direction.RIGHT] = [
            PLANT_ATTACK_R1,
            PLANT_ATTACK_R2,
            PLANT_ATTACK_R3,
            PLANT_ATTACK_R4,
        ]
        self.sprites[Action.ATTACKING, Direction.LEFT] = [
            PLANT_ATTACK_L1,
            PLANT_ATTACK_L2,
            PLANT_ATTACK_L3,
            PLANT_ATTACK_L4,
        ]

        self.sprites[Action.SPAWNING, Direction.RIGHT] = [
            PLANT_SPAWN_R1,
            PLANT_SPAWN_R2,
            PLANT_SPAWN_R3,
            PLANT_SPAWN_R4,
        ]
        self.sprites[Action.SPAWNING, Direction.LEFT] = [
            PLANT_SPAWN_L1,
            PLANT_SPAWN_L2,
            PLANT_SPAWN_L3,
            PLANT_SPAWN_L4,
        ]

        self.sprites[Action.DEAD, Direction.RIGHT] = []
        self.sprites[Action.DEAD, Direction.LEFT] = []

    # === INTERFACE IMPLEMENTATION ===
    def pos(self) -> tuple[float, float]:
        return self.x, self.y

    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def move(self, arena: "Game") -> None:
        if self.state.action == Action.DEAD:
            return

        self.damage_cooldown -= 1

        # SPAWNING
        if self.state.action == Action.SPAWNING:
            if self._locked_anim_finished():
                self._set_state_action(Action.IDLE)
            return

        # IDLE
        if self.state.action == Action.IDLE:
            if self.attack_cooldown > 0:
                self.attack_cooldown -= 1

            if self.attack_cooldown <= 0 and arena.player is not None:
                player = arena.player
                # -> scelgo la direzione in base alla posizione di Arthur
                if player.x + player.width / 2 >= self.x + self.width / 2:
                    self.state.direction = Direction.RIGHT
                else:
                    self.state.direction = Direction.LEFT

                self._set_state_action(Action.ATTACKING)
                self.attack_cooldown = self.attack_interval

        # ATTACKING -> alla fine della animazione spara "EyeBall"
        elif self.state.action == Action.ATTACKING:
            if self._locked_anim_finished():
                self._shoot_eyeball(arena)
                self._set_state_action(Action.IDLE)

    def sprite(self) -> Sprite | None:
        key = (self.state.action, self.state.direction)
        if key not in self.sprites:
            return None

        sprites = self.sprites[key]

        match self.state.action:
            case Action.IDLE: return self._looping_sprite_selection(sprites)
            case Action.ATTACKING | Action.SPAWNING: return self._locked_looping_sprite_selection(sprites)
            case Action.DEAD: return None
            case _: return None

    def hit(self, damage: int | float) -> None:
        self.health -= damage
        if self.health <= 0:
            self.state.action = Action.DEAD

    # ======== COLLISION HANDLERS (come nello Zombie) ========
    def on_arthur_collision(self, arthur: "Arthur") -> None:
        """
        chiamato da game quando Plant collide con Arthur.
        """
        if self.state.action in (Action.SPAWNING, Action.DEAD):
            return

        if self.damage_cooldown <= 0:
            arthur.hit(self.damage)
            self.damage_cooldown = self.damage_interval

    def on_platform_collision(self, direction: Direction | None, dx: float, dy: float) -> None:
        """
        chiamato da Game quando il Plant collide con una Platform.
        """
        if direction is None:
            return

        if dx:
            self.x += dx
        if dy:
            self.y += dy

    @property
    def gui(self) -> list[GUIComponent]:
        bar_w, bar_h = self.width, 3
        return [
            Bar(
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
                fixed=False,
            )
        ]

    # ======== HELPER METHODS ========
    def _locked_anim_finished(self) -> bool:
        sprites = self.sprites[(self.state.action, self.state.direction)]
        i = self.sprite_cycle_counter // self.sprite_cycle_speed
        return i >= len(sprites) - 1

    def _looping_sprite_selection(self, sprites: list[Sprite]) -> Sprite:
        self.sprite_cycle_counter += 1
        sprite = sprites[(self.sprite_cycle_counter // self.sprite_cycle_speed) % len(sprites)]

        self.y = self.y + self.height - sprite.height
        self.height = sprite.height

        return sprite

    def _locked_looping_sprite_selection(self, sprites: list[Sprite]) -> Sprite:
        self.sprite_cycle_counter += 1
        i = self.sprite_cycle_counter // self.sprite_cycle_speed
        sprite = sprites[i if i < len(sprites) else -1]

        self.y = self.y + self.height - sprite.height
        self.height = sprite.height

        return sprite

    def _set_state_action(self, action: Action) -> None:
        if self.state.action != action:
            _ = self.reset_sprite_cycle_counter

            old_height = self.height
            self.state.action = action

            if (self.state.action, self.state.direction) in self.sprites:
                new_sprite = self.sprites[self.state.action, self.state.direction][0]
                # -> mantiene il plant "ancorato" al terreno
                self.y = self.y + old_height - new_sprite.height
                self.width = new_sprite.width
                self.height = new_sprite.height

    def _shoot_eyeball(self, arena: "Game") -> None:
        if self.state.direction == Direction.RIGHT:
            offset_x = self.width + 5
        else:
            offset_x = -5

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

    # ======== AUTO CONSTRUCTOR ========
    @classmethod
    def auto_init(cls, player: "Arthur", game: "Game", min_dist_x = 100, max_dist_x = 150) -> "Plant":
        """
        Inizializza automaticamente un'istanza di Plant in una posizione valida
        rispetto al giocatore (Arthur) e all'arena.

        Il metodo seleziona una piattaforma disponibile nell'arena, calcola un
        intervallo di spawn a distanza minima e massima dal giocatore, e sceglie
        casualmente una posizione e direzione tra i candidati validi.

        Args:
            player (Arthur): Il giocatore di riferimento per calcolare la distanza.
            game (Game): L'oggetto "Game" contenente piattaforme e attori.
            min_dist_x (int, opzionale): Distanza minima orizzontale dal centro del giocatore. Default 100.
            max_dist_x (int, opzionale): Ampiezza del range oltre la distanza minima. Default 150.

        Returns:
            Plant: Una nuova istanza di Plant posizionata su una piattaforma valida.
        """
        # -> regione di spawn da Arthur
        min_dist_x = min_dist_x  # -> distanza minima da Arthur
        max_dist_x = max_dist_x  # -> ampiezza del range oltre la distanza minima
        plant_width = PLANT_IDLE_R1.width  # -> larghezza plant
        plant_height = PLANT_IDLE_R1.height  # -> altezza "finale" del plant

        player_cx, player_cy = player.x + player.width // 2, player.y + player.height // 2

        platforms: list[Platform] = [
            _ for _ in game.actors()
            if isinstance(_, Platform)
            and not isinstance(_, (GraveStone, Ladder))
            and round(_.damage) == 0
            and Direction.UP in (_.contact_surfaces if _.contact_surfaces is not None else [])
        ]  # -> selezione delle Platform su cui è possibile spawnare

        candidates: list[Candidate] = []  # -> candidati con range valido, distanza e direzione iniziale

        for platform in platforms:
            # left -> gestione del range sinistro
            if (max(platform.x, player_cx - min_dist_x - max_dist_x) <= platform.x + platform.width
                    and min(platform.x + platform.width, player_cx - min_dist_x) >= platform.x):
                min_x = max(platform.x, player_cx - min_dist_x - max_dist_x)
                max_x = min(platform.x + platform.width, player_cx - min_dist_x)

                distance = abs(platform.y - (player.y + player.height)) + (player_cx - max_x)

                if max_x - min_x > plant_width:
                    candidates.append(
                        Candidate(
                            distance=distance,
                            height=platform.y,
                            range=Range(min_x, max_x),
                            direction=Direction.RIGHT,
                        )
                    )

            # right -> gestione del range destro
            if (max(platform.x, player_cx + min_dist_x) <= platform.x + platform.width
                    and min(platform.x + platform.width, player_cx + min_dist_x + max_dist_x) >= platform.x):
                min_x = max(platform.x, player_cx + min_dist_x)
                max_x = min(platform.x + platform.width, player_cx + min_dist_x + max_dist_x)

                distance = abs(platform.y - (player.y + player.height)) + (min_x - player_cx)

                if max_x - min_x > plant_width:
                    candidates.append(
                        Candidate(
                            distance=distance,
                            height=platform.y,
                            range=Range(min_x, max_x),
                            direction=Direction.LEFT,
                        )
                    )

        candidates.sort(key=lambda candidate: candidate.distance)
        candidates = candidates[:3]

        chosen_platform = random.choice(candidates)
        x = random.uniform(chosen_platform.range.min, chosen_platform.range.max - plant_width)
        y = chosen_platform.height - plant_height
        d = chosen_platform.direction

        return cls(
            x=x,
            y=y,
            direction=d,
        )
