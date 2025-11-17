from .states import Action, Direction
from .sprite import Sprite


class SpriteCollection:
    def __init__(self,
                 sprites: dict[Action, dict[Direction, Sprite | list[Sprite]]] | None = None
                 ) -> None:
        self.sprites = sprites

    # ======== MAGIC METHODS ========
    def __getitem__(self, key: tuple[Action, Direction]) -> list[Sprite]:
        action, direction = self._unpack_key(key)
        return self.__sprites[action][direction]

    def __setitem__(self, key: tuple[Action, Direction], value: Sprite | list[Sprite]) -> None:
        action, direction = self._unpack_key(key)
        norm = self._normalize_value(value)
        self.__sprites.setdefault(action, {})[direction] = norm

    def __delitem__(self, key: tuple[Action, Direction]) -> None:
        action, direction = self._unpack_key(key)
        if action not in self.__sprites or direction not in self.__sprites[action]:
            raise KeyError("key (action, direction) not found")
        del self.__sprites[action][direction]
        if not self.__sprites[action]:
            del self.__sprites[action]

    def __iter__(self):
        pairs = []
        for a, inner in self.__sprites.items():
            for d in inner:
                pairs.append((a, d))
        return iter(pairs)

    def __len__(self) -> int:
        total = 0
        for inner in self.__sprites.values():
            total += len(inner)
        return total

    # ======== PROPERTIES ========
    @property
    def sprites(self) -> dict[Action, dict[Direction, list[Sprite]]]:
        return self.__sprites

    @sprites.setter
    def sprites(self, value: dict[Action, dict[Direction, Sprite | list[Sprite]]] | None) -> None:
        if value is None:
            self.__sprites: dict[Action, dict[Direction, list[Sprite]]] = {}
            return
        if not isinstance(value, dict):
            raise TypeError("sprites must be a dict[Action, dict[Direction, Sprite|list[Sprite]]]")

        normalized: dict[Action, dict[Direction, list[Sprite]]] = {}
        for a, m in value.items():
            if not isinstance(a, Action):
                raise TypeError("top-level keys must be Action")
            if not isinstance(m, dict):
                raise TypeError("each value must be a dict[Direction, Sprite|list[Sprite]]")
            inner: dict[Direction, list[Sprite]] = {}
            for d, v in m.items():
                if not isinstance(d, Direction):
                    raise TypeError("second-level keys must be Direction")
                inner[d] = self._normalize_value(v)
            normalized[a] = inner

        self.__sprites = normalized

    # ======== METHODS ========
    def add_sprite(self, action: Action, direction: Direction, sprite: Sprite) -> None:
        if not isinstance(action, Action):
            raise TypeError("action must be Action")
        if not isinstance(direction, Direction):
            raise TypeError("direction must be Direction")
        if not isinstance(sprite, Sprite):
            raise TypeError("sprite must be Sprite")

        self.__sprites.setdefault(action, {}).setdefault(direction, []).append(sprite)

    def add_sprites(self, action: Action, direction: Direction, sprites: list[Sprite]) -> None:
        if not isinstance(action, Action):
            raise TypeError("action must be Action")
        if not isinstance(direction, Direction):
            raise TypeError("direction must be Direction")
        if not isinstance(sprites, list) or not all(isinstance(s, Sprite) for s in sprites):
            raise TypeError("sprites must be list[Sprite]")

        self.__sprites.setdefault(action, {}).setdefault(direction, []).extend(list(sprites))

    def remove_sprite(self, action: Action, direction: Direction, sprite: Sprite | None = None) -> None:
        if action not in self.__sprites or direction not in self.__sprites[action]:
            raise KeyError("key (action, direction) not found")

        if sprite is None:
            del self.__sprites[action][direction]
            if not self.__sprites[action]:
                del self.__sprites[action]
            return

        lst = self.__sprites[action][direction]
        try:
            lst.remove(sprite)
        except ValueError:
            raise KeyError("sprite not found for given (action, direction)")
        if not lst:
            del self.__sprites[action][direction]
            if not self.__sprites[action]:
                del self.__sprites[action]

    def get_sprites(self, action: Action, direction: Direction) -> list[Sprite]:
        if action not in self.__sprites or direction not in self.__sprites[action]:
            raise KeyError("key (action, direction) not found")
        return self.__sprites[action][direction]

    def get_sprite(self, action: Action, direction: Direction) -> list[Sprite]:
        return self.get_sprites(action, direction)

    def get_actions(self) -> list[Action]:
        return list(self.__sprites.keys())

    def get_directions(self, action: Action) -> list[Direction]:
        if action not in self.__sprites:
            return []
        return list(self.__sprites[action].keys())

    def get_values(self) -> list[list[Sprite]]:
        vals: list[list[Sprite]] = []
        for inner in self.__sprites.values():
            vals.extend(inner.values())
        return vals

    # ======== HELPERS ========
    @staticmethod
    def _normalize_value(value: Sprite | list[Sprite]) -> list[Sprite]:
        if isinstance(value, Sprite):
            return [value]
        if isinstance(value, list) and all(isinstance(s, Sprite) for s in value):
            return list(value)
        raise TypeError("values must be Sprite or list[Sprite]")

    @staticmethod
    def _unpack_key(key: tuple[Action, Direction]) -> tuple[Action, Direction]:
        if not (isinstance(key, tuple) and len(key) == 2):
            raise TypeError("key must be a tuple (Action, Direction)")
        a, d = key
        if not isinstance(a, Action) or not isinstance(d, Direction):
            raise TypeError("key must be (Action, Direction)")
        return a, d
