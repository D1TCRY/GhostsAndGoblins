from actor import Arena, Actor
from Arthur import Arthur
from src.Arthur import Arthur
from src.actor import Actor
from copy import deepcopy


class Game(Arena):
    def __init__(self, size: tuple[int, int], *, spawn_queue: list[Actor] | None = None):
        super().__init__(size=size)

        self.spawn_queue = spawn_queue
        self.empty_queue()

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
        super().tick(keys)

