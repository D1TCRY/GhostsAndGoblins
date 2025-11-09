from Camera import Camera
from src.actor import Actor
from guis import GUIComponent

from status import Sprite
from g2d_lib import g2d


class GraphicalInterface:
    def __init__(self, camera: Camera, *, gui_components: list[GUIComponent] | None = None):
        self.camera = camera
        self.gui: list[GUIComponent] = gui_components

    # ======== PROPERTIES ========
    @property
    def camera(self) -> Camera:
        return self.__camera
    @camera.setter
    def camera(self, value: Camera) -> None:
        if not isinstance(value, Camera):
            raise TypeError("camera must be of type Camera")
        self.__camera: Camera = value

    @property
    def gui(self) -> list[GUIComponent] | None:
        return self.__gui
    @gui.setter
    def gui(self, value: list[GUIComponent] | None) -> None:
        if not isinstance(value, (list, type(None))):
            raise TypeError("gui must be a list or None")
        self.__gui: list[GUIComponent] | None = value


    # ======== METHODS ========
    def render(self, actors: list[Actor], gui_components: list[GUIComponent]):
        self.render_game(actors)

    def render_game(self, actors: list[Actor]):
        for actor in reversed(actors): # end=arthur
            sprite: Sprite | tuple[float, float] | None = actor.sprite()
            if isinstance(sprite, Sprite):
                pos = actor.pos()[0] - self.camera.view_x, actor.pos()[1] - self.camera.view_y
                g2d.draw_image(src=sprite.path, pos=pos, clip_pos=sprite.pos, clip_size=sprite.size)


    def render_gui(self, gui_components: list[GUIComponent]):
        for gui_component in gui_components:
            info = gui_component.render_info() #type: ignore
            for item in info:
                type_ = item.get("type", None)
                color = item.get("color", None)
                text = item.get("text", None)
                pos = item.get("pos", None)
                center = item.get("center", None)
                size = item.get("size", None)
                text = item.get("text", None)
                font_size = item.get("font_size", None)

                if color is not None: g2d.set_color(color)

                if type_ == "rect" and pos is not None and size is not None: g2d.draw_rect(pos=pos, size=size)
                elif type_ == "text" and text is not None: g2d.draw_text(text, pos=pos, center=center, size=size, font_size=font_size)

    # ======== SET METHODS ========
    def add_gui_component(self, gui_component: GUIComponent) -> "GraphicalInterface":
        if not isinstance(gui_component, GUIComponent):
            raise TypeError("gui_component must be of type GUIComponent")

        if self.gui is None: self.gui = [gui_component]
        else: self.gui.append(gui_component)

        return self

    def remove_gui_component(self, gui_component: GUIComponent) -> "GraphicalInterface":
        if not isinstance(gui_component, GUIComponent):
            raise TypeError("gui_component must be of type GUIComponent")

        if self.gui is None: return self
        self.gui.remove(gui_component)

        return self

    def insert_gui_component(self, index: int, gui_component: GUIComponent) -> "GraphicalInterface":
        if not isinstance(gui_component, GUIComponent):
            raise TypeError("gui_component must be of type GUIComponent")

        if self.gui is None: self.gui = [gui_component]
        else: self.gui.insert(index, gui_component)

        return self
