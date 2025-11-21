from .states import Action, Direction




class EntityState:
    """Rappresenta lo stato logico di una entita, composto da azione e direzione.

    Incapsula una coppia (Action, Direction) e fornisce confronti, hash e
    controlli di tipo per garantire stati consistenti.
    """

    def __init__(self, action: Action, direction: Direction) -> None:
        self.action = action
        self.direction = direction
    
    # ======== MAGIC METHODS ========
    def __str__(self) -> str:
        return f"State(action={str(self.action)}, direction={str(self.direction)})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(action={repr(self.action)}, direction={repr(self.direction)})"
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, EntityState):
            return False
        return self.action is value.action and self.direction is value.direction

    def __hash__(self) -> int:
        return hash((self.action, self.direction))
    
    # ======== PROPERTIES ========
    @property
    def action(self) -> Action:
        return self.__action
    @action.setter
    def action(self, value: Action):
        if not isinstance(value, Action):
            raise TypeError("action must be an instance of Action Enum")
        self.__action: Action = value
    
    @property
    def direction(self) -> Direction:
        return self.__direction
    @direction.setter
    def direction(self, value: Direction):
        if not isinstance(value, Direction):
            raise TypeError("direction must be an instance of Direction Enum")
        self.__direction: Direction = value

