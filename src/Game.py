# Game.py
import random
from collections.abc import Callable

from actor import Arena, Actor, check_collision
from Arthur import Arthur
from Zombie import Zombie
from Platform import Platform
from Ladder import Ladder
from Torch import Torch
from Flame import Flame
from status import Phase, Action, Sprite, Direction

from Plant import Plant
from EyeBall import EyeBall




class Game(Arena):
    def __init__(self, size: tuple[int, int], *, background: Sprite | None = None, spawn_queue: list[Actor] | None = None):
        super().__init__(size=size)

        self.background = background
        self.spawn_queue = spawn_queue
        self.empty_queue()

        self.game_phase = Phase.PLAYING

        self._collision_handlers: dict[
            tuple[type, type],
            Callable[[Actor, Actor, "Game"], None]
        ] = {}
        self._register_default_collision_handlers()

    @property
    def background(self) -> Sprite | None:
        return self.__background
    @background.setter
    def background(self, value: Sprite | None) -> None:
        if not isinstance(value, (Sprite, type(None))):
            raise TypeError("background must be a Sprite or None")
        self.__background = value

    @property
    def spawn_queue(self) -> list[Actor] | None:
        return self.__spawn_queue
    @spawn_queue.setter
    def spawn_queue(self, value: list[Actor] | None) -> None:
        if not isinstance(value, (list, type(None))):
            raise TypeError("spawn_queue must be a list or None")
        self.__spawn_queue = value

    @property
    def player(self) -> Arthur | None:
        actors: list[Actor] = self.actors()

        if isinstance(actors[0], Arthur): return actors[0] # type: ignore

        for actor in self.actors():
            if isinstance(actor, Arthur):
                return actor
        return None

    @property
    def game_phase(self) -> Phase:
        return self.__game_phase
    @game_phase.setter
    def game_phase(self, value: Phase) -> None:
        if not isinstance(value, Phase):
            raise TypeError("game_phase must be of type Phase")
        self.__game_phase = value

    @property
    def _collision_handlers(self) -> dict[tuple[type, type], Callable[[Actor, Actor, "Game"], None]]:
        return self.__collision_handlers
    @_collision_handlers.setter
    def _collision_handlers(self, value: dict[tuple[type, type], Callable[[Actor, Actor, "Game"], None]]) -> None:
        if not isinstance(value, dict):
            raise TypeError("_collision_handlers must be a dict")
        self.__collision_handlers = value

    @property
    def game_over(self) -> bool:
        return self.game_phase == Phase.GAME_OVER

    # ======== HELPER METHODS ========
    def _register_default_collision_handlers(self) -> None:
        # ARTHUR - PLATFORM, LADDER
        self.add_collision_handler(Arthur, Platform, self._handle_arthur_platform)
        self.add_collision_handler(Arthur, Ladder, self._handle_arthur_ladder)

        # TORCH - GENERIC
        self.add_collision_handler(Torch, Zombie, self._handle_torch_generic)
        self.add_collision_handler(Torch, Plant, self._handle_torch_generic)

        # FLAME - GENERIC
        self.add_collision_handler(Flame, Zombie, self._handle_flame_generic)
        self.add_collision_handler(Flame, Plant, self._handle_flame_generic)
        self.add_collision_handler(Flame, EyeBall, self._handle_flame_generic)

        # EYEBALL - GENERIC
        self.add_collision_handler(EyeBall, Arthur, self._handle_eyeball_generic)
        self.add_collision_handler(EyeBall, Platform, self._handle_eyeball_generic)
        self.add_collision_handler(EyeBall, Zombie, self._handle_eyeball_generic)



    def add_collision_handler(
        self,
        t1: type,
        t2: type,
        func: Callable[[Actor, Actor, "Game"], None]
    ) -> None:
        self._collision_handlers[(t1, t2)] = func

        if t1 is not t2:
            self._collision_handlers[(t2, t1)] = lambda a, b, g: func(b, a, g)

    def _handle_collisions(self) -> None:
        actors = self.actors()
        n = len(actors)

        is_arthur_ladder_collision = False
        for i in range(n):
            a1 = actors[i]
            for j in range(i + 1, n):
                a2 = actors[j]

                if not check_collision(a1, a2):
                    continue

                handler = self._collision_handlers.get((type(a1), type(a2)))
                if handler is not None:
                    handler(a1, a2, self)

                    if isinstance(a1, Arthur) and isinstance(a2, Ladder):
                        is_arthur_ladder_collision = True

        if not is_arthur_ladder_collision:
            self._handle_not_arthur_on_ladder(self)

    @staticmethod
    def _generic_damage(a1: Actor, a2: Actor, game: "Game") -> None:
        if hasattr(a1, "damage") and hasattr(a2, "hit"):
            a2.hit(damage=a1.damage)
        elif hasattr(a2, "damage") and hasattr(a1, "hit"):
            a1.hit(damage=a2.damage)

    # ARTHUR - PLATFORM, LADDER
    def _handle_arthur_platform(self, arthur: Arthur | Actor, platform: Platform | Actor, game: "Game") -> None:
        self._generic_damage(arthur, platform, game)
        direction, dx, dy = platform.clamp(arthur)
        if direction is None:
            return
        arthur.on_platform_collision(direction, dx, dy)
    def _handle_arthur_ladder(self, arthur: Arthur | Actor, ladder: Ladder | Actor, game: "Game") -> None:
        self._generic_damage(arthur, ladder, game)
        keys = game.current_keys()
        arthur.on_ladder_collision(keys, ladder.pos(), ladder.size())
    @staticmethod
    def _handle_not_arthur_on_ladder(game: "Game") -> None:
        game.player.not_on_ladder_collision()

    # TORCH - GENERIC
    def _handle_torch_generic(self, torch: Torch | Actor, actor: Actor, game: "Game") -> None:
        self._generic_damage(torch, actor, game)
        game.kill(torch)

    # FLAME - GENERIC
    def _handle_flame_generic(self, flame: Flame | Actor, actor: Actor, game: "Game") -> None:
        self._generic_damage(flame, actor, game)

    # EYEBALL - GENERIC
    def _handle_eyeball_generic(self, eyeball: EyeBall | Actor, actor: Actor, game: "Game") -> None:
        self._generic_damage(eyeball, actor, game)
        game.kill(eyeball)





    # ======== METHODS ========
    def get_actors_by_instance(self, cls: type) -> list[object]:
        return [a for a in self.actors() if isinstance(a, cls)]

    def empty_queue(self) -> None:
        if self.spawn_queue is None:
            return

        for idx, actor in enumerate(self.spawn_queue):
            if isinstance(actor, Arthur):
                player = self.spawn_queue.pop(idx)
                self.spawn_queue.insert(0, player)
                break

        for actor in list(self.spawn_queue):
            self.spawn(actor)

    def tick(self, keys: list[str] | None = None) -> None:
        for actor in self.actors():
            if hasattr(actor, "state") and actor.state.action == Action.DEAD:
                self.kill(actor)

        super().tick(keys)

        self._handle_collisions()

        if random.uniform(0, 1) < 0.01:
            self.spawn(Zombie.auto_init(player=self.player, arena=self))

        if random.uniform(0, 1) < 0.01 and self.player is not None:
            self.spawn(Plant.auto_init(player=self.player, arena=self))
