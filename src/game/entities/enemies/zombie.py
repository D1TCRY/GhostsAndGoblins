from typing import TYPE_CHECKING
import random
import pathlib
from dataclasses import dataclass

# CORE
if TYPE_CHECKING: from ...core import Game
from ...core.file_management import read_settings

# ACTOR
from ..actor import Actor

# PLAYER
if TYPE_CHECKING: from ..player import Arthur

# OBJECTS
from ..objects import Ladder
from ..objects import  Platform
from ..objects import GraveStone


# GUI
from ...gui import GUIComponent, Bar

# STATE
from ...state import Action, Direction, Sprite, SpriteCollection, EntityState






# HELPER CLASSES
@dataclass
class Range:
    """Rappresenta un intervallo numerico con valore minimo e massimo."""

    min: float
    max: float

    def __str__(self) -> str:
        return f"<{self.min} -> {self.max}>"

    def __repr__(self) -> str:
        return f"Range({self.min}, {self.max})"

@dataclass
class Candidate:
    """Rappresenta un possibile punto di spawn con distanza, altezza, range e direzione."""

    distance: float
    height: float
    range: Range
    direction: Direction

    def __str__(self) -> str:
        return f"< Candidate | {self.distance}, {self.height}, {self.range}, {self.direction} >"

    def __repr__(self) -> str:
        return f"Candidate({repr(self.distance)}, {repr(self.height)}, {repr(self.range)}, {repr(self.direction)})"


path = pathlib.Path(__file__).parent.parent.parent.parent / "data" / "textures" / "ghosts-goblins.png"

# EMERGING
ZOMBIE_EMERGING_L1: Sprite = Sprite(path=path, x=512, y=65, width=16, height=32)
ZOMBIE_EMERGING_L2: Sprite = Sprite(path=path, x=533, y=65, width=25, height=32)
ZOMBIE_EMERGING_L3: Sprite = Sprite(path=path, x=562, y=65, width=18, height=32)
ZOMBIE_EMERGING_L4: Sprite = Sprite(path=path, x=610, y=65, width=18, height=32)

ZOMBIE_EMERGING_R1: Sprite = Sprite(path=path, x=778, y=65, width=16, height=32)
ZOMBIE_EMERGING_R2: Sprite = Sprite(path=path, x=748, y=65, width=25, height=32)
ZOMBIE_EMERGING_R3: Sprite = Sprite(path=path, x=726, y=65, width=18, height=32)
ZOMBIE_EMERGING_R4: Sprite = Sprite(path=path, x=678, y=65, width=18, height=32)

# WALK
ZOMBIE_WALK_L1: Sprite = Sprite(path=path, x=585, y=65, width=21, height=32)
ZOMBIE_WALK_L2: Sprite = Sprite(path=path, x=610, y=65, width=18, height=32)
ZOMBIE_WALK_L3: Sprite = Sprite(path=path, x=631, y=65, width=20, height=32)

ZOMBIE_WALK_R1: Sprite = Sprite(path=path, x=700, y=65, width=21, height=32)
ZOMBIE_WALK_R2: Sprite = Sprite(path=path, x=678, y=65, width=18, height=32)
ZOMBIE_WALK_R3: Sprite = Sprite(path=path, x=655, y=65, width=20, height=32)




class Zombie(Actor):
    def __init__(
        self,
        name: str,
        x: int | float,
        y: int | float,
        health: float | None = None,
        speed: float | None = None,
        gravity: float | None = None,
        min_walk_distance: float | None = None,
        max_walk_distance: float | None = None,
        sprite_cycle_speed: int | None = None,
        direction: Direction | None = None,
        damage: float | None = None,
        attack_interval: int | None = None,
    ) -> None:
        defaults: dict = read_settings().get("Zombie", {}).get("defaults", {})

        # FORCED INIT
        self.name = name
        self.x = x
        self.y = y

        # INIT WITH DEFAULTS
        self.max_health = defaults.get("max_health", 70.0)
        self.health = health if health is not None else defaults.get("health", 70.0)
        self.speed = speed if speed is not None else defaults.get("speed", 1.0)
        self.gravity = gravity if gravity is not None else defaults.get("gravity", 0.7)
        self.min_walk_distance = min_walk_distance if min_walk_distance is not None else defaults.get("min_walk_distance", 150.0)
        self.max_walk_distance = max_walk_distance if max_walk_distance is not None else defaults.get("max_walk_distance", 300.0)
        self.sprite_cycle_speed = sprite_cycle_speed if sprite_cycle_speed is not None else defaults.get("sprite_cycle_speed", 6)
        self.direction = direction if direction is not None else getattr(Direction, defaults.get("direction", "RIGHT"), Direction.RIGHT)
        self.damage = damage if damage is not None else defaults.get("damage", 30.0)
        self.attack_interval = attack_interval if attack_interval is not None else defaults.get("attack_interval", 50)

        # STATE
        self.attack_cooldown = 0
        self.x_step = 0.0
        self.y_step = 0
        self.distance_to_walk = random.uniform(self.min_walk_distance, self.max_walk_distance)
        self.walked_distance = 0.0

        self.state = EntityState(action=Action.EMERGING, direction=self.direction)
        self.sprite_cycle_counter = 0

        self.grounded = False

        # SPRITES
        self.sprites = SpriteCollection()
        self.__init_sprites()

        first = self.sprites[self.state.action, self.state.direction][0]
        self.width = first.width
        self.height = first.height


    def __init_sprites(self) -> None:
        global ZOMBIE_EMERGING_L1, ZOMBIE_EMERGING_L2, ZOMBIE_EMERGING_L3, ZOMBIE_EMERGING_L4
        global ZOMBIE_EMERGING_R1, ZOMBIE_EMERGING_R2, ZOMBIE_EMERGING_R3, ZOMBIE_EMERGING_R4
        global ZOMBIE_WALK_L1, ZOMBIE_WALK_L2, ZOMBIE_WALK_L3
        global ZOMBIE_WALK_R1, ZOMBIE_WALK_R2, ZOMBIE_WALK_R3

        self.sprites[Action.EMERGING, Direction.LEFT] = [
            ZOMBIE_EMERGING_L1, ZOMBIE_EMERGING_L2, ZOMBIE_EMERGING_L3, ZOMBIE_EMERGING_L4
        ]
        self.sprites[Action.EMERGING, Direction.RIGHT] = [
            ZOMBIE_EMERGING_R1, ZOMBIE_EMERGING_R2, ZOMBIE_EMERGING_R3, ZOMBIE_EMERGING_R4
        ]

        self.sprites[Action.IMMERSING, Direction.LEFT] = list(
            reversed(self.sprites[(Action.EMERGING, Direction.LEFT)]))
        self.sprites[(Action.IMMERSING, Direction.RIGHT)] = list(
            reversed(self.sprites[(Action.EMERGING, Direction.RIGHT)]))

        self.sprites[Action.WALKING, Direction.LEFT] = [ZOMBIE_WALK_L1, ZOMBIE_WALK_L2, ZOMBIE_WALK_L3]
        self.sprites[Action.WALKING, Direction.RIGHT] = [ZOMBIE_WALK_R1, ZOMBIE_WALK_R2, ZOMBIE_WALK_R3]

        self.sprites[Action.DEAD, Direction.LEFT] = []
        self.sprites[Action.DEAD, Direction.RIGHT] = []


    # ======== INTERFACE IMPLEMENTATION ========
    def pos(self) -> tuple[float, float]:
        return self.x, self.y

    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def move(self, arena: "Game") -> None:
        """Aggiorna lo stato logico e la posizione dello zombie per il frame corrente.

        Gestisce:
        - il cooldown di attacco
        - il movimento verticale con gravita (solo fuori dalla fase EMERGING)
        - la transizione da EMERGING a WALKING al termine dell animazione
        - il movimento orizzontale in WALKING e l'accumulo della distanza percorsa
        - il passaggio a IMMERSING quando ha camminato abbastanza ed è a terra
        - la transizione a DEAD al termine della animazione di IMMERSING

        Se lo zombie è in stato DEAD il metodo non esegue alcuna azione.
        """

        if self.state.action == Action.DEAD:
            return

        self.attack_cooldown -= 1

        # --- VERTICAL ---
        if self.state.action != Action.EMERGING:  # -> la gravità agisce solo quando non sta emergendo dal terreno
            self.y_step += self.gravity  # -> aggiornamento velocita verticale applicando la gravita
            self.y += self.y_step  # -> aggiornamento posizione verticale in base alla velocita

        # --- HORIZONTAL ---
        if self.state.action == Action.EMERGING:
            if self._locked_anim_finished():  # -> attende che l'animazione di emersione sia terminata
                self._set_state_action(Action.WALKING)  # -> quando finita passa allo stato di camminata
        elif self.state.action == Action.WALKING:
            self.x_step = self.speed if self.state.direction == Direction.RIGHT else -self.speed
            self.x += self.x_step  # -> aggiornamento posizione orizzontale

            self.walked_distance += abs(self.x_step)  # -> accumulo della distanza totale percorsa camminando
            if self.walked_distance >= self.distance_to_walk and self.grounded:  # -> se ha camminato abbastanza ed è a terra, inizia l'immersione
                self._set_state_action(Action.IMMERSING)
        elif self.state.action == Action.IMMERSING:
            if self._locked_anim_finished():  # -> quando l'animazione di immersione è conclusa viene segnato come morto
                self._set_state_action(Action.DEAD)


    def sprite(self) -> "Sprite | None":  # type: ignore
        """Restituisce lo sprite corrente dello zombie in base allo stato.

        Usa la coppia (Action, Direction) per scegliere la lista di sprite
        appropriata e:
        - in stato WALKING seleziona i frame in modo ciclico continuo
        - in stato EMERGING e IMMERSING avanza l'animazione in modo bloccato,
          fermandosi sull ultimo frame
        - in stato DEAD restituisce sempre None

        Se lo stato non è gestito esplicitamente, restituisce None.
        """

        sprites = self.sprites[self.state.action, self.state.direction]
        match self.state.action:
            case Action.WALKING: return self._looping_sprite_selection(sprites)
            case Action.EMERGING | Action.IMMERSING: return self._locked_looping_sprite_selection(sprites)
            case Action.DEAD: return None
            case _: return None

    @property
    def gui(self) -> list[GUIComponent]:
        """Restituisce una lista di GUIComponent che rappresentano lo stato corrente dello zombie."""

        bar_w, bar_h = self.width, 3
        return [Bar(
            name_id=self.name,
            x=self.x,
            y=self.y - bar_h - 1,
            width=bar_w,
            height=bar_h,
            text="",
            text_size=1,
            text_color=(0, 0, 0, 0),
            background_color=(116, 16, 8),
            bar_color=(128, 248, 96),
            max_value=self.max_health,
            value=self.health,
            padding=0,
            fixed=False
        )]

    # ======= METHODS ========
    def hit(self, damage: float) -> None:
        """Applica un danno allo zombie riducendone la salute.

        Sottrae alla salute corrente il valore damage. Se la salute
        scende a zero o sotto, la logica di cambio stato a DEAD viene
        gestita dalla property health.
        """

        self.health -= damage

    # ======== HELPERS ========
    def on_arthur_collision(self, arthur: "Arthur") -> None:
        """Gestisce la collisione tra lo zombie e Arthur.

        Se lo zombie è in stato EMERGING, IMMERSING o DEAD non infligge
        alcun danno. Negli altri casi, se il cooldown di attacco è terminato,
        colpisce Arthur infliggendo un danno pari a damage e reimposta
        il cooldown ad attack_interval, così da non colpirlo ogni frame.
        """

        if self.state.action in (Action.EMERGING, Action.IMMERSING, Action.DEAD):
            return

        if self.attack_cooldown <= 0:
            arthur.hit(self.damage)
            self.attack_cooldown = self.attack_interval

    def on_platform_collision(self, direction: Direction | None, dx: float, dy: float) -> None: # called by "Game"
        """Gestisce la collisione tra lo zombie e una piattaforma.

        Applica gli offset di correzione dx e dy alla posizione per
        evitare intersezioni e, in base alla direzione di collisione:
        - se è LEFT o RIGHT, aggiorna la direzione dello zombie
        - altrimenti azzera la velocità verticale y_step e, se la
          collisione avviene dall alto (Direction.UP), segna lo zombie come
          grounded (a terra).
        """

        if direction is None:
            return

        if dx: self.x += dx
        if dy: self.y += dy

        if direction in (Direction.LEFT, Direction.RIGHT):
            self.state.direction = direction
        else:
            self.y_step = 0.0
            if direction == Direction.UP:
                self.grounded = True


    def _set_state_action(self, action: Action) -> None:
        """Cambia l'azione dello stato dello zombie e aggiorna lo sprite di base.

        Se l'azione è diversa da quella corrente:
        - azzera il contatore del ciclo sprite
        - se la nuova azione non è DEAD, prende il primo sprite della nuova
          combinazione (Action, Direction) e aggiorna altezza, larghezza e
          posizione verticale per mantenerlo appoggiato al terreno
        - imposta la nuova azione nello stato.
        """

        if self.state.action != action:
            self.reset_sprite_cycle_counter()
            # update width, height, y based on the first sprite
            if action not in (Action.DEAD,):
                first = self.sprites[(action, self.state.direction)][0]
                self.y = self.y + self.height - first.height  # mantenere sul terreno
                self.width = first.width
                self.height = first.height
            self.state.action = action

    def _looping_sprite_selection(self, sprites: list["Sprite"]) -> "Sprite":
        """Seleziona il prossimo sprite in una animazione ciclica.

        Incrementa lo sprite_cycle_counter e sceglie il frame successivo
        nella lista sprites, ripetendola in loop in base alla velocità
        sprite_cycle_speed.

        Restituisce lo sprite selezionato.
        """

        self.sprite_cycle_counter += 1
        return sprites[(self.sprite_cycle_counter // self.sprite_cycle_speed) % len(sprites)]

    def _locked_looping_sprite_selection(self, sprites: list["Sprite"]) -> "Sprite":
        """Seleziona il prossimo sprite in una animazione bloccata.

        Incrementa lo sprite_cycle_counter e avanza nell elenco sprites
        in base a sprite_cycle_speed. Una volta raggiunto l ultimo frame,
        continua a restituire sempre l'ultimo sprite disponibile senza
        tornare all inizio della lista.

        Restituisce lo sprite selezionato.
        """

        self.sprite_cycle_counter += 1
        i = self.sprite_cycle_counter // self.sprite_cycle_speed
        return sprites[i if i < len(sprites) else -1]

    def _locked_anim_finished(self) -> bool:
        """Verifica se l'animazione bloccata corrente è arrivata all ultimo frame.

        Calcola l'indice del frame da mostrare usando sprite_cycle_counter
        e sprite_cycle_speed, e restituisce True se l'indice ha superato
        l'ultimo sprite disponibile per la combinazione (Action, Direction)
        corrente. In caso contrario restituisce False.
        """

        sprites = self.sprites[(self.state.action, self.state.direction)]
        i = self.sprite_cycle_counter // self.sprite_cycle_speed
        return i >= len(sprites) - 1


    # ======== AUTO CONSTRUCTOR ========
    @classmethod
    def auto_init(cls, player: "Arthur", game: "Game") -> "Zombie":
        settings: dict = read_settings()
        defaults: dict = settings.get("Zombie", {}).get("defaults", {})

        # -> regione di spawn da arthur
        min_dist_x = defaults.get("spawn_min_dist_x", 50)  # -> distanza minima da Arthur
        max_dist_x = defaults.get("spawn_max_dist_x", 250)  # -> ampiezza del range oltre la distanza minima
        zombie_width = defaults.get("width", 21)  # -> larghezza zombie
        zombie_height = defaults.get("height", 70)  # -> altezza zombie

        player_cx, player_cy = player.x + player.width // 2, player.y + player.height // 2

        platforms: list[Platform] = [
            _ for _ in game.actors()
            if isinstance(_, Platform)
               and not isinstance(_, (GraveStone, Ladder))
               and round(_.damage) == round(0)
               and Direction.UP in (
                   _.contact_surfaces
                   if _.contact_surfaces is not None
                   else [])
        ]  # -> selezione delle Platform su cui è possibile spawnare

        candidates: list[Candidate] = []  # -> lista contenente i candidati (ossia degli oggetti che rapparesentano le coordinate valide per lo spawn e altre proprieta come la distanza da arthur)
        for platform in platforms:
            # left -> gestione del range sinistro
            if max(platform.x, player_cx - min_dist_x - max_dist_x) <= platform.x + platform.width and min(platform.x + platform.width, player_cx - min_dist_x) >= platform.x:  # -> se la piattaforma interseca la regione x di spawn sinistra...
                min_x = max(platform.x, player_cx - min_dist_x - max_dist_x)  # -> estremo sinistro del range valido per lo spawn
                max_x = min(platform.x + platform.width, player_cx - min_dist_x)  # -> estremo destro del range valido per lo spawn

                distance = abs(platform.y - (player.y + player.height)) + (player_cx - max_x)

                if max_x - min_x > zombie_width:
                    candidates.append(Candidate(distance=distance, height=platform.y, range=Range(min_x, max_x), direction=Direction.RIGHT))

            # right -> gestione del range destro
            if max(platform.x, player_cx + min_dist_x) <= platform.x + platform.width and min(platform.x + platform.width, player_cx + min_dist_x + max_dist_x) >= platform.x:  # -> se la piattaforma interseca la regione x di spawn destra...
                min_x = max(platform.x, player_cx + min_dist_x)  # -> estremo sinistro del range valido per lo spawn
                max_x = min(platform.x + platform.width, player_cx + min_dist_x + max_dist_x)  # -> estremo destro del range valido per lo spawn

                distance = abs(platform.y - (player.y + player.height)) + (min_x - player_cx)

                if max_x - min_x > zombie_width:
                    candidates.append(Candidate(distance=distance, height=platform.y, range=Range(min_x, max_x), direction=Direction.LEFT))

        candidates.sort(key=lambda candidate: candidate.distance)

        chosen_platform = random.choice(candidates)
        x, y, d = random.uniform(chosen_platform.range.min, chosen_platform.range.max - zombie_width), chosen_platform.height - zombie_height, chosen_platform.direction

        return cls(
            name="Zombie",
            x=x,
            y=y,
            direction=d,
        )


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
        self.__health = max(0, min(value, self.max_health))
        if self.__health == 0:
            self._set_state_action(Action.DEAD)
            self.walked_distance = 0.0
            self.distance_to_walk = random.uniform(self.min_walk_distance, self.max_walk_distance)

    @property
    def max_health(self) -> float:
        return self.__max_health
    @max_health.setter
    def max_health(self, value: int | float):
        if not isinstance(value, (int, float)) or value <= 0.0:
            raise TypeError("max_health must be an int or float")
        self.__max_health: float = float(value)

    @property
    def damage(self) -> float:
        return self.__damage
    @damage.setter
    def damage(self, value: int | float):
        if not isinstance(value, (int, float)):
            raise TypeError("damage must be an int or float")
        self.__damage = float(value)

    @property
    def attack_interval(self) -> int:
        return self.__attack_interval
    @attack_interval.setter
    def attack_interval(self, value: int | float):
        if not isinstance(value, (int,)):
            raise TypeError("attack_interval must be an int")
        self.__attack_interval: int = value

    @property
    def attack_cooldown(self) -> int:
        return self.__attack_cooldown
    @attack_cooldown.setter
    def attack_cooldown(self, value: int) -> None:
        if not isinstance(value, (int,)):
            raise TypeError("attack_cooldown must be an int")
        self.__attack_cooldown: int = value if value >= 0 else 0

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
    def state(self) -> "EntityState":
        return self.__state
    @state.setter
    def state(self, value: "EntityState"):
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

    def reset_sprite_cycle_counter(self) -> int:
        self.sprite_cycle_counter = 0
        return self.sprite_cycle_counter

    @property
    def increment_sprite_cycle_counter(self) -> int:
        self.sprite_cycle_counter += 1
        return self.sprite_cycle_counter
