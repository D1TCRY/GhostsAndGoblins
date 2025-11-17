import random
from collections.abc import Callable

# ENTITIES
from ..entities import Actor, Arena, check_collision, Arthur, Zombie, Arthur, Zombie, Platform, GraveStone, Ladder, Weapon, Torch, Flame, Plant, EyeBall

# STATE
from ..state import Phase, Action, Sprite



class Game(Arena):
    def __init__(self, size: tuple[int, int], *, background: Sprite | None = None, spawn_queue: list[Actor] | None = None):
        super().__init__(size=size)

        self.background = background
        self.spawn_queue = spawn_queue
        self.empty_queue()

        self.game_phase = Phase.PLAYING

        self._collision_handlers = {}
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


    def _register_default_collision_handlers(self) -> None:
        # ARTHUR - PLATFORM, LADDER, GRAVESTONE
        self.add_collision_handler(Arthur, Platform, self._handle_arthur_platform)
        self.add_collision_handler(Arthur, GraveStone, self._handle_arthur_platform)
        self.add_collision_handler(Arthur, Ladder, self._handle_arthur_ladder)

        # ZOMBIE - PLATFORM
        self.add_collision_handler(Zombie, Platform, self._handle_zombie_platform)
        self.add_collision_handler(Zombie, Arthur, self._handle_zombie_arthur)

        # TORCH - GENERIC
        self.add_collision_handler(Torch, Zombie, self._handle_torch_generic)
        self.add_collision_handler(Torch, Plant, self._handle_torch_generic)
        self.add_collision_handler(Torch, EyeBall, self._handle_torch_generic)
        self.add_collision_handler(Torch, Platform, self._handle_torch_platform)
        self.add_collision_handler(Torch, GraveStone, self._handle_torch_platform)

        # FLAME - GENERIC
        self.add_collision_handler(Flame, Zombie, self._handle_flame_generic)
        self.add_collision_handler(Flame, Plant, self._handle_flame_generic)
        self.add_collision_handler(Flame, EyeBall, self._handle_flame_generic)
        self.add_collision_handler(Flame, Platform, self._handle_flame_platform)
        self.add_collision_handler(Flame, GraveStone, self._handle_flame_platform)

        # EYEBALL - GENERIC
        self.add_collision_handler(EyeBall, Arthur, self._handle_eyeball_generic)
        self.add_collision_handler(EyeBall, Platform, self._handle_eyeball_generic)
        self.add_collision_handler(EyeBall, Zombie, self._handle_eyeball_generic)
        self.add_collision_handler(EyeBall, Weapon, self._handle_eyeball_generic)

        # PLANT - PLATFORM, ARTHUR
        self.add_collision_handler(Plant, Platform, self._handle_plant_platform)
        self.add_collision_handler(Plant, Arthur, self._handle_plant_arthur)



    # ======== COLLISION HANDLERS ========
    @staticmethod
    def _generic_damage(a1: Actor, a2: Actor, game: "Game") -> bool:
        result: bool = False

        if hasattr(a1, "damage") and hasattr(a2, "hit"):
            a2.hit(damage=a1.damage)
            result = True

        if hasattr(a2, "damage") and hasattr(a1, "hit"):
            a1.hit(damage=a2.damage)
            result = True

        return result


    # ARTHUR - PLATFORM, LADDER
    def _handle_arthur_platform(self, arthur: Arthur | Actor, platform: Platform | GraveStone | Actor, game: "Game") -> None:
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
        if game.player is not None:
            game.player.not_on_ladder_collision()


    # ZOMBIE - PLATFORM, ARTHUR
    def _handle_zombie_platform(self, zombie: Zombie | Actor, platform: Platform | Actor, game: "Game") -> None:
        if isinstance(platform, (GraveStone,)):
            return
        self._generic_damage(zombie, platform, game)
        direction, dx, dy = platform.clamp(zombie)
        if direction is None:
            return
        zombie.on_platform_collision(direction, dx, dy)
    @staticmethod
    def _handle_zombie_arthur(zombie: Zombie | Actor, arthur: Arthur | Actor, game: "Game") -> None:
        zombie.on_arthur_collision(arthur)


    # TORCH - GENERIC
    def _handle_torch_generic(self, torch: Torch | Actor, actor: Actor, game: "Game") -> None:
        if self._generic_damage(torch, actor, game):
            game.kill(torch)
    @staticmethod
    def _handle_torch_platform(torch: Torch | Actor, platform: Platform | Actor, game: "Game") -> None:
        direction, dx, dy = platform.clamp(torch)
        if direction is None:
            return
        torch.on_platform_collision(direction, dx, dy, game)


    # FLAME - GENERIC
    def _handle_flame_generic(self, flame: Flame | Actor, actor: Actor, game: "Game") -> None:
        self._generic_damage(flame, actor, game)
    @staticmethod
    def _handle_flame_platform(flame: Flame | Actor, platform: Platform | Actor, game: "Game") -> None:
        direction, dx, dy = platform.clamp(flame)
        flame.on_platform_collision(direction, dx, dy)


    # EYEBALL - GENERIC, WEAPON
    def _handle_eyeball_generic(self, eyeball: EyeBall | Actor, actor: Actor, game: "Game") -> None:
        self._generic_damage(eyeball, actor, game)
        game.kill(eyeball)
    def _handle_eyeball_weapon(self, eyeball: EyeBall | Actor, weapon: Weapon | Actor, game: "Game") -> None:
        if isinstance(weapon, EyeBall):
            return
        self._generic_damage(weapon, eyeball, game)


    # PLANT - PLATFORM
    @staticmethod
    def _handle_plant_platform(plant: Plant | Actor, platform: Platform | Actor, game: "Game") -> None:
        direction, dx, dy = platform.clamp(plant)
        if direction is None:
            return
        plant.on_platform_collision(direction, dx, dy)
    @staticmethod
    def _handle_plant_arthur(plant: Plant | Actor, arthur: Arthur | Actor, game: "Game") -> None:
        plant.on_arthur_collision(arthur)


    # ======== METHODS ========
    def inside_arena(self, o: Actor) -> bool:
        (x, y), (w, h) = o.pos(), o.size()
        aw, ah = self.size()
        return 0 <= x <= aw - w and y <= ah - h

    @staticmethod
    def distance(o1: Actor, o2: Actor) -> float:
        return ((o1.pos()[0] - o2.pos()[0]) ** 2 + (o1.pos()[1] - o2.pos()[1]) ** 2) ** 0.5

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
        if self.player is None:
            self.game_phase = Phase.GAME_OVER
            return

        if not self.inside_arena(self.player):
            self.game_phase = Phase.GAME_OVER
            self.player.health = 0
            return

        for actor in self.actors():
            if (hasattr(actor, "state") and actor.state.action is Action.DEAD) or not self.inside_arena(actor):
                self.kill(actor)

            if not isinstance(actor, (Platform,GraveStone,Ladder)) and self.distance(actor, self.player) > 300 and False:
                self.kill(actor)


        super().tick(keys)

        self._handle_collisions()

        if random.uniform(0, 1) < 0.01:
            self.spawn(Zombie.auto_init(player=self.player, game=self))

        if random.uniform(0, 1) < 0.01 and self.player is not None:
            self.spawn(Plant.auto_init(player=self.player, game=self))
