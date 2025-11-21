import pathlib

# CORE
from ...core.file_management import read_settings

# ACTOR
from ..actor import Actor, Arena

# STATE
from ...state import Action, Direction, Sprite, SpriteCollection, EntityState


SPR_PATH = pathlib.Path(__file__).parent.parent.parent.parent / "data" / "textures" / "ghosts-goblins.png"
FLAME_BIG_R1 = Sprite(SPR_PATH, 116, 427, 34, 33)
FLAME_BIG_R2 = Sprite(SPR_PATH, 152, 427, 26, 33)

FLAME_SMALL_R3 = Sprite(SPR_PATH, 209, 442, 18, 18)
FLAME_SMALL_R4 = Sprite(SPR_PATH, 228, 442, 12, 18)

FLAME_BIG_L1 = Sprite(SPR_PATH, 362, 427, 34, 33)
FLAME_BIG_L2 = Sprite(SPR_PATH, 334, 427, 26, 33)

FLAME_SMALL_L3 = Sprite(SPR_PATH, 285, 442, 18, 18)
FLAME_SMALL_L4 = Sprite(SPR_PATH, 272, 442, 12, 18)


class Flame(Actor):
    def __init__(
        self,
        x: float,
        ground_y: float,
        *,
        damage: int | None = None,
        life_time: int | None = None,
        sprite_cycle_speed: int | None = None,
    ) -> None:
        defaults: dict = read_settings().get("Flame", {}).get("defaults", {})

        # FORCED INIT
        self.ground_y = ground_y
        self.age = 0

        # DEFAULTS
        self.life_time = life_time if life_time is not None else defaults.get("life_time", 60)
        self.damage = damage if damage is not None else defaults.get("damage", 1)
        self.sprite_cycle_speed = sprite_cycle_speed if sprite_cycle_speed is not None else defaults.get("sprite_cycle_speed", 6)

        # STATE
        self.state = EntityState(action=Action.BIG, direction=Direction.RIGHT)
        self.sprite_cycle_counter = 0

        # SPRITES
        self.sprites = SpriteCollection()
        self._init_sprites()

        first = self.sprites[self.state.action, self.state.direction][0]
        self.width = first.width
        self.height = first.height

        # POSITION
        self.x = x - self.width // 2
        self.y = self.ground_y - self.height



    # ======== INTERFACE IMPLEMENTATION ========
    def pos(self) -> tuple[float, float]:
        return self.x, self.y

    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def move(self, arena: Arena) -> None:
        """Aggiorna lo stato logico della fiamma per il frame corrente.

        Incrementa l'eta della fiamma e, se supera life_time, imposta
        l'azione su DEAD in modo che venga rimossa dal gioco.

        Quando l'eta raggiunge circa metà della durata totale, passa
        dallo stato BIG allo stato SMALL aggiornando anche lo sprite.
        """

        if self.state.action == Action.DEAD:
            return

        self.age += 1
        if self.age >= self.life_time:
            self.state.action = Action.DEAD
            return

        if self.state.action != Action.SMALL and self.age >= self.life_time // 2:
            self._set_state_action(Action.SMALL)


    def sprite(self) -> Sprite | None:  # type: ignore
        """Restituisce lo sprite corrente della fiamma in base allo stato.
        Se l'azione è DEAD restituisce None.
        """

        if self.state.action == Action.DEAD:
            return None
        sprites = self.sprites[self.state.action, self.state.direction]
        return self._looping_sprite_selection(sprites)


    # ======== METHODS ========
    def on_platform_collision(self, direction: Direction | None, dx: float, dy: float) -> None:
        """Se la collisione con platform è valida, applica la traslazione imposta da dx e dy."""

        if direction is None:
            return

        if dx: self.x += dx
        if dy: self.y += dy


    # ======== HELPER METHODS ========
    def _init_sprites(self) -> None:
        global FLAME_BIG_R1, FLAME_BIG_R2, FLAME_BIG_L1, FLAME_BIG_L2
        global FLAME_SMALL_R3, FLAME_SMALL_R4, FLAME_SMALL_L3, FLAME_SMALL_L4

        self.sprites[Action.BIG, Direction.RIGHT] = [FLAME_BIG_R1, FLAME_BIG_R2] * 2
        self.sprites[Action.BIG, Direction.LEFT] = [FLAME_BIG_L1, FLAME_BIG_L2] * 2
        self.sprites[Action.SMALL, Direction.RIGHT] = [FLAME_SMALL_R3, FLAME_SMALL_R4] * 2
        self.sprites[Action.SMALL, Direction.LEFT] = [FLAME_SMALL_L3, FLAME_SMALL_L4] * 2

    def _set_state_action(self, action: Action, *, reset: bool = True) -> None:
        """Cambia l'azione della fiamma e aggiorna dimensioni e posizione.

        Se l'azione cambia e reset è True, azzera il contatore degli
        sprite per far ripartire l'animazione dall'inizio.

        Se esiste una lista di sprite per la nuova Action e Direction:
        - aggiorna larghezza e altezza in base al primo sprite
        - centra la fiamma sull asse x mantenendo il centro orizzontale
        - riallinea la posizione verticale in modo che rimanga appoggiata
          al valore ground_y.
        """

        if self.state.action != action and reset:
            self.reset_sprite_cycle_counter()

        self.state.action = action

        if (self.state.action, self.state.direction) in self.sprites.__iter__():
            first = self.sprites[self.state.action, self.state.direction][0]
            prev_width = self.width
            self.width = first.width
            self.x = self.x + prev_width//2 - self.width//2

            self.height = first.height
            self.y = (self.ground_y - self.height) + 1

    def _looping_sprite_selection(self, sprites: list[Sprite]) -> Sprite:
        """Seleziona il prossimo sprite in una animazione ciclica della fiamma.

        Incrementa sprite_cycle_counter e restituisce il frame successivo
        dell elenco sprites, ripetendolo in loop in base a
        sprite_cycle_speed.
        """

        self.sprite_cycle_counter += 1
        return sprites[(self.sprite_cycle_counter // self.sprite_cycle_speed) % len(sprites)]

    def reset_sprite_cycle_counter(self) -> int:
        last = self.sprite_cycle_counter
        self.sprite_cycle_counter = 0
        return last


    # ======== PROPERTIES ========
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
    def life_time(self) -> int:
        return self.__life_frames
    @life_time.setter
    def life_time(self, value: int) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("life_time must be a number")
        self.__life_frames = int(value)

    @property
    def state(self) -> EntityState:
        return self.__state
    @state.setter
    def state(self, value: EntityState) -> None:
        if not isinstance(value, EntityState):
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
    def ground_y(self) -> float:
        return self.__ground_y
    @ground_y.setter
    def ground_y(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("ground_y must be a number")
        self.__ground_y = float(value)

    @property
    def age(self) -> int:
        return self.__age
    @age.setter
    def age(self, value: int) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("age must be a number")
        self.__age = int(value)


