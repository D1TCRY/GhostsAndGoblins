from email.quoprimime import header_length
from typing import TYPE_CHECKING
import pathlib

# ACTOR
from ..actor import Actor, Arena

# CORE
if TYPE_CHECKING: from ...core import Game
from ...core.file_management import read_settings

# WEAPON
from ..weapons import Torch

# GUI
from ...gui import GUIComponent, Bar

# STATE
from ...state import Sprite, EntityState, Action, Direction, SpriteCollection



ARTHUR_SPRITE_PATH = pathlib.Path(__file__).parent.parent.parent.parent / "data" / "textures" / "ghosts-goblins.png"


# IDLE
ARTHUR_SPRITE_IDLE_R: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=7, y=42, width=19, height=32)
ARTHUR_SPRITE_IDLE_L: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=486, y=42, width=19, height=32)

# WALKING
ARTHUR_SPRITE_WALKING_R1: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=41, y=42, width=22, height=32)
ARTHUR_SPRITE_WALKING_R2: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=67, y=42, width=18, height=32)
ARTHUR_SPRITE_WALKING_R3: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=89, y=42, width=18, height=32)
ARTHUR_SPRITE_WALKING_R4: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=110, y=42, width=23, height=32)

ARTHUR_SPRITE_WALKING_L1: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=449, y=42, width=22, height=32)
ARTHUR_SPRITE_WALKING_L2: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=427, y=42, width=18, height=32)
ARTHUR_SPRITE_WALKING_L3: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=405, y=42, width=18, height=32)
ARTHUR_SPRITE_WALKING_L4: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=379, y=42, width=23, height=32)

# JUMPING
ARTHUR_SPRITE_JUMPING_R1: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=144, y=29, width=32, height=32)
ARTHUR_SPRITE_JUMPING_R2: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=181, y=29, width=26, height=32)

ARTHUR_SPRITE_JUMPING_L1: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=336, y=29, width=32, height=32)
ARTHUR_SPRITE_JUMPING_L2: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=305, y=29, width=26, height=32)

# CROUCHING
ARTHUR_SPRITE_CROUCHING_R: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=223, y=51, width=22, height=23)
ARTHUR_SPRITE_CROUCHING_L: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=267, y=51, width=22, height=23)

# CLIMBING
ARTHUR_SPRITE_CLIMBING_R: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=150, y=132, width=22, height=31)
ARTHUR_SPRITE_CLIMBING_L: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=340, y=132, width=22, height=31)

# NORMAL THROW
ARTHUR_SPRITE_NORMAL_THROW_R1: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=5, y=131, width=23, height=32)
ARTHUR_SPRITE_NORMAL_THROW_R2: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=30, y=131, width=23, height=32)
ARTHUR_SPRITE_NORMAL_THROW_L1: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=484, y=131, width=23, height=32)
ARTHUR_SPRITE_NORMAL_THROW_L2: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=459, y=131, width=23, height=32)

# CROUCHED THROW
ARTHUR_SPRITE_CROUCHED_THROW_R1: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=75, y=140, width=22, height=23)
ARTHUR_SPRITE_CROUCHED_THROW_R2: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=101, y=140, width=27, height=23)
ARTHUR_SPRITE_CROUCHED_THROW_L1: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=415, y=140, width=22, height=23)
ARTHUR_SPRITE_CROUCHED_THROW_L2: Sprite = Sprite(path=ARTHUR_SPRITE_PATH, x=384, y=140, width=27, height=23)



class Arthur(Actor):
    def __init__(self, 
        name: str, 
        x: int | float, 
        y: int | float, 
        width: int | None = None,
        height: int | None = None,
        speed: float | None = None,
        gravity: float | None = None,
        jump_speed: float | None = None,
        health: int | float | None = None,
        max_health: int | float | None = None,
        throw_interval: int | None = None
    ) -> None:
        settings: dict = read_settings()
        defaults: dict = settings.get("Arthur", {}).get("defaults", {})

        # FORCED INIT
        self.name = name
        self.x = x
        self.y = y

        # INIT WITH DEFAULTS
        self.width = width if width is not None else defaults.get("width", 21)
        self.height = height if height is not None else defaults.get("height", 32)
        self.speed = speed if speed is not None else defaults.get("speed", 5)
        self.gravity = gravity if gravity is not None else defaults.get("gravity", 0.7)
        self.jump_speed = jump_speed if jump_speed is not None else defaults.get("jump_speed", 10.0)
        self.max_health = max_health if max_health is not None else defaults.get("max_health", 100)
        self.health = health if health is not None else defaults.get("health", 100)

        # STATE
        self.x_step = 0
        self.y_step = 0
        self.invincibility_countdown = 0
        self.invincibility_time = defaults.get("invincibility_time", 60)

        self.state = EntityState(action=Action.WALKING, direction=Direction.RIGHT)
        self.sprite_cycle_counter = 0
        self.sprite_cycle_speed = defaults.get("sprite_cycle_speed", 4)

        self.grounded = False
        self.laddered = False
        self.throw_cooldown = 0
        self.throw_interval = throw_interval if throw_interval is not None else defaults.get("throw_interval", 10)

        # SPRITES
        self.sprites = SpriteCollection()
        self.__init_sprites()

        # INTERNAL PROPERTIES
        self._priority_action = None
        self._default_height = defaults.get("default_height", 32)
        self._crouched_height = defaults.get("crouched_height", 23)
        self._default_width = defaults.get("default_width", 21)
        self._laddered_width = defaults.get("laddered_width", 19)

    def __init_sprites(self) -> None:
        """Inizializza la collezione di sprite di Arthur.

        Associa a ogni coppia (Action, Direction) la lista di sprite corretta
        per gli stati principali:
        - IDLE
        - WALKING
        - JUMPING
        - CROUCHING
        - CLIMBING e CLIMBING_POSE
        - ATTACKING e ATTACKING_CROUCHED

        Queste mappe vengono poi usate dal metodo sprite per scegliere il
        frame giusto in base allo stato corrente.
        """

        global ARTHUR_SPRITE_IDLE_R, ARTHUR_SPRITE_IDLE_L
        global ARTHUR_SPRITE_WALKING_R1, ARTHUR_SPRITE_WALKING_R2, ARTHUR_SPRITE_WALKING_R3, ARTHUR_SPRITE_WALKING_R4
        global ARTHUR_SPRITE_WALKING_L1, ARTHUR_SPRITE_WALKING_L2, ARTHUR_SPRITE_WALKING_L3, ARTHUR_SPRITE_WALKING_L4
        global ARTHUR_SPRITE_JUMPING_R1, ARTHUR_SPRITE_JUMPING_R2
        global ARTHUR_SPRITE_JUMPING_L1, ARTHUR_SPRITE_JUMPING_L2
        global ARTHUR_SPRITE_CROUCHING_R, ARTHUR_SPRITE_CROUCHING_L
        global ARTHUR_SPRITE_CLIMBING_R, ARTHUR_SPRITE_CLIMBING_L
        global ARTHUR_SPRITE_NORMAL_THROW_R1, ARTHUR_SPRITE_NORMAL_THROW_R2, ARTHUR_SPRITE_NORMAL_THROW_L1, ARTHUR_SPRITE_NORMAL_THROW_L2
        global ARTHUR_SPRITE_CROUCHED_THROW_R1, ARTHUR_SPRITE_CROUCHED_THROW_R2, ARTHUR_SPRITE_CROUCHED_THROW_L1, ARTHUR_SPRITE_CROUCHED_THROW_L2

        self.sprites[Action.IDLE, Direction.RIGHT] = [ARTHUR_SPRITE_IDLE_R]
        self.sprites[Action.IDLE, Direction.LEFT] = [ARTHUR_SPRITE_IDLE_L]

        self.sprites[Action.WALKING, Direction.RIGHT] = [ARTHUR_SPRITE_WALKING_R1, ARTHUR_SPRITE_WALKING_R2,
                                                         ARTHUR_SPRITE_WALKING_R3, ARTHUR_SPRITE_WALKING_R4] + [
                                                            ARTHUR_SPRITE_WALKING_R3, ARTHUR_SPRITE_WALKING_R2]
        self.sprites[Action.WALKING, Direction.LEFT] = [ARTHUR_SPRITE_WALKING_L1, ARTHUR_SPRITE_WALKING_L2,
                                                        ARTHUR_SPRITE_WALKING_L3, ARTHUR_SPRITE_WALKING_L4] + [
                                                           ARTHUR_SPRITE_WALKING_L3, ARTHUR_SPRITE_WALKING_L2]

        self.sprites[Action.JUMPING, Direction.RIGHT] = [ARTHUR_SPRITE_JUMPING_R1] * 3 + [ARTHUR_SPRITE_JUMPING_R2]
        self.sprites[Action.JUMPING, Direction.LEFT] = [ARTHUR_SPRITE_JUMPING_L1] * 3 + [ARTHUR_SPRITE_JUMPING_L2]

        self.sprites[Action.CROUCHING, Direction.RIGHT] = [ARTHUR_SPRITE_CROUCHING_R]
        self.sprites[Action.CROUCHING, Direction.LEFT] = [ARTHUR_SPRITE_CROUCHING_L]

        self.sprites[Action.CLIMBING, Direction.RIGHT] = [ARTHUR_SPRITE_CLIMBING_R, ARTHUR_SPRITE_CLIMBING_L]
        self.sprites[Action.CLIMBING, Direction.LEFT] = [ARTHUR_SPRITE_CLIMBING_L, ARTHUR_SPRITE_CLIMBING_R]

        self.sprites[Action.CLIMBING_POSE, Direction.RIGHT] = [ARTHUR_SPRITE_CLIMBING_R]
        self.sprites[Action.CLIMBING_POSE, Direction.LEFT] = [ARTHUR_SPRITE_CLIMBING_L]

        self.sprites[Action.ATTACKING, Direction.RIGHT] = [ARTHUR_SPRITE_NORMAL_THROW_R1, ARTHUR_SPRITE_NORMAL_THROW_R2]
        self.sprites[Action.ATTACKING, Direction.LEFT] = [ARTHUR_SPRITE_NORMAL_THROW_L1, ARTHUR_SPRITE_NORMAL_THROW_L2]

        self.sprites[Action.ATTACKING_CROUCHED, Direction.RIGHT] = [ARTHUR_SPRITE_CROUCHED_THROW_R1, ARTHUR_SPRITE_CROUCHED_THROW_R2]
        self.sprites[Action.ATTACKING_CROUCHED, Direction.LEFT] = [ARTHUR_SPRITE_CROUCHED_THROW_L1, ARTHUR_SPRITE_CROUCHED_THROW_L2]
    
    # ======== ======== ======== ========
    # INTERFACE IMPLEMENTATION 
    # ........ ........ ........ ........
    def pos(self) -> tuple[float, float]:
        return self.x, self.y
    
    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def move(self, arena: "Game") -> None:
        """Aggiorna lo stato logico e la posizione di Arthur per il frame corrente.

        Legge i tasti correnti dall oggetto Game e gestisce:
        - conto alla rovescia di invincibilita e tempo di ricarica del lancio
        - lancio della Torcia quando viene premuto il tasto "1", se il cooldown è
          finito e Arthur non è su una scala, impostando eventualmente una
          azione prioritaria di ATTACKING o ATTACKING_CROUCHED
        - movimento verticale: salto, caduta con gravita, posizione accovacciata
        - movimento orizzontale: camminata a sinistra o destra e direzione
          del personaggio
        - aggiornamento dello stato (IDLE, WALKING, JUMPING, CROUCHING) in base
          ai tasti e alla situazione corrente

        Alla fine del metodo, la proprieta grounded viene azzerata; sara poi
        Game a reimpostarla in caso di collisione con una piattaforma.
        """

        if self.state.action is Action.DEAD:
            return

        keys: list[str] = arena.current_keys()

        self.invincibility_countdown -= 1
        if self.throw_cooldown > 0:
            self.throw_cooldown -= 1

        # --- THROW TORCH ---
        if "1" in keys and self.throw_cooldown == 0 and not self.laddered:
            offset_x = 10 if self.state.direction == Direction.RIGHT else -10
            spawn_x = self.x + (self.width // 2) + offset_x
            spawn_y = self.y + self.height * 0.1

            torch = Torch(x=spawn_x, y=spawn_y, direction=self.state.direction)
            if hasattr(arena, "spawn"): arena.spawn(torch)

            self.throw_cooldown = self.throw_interval

            if self.state.action in (Action.IDLE, Action.WALKING, Action.JUMPING):
                self._priority_action = Action.ATTACKING
                self.reset_sprite_cycle_counter()
            elif self.state.action in (Action.CROUCHING,):
                self._priority_action = Action.ATTACKING_CROUCHED
                self.reset_sprite_cycle_counter()

        # --- VERTICAL ---
        can_jump = self.grounded

        if "ArrowUp" in keys and can_jump and not self.laddered:
            self.y_step = -self.jump_speed
            self._set_state_action(Action.JUMPING)
        elif "ArrowDown" in keys and self.grounded:
            self._set_state_action(Action.CROUCHING)
        elif self.grounded:
            self._set_state_action(Action.WALKING if self.x_step != 0.0 else Action.IDLE)
        elif not self.laddered:
            self._set_state_action(Action.JUMPING, reset=False)

        if not self.laddered:
            self.y_step += self.gravity
            self.y += self.y_step


        # --- HORIZONTAL ---
        self.x_step = 0.0
        if "ArrowLeft" in keys and self.state.action not in (Action.CROUCHING,):
            self.x_step = -self.speed
            self.state.direction = Direction.LEFT
        elif "ArrowRight" in keys and self.state.action not in (Action.CROUCHING,):
            self.x_step = self.speed
            self.state.direction = Direction.RIGHT

        if self.state.action not in (Action.JUMPING, Action.CROUCHING):
            self._set_state_action(Action.WALKING if self.x_step != 0.0 else Action.IDLE, reset=False)
        self.x += self.x_step


        self.grounded = False   # -> if collision with Platform, Game will update it



    def sprite(self) -> Sprite | None: # type: ignore
        """Restituisce lo sprite corrente di Arthur in base allo stato.

        Determina l azione effettiva da visualizzare usando una eventuale
        azione prioritaria (per esempio durante un attacco), quindi:

        - verifica che esista una lista di sprite per (Action, Direction)
        - imposta la proprieta blinking degli sprite se Arthur è in stato
          di invincibilita (invincibility_countdown > 0)
        - se l'animazione prioritaria è terminata, rimuove la priorita

        In base all azione effettiva:
        - usa una selezione ciclica per WALKING e CLIMBING
        - usa una selezione bloccata per IDLE, JUMPING, CROUCHING,
          CLIMBING_POSE, ATTACKING e ATTACKING_CROUCHED
        - restituisce None se non ce sprite valido per lo stato corrente.
        """

        action = self.state.action if self._priority_action is None else self._priority_action
        direction = self.state.direction

        if (action, direction) not in self.sprites.__iter__():
            return None

        list_sprites = self.sprites[action, direction]
        for sprite in list_sprites:
            sprite.blinking = self.invincibility_countdown > 0

        if self._priority_action is not None and self._locked_anim_finished():
            self._priority_action = None

        match action:
            case Action.IDLE: return self._locked_looping_sprite_selection(list_sprites)
            case Action.WALKING: return self._looping_sprite_selection(list_sprites)
            case Action.JUMPING: return self._locked_looping_sprite_selection(list_sprites)
            case Action.CROUCHING: return self._locked_looping_sprite_selection(list_sprites)
            case Action.CLIMBING: return self._looping_sprite_selection(list_sprites)
            case Action.CLIMBING_POSE: return self._locked_looping_sprite_selection(list_sprites)
            case Action.ATTACKING: return self._locked_looping_sprite_selection(list_sprites)
            case Action.ATTACKING_CROUCHED: return self._locked_looping_sprite_selection(list_sprites)
            case _: return None

    @property
    def gui(self) -> list[GUIComponent]:
        """Restituisce una lista di GUIComponent da visualizzare nella GUI."""

        health_bar: GUIComponent = Bar(
                name_id="health_bar",
                x=3, y=3, padding=1,
                text="Health: {value}",
                max_value=self.max_health,
                value=lambda: self.health,
                fixed=True,
            )

        invincibility_bar: GUIComponent = Bar(
                name_id="invincibility_bar",
                x=3, y=20+14+3, padding=1,
                width=72, height=14,
                background_color=(64, 64, 64), bar_color=(156, 156, 156),
                text="Invincibility", text_size=10, text_color=(248, 248, 248),
                max_value=self.invincibility_time, value=self.invincibility_countdown,
                fixed=True
            )

        weapon_bar: GUIComponent = Bar(
            name_id="weapon_bar",
            x=3, y=20, padding=1,
            width=72, height=14,
            text="Attack [1]", text_size=10, text_color=(248, 248, 248),
            max_value=self.throw_interval, value=self.throw_interval - self.throw_cooldown,
            background_color=(8, 16, 116), bar_color=(96, 128, 248),
            fixed=True
        )

        return [health_bar] + ([invincibility_bar] if self.invincibility_countdown > 0 else []) + ([weapon_bar])

    def hit(self, damage: float) -> None:
        """Applica un danno ad Arthur tenendo conto dell invincibilita.

        Se il contatore di invincibilita è a zero e il danno è positivo:
        - riduce la salute di un valore pari a damage
        - reimposta il contatore di invincibilita a invincibility_time,
          cosi da evitare di subire danni ogni singolo frame.
        """

        if self.invincibility_countdown <= 0 < damage:
            self.health -= damage
            self.invincibility_countdown = self.invincibility_time
    # ^^^^^^^^ ^^^^^^^^ ^^^^^^^^ ^^^^^^^^
    # INTERFACE IMPLEMENTATION 
    # ======== ======== ======== ========
    
    # ======== ======== ======== ========
    # HELPER METHODS 
    # ........ ........ ........ ........
    def on_platform_collision(self, direction: Direction | None, dx: float, dy: float) -> None: # called by Game
        """Gestisce la collisione tra Arthur e una piattaforma.

        Se la direzione è definita:
        - applica gli offset dx e dy alla posizione per correggere eventuali
          compenetrazioni
        - se la collisione è laterale (LEFT o RIGHT), azzera la velocita
          orizzontale x_step
        - altrimenti azzera la velocita verticale y_step e, se la collisione
          arriva dall alto (Direction.UP), segna Arthur come grounded e disattiva lo
          stato di laddered.
        """

        if direction is None:
            return

        if dx:
            self.x += dx
        if dy:
            self.y += dy

        if direction in (Direction.LEFT, Direction.RIGHT):
            self.x_step = 0.0
        else:
            self.y_step = 0.0
            if direction == Direction.UP:
                self.grounded = True
                self.laddered = False

    def on_ladder_collision(self, keys: list[str], ladder_pos: tuple[float, float], ladder_size: tuple[float, float]) -> None:
        """Gestisce la collisione di Arthur con una scala e il movimento su di essa.

        Se Arthur non è morto:
        - calcola se la sua posizione è all interno dell area verticale
          della scala
        - ignora il comportamento se si trova esattamente sopra o sotto
          la scala

        Se viene premuto ArrowUp o ArrowDown e non è sul fondo:
        - abilita lo stato laddered e azzera la velocita verticale
        - sposta Arthur verso l'alto o verso il basso di un piccolo passo
        - se si sta muovendo e si trova dentro i limiti verticali della
          scala, imposta l'azione su CLIMBING
        - se è fermo ma ancora dentro l'area della scala, imposta
          CLIMBING_POSE.
        """

        if self.state.action is Action.DEAD:
            return

        ladder_x, ladder_y = ladder_pos
        ladder_width, ladder_height = ladder_size
        inside_ladder: bool = ladder_y - self.height*0.85 < self.y < ladder_y + ladder_height

        on_bottom = self.y + self.height >= ladder_y + ladder_height
        on_top = self.y + self.height <= ladder_y

        if on_bottom or on_top:
            return

        if "ArrowUp" in keys or "ArrowDown" in keys or not on_bottom:
            self.laddered = True
            self.y_step = 0.0

        if "ArrowUp" in keys:
            self.y -= 2
        elif "ArrowDown" in keys:
            self.y += 2

        if ("ArrowUp" in keys or "ArrowDown" in keys) and inside_ladder:
            self._set_state_action(Action.CLIMBING, reset=False)
        elif inside_ladder:
            self._set_state_action(Action.CLIMBING_POSE)

    def not_on_ladder_collision(self) -> None:
        """Segnala che Arthur non è piu in contatto con una scala."""

        self.laddered = False

    def _looping_sprite_selection(self, sprites: list[Sprite]) -> Sprite:
        """Seleziona il prossimo sprite in una animazione ciclica.

        Incrementa lo sprite_cycle_counter e sceglie il frame successivo
        nella lista sprites, ripetendola in loop in base alla velocità
        sprite_cycle_speed.

        Restituisce lo sprite selezionato.
        """
        self.increment_sprite_cycle_counter()
        return sprites[(self.sprite_cycle_counter // self.__sprite_cycle_speed) % len(sprites)]

    def _locked_looping_sprite_selection(self, sprites: list[Sprite]) -> Sprite:
        """Seleziona il prossimo sprite in una animazione bloccata.

        Incrementa lo sprite_cycle_counter e avanza nell elenco sprites
        in base a sprite_cycle_speed. Una volta raggiunto l ultimo frame,
        continua a restituire sempre l'ultimo sprite disponibile senza
        tornare all inizio della lista.

        Restituisce lo sprite selezionato.
        """
        self.increment_sprite_cycle_counter()
        i = self.sprite_cycle_counter // self.__sprite_cycle_speed
        return sprites[i if i < len(sprites) else -1]

    def _locked_anim_finished(self) -> bool:
        """Verifica se l'animazione bloccata corrente è arrivata all ultimo frame.

        Calcola l'indice del frame da mostrare usando sprite_cycle_counter
        e sprite_cycle_speed, e restituisce True se l'indice ha superato
        l'ultimo sprite disponibile per la combinazione (Action, Direction)
        corrente. In caso contrario restituisce False.
        """

        action = self.state.action if self._priority_action is None else self._priority_action
        direction = self.state.direction

        if (action, direction) not in self.sprites.__iter__():
            return True

        sprites = self.sprites[action, direction]
        i = self.sprite_cycle_counter // self.sprite_cycle_speed
        return i >= len(sprites) - 1

    def _set_state_action(self, action: Action, *, reset: bool = True) -> None:
        """Cambia l'azione dello stato di Arthur e adatta dimensioni e posizione.

        Se l'azione cambia e reset è True, azzera il contatore degli sprite.

        Se esiste almeno uno sprite per la nuova combinazione (Action, Direction):
        - imposta altezza e posizione verticale in modo da mantenere i piedi
          di Arthur sul terreno, usando default_height o crouched_height a
          seconda che sia accovacciato o meno
        - imposta la larghezza a laddered_width quando si trova su una scala,
          altrimenti usa default_width

        Infine aggiorna la proprieta state.action con il nuovo valore.
        """

        if self.state.action != action and reset:
            self.reset_sprite_cycle_counter()

        self.state.action = action

        if (self.state.action, self.state.direction) in self.sprites.__iter__():
            if self.state.action in (Action.CROUCHING, Action.ATTACKING_CROUCHED):
                self.y = self.y + self.height - self._crouched_height
                self.height = self._crouched_height
            else:
                self.y = self.y + self.height - self._default_height
                self.height = self._default_height

            if self.laddered:
                self.width = 19
            else:
                self.width = self._default_width

            return
    # ^^^^^^^^ ^^^^^^^^ ^^^^^^^^ ^^^^^^^^
    # HELPER METHODS
    # ======== ======== ======== ========

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
        if not isinstance(value, (int, float)) or value < 0.0:
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
        self.__health: float = max(0.0, min(float(value), self.max_health))

    @property
    def max_health(self) -> float:
        return self.__max_health
    @max_health.setter
    def max_health(self, value: int | float):
        if not isinstance(value, (int, float)) or value <= 0.0:
            raise TypeError("max_health must be an int or float")
        self.__max_health: float = float(value)

    @property
    def invincibility_countdown(self) -> int:
        return self.__invincibility
    @invincibility_countdown.setter
    def invincibility_countdown(self, value: int):
        if not isinstance(value, int):
            raise TypeError("invincibility must be an int")
        self.__invincibility: int = value if value > 0 else 0

    @property
    def invincibility(self) -> bool:
        return self.invincibility_countdown > 0

    @property
    def invincibility_time(self) -> int:
        return self.__invincibility_time
    @invincibility_time.setter
    def invincibility_time(self, value: int):
        if not isinstance(value, (int, float)):
            raise TypeError("invincibility_time must be an int or float")
        self.__invincibility_time: int = int(value) if int(value) > 0 else 0

    @property
    def state(self) -> EntityState:
        return self.__state
    @state.setter
    def state(self, value: EntityState):
        if not isinstance(value, EntityState):
            raise TypeError("state must be an instance of State")
        self.__state: EntityState = value

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
    def laddered(self) -> bool:
        return self.__laddered
    @laddered.setter
    def laddered(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("laddered must be boolean")
        self.__laddered: bool = bool(value)

    @property
    def throw_cooldown(self) -> int:
        return self.__throw_cooldown
    @throw_cooldown.setter
    def throw_cooldown(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("throw_cooldown must be an int")
        self.__throw_cooldown: int = int(value)

    @property
    def throw_interval(self) -> int:
        return self.__throw_interval
    @throw_interval.setter
    def throw_interval(self, value: int):
        if not isinstance(value, int):
            raise TypeError("throw_interval must be an int")
        self.__throw_interval: int = int(value)

    def reset_sprite_cycle_counter(self) -> int:
        self.sprite_cycle_counter = 0
        return self.sprite_cycle_counter
    def increment_sprite_cycle_counter(self) -> int:
        self.sprite_cycle_counter += 1
        return self.sprite_cycle_counter

    @property
    def _priority_action(self) -> Action | None:
        return self.__priority_action
    @_priority_action.setter
    def _priority_action(self, value: Action | None):
        if value is not None and not isinstance(value, Action):
            raise TypeError("_priority_action must be an instance of Action")
        self.__priority_action: Action | None = value
    # ^^^^^^^^ ^^^^^^^^ ^^^^^^^^ ^^^^^^^^
    # PROPERTIES
    # ======== ======== ======== ========