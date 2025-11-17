import pathlib
try: from PIL import Image, ImageEnhance
except ImportError: Image = None; ImageEnhance = None

# G2D
from src.g2d_lib import g2d

# CORE
from .game import Game
from .camera import Camera

# ENTITIES
from ..entities import Actor

# GUI
from ..gui import GUIComponent

# STATE
from ..state import Sprite



class GraphicalInterface:
    def __init__(self, camera: Camera, *, gui_components: list[GUIComponent] | None = None):
        self.camera = camera
        self.gui: list[GUIComponent] = gui_components

        self.__frame = 0
        self.__gui_actors_components = []

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
        self.__frame += 1
        self.camera.tick(game)

        self.render_sprites(game)
        self.render_guis()

    def render_sprites(self, game: Game):
        world_sprite: Sprite = game.background
        if world_sprite is not None:
            pos = world_sprite.pos[0] + self.camera.view_x, world_sprite.pos[1] + self.camera.view_y
            size = self.camera.size
            g2d.draw_image(src=world_sprite.path, pos=(0, 0), clip_pos=pos, clip_size=size)

        actors: list[Actor] = game.actors()

        self.__gui_actors_components: list[GUIComponent] = []
        for actor in reversed(actors): # end=arthur
            sprite: Sprite | tuple[float, float] | None = actor.sprite()
            if isinstance(sprite, Sprite):
                pos = actor.pos()[0] - self.camera.view_x, actor.pos()[1] - self.camera.view_y

                if not sprite.blinking:
                    g2d.draw_image(src=sprite.path, pos=pos, clip_pos=sprite.pos, clip_size=sprite.size)
                else: # blinking == True -> ogni 5 frame si alterna tra immagine diegnata e nulla. in caso pillow sia stato importato si alterna tra la immagine stessa e una versione con un filtro applicato
                    if Image is None or ImageEnhance is None or not isinstance(sprite.path, pathlib.Path):
                        # -> modalità senza pillow
                        if (self.__frame // 5) % 2 == 0:
                            g2d.draw_image(src=sprite.path, pos=pos, clip_pos=sprite.pos, clip_size=sprite.size)
                    else:
                        # -> modalità con pillow
                        if (self.__frame // 5) % 2 == 0:
                            g2d.draw_image(src=sprite.path, pos=pos, clip_pos=sprite.pos, clip_size=sprite.size)
                        else:
                            bright_path = getattr(sprite, "_bright_path", None) # -> controllo dell'esistenza del bright_path (percorso che punta a un file immagine con un filtro gia applicato)
                            if bright_path is None:
                                path = str(sprite.path)
                                # -> preparazione del nuovo percorso dell'immagine col filtro applicato
                                if "." in path:
                                    bright_path = path.replace(".", "-bright.", 1)
                                else:
                                    bright_path = path + "-bright"

                                img = Image.open(path) # -> apertura immagine corrente
                                enhancer = ImageEnhance.Brightness(img) # -> creazione di un enhancer
                                img_bright = enhancer.enhance(3) # -> applicazione del filtro
                                img_bright.save(bright_path) # -> salvataggio della immagine nel nuovo percorso
                                sprite._bright_path = bright_path # -> creazione di un attributo in sprite da usare per evitare di riapplicare il filtro e salvare ogni volta

                            g2d.draw_image(src=bright_path, pos=pos, clip_pos=sprite.pos, clip_size=sprite.size)

            if hasattr(actor, "gui"): # -> ottengo eventuali elementi di interfaccia grafica appartenenti agli attori da renderizzare
                self.__gui_actors_components.extend(actor.gui)

    def render_guis(self):
        # -> rendering di tutti gli elementi grafici (appartenenti agli attori o no)
        for gui_component in self.gui + self.__gui_actors_components:
            info = gui_component.render_info() #type: ignore # -> ottengo le informazioni necessarie per disegnere un componente grafico
            for item in info: # ogni componente grafico puo essere composto da piu figure da disegnare e sono possibili varie configurazioni e proprietà, quindi le estraggo
                type_ = item.get("type", None)
                color = item.get("color", None)
                text = item.get("text", None)
                pos = item.get("pos", None)
                center = item.get("center", None)
                size = item.get("size", None)
                font_size = item.get("font_size", None)

                if not gui_component.fixed: # -> serve per stabilire se le coordinarte del componente grafico sono relative alla Camera o relative alla finestra vera e propria
                    if pos is not None: pos = pos[0] - self.camera.view_x, pos[1] - self.camera.view_y
                    if center is not None: center = center[0] - self.camera.view_x, center[1] - self.camera.view_y

                if color is not None: g2d.set_color(color)

                if ( # -> condizioni necessarie per disegnare un oggetto di tipo "rect"
                    type_ == "rect" and
                    pos is not None and
                    size is not None
                ): g2d.draw_rect(pos=pos, size=size)
                elif ( # -> condizioni necessarie per disegnare un oggetto di tipo "text"
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
