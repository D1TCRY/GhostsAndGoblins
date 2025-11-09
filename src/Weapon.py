from actor import Actor, Arena
from status import Action, Direction, Sprite, SpriteCollection, State


class Weapon(Actor):
    def __init__(self,
        *,
        owner: Actor = None,
        action: Action = Action.ATTACKING,
        direction: Direction = Direction.RIGHT,
        sprite_cycle_speed: int = 4
    ) -> None:
        self.state = State(action=action, direction=direction)
        self.sprites = SpriteCollection()
        self.sprite_cycle_counter = 0
        self.sprite_cycle_speed = int(sprite_cycle_speed)

    # ======== PROPERTIES ========
    @property
    def reset_sprite_cycle_counter(self) -> int:
        self.sprite_cycle_counter = 0
        return self.sprite_cycle_counter

    @property
    def increment_sprite_cycle_counter(self) -> int:
        self.sprite_cycle_counter += 1
        return self.sprite_cycle_counter

    # ======== INTERFACE IMPLEMENTATION ========
    def pos(self) -> tuple[float, float]: ...
    def size(self) -> tuple[int, int]: ...
    def move(self, arena: Arena) -> None: ...
    def sprite(self) -> Sprite | None: ...

    # ======== HELPER METHODS ========
    def _looping_sprite_selection(self, sprites: list[Sprite]) -> Sprite:
        self.sprite_cycle_counter += 1
        return sprites[(self.sprite_cycle_counter // self.sprite_cycle_speed) % len(sprites)]

    def _locked_looping_sprite_selection(self, sprites: list[Sprite]) -> Sprite:
        self.sprite_cycle_counter += 1
        i = self.sprite_cycle_counter // self.sprite_cycle_speed
        return sprites[i if i < len(sprites) else -1]
