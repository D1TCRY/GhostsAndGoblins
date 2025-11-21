import pathlib
from typing import TYPE_CHECKING

# STATE
from ..state.states import MenuPhase, Phase
from ..state import Sprite

# CORE
if TYPE_CHECKING: from .app import App, CAMERA_WIDTH, CAMERA_HEIGHT
from .file_management import read_settings
from .graphical_interface import GraphicalInterface

# GUI
from ..gui import Button, Color, Text


settings = read_settings()
CAMERA_WIDTH, CAMERA_HEIGHT = settings.get("camera_width", 430), settings.get("camera_height", 230)
SCALE = settings.get("scale", 1)

BUTTON_WIDTH, BUTTON_HEIGHT = 100, 30


class MenuManager:
    def __init__(self, master) -> None:
        """Inizializza il MenuManager e le grafiche usate.

        Collega il master, cioe l'istanza principale di App, e imposta la
        fase iniziale del menu su MenuPhase.MAIN.

        Inizializza inoltre il dizionario interno _graphics, che associa
        ad ogni valore di MenuPhase una istanza di GraphicalInterface:
        - MenuPhase.MAIN: crea un interfaccia con sfondo del menu
          principale e due pulsanti: Play (avvia il gioco) e Quit (chiude
          l'applicazione)
        - MenuPhase.GAME_WON, MenuPhase.GAME_OVER: crea due interfacce
          molto semplici con uno sfondo scuro e un testo centrale che mostra
          rispettivamente GAME WON o GAME OVER

        Ogni GraphicalInterface si occupa di:
        - disegnare lo sfondo, che puo essere uno Sprite o un colore
        - gestire e disegnare i componenti grafici di interfaccia (Text,
          Button e altri eventuali GUIComponent)

        Infine inizializza count_down, un contatore di frame usato per
        determinare per quanto tempo rimangono visibili le schermate di
        vittoria e di game over prima di tornare automaticamente al menu
        principale.
        """

        self.master = master
        self.phase = MenuPhase.MAIN
        self._graphics: dict[MenuPhase, GraphicalInterface] = {
            MenuPhase.MAIN: GraphicalInterface(
                clear_canvas=False,
                camera=None,
                background=Sprite(pathlib.Path(__file__).parents[2] / "data" / "textures" / "main-menu-bg-430.png", 0, 0, 430, 230),
                gui_components=[
                    Text(
                        x=CAMERA_WIDTH/2,
                        y=CAMERA_HEIGHT - 10,
                        text="< 386276 | Cecchelani Diego >",
                        text_size=10,
                        text_color=(150, 150, 150),
                    ),
                    Button(
                        x=CAMERA_WIDTH/2 - BUTTON_WIDTH/2,
                        y=CAMERA_HEIGHT/2 - BUTTON_HEIGHT/2,
                        width=BUTTON_WIDTH,
                        height=BUTTON_HEIGHT,
                        text="Play",
                        text_size=15,
                        text_color=Color(248, 248, 248),
                        background_color=Color(48, 48, 64, 192),
                        hover_color=Color(208, 176, 48, 128),
                        pressed_color=Color(240, 208, 216, 64),
                        command=self.start_game,
                        activate_keys=["LeftButton"]
                    ),
                    Button(
                        x=CAMERA_WIDTH / 2 - BUTTON_WIDTH / 2,
                        y=CAMERA_HEIGHT / 2 + BUTTON_HEIGHT / 2 + 5,
                        width=BUTTON_WIDTH,
                        height=BUTTON_HEIGHT,
                        text="Quit",
                        text_size=15,
                        text_color=Color(248, 248, 248),
                        background_color=Color(48, 48, 64, 192),
                        hover_color=Color(48, 48, 192, 128),
                        pressed_color=Color(48, 64, 224, 64),
                        command=self.quit,
                        activate_keys=["LeftButton"]
                    )
                ]
            ),
            MenuPhase.GAME_WON: GraphicalInterface(
                clear_canvas=False,
                camera=None,
                background=Color(0,0,0,2),
                gui_components=[
                    Text(
                        x=CAMERA_WIDTH/2,
                        y=CAMERA_HEIGHT/2,
                        text="GAME WON",
                        text_size=50,
                        text_color=(16, 248, 16),
                    )
                ]
            ),
            MenuPhase.GAME_OVER: GraphicalInterface(
                clear_canvas=False,
                camera=None,
                background=Color(0,0,0,2),
                gui_components=[
                    Text(
                        x=CAMERA_WIDTH/2,
                        y=CAMERA_HEIGHT/2,
                        text="GAME OVER",
                        text_size=50,
                        text_color=(248, 16, 16),
                    )
                ]
            )
        }

        self.count_down = 0

    def start_game(self) -> None:
        self.master.app_phase = Phase.START_GAME

    def quit(self) -> None:
        self.master.app_phase = Phase.QUIT

    def tick(self, keys: list[str], cursor_pos: tuple[float, float]) -> None:
        """Aggiorna lo stato del menu per il frame corrente.

        Riceve in ingresso:
        - keys: la lista dei tasti correnti premuti
        - cursor_pos: la posizione attuale del cursore del mouse

        Se la fase corrente è GAME_WON o GAME_OVER, decrementa il contatore
        count_down; quando il contatore arriva a zero richiama set_home e
        torna al menu principale interrompendo il resto dell aggiornamento.

        Se la fase è ancora attiva:
        - recupera la GraphicalInterface associata alla fase corrente dal
          dizionario _graphics
        - per ogni componente della interfaccia che è un Button, richiama
          il suo metodo tick passando keys e cursor_pos, in modo da gestire
          hover, pressione ed eventuale esecuzione del comando associato
        - chiede poi alla GraphicalInterface di disegnare lo sfondo
          (render_background) e tutti i componenti grafici di interfaccia
          (render_guis) per produrre il frame del menu da mostrare a schermo
        """

        if self.phase in (MenuPhase.GAME_WON, MenuPhase.GAME_OVER):
            self.count_down -= 1

        if self.count_down <= 0:
            self.set_home()
            return

        gi: GraphicalInterface = self._graphics[self.phase]

        for component in gi.gui:
            if isinstance(component, Button):
                component.tick(keys, cursor_pos)

        gi.render_background()
        gi.render_guis()

    def set_home(self) -> None:
        self.phase = MenuPhase.MAIN
        self.count_down = 1

    def set_game_won(self) -> None:
        self.phase = MenuPhase.GAME_WON
        self.count_down = 90

    def set_game_over(self) -> None:
        self.phase = MenuPhase.GAME_OVER
        self.count_down = 90

    @property
    def master(self) -> "App":
        return self.__master
    @master.setter
    def master(self, value: "App"):
        self.__master: "App" = value


    @property
    def phase(self) -> MenuPhase:
        return self.__phase
    @phase.setter
    def phase(self, value: MenuPhase) -> None:
        if not isinstance(value, MenuPhase):
            raise TypeError("phase must be a MenuPhase")
        self.__phase = value

    @property
    def count_down(self) -> int:
        return self.__count_down
    @count_down.setter
    def count_down(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("count_down must be an int")
        self.__count_down = max(0, value)