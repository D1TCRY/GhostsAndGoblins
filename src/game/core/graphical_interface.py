import pathlib
from collections.abc import Callable

from PIL.ImageMath import lambda_eval

try:
    from PIL import Image, ImageEnhance
except ImportError:
    Image = None; ImageEnhance = None

# G2D
from src.g2d_lib import g2d

# CORE
from .game import Game
from .camera import Camera
from .file_management import read_settings

# ENTITIES
from ..entities import Actor, Arthur

# GUI
from ..gui import GUIComponent, Color

# STATE
from ..state import Sprite

settings = read_settings()
CAMERA_WIDTH, CAMERA_HEIGHT = settings.get("camera_width", 430), settings.get("camera_height", 230)


def init_canvas(tick: Callable[[], []], size: tuple[int, int] | None = None, scale: float = 1, fps: int = 30) -> None:
    """Inizializzazione del canvas iniziale e avvio del loop principale."""

    g2d.init_canvas(size=size, scale=scale)
    g2d.main_loop(tick=tick, fps=fps)


class GraphicalInterface:
    def __init__(self, camera: Camera | None, *, gui_components: list[GUIComponent] | None = None,
                 background: Sprite | Color | None = None, clear_canvas: bool = True):
        self.camera = camera
        self.gui: list[GUIComponent] = gui_components
        self.background = background
        self.clear_canvas = clear_canvas

        self.__frame = 0
        self.__gui_actors_components = []

    # ======== PROPERTIES ========
    @property
    def camera(self) -> Camera:
        return self.__camera

    @camera.setter
    def camera(self, value: Camera | None) -> None:
        if not isinstance(value, (Camera, type(None))):
            raise TypeError("camera must be of type Camera or None")
        self.__camera: Camera = value if value is not None else Camera(0, 0, CAMERA_WIDTH, CAMERA_HEIGHT)

    @property
    def gui(self) -> list[GUIComponent]:
        if self.__gui is None:
            self.__gui = []
        return self.__gui

    @gui.setter
    def gui(self, value: list[GUIComponent] | None) -> None:
        if not isinstance(value, (list, type(None))):
            raise TypeError("gui must be a list or None")
        self.__gui: list[GUIComponent] | None = value

    @property
    def background(self) -> Sprite | Color | None:
        return self.__background

    @background.setter
    def background(self, value: Sprite | Color | None) -> None:
        if not isinstance(value, (Sprite, Color, type(None))):
            raise TypeError("background must be of type Sprite, Color or None")
        self.__background: Sprite | Color | None = value

    @property
    def clear_canvas(self) -> bool:
        return self.__clear_canvas

    @clear_canvas.setter
    def clear_canvas(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("clear_canvas must be of type bool")
        self.__clear_canvas: bool = value

    # ======== METHODS ========
    def render(self, game: Game):
        """Esegue il rendering completo di un frame di gioco.

        Se clear_canvas è vero pulisce il canvas, aggiorna il frame interno
        e chiama il metodo tick della camera per allinearla allo stato
        corrente del gioco.

        Successivamente disegna nell ordine:
        - lo sfondo, tramite render_background
        - tutti gli sprite di gioco, tramite render_sprites
        - tutti i componenti grafici di interfaccia, tramite render_guis
        """

        if self.clear_canvas: g2d.clear_canvas()

        self.__frame += 1
        self.camera.tick(game)

        self.render_background(self.background)
        self.render_sprites(game, clear_canvas=False)
        self.render_guis(clear_canvas=False)

    def render_sprites(self, game: Game, clear_canvas: bool | None = None):
        """Disegna sul canvas lo sfondo del mondo di gioco e tutti gli attori.

        Gestisce opzionalmente la pulizia del canvas in base al parametro
        clear_canvas e alla proprieta clear_canvas della interfaccia.

        Per prima cosa disegna lo sprite di sfondo del mondo in base alla
        posizione della camera, poi:
        - recupera la lista degli attori dal Game
        - sposta Arthur in fondo alla lista in modo che venga disegnato per ultimo
        - per ogni attore ottiene lo sprite e lo disegna in posizione relativa
          alla camera

        Per gli sprite lampeggianti gestisce un effetto visivo:
        - se Pillow non sono disponibile, alterna tra sprite visibile
          e sprite nascosto ogni pochi frame
        - se Pillow è disponibile genera, solo la prima volta, una versione
          schiarita dell immagine e alterna tra immagine normale e immagine
          schiarita salvata su file

        Infine raccoglie eventuali elementi di interfaccia grafica associati
        agli attori e li memorizza in __gui_actors_components per il
        rendering successivo.
        """

        if clear_canvas is None and self.clear_canvas:
            g2d.clear_canvas()
        elif clear_canvas:
            g2d.clear_canvas()

        world_sprite: Sprite = game.background
        if world_sprite is not None:
            pos = world_sprite.pos[0] + self.camera.view_x, world_sprite.pos[1] + self.camera.view_y
            size = self.camera.size
            g2d.draw_image(src=world_sprite.path, pos=(0, 0), clip_pos=pos, clip_size=size)

        actors: list[Actor] = game.actors()
        index = 0
        if not isinstance(actors[index], Arthur):
            for i, actor in enumerate(actors):
                if isinstance(actor, Arthur):
                    index = i
                    break
        arthur = actors.pop(index)
        actors.append(arthur)

        self.__gui_actors_components: list[GUIComponent] = []
        for actor in actors:  # end=arthur
            sprite: Sprite | tuple[float, float] | None = actor.sprite()
            if isinstance(sprite, Sprite):
                pos = actor.pos()[0] - self.camera.view_x, actor.pos()[1] - self.camera.view_y

                if not sprite.blinking:
                    g2d.draw_image(src=sprite.path, pos=pos, clip_pos=sprite.pos, clip_size=sprite.size)
                else:  # blinking == True -> ogni 5 frame si alterna tra immagine diegnata e nulla. in caso pillow sia stato importato si alterna tra la immagine stessa e una versione con un filtro applicato
                    if Image is None or ImageEnhance is None or not isinstance(sprite.path, pathlib.Path):
                        # -> modalità senza pillow
                        if (self.__frame // 5) % 2 == 0:
                            g2d.draw_image(src=sprite.path, pos=pos, clip_pos=sprite.pos, clip_size=sprite.size)
                    else:
                        # -> modalità con pillow
                        if (self.__frame // 5) % 2 == 0:
                            g2d.draw_image(src=sprite.path, pos=pos, clip_pos=sprite.pos, clip_size=sprite.size)
                        else:
                            bright_path = getattr(sprite, "_bright_path", None)  # -> controllo dell'esistenza del bright_path (percorso che punta a un file immagine con un filtro gia applicato)
                            if bright_path is None:
                                path = str(sprite.path)
                                # -> preparazione del nuovo percorso dell'immagine col filtro applicato
                                if "." in path:
                                    bright_path = path.replace(".", "-bright.", 1)
                                else:
                                    bright_path = path + "-bright"

                                img = Image.open(path)  # -> apertura immagine corrente
                                enhancer = ImageEnhance.Brightness(img)  # -> creazione di un enhancer
                                img_bright = enhancer.enhance(3)  # -> applicazione del filtro
                                img_bright.save(bright_path)  # -> salvataggio della immagine nel nuovo percorso
                                sprite._bright_path = bright_path  # -> creazione di un attributo in sprite da usare per evitare di riapplicare il filtro e salvare ogni volta

                            g2d.draw_image(src=bright_path, pos=pos, clip_pos=sprite.pos, clip_size=sprite.size)

            if hasattr(actor, "gui"):  # -> ottengo eventuali elementi di interfaccia grafica appartenenti agli attori da renderizzare
                self.__gui_actors_components.extend(actor.gui)

    def render_guis(self, clear_canvas: bool | None = None):
        """Renderizza tutti i componenti di interfaccia grafica presenti.

        Gestisce opzionalmente la pulizia del canvas in base al parametro
        clear_canvas e alla proprieta clear_canvas.

        Disegna sia i componenti contenuti nella lista gui della interfaccia
        sia quelli raccolti dagli attori in __gui_actors_components.

        Per ogni componente:
        - ottiene le informazioni di disegno tramite render_info
        - adatta eventualmente le coordinate in base alla camera se il
          componente non è fissato alla finestra (fixed == False)
        - imposta il colore desiderato
        - disegna rettangoli o testo a seconda del tipo specificato nelle
          informazioni (rect o text)
        """

        if clear_canvas is None and self.clear_canvas:
            g2d.clear_canvas()
        elif clear_canvas:
            g2d.clear_canvas()

        # -> rendering di tutti gli elementi grafici (appartenenti agli attori o no)
        for gui_component in self.gui + self.__gui_actors_components:
            info = gui_component.render_info()  #type: ignore # -> ottengo le informazioni necessarie per disegnere un componente grafico
            for item in info:  # ogni componente grafico puo essere composto da piu figure da disegnare e sono possibili varie configurazioni e proprietà, quindi le estraggo
                type_ = item.get("type", None)
                color = item.get("color", None)
                text = item.get("text", None)
                pos = item.get("pos", None)
                center = item.get("center", None)
                size = item.get("size", None)
                font_size = item.get("font_size", None)

                if not gui_component.fixed:  # -> serve per stabilire se le coordinarte del componente grafico sono relative alla Camera o relative alla finestra vera e propria
                    if pos is not None: pos = pos[0] - self.camera.view_x, pos[1] - self.camera.view_y
                    if center is not None: center = center[0] - self.camera.view_x, center[1] - self.camera.view_y

                if color is not None: g2d.set_color(color)

                if (  # -> condizioni necessarie per disegnare un oggetto di tipo "rect"
                        type_ == "rect" and
                        pos is not None and
                        size is not None
                ):
                    g2d.draw_rect(pos=pos, size=size)
                elif (  # -> condizioni necessarie per disegnare un oggetto di tipo "text"
                        type_ == "text" and
                        text is not None and
                        center is not None and
                        font_size is not None
                ):
                    g2d.draw_text(text=text, center=center, size=font_size)

    def render_background(self, bg: Sprite | Color | tuple[int, int, int] | tuple[int, int, int, int] | None = None) -> bool:
        """Gestisce il rendering dello sfondo della interfaccia.

        Se bg non è specificato usa lo sfondo predefinito della interfaccia,
        cioe lattributo background.

        Comportamento in base al tipo di bg:
        - Sprite: disegna lo sprite come sfondo, ritagliandolo in base alla
          posizione e alla dimensione della camera
        - tupla di componenti di colore: converte la tupla in un oggetto Color
          e pulisce il canvas con quel colore
        - Color: pulisce il canvas con il colore specificato

        Restituisce True se uno sfondo viene effettivamente applicato,
        False altrimenti.
        """

        if bg is None:
            bg = self.background

        if isinstance(bg, Sprite):
            pos = bg.pos[0] + self.camera.view_x, bg.pos[1] + self.camera.view_y
            size = self.camera.size
            g2d.draw_image(src=bg.path, pos=(0, 0), clip_pos=pos, clip_size=size)
            return True
        elif isinstance(bg, tuple):
            bg = Color(bg)

        if isinstance(bg, Color):
            g2d.clear_canvas(bg.rgba)  #type: ignore
            return True

        return False

    # ======== SET METHODS ========
    def add_gui_component(self, gui_component: GUIComponent) -> "GraphicalInterface":
        if not isinstance(gui_component, GUIComponent):
            raise TypeError("gui_component must be of type GUIComponent")
        self.gui.append(gui_component)
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

        if self.gui is None:
            self.gui = [gui_component]
        else:
            self.gui.insert(index, gui_component)

        return self
