from enum import Enum, auto


class Action(Enum):
    """Enum che rappresenta le azioni possibili di una entita, come movimento, attacco o stato visivo."""

    BIG = auto()
    SMALL = auto()

    CLOSE = auto()
    OPEN = auto()

    LOCKED = auto()
    IDLE = auto()
    DEAD = auto()

    WALKING = auto()
    JUMPING = auto()
    CROUCHING = auto()
    CLIMBING = auto()
    CLIMBING_POSE = auto()

    ATTACKING = auto()
    ATTACKING_CROUCHED = auto()

    EMERGING = auto()
    IMMERSING = auto()

    SPAWNING = auto()

    def __str__(self) -> str:
        return f"<{self.name.capitalize()}>"

    def __repr__(self) -> str:
        return self.__str__()


class Direction(Enum):
    """Enum che rappresenta le direzioni principali usate per movimento e collisioni."""

    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()

    def __str__(self) -> str:
        return f"<{self.name.capitalize()}>"

    def __repr__(self) -> str:
        return self.__str__()


class Phase(Enum):
    """Enum che descrive le fasi principali dell applicazione e dello stato di gioco."""

    # APP
    MENU = auto()
    START_GAME = auto()
    PLAYING = auto()
    END_GAME = auto()
    QUIT = auto()

    # GAME
    GAME_WON = auto()
    GAME_OVER = auto()

    def __str__(self) -> str:
        return f"<{self.name.capitalize()}>"

    def __repr__(self) -> str:
        return self.__str__()


class MenuPhase(Enum):
    """Enum che rappresenta le diverse schermate o stati del menu principale."""

    MAIN = auto()
    GAME_WON = auto()
    GAME_OVER = auto()

    def __str__(self) -> str:
        return f"<{self.name.capitalize()}>"

    def __repr__(self) -> str:
        return self.__str__()