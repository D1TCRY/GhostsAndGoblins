from __future__ import annotations

from g2d_lib import g2d
from actor import Actor

from Arthur import Arthur
from Platform import Platform
from Ladder import Ladder

from Camera import Camera
from guis import GUIComponent

from status import Sprite, Phase

from Game import Game
from GraphicalInterface import GraphicalInterface

import pathlib



CAMERA_WIDTH, CAMERA_HEIGHT = 430, 230




class App(object):
    def __init__(self) -> None:
        global CAMERA_WIDTH, CAMERA_HEIGHT
        
        self.app_phase = Phase.START_GAME
        self.size = (CAMERA_WIDTH, CAMERA_HEIGHT)

    
    # ======== PROPERTIES ========
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
        # === GAME ===
        # --- WORLD ---
        world_background: Sprite = Sprite(pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins-bg.png", 2, 10,
                                   3584, 240)

        # --- ACTORS ---
        spawn_queue: list[Actor] = list()
        # Player
        spawn_queue.append(Arthur(name="Player", x=50, y=50))
        # Wall left
        spawn_queue.extend([
            Platform(x=-10, y=0, width=10, height=round(self.size[1]), damage=0)
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
        ])
        # Floating Platforms
        spawn_queue.extend([
            Platform(x=610 - 2, y=122 - 10, width=111, height=18, damage=0, name="FloatingPlatform 1"),
        ])

        self.game: Game = Game(world_background.size, background=world_background, spawn_queue=spawn_queue)


        # === GRAPHICAL INTERFACE ===
        camera = Camera(view_x=0, view_y=0, width=CAMERA_WIDTH, height=CAMERA_HEIGHT, target=self.game.player)

        gui_components: list[GUIComponent] = list()

        self.gui: GraphicalInterface = GraphicalInterface(camera=camera, gui_components=gui_components)

        self.app_phase = Phase.PLAYING


    def play_game(self) -> None:
        if not (hasattr(self, "game") and hasattr(self, "gui")):
            self.app_phase = Phase.MENU
            return

        self.game.tick(keys=g2d.current_keys())
        self.gui.render(self.game)

    def tick(self) -> None:
        if self.app_phase == Phase.START_GAME:
            g2d.clear_canvas()
            self.load_game()
        elif self.app_phase == Phase.PLAYING:
            g2d.clear_canvas()
            self.play_game()
        elif self.app_phase == Phase.END_GAME:
            g2d.set_color((0, 0, 0, 1)) # type: ignore
            g2d.draw_rect(pos=(0, 0), size=(self.size[0], self.size[1]))

            g2d.set_color((96, 0, 0))
            g2d.draw_text(text="GAME OVER", center=(self.size[0]/2, self.size[1]/2), size=50)


def main() -> None:
    global CAMERA_WIDTH, CAMERA_HEIGHT
    app = App()
    
    g2d.init_canvas(size=(CAMERA_WIDTH, CAMERA_HEIGHT), scale=2)
    g2d.main_loop(tick=app.tick, fps=30)


if __name__ == "__main__":
    main()
