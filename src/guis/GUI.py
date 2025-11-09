from .GUIComponent import GUIComponent
from typing import Collection


class GUI(object):
    def __init__(self, g2d, items: list[GUIComponent] = None):
        self.g2d = g2d
        self.items = items

    @property
    def g2d(self):
        return self.__g2d
    @g2d.setter
    def g2d(self, value) -> None:
        if not hasattr(value, "draw_rect") or not hasattr(value, "draw_text") or not hasattr(value, "set_color"):
            raise TypeError("g2d must have draw_rect, draw_text and set_color methods")
        self.__g2d = value

    @property
    def items(self) -> list[GUIComponent] | None:
        return self.__items
    @items.setter
    def items(self, value) -> None:
        if not (isinstance(value, list) or value is None):
            raise TypeError("items must be a list of GUIComponent objects")
        self.__items: list[GUIComponent] | None = value

    def add(self, item: GUIComponent) -> "GUI":
        if not isinstance(item, GUIComponent):
            raise TypeError("item must be an instance of GUIComponent")
        if self.items is not None and item in self.items:
            raise ValueError("item already exists in the GUI")

        if self.items is not None: self.items.append(item)
        else: self.items = [item]

        return self

    def remove(self, item: GUIComponent) -> "GUI":
        if not isinstance(item, GUIComponent):
            raise TypeError("item must be an instance of GUIComponent")

        if self.items is not None:
            self.items.remove(item)

        return self

    def draw(self, **kwargs) -> "GUI":
        for item in self.items:
            value = None
            for k, v in kwargs.items():
                if k == item.name_id:
                    value = [v] if not isinstance(v, Collection) else list(v)
                    break
            item.g2d_draw() if value is None else item.g2d_draw(*value)
        return self