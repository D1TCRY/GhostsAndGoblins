from Game import Game
from Camera import Camera
from actor import Actor
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
    def gui(self) -> list[GUIComponent]:
        if self.__gui is None: return []
        return self.__gui
    @gui.setter
    def gui(self, value: list[GUIComponent] | None) -> None:
        if not isinstance(value, (list, type(None))):
            raise TypeError("gui must be a list or None")
        self.__gui: list[GUIComponent] | None = value


    # ======== METHODS ========
    def render(self, game: Game):
        self.camera.tick(game)

        world_sprite: Sprite = game.background
        if world_sprite is not None:
            pos = world_sprite.pos[0] + self.camera.view_x, world_sprite.pos[1] + self.camera.view_y
            size = self.camera.size
            g2d.draw_image(src=world_sprite.path, pos=(0, 0), clip_pos=pos, clip_size=size)

        actors: list[Actor] = game.actors()

        gui_actors_components: list[GUIComponent] = []
        for actor in reversed(actors): # end=arthur
            sprite: Sprite | tuple[float, float] | None = actor.sprite()
            if isinstance(sprite, Sprite):
                pos = actor.pos()[0] - self.camera.view_x, actor.pos()[1] - self.camera.view_y
                g2d.draw_image(src=sprite.path, pos=pos, clip_pos=sprite.pos, clip_size=sprite.size)

            if hasattr(actor, "gui"):
                gui_actors_components.extend(actor.gui)


        for gui_component in self.gui + gui_actors_components:
            info = gui_component.render_info() #type: ignore
            for item in info:
                type_ = item.get("type", None)
                color = item.get("color", None)
                text = item.get("text", None)
                pos = item.get("pos", None)
                center = item.get("center", None)
                size = item.get("size", None)
                font_size = item.get("font_size", None)

                if not gui_component.fixed:
                    if pos is not None: pos = pos[0] - self.camera.view_x, pos[1] - self.camera.view_y
                    if center is not None: center = center[0] - self.camera.view_x, center[1] - self.camera.view_y

                if color is not None: g2d.set_color(color)

                if (
                    type_ == "rect" and
                    pos is not None and
                    size is not None
                ): g2d.draw_rect(pos=pos, size=size)
                elif (
                    type_ == "text" and
                    text is not None and
                    center is not None and
                    font_size is not None
                ): g2d.draw_text(text=text, center=center, size=font_size)

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
