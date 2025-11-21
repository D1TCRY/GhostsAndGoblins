from __future__ import annotations
import pathlib
from collections.abc import Callable

# G2D
from src.g2d_lib import g2d

# CORE
from .camera import Camera
from .game import Game
from .graphical_interface import GraphicalInterface, init_canvas
from .file_management import read_settings
from .menu_manager import MenuManager

# ENTITIES
from ..entities import Actor, Platform, Ladder, GraveStone, Arthur, Door

# GUI
from ..gui import GUIComponent

# STATE
from ..state import Sprite, Phase, Direction


settings = read_settings()
CAMERA_WIDTH, CAMERA_HEIGHT = settings.get("camera_width", 430), settings.get("camera_height", 230)
SCALE = settings.get("scale", 1)
FPS = settings.get("fps", 30)


class App(object):
    def __init__(self,
                 get_keys_from: Callable[[], list[str]],
                 get_mouse_pos_from: Callable[[], tuple[float | int, float | int]]) -> None:
        global CAMERA_WIDTH, CAMERA_HEIGHT

        self.get_keys_from = get_keys_from
        self.get_mouse_pos_from = get_mouse_pos_from

        self.app_phase = Phase.MENU
        self.size = (CAMERA_WIDTH, CAMERA_HEIGHT)
        self.menu = MenuManager(master=self)


    
    # ======== PROPERTIES ========
    @property
    def get_keys_from(self) -> Callable[[], list[str]]:
        return self.__get_keys_from
    @get_keys_from.setter
    def get_keys_from(self, value: Callable[[], list[str]]) -> None:
        if not callable(value):
            raise TypeError("get_keys_from must be a callable")
        self.__get_keys_from: Callable[[], list[str]] = value

    @property
    def get_mouse_pos_from(self) -> Callable[[], tuple[float | int, float | int]]:
        return self.__get_mouse_pos_from
    @get_mouse_pos_from.setter
    def get_mouse_pos_from(self, value: Callable[[], tuple[float | int, float | int]]) -> None:
        if not callable(value):
            raise TypeError("get_mouse_pos_from must be a callable")
        self.__get_mouse_pos_from: Callable[[], tuple[float | int, float | int]] = value

    @property
    def keys(self) -> list[str]:
        return self.get_keys_from()

    @property
    def mouse_pos(self) -> tuple[float | int, float | int]:
        return self.get_mouse_pos_from()

    @property
    def size(self) -> tuple[int, int]:
        return self.__size
    @size.setter
    def size(self, value: tuple[int, int]) -> None:
        if not isinstance(value, tuple) or len(value) != 2:
            raise TypeError("size must be a tuple of length 2")
        self.__size: tuple[int, int] = value

    @property
    def app_phase(self) -> Phase:
        return self.__app_status
    @app_phase.setter
    def app_phase(self, new: Phase) -> None:
        self.__app_status = new
    
    
    # ======= METHODS ========
    def load_game(self) -> None:
        """Inizializza una nuova partita creando istanze di Game
        e GraphicalInterface.

        ### Game:
        Definisce lo sfondo di gioco e le dimensioni dell'arena,
        gli attori che popolano il mondo e ne conferiscono coerenza e
        struttura (come Platform, Gravestone, Arthur, ...)

        ### GraphicalInterface:
        Definisce la 'Camera' e i componenti GUI da mostrare sulla schermata,
        questo è l'oggetto che gestisce completamente e autonomamente il rendering
        grafico dell'applicazione.

        Infine imposta l'attributo app_phase su PLAYING.
        """

        # === GAME ===
        # --- WORLD ---
        world_background: Sprite = Sprite(pathlib.Path(__file__).parent.parent.parent / "data" / "textures" / "ghosts-goblins-bg.png", 2, 10,
                                   3584, 240)

        # --- ACTORS ---
        spawn_queue: list[Actor] = list()
        # player
        spawn_queue.append(Arthur(name="player", x=50, y=50))
        # Wall left
        spawn_queue.extend([
            Platform(x=-10, y=0, width=10, height=round(self.size[1]), damage=0, contact_surfaces=[Direction.LEFT, Direction.RIGHT, Direction.DOWN], name="Wall Left"),
        ])
        # Wall right
        spawn_queue.extend([
            Platform(x=world_background.size[0], y=0, width=10, height=round(self.size[1]), damage=0,
                     contact_surfaces=[Direction.LEFT, Direction.RIGHT, Direction.DOWN], name="Wall Left"),
        ])
        # Ground
        spawn_queue.extend([
            Platform(x=2 - 2, y=202 - 10, width=1664, height=48, damage=0, name="Ground 1"),
            Platform(x=1794 - 2, y=202 - 10, width=160, height=48, damage=0, name="Ground 2"),
            Platform(x=1986 - 2, y=202 - 10, width=32, height=48, damage=0, name="Ground 3"),
            Platform(x=2050 - 2, y=202 - 10, width=400, height=48, damage=0, name="Ground 4"),
            Platform(x=2482 - 2, y=202 - 10, width=224, height=48, damage=0, name="Ground 5"),
            Platform(x=2738 - 2, y=202 - 10, width=848, height=48, damage=0, name="Ground 6"),
        ])
        # Water
        spawn_queue.extend([
            Platform(x=1666 - 2, y=218 - 10, width=128, height=32, damage=16, contact_surfaces=None, name="Water 1"),
            Platform(x=1954 - 2, y=218 - 10, width=32, height=32, damage=16, contact_surfaces=None, name="Water 2"),
            Platform(x=2018 - 2, y=218 - 10, width=32, height=32, damage=16, contact_surfaces=None, name="Water 3"),
            Platform(x=2450 - 2, y=218 - 10, width=32, height=32, damage=16, contact_surfaces=None, name="Water 4"),
            Platform(x=2706 - 2, y=218 - 10, width=32, height=32, damage=16, contact_surfaces=None, name="Water 5"),
        ])
        # Ladders
        spawn_queue.extend([
            Ladder(x=721 - 2, y=122 - 10, width=18, height=80, damage=0, contact_surfaces=None, name="Ladder 1"),
            Ladder(x=913 - 2, y=122 - 10, width=18, height=80, damage=0, contact_surfaces=None, name="Ladder 2"),
            Ladder(x=1073 - 2, y=122 - 10, width=18, height=80, damage=0, contact_surfaces=None, name="Ladder 3"),
        ])
        # Floating Platforms
        spawn_queue.extend([
            Platform(x=610 - 2, y=122 - 10, width=111 - 3, height=12, damage=0, name="FloatingPlatform 1"),
            Platform(x=739 - 2 + 3, y=122 - 10, width=174 - 3 - 3, height=12, damage=0, name="FloatingPlatform 2"),
            Platform(x=931 - 2 + 3, y=122 - 10, width=142 - 3 - 3, height=12, damage=0, name="FloatingPlatform 3"),
            Platform(x=1091 - 2 + 3, y=122 - 10, width=30 - 3, height=12, damage=0, name="FloatingPlatform 4"),
        ])
        # Gravestones
        spawn_queue.extend([
            GraveStone(x=50-2, y=186-10, width=16, height=16, damage=0, name="GraveStone 1"),
            GraveStone(x=242-2, y=186-10, width=16, height=16, damage=0, name="GraveStone 2"),
            GraveStone(x=530-2, y=186-10, width=16, height=16, damage=0, name="GraveStone 3"),
            GraveStone(x=754-2, y=186-10, width=16, height=16, damage=0, name="GraveStone 4"),
            GraveStone(x=962-2, y=186-10, width=16, height=16, damage=0, name="GraveStone 5"),
            GraveStone(x=1106-2, y=186-10, width=16, height=16, damage=0, name="GraveStone 6"),
            GraveStone(x=1522-2, y=186-10, width=16, height=16, damage=0, name="GraveStone 7"),
            GraveStone(x=866-2, y=106-10, width=16, height=16, damage=0, name="GraveStone 8"),
        ])
        spawn_queue.extend([
            GraveStone(x=418 - 2, y=188 - 10, width=17, height=14, damage=0, name="GraveStone 9"),
            GraveStone(x=770 - 2, y=108 - 10, width=17, height=14, damage=0, name="GraveStone 10"),
            GraveStone(x=962 - 2, y=108 - 10, width=17, height=14, damage=0, name="GraveStone 11"),
            GraveStone(x=1266 - 2, y=188 - 10, width=17, height=14, damage=0, name="GraveStone 12"),
        ])

        # Door
        spawn_queue.extend([
            Door(x=3458-2, y=138-10, width=48, height=64, name="Door")
        ])


        self.game: Game = Game(world_background.size, background=world_background, spawn_queue=spawn_queue)


        # === GRAPHICAL INTERFACE ===
        camera = Camera(view_x=0, view_y=0, width=CAMERA_WIDTH, height=CAMERA_HEIGHT, target=self.game.player)

        gui_components: list[GUIComponent] = list()

        self.gui: GraphicalInterface = GraphicalInterface(camera=camera, gui_components=gui_components)

        self.app_phase = Phase.PLAYING


    def play_game(self, keys: list[str]) -> None:
        """Gestisce un singolo aggiornamento della partita in corso.

        ### Input
        Legge i tasti correnti da g2d e, se è premuto Escape, ritorna al menu
        principale impostando app_phase su MENU e interrompendo l'aggiornamento
        della partita.

        ### Logica di gioco
        Verifica che gli attributi game e gui siano stati correttamente
        inizializzati; in caso contrario riporta l'applicazione al menu.
        Controlla inoltre se la partita è terminata con vittoria o sconfitta
        e aggiorna di conseguenza app_phase (GAME_WON o GAME_OVER).

        ### Rendering
        Delegando a Game l'aggiornamento della logica di gioco (metodo tick)
        e a GraphicalInterface il rendering, produce il frame corrente della
        partita da mostrare a schermo.
        """

        if "Escape" in keys:
            self.menu.set_home()
            self.app_phase = Phase.MENU
            return

        if not (hasattr(self, "game") and hasattr(self, "gui")):
            self.app_phase = Phase.MENU
            return

        if self.game.game_over:
            self.app_phase = Phase.GAME_OVER

        if self.game.game_won:
            self.app_phase = Phase.GAME_WON

        self.game.tick(keys=keys)
        self.gui.render(self.game)


    def load_menu(self, keys: list[str], pos: tuple[float, float]) -> None:
        """Gestisce l'aggiornamento del menu principale per il frame corrente.

        ### Input
        Legge i tasti correnti e la posizione del cursore del mouse tramite g2d.

        ### MenuManager
        Passa i dati di input al MenuManager, che si occupa di aggiornare lo stato
        del menu, la selezione delle voci e le eventuali transizioni di schermata.
        """

        self.menu.tick(keys=keys, cursor_pos=pos)

    def tick(self) -> None:
        """Metodo principale richiamato a ogni frame dal ciclo di gioco.

        In base al valore di app_phase smista la logica dell applicazione alla
        fase corretta, passando alle funzioni i dati necessari.

        ### Fasi gestite
        - MENU: richiama load_menu passando i tasti correnti e la posizione
          del mouse per aggiornare lo stato del menu.
        - START_GAME: inizializza una nuova partita tramite load_game.
        - PLAYING: aggiorna la partita in corso tramite play_game, passando
          i tasti correnti.
        - GAME_WON e GAME_OVER: aggiorna il menu con la schermata di vittoria
          o di sconfitta e riporta app_phase a MENU.
        - END_GAME: ripristina il menu alla schermata principale e imposta
          app_phase su MENU.
        - QUIT: termina l'applicazione chiudendo il programma.

        Per qualsiasi altro valore non valido di app_phase, reimposta la fase
        corrente a MENU come comportamento predefinito.
        """

        match self.app_phase:
            case Phase.MENU:
                self.load_menu(self.keys, self.mouse_pos)
            case Phase.START_GAME:
                self.load_game()
            case Phase.PLAYING:
                self.play_game(self.keys)
            case Phase.GAME_WON:
                self.menu.set_game_won()
                self.app_phase = Phase.MENU
            case Phase.GAME_OVER:
                self.menu.set_game_over()
                self.app_phase = Phase.MENU
            case Phase.END_GAME:
                self.menu.set_home()
                self.app_phase = Phase.MENU
            case Phase.QUIT:
                exit()
            case _:
                self.app_phase = Phase.MENU


def main() -> None:
    global CAMERA_WIDTH, CAMERA_HEIGHT, SCALE, FPS
    app = App(get_keys_from=g2d.current_keys, get_mouse_pos_from=g2d.mouse_pos)

    init_canvas(tick=app.tick, size=(CAMERA_WIDTH, CAMERA_HEIGHT), scale=SCALE, fps=FPS)

