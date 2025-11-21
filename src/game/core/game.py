import random
from collections.abc import Callable
from typing import Any

# CORE
from .file_management import read_settings

# ENTITIES
from ..entities import Actor, Arena, check_collision, Arthur, Zombie, Arthur, Zombie, Platform, GraveStone, Ladder, Weapon, Torch, Flame, Plant, EyeBall, Door

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
        self._collision_free_handlers = {}
        self._register_default_collision_handlers()
        self._register_default_collision_free_handlers()

        self._settings = read_settings()


    @property
    def _settings(self) -> dict[str, Any]:
        return self.__settings
    @_settings.setter
    def _settings(self, value: dict[str, Any]) -> None:
        if not isinstance(value, dict):
            raise TypeError("_settings must be a dict")
        self.__settings = value

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
    def _collision_free_handlers(self) -> dict[tuple[type, type], Callable[[Actor, Actor, "Game"], None]]:
        return self.__collision_free_handlers
    @_collision_free_handlers.setter
    def _collision_free_handlers(self, value: dict[tuple[type, type], Callable[[Actor, Actor, "Game"], None]]) -> None:
        if not isinstance(value, dict):
            raise TypeError("_collision_free_handlers must be a dict")
        self.__collision_free_handlers = value

    @property
    def game_over(self) -> bool:
        return self.game_phase is Phase.GAME_OVER

    @property
    def game_won(self) -> bool:
        return self.game_phase is Phase.GAME_WON


    # ======== HELPER METHODS ========
    def add_collision_handler(
        self,
        t1: type,
        t2: type,
        func: Callable[[Actor, Actor, "Game"], None]
    ) -> None:
        """Aggiunge un gestore di collisione per una coppia di tipi di attori.

        Registra la funzione func come handler per le collisioni tra istanze
        dei tipi t1 e t2. Se t1 e t2 sono diversi, crea automaticamente anche
        la versione simmetrica, in modo che il gestore venga chiamato
        indipendentemente dall ordine con cui gli attori vengono passati
        alla funzione di controllo collisioni.
        """

        self._collision_handlers[(t1, t2)] = func

        if t1 is not t2:
            self._collision_handlers[(t2, t1)] = lambda a, b, g: func(b, a, g)

    def add_collision_free_handler(
        self,
        t1: type,
        t2: type,
        func: Callable[[Actor, Actor, "Game"], None]
    ) -> None:
        """Aggiunge un gestore per la condizione di non collisione tra due tipi.

        Similmente ad add_collision_handler.
        """

        self._collision_free_handlers[(t1, t2)] = func

        if t1 is not t2:
            self._collision_free_handlers[(t2, t1)] = lambda a, b, g: func(b, a, g)

    def _handle_collisions(self) -> None:
        """Gestisce tutte le collisioni e non collisioni tra attori presenti nel gioco.

        Scorre tutte le coppie di attori nella arena e per ciascuna coppia:
        - se ce collisione, invoca il relativo gestore registrato in
          _collision_handlers, se presente, e segna che per quella coppia
          di tipi si e verificata almeno una collisione
        - se non ce collisione, e se esiste un gestore di non collisione
          in _collision_free_handlers, salva una coppia di attori di esempio
          per quel pair di tipi

        Al termine, per ogni coppia di tipi che ha un esempio di non
        collisione ma non ha mai avuto collisioni nel frame corrente,
        invoca il relativo gestore di non collisione una sola volta usando
        la coppia di esempio salvata.
        """

        actors = self.actors()
        n = len(actors)

        # -> ha almeno una collisione per pair di tipi
        had_collision: set[tuple[type, type]] = set()
        # -> un esempio di coppia non-collidente per quel pair di tipi
        free_example: dict[tuple[type, type], tuple[Actor, Actor]] = {}

        for i in range(n):
            a1 = actors[i]
            for j in range(i + 1, n):
                a2 = actors[j]
                t1, t2 = type(a1), type(a2)

                if check_collision(a1, a2):
                    # -> collision handler
                    handler = self._collision_handlers.get((t1, t2))
                    if handler is not None:
                        handler(a1, a2, self)

                    # -> segna collisione per entrambi gli ordini di tipi
                    had_collision.add((t1, t2))
                    had_collision.add((t2, t1))

                else:
                    # -> non-collisione salva solo se esiste un handler_free
                    handler_free = self._collision_free_handlers.get((t1, t2))
                    if handler_free is not None and (t1, t2) not in free_example:
                        # salva una coppia "esempio"
                        free_example[(t1, t2)] = (a1, a2)
                        free_example[(t2, t1)] = (a2, a1)

        done: set[tuple[type, type]] = set()
        for (t1, t2), (a1, a2) in free_example.items():
            if (t1, t2) in done:
                continue

            # -> handler_free solo se per quel pair di tipi non si è mai verificata una collisione
            if (t1, t2) not in had_collision:
                handler_free = self._collision_free_handlers.get((t1, t2))
                if handler_free is not None:
                    handler_free(a1, a2, self)

            done.add((t1, t2))
            done.add((t2, t1))


    def _register_default_collision_handlers(self) -> None:
        """Registra tutti i gestori di collisione predefiniti del gioco.

        Associa alle principali combinazioni di tipi di attori le funzioni
        interne che descrivono cosa accade in caso di collisione.

        Queste associazioni popolano il dizionario _collision_handlers,
        utilizzato da _handle_collisions durante l'aggiornamento del gioco.
        """

        # ARTHUR - PLATFORM, LADDER, GRAVESTONE, DOOR
        self.add_collision_handler(Arthur, Platform, self._handle_arthur_platform)
        self.add_collision_handler(Arthur, GraveStone, self._handle_arthur_platform)
        self.add_collision_handler(Arthur, Ladder, self._handle_arthur_ladder)
        self.add_collision_handler(Arthur, Door, self._handle_arthur_door)

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

    def _register_default_collision_free_handlers(self):
        """Registra i gestori per le situazioni di non collisione predefinite.

        Similmente a _register_default_collision_handlers.
        """

        self.add_collision_free_handler(Arthur, Ladder, self._handle_not_arthur_on_ladder)
        self.add_collision_free_handler(Arthur, Door, self._handle_not_arthur_door)


    # ======== COLLISION HANDLERS ========
    @staticmethod
    def _generic_damage(a1: Actor, a2: Actor) -> bool:
        result: bool = False

        if hasattr(a1, "damage") and hasattr(a2, "hit"):
            a2.hit(damage=a1.damage)
            result = True

        if hasattr(a2, "damage") and hasattr(a1, "hit"):
            a1.hit(damage=a2.damage)
            result = True

        return result


    # ARTHUR - PLATFORM, LADDER, DOOR
    def _handle_arthur_platform(self, arthur: Arthur | Actor, platform: Platform | GraveStone | Actor, game: "Game") -> None:
        self._generic_damage(arthur, platform)
        direction, dx, dy = platform.clamp(arthur)
        if direction is None:
            return
        arthur.on_platform_collision(direction, dx, dy)
    def _handle_arthur_ladder(self, arthur: Arthur | Actor, ladder: Ladder | Actor, game: "Game") -> None:
        self._generic_damage(arthur, ladder)
        keys = game.current_keys()
        arthur.on_ladder_collision(keys, ladder.pos(), ladder.size())
    @staticmethod
    def _handle_arthur_door(arthur: Arthur | Actor, door: Door | Actor, game: "Game") -> None:
        door.on_arthur_collision()

    # NOT ARTHUR - LADDER, DOOR
    @staticmethod
    def _handle_not_arthur_on_ladder(arthur: Arthur | Actor, ladder: Ladder | Actor, game: "Game") -> None:
        if game.player is not None:
            game.player.not_on_ladder_collision()
    @staticmethod
    def _handle_not_arthur_door(arthur: Arthur | Actor, door: Door | Actor, game: "Game") -> None:
        door.not_on_arthur_collision()


    # ZOMBIE - PLATFORM, ARTHUR
    def _handle_zombie_platform(self, zombie: Zombie | Actor, platform: Platform | Actor, game: "Game") -> None:
        if isinstance(platform, (GraveStone,)):
            return
        self._generic_damage(zombie, platform)
        direction, dx, dy = platform.clamp(zombie)
        if direction is None:
            return
        zombie.on_platform_collision(direction, dx, dy)
    @staticmethod
    def _handle_zombie_arthur(zombie: Zombie | Actor, arthur: Arthur | Actor, game: "Game") -> None:
        zombie.on_arthur_collision(arthur)


    # TORCH - GENERIC
    def _handle_torch_generic(self, torch: Torch | Actor, actor: Actor, game: "Game") -> None:
        if self._generic_damage(torch, actor):
            game.kill(torch)
    @staticmethod
    def _handle_torch_platform(torch: Torch | Actor, platform: Platform | Actor, game: "Game") -> None:
        direction, dx, dy = platform.clamp(torch)
        if direction is None:
            return
        torch.on_platform_collision(direction, dx, dy, game)


    # FLAME - GENERIC
    def _handle_flame_generic(self, flame: Flame | Actor, actor: Actor, game: "Game") -> None:
        self._generic_damage(flame, actor)
    @staticmethod
    def _handle_flame_platform(flame: Flame | Actor, platform: Platform | Actor, game: "Game") -> None:
        direction, dx, dy = platform.clamp(flame)
        flame.on_platform_collision(direction, dx, dy)


    # EYEBALL - GENERIC, WEAPON
    def _handle_eyeball_generic(self, eyeball: EyeBall | Actor, actor: Actor, game: "Game") -> None:
        self._generic_damage(eyeball, actor)
        game.kill(eyeball)
    def _handle_eyeball_weapon(self, eyeball: EyeBall | Actor, weapon: Weapon | Actor, game: "Game") -> None:
        if isinstance(weapon, EyeBall):
            return
        self._generic_damage(weapon, eyeball)


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

    def empty_queue(self) -> None:
        """Svuota la coda di spawn iniziale popolando l arena con gli attori.

        Dopo l esecuzione, tutti gli attori nella coda di spawn risultano
        inseriti nel mondo di gioco.
        """

        if self.spawn_queue is None:
            return

        for idx, actor in enumerate(self.spawn_queue):
            if isinstance(actor, Arthur):
                player = self.spawn_queue.pop(idx)
                self.spawn_queue.insert(0, player)
                break

        for actor in list(self.spawn_queue):
            self.spawn(actor)
        self.spawn_queue.clear()

    def tick(self, keys: list[str] | None = None) -> None:
        """Aggiorna lo stato del gioco per il frame corrente.

        Gestisce la logica principale di partita:
        - se il giocatore non esiste oppure la sua azione e DEAD, imposta
          game_phase su GAME_OVER e termina
        - se la salute del giocatore scende a zero, imposta la sua azione
          su DEAD
        - se il giocatore esce dai limiti della arena, imposta game_phase su
          GAME_OVER, porta la sua salute a zero e termina
        - se esiste una porta ed e stata attraversata, imposta game_phase
          su GAME_WON

        Successivamente:
        - elimina attori non giocatori che sono morti oppure usciti dalla
          arena
        - elimina attori non statici troppo lontani dal giocatore per
          ottimizzazione

        Poi richiama il tick della classe base Arena per aggiornare la
        posizione e lo stato di tutti gli attori in base ai tasti premuti,
        e invoca _handle_collisions per gestire tutte le collisioni del
        frame.

        Infine, con una piccola probabilita casuale a ogni frame, genera
        e spawna nuovi nemici come Zombie e Plant, usando i rispettivi
        metodi auto_init e la posizione/stato del giocatore.
        """

        if self.player is None or self.player.state.action is Action.DEAD:
            self.game_phase = Phase.GAME_OVER
            return

        if self.player.health <= 0:
            self.player.state.action = Action.DEAD

        if not self.inside_arena(self.player):
            self.game_phase = Phase.GAME_OVER
            self.player.health = 0
            return

        doors = [a for a in self.actors() if isinstance(a, Door)]
        door: Door = doors[0] if len(doors) > 0 else None # type: ignore
        if door is not None and door.passed:
            self.game_phase = Phase.GAME_WON

        for actor in self.actors():
            if not isinstance(actor, (Platform, Arthur)) and ((hasattr(actor, "state") and actor.state.action is Action.DEAD) or (not self.inside_arena(actor))):
                self.kill(actor)

            if self.player is not None and (not isinstance(actor, (Platform,GraveStone,Ladder,Arthur,Door)) and self.distance(actor, self.player) > 300):
                self.kill(actor)

        super().tick(keys)
        self._handle_collisions()

        if random.uniform(0, 1) < self._settings.get("Zombie", {}).get("defaults", {}).get("spawn_chance", 0.005) and self.player is not None:
            self.spawn(Zombie.auto_init(player=self.player, game=self))

        if random.uniform(0, 1) < self._settings.get("Plant", {}).get("defaults", {}).get("spawn_chance", 0.005) and self.player is not None:
            self.spawn(Plant.auto_init(player=self.player, game=self))
