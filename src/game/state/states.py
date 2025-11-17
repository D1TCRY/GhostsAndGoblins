from enum import Enum, auto


class Action(Enum):
    BIG = auto()
    SMALL = auto()

    LOCKED = auto()
    IDLE = auto()
    DEAD = auto()

    WALKING = auto()
    JUMPING = auto()
    CROUCHING = auto()
    CLIMBING = auto()
    CLIMBING_POSE = auto()

    ATTACKING = auto()

    EMERGING = auto()
    IMMERSING = auto()

    SPAWNING = auto()

    def __str__(self) -> str:
        return f"<{self.name.capitalize()}>"

    def __repr__(self) -> str:
        return self.__str__()


class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()

    def __str__(self) -> str:
        return f"<{self.name.capitalize()}>"

    def __repr__(self) -> str:
        return self.__str__()


class Phase(Enum):
    MENU = auto()
    START_GAME = auto()
    PLAYING = auto()
    END_GAME = auto()
    PAUSED = auto()
    GAME_OVER = auto()

    def __str__(self) -> str:
        return f"<{self.name.capitalize()}>"

    def __repr__(self) -> str:
        return self.__str__()

