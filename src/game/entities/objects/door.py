from typing import TYPE_CHECKING
import pathlib

from ...gui import GUIComponent, Bar

# CORE
if TYPE_CHECKING: from ...core import Game
from ...core.file_management import read_settings

#ACTOR
from ..actor import Actor

# STATE
from ...state import Sprite, EntityState, SpriteCollection, Action, Direction


CAMERA_W = read_settings().get("camera_width", 430)
CAMERA_H = read_settings().get("camera_height", 230)


DOOR_SPRITE_PATH: pathlib.Path = pathlib.Path(__file__).parent.parent.parent.parent / "data" / "textures" / "ghosts-goblins-bg.png"

DOOR_SPRITE_CLOSE: Sprite = Sprite(path=DOOR_SPRITE_PATH, x=2, y=261, width=48, height=64)
DOOR_SPRITE_HALF: Sprite = Sprite(path=DOOR_SPRITE_PATH, x=53, y=261, width=48, height=64)
DOOR_SPRITE_OPEN: Sprite = Sprite(path=DOOR_SPRITE_PATH, x=104, y=261, width=48, height=64)


class Door(Actor):
    def __init__(
        self,
        x: float,
        y: float,
        width: int | float,
        height: int | float,
        *,
        name: str | None = None,
        speed: float | None = None,  # px/frame
        sprite_cycle_speed: int | None = None,
        passage_delay: int | None = None,  # n of frames
    ) -> None:
        defaults: dict = read_settings().get("Door", {}).get("defaults", {})

        # FORCED INIT
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # DEFAULTS
        self.name = name if name is not None else defaults.get("name", "Door")
        self.speed = speed if speed is not None else defaults.get("speed", 3.0)
        self.sprite_cycle_speed = sprite_cycle_speed if sprite_cycle_speed is not None else defaults.get("sprite_cycle_speed", 6)
        self.passage_delay = passage_delay if passage_delay is not None else defaults.get("passage_delay", 60)

        # STATE
        self.state = EntityState(action=Action.CLOSE, direction=Direction.DOWN)

        # SPRITES
        self.sprites = SpriteCollection()
        self.sprites[Action.CLOSE, Direction.DOWN] = [DOOR_SPRITE_OPEN, DOOR_SPRITE_HALF, DOOR_SPRITE_CLOSE]
        self.sprites[Action.OPEN, Direction.DOWN] = [DOOR_SPRITE_CLOSE, DOOR_SPRITE_HALF, DOOR_SPRITE_OPEN]

        self.sprite_cycle_counter = 0

        # INTERNAL STATE
        self.door_timer = 0
        self.passed = False


    # ======== INTERFACE IMPLEMENTATION ========
    def pos(self) -> tuple[float, float]:
        return self.x, self.y

    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def move(self, game: "Game"):
        """Aggiorna lo stato logico della porta per il frame corrente.

        Se la porta è in stato DEAD non fa nulla.

        Gestisce un timer interno:
        - quando la porta è in stato OPEN incrementa door_timer
        - quando la porta è in stato CLOSE azzera door_timer

        Quando door_timer raggiunge passage_delay imposta passed su True,
        indicando che la porta è stata attraversata con successo.
        """

        if self.state.action == Action.DEAD:
            return

        if self.state.action == Action.OPEN:
            self.door_timer += 1

        if self.state.action == Action.CLOSE:
            self.door_timer = 0

        if self.door_timer == self.passage_delay:
            self.passed = True

    def sprite(self) -> Sprite | None:
        """Restituisce lo sprite corrente della porta in base allo stato.

        Se la porta è in stato DEAD o non esiste una lista di sprite per
        la combinazione (azione, direzione) corrente, restituisce None.

        Per gli stati OPEN e CLOSE utilizza una selezione bloccata degli
        sprite, facendo avanzare l animazione e fermandosi sull ultimo
        frame disponibile.
        """

        if self.state.action == Action.DEAD:
            return None

        if not (self.state.action, self.state.direction) in self.sprites:
            return None

        sprites = self.sprites[self.state.action, self.state.direction]
        match self.state.action:
            case Action.DEAD: return None
            case Action.OPEN | Action.CLOSE: return self._locked_looping_sprite_selection(sprites)
            case _: return None

    @property
    def gui(self) -> list[GUIComponent]:
        global CAMERA_W, CAMERA_H

        door_passage: GUIComponent = Bar(
            name_id="door_passage",
            x=CAMERA_W/2 - (72/2), y=3, padding=1,
            width=72, height=14,
            text="Crossing...", text_size=10, text_color=(255, 255, 255),
            max_value=self.passage_delay, value=self.door_timer,
            background_color=(116, 116, 8), bar_color=(224, 224, 96),
            fixed=True
        )

        return [door_passage] if self.door_timer > 0 else []


    # ======== HELPER METHODS ========
    def on_arthur_collision(self) -> None:
        """Gestisce la collisione tra Arthur e la porta.

        Quando viene chiamato, imposta lo stato della porta su OPEN
        avviando lanimazione di apertura e il conteggio del timer.
        """

        self._set_state_action(Action.OPEN)

    def not_on_arthur_collision(self) -> None:
        """Gestisce la situazione in cui Arthur non è piu a contatto con la porta.

        Imposta lo stato della porta su CLOSE, avviando l'animazione
        di chiusura e azzerando il timer di passaggio.
        """

        self._set_state_action(Action.CLOSE)

    def reset_sprite_cycle_counter(self) -> int:
        self.sprite_cycle_counter = 0
        return self.sprite_cycle_counter

    def _set_state_action(self, action: Action, reset=True) -> None:
        """Cambia l'azione dello stato della porta e aggiorna lo sprite base.

        Se l'azione è diversa da quella corrente:
        - opzionalmente azzera il contatore degli sprite se reset è True
        - se la nuova azione non è DEAD, prende il primo sprite associato
          e aggiorna larghezza e altezza della porta in base a esso
        - imposta la nuova azione nella proprietà state.action
        """

        if self.state.action != action:
            if reset:
                self.reset_sprite_cycle_counter()

            if action not in (Action.DEAD,):
                first = self.sprites[action, self.state.direction][0]
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
    def speed(self) -> float:
        return self.__speed
    @speed.setter
    def speed(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("speed must be a number")
        self.__speed = float(value)

    @property
    def name(self) -> str:
        return self.__name
    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("name must be a string")
        self.__name = str(value)

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
        if not isinstance(value, int):
            raise TypeError("sprite_cycle_speed must be int")
        self.__sprite_cycle_speed = int(value)

    @property
    def passage_delay(self) -> int:
        return self.__passage_delay
    @passage_delay.setter
    def passage_delay(self, value: int) -> None:
        if not isinstance(value, int) or not value > 0:
            raise TypeError("passage_delay must be a positive int")
        self.__passage_delay = int(value)

    @property
    def door_timer(self) -> int:
        return self.__door_timer
    @door_timer.setter
    def door_timer(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("door_timer must be int")
        self.__door_timer = max(0, min(value, self.passage_delay))

    @property
    def passed(self) -> bool:
        return self.__passed
    @passed.setter
    def passed(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("passed must be bool")
        self.__passed = value