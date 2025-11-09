from __future__ import annotations
import random

from g2d_lib import g2d
from actor import Arena, Actor

from Arthur import Arthur
from Zombie import Zombie
from Platform import Platform
from Ladder import Ladder
from Torch import Torch
from Flame import Flame

from Camera import Camera
from src.guis import GUIComponent

from status import Sprite, Phase
from guis import Bar, GUI

from Game import Game
from GraphicalInterface import GraphicalInterface

import pathlib


SPR_WORLD: Sprite = Sprite(pathlib.Path(__file__).parent / "data" / "textures" / "ghosts-goblins-bg.png", 2, 10, 3584, 240)
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
        
    @property
    def arena(self) -> Arena:
        return self.__arena
    @arena.setter
    def arena(self, new: Arena) -> None:
        if not isinstance(new, Arena):
            raise TypeError("arena must be an instance of Arena")
        self.__arena: Arena = new

    @property
    def player(self) -> Arthur:
        return self.__player
    @player.setter
    def player(self, new: Arthur) -> None:
        if not isinstance(new, Arthur):
            raise TypeError("player must be an instance of Arthur")
        self.__player: Arthur = new
    
    @property
    def camera(self) -> Camera:
        return self.__camera
    @camera.setter
    def camera(self, new: Camera) -> None:
        if not isinstance(new, Camera):
            raise TypeError("camera must be of type Camera")
        self.__camera: Camera = new
    
    
    # ======= METHODS ========
    def load_game2(self) -> None:
        global SPR_WORLD, CAMERA_WIDTH, CAMERA_HEIGHT
        self.camera = Camera(view_x=0, view_y=0, width=CAMERA_WIDTH, height=CAMERA_HEIGHT)
        self.arena = Arena(SPR_WORLD.size)
        self.arena.set_sprite(SPR_WORLD)
        self.player = Arthur(name="Player", x=50, y=50, speed=5)

        # --- ACTORS ---
        spawn_queue: list[Actor] = list()
        # Wall left
        spawn_queue.append(Platform(x=-10, y=0, width=10, height=round(self.arena.size()[1]), damage=0))
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
            Ladder(x=721-2, y=122-10, width=18, height=80, damage=0, contact_surfaces=None, name="Ladder 1"),
        ])
        # Floating Platforms
        spawn_queue.extend([
            Platform(x=610-2, y=122-10, width=111, height=18, damage=0, name="FloatingPlatform 1"),
        ])



        # --- ACTOR SPAWNS ---
        self.arena.spawn(self.player)
        for actor in spawn_queue:
            self.arena.spawn(actor)

        # --- GUI ---
        self.GUI = GUI(g2d=g2d)
        health_bar: Bar = Bar(g2d=g2d, name_id="health_bar", x=3, y=3, padding=1, text="Health: {value}", max_value=100, value=100)
        self.GUI.add(health_bar)

        self.camera.target = self.player
        self.app_phase = Phase.PLAYING

    def load_game(self) -> None:
        global CAMERA_WIDTH, CAMERA_HEIGHT

        # === GAME ===
        # --- ACTORS ---
        spawn_queue: list[Actor] = list()
        # Player
        spawn_queue.append(Arthur(name="Player", x=50, y=50))
        # Wall left
        spawn_queue.extend([
            Platform(x=-10, y=0, width=10, height=round(self.arena.size()[1]), damage=0)
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

        self.game: Game = Game(self.size, spawn_queue=spawn_queue)


        # === GRAPHICAL INTERFACE ===
        camera = Camera(view_x=0, view_y=0, width=CAMERA_WIDTH, height=CAMERA_HEIGHT)

        gui_components: list[GUIComponent] = list()

        gui_components.extend([
            Bar(g2d=g2d, name_id="health_bar", x=3, y=3, padding=1, text="Health: {value}", max_value=100, value=self.game.player.get_health_value)
        ])

        self.gui: GraphicalInterface = GraphicalInterface(camera, init_gui_components=gui_components)

        self.app_phase = Phase.PLAYING

    def render_game2(self) -> None:
        view_x, view_y = self.camera.pos
        world_sprite = self.arena.sprite()

        # --- END GAME ---
        if (not self.player.inside_arena(self.arena)) or self.player.health <= 0:
            self.player.health = 0
            self.arena.kill(self.player)
            self.app_phase = Phase.END_GAME

        # --- TICKS ---
        self.arena.tick(g2d.current_keys())
        self.camera.tick(self.arena)

        # --- WORLD ---
        g2d.draw_image(src=str(world_sprite.path), pos=(0, 0),
                       clip_pos=(view_x + world_sprite.x, view_y + world_sprite.y), clip_size=world_sprite.size)

        # --- ZOMBIES ---
        if random.randint(0, 100) == 0:
            self.arena.spawn(Zombie.auto_init(player=self.player, arena=self.arena))

        # --- OTHER ACTORS ---
        for actor in self.arena.actors():
            if isinstance(actor, Platform):
                platform = actor

                # Draw platform
                #g2d.set_color((random.randrange(256), random.randrange(256), random.randrange(256)))
                #g2d.draw_rect(pos=(actor.x - view_x, actor.y - view_y), size=actor.size())

                if platform.check_collision(self.player):
                    self.player.health -= platform.damage
            elif isinstance(actor, Zombie):
                zombie = actor
                sprite: Sprite | None = zombie.sprite()
                pos: tuple[float, float] = zombie.x - view_x, zombie.y - view_y
                if sprite is not None: g2d.draw_image(
                    src=sprite.path,
                    pos=pos,
                    clip_pos=sprite.pos,
                    clip_size=sprite.size
                )
            elif isinstance(actor, (Torch, Flame)):
                sprite = actor.sprite()
                if sprite is not None:
                    g2d.draw_image(
                        src=sprite.path,
                        pos=(actor.x - view_x, actor.y - view_y),
                        clip_pos=sprite.pos,
                        clip_size=sprite.size
                    )


        # --- PLAYER ---
        sprite: Sprite | None = self.player.sprite()
        pos: tuple[float, float] = self.player.x - view_x, self.player.y - view_y
        if sprite is not None: g2d.draw_image(
            src=sprite.path,
            pos=pos,
            clip_pos=sprite.pos,
            clip_size=sprite.size
        )

        # --- DRAW GUI ---
        if hasattr(self, "GUI"):
            self.GUI.draw(health_bar=self.player.health)


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
            self.render_game()
        elif self.app_phase == Phase.END_GAME:
            g2d.set_color((0, 0, 0, 1)) # type: ignore
            g2d.draw_rect(pos=(0, 0), size=(self.camera.width, self.camera.height))

            g2d.set_color((96, 0, 0))
            g2d.draw_text(text="GAME OVER", center=(self.camera.width/2, self.camera.height/2), size=50)


def main() -> None:
    global CAMERA_WIDTH, CAMERA_HEIGHT
    app = App()
    
    g2d.init_canvas(size=(CAMERA_WIDTH, CAMERA_HEIGHT), scale=2)
    g2d.main_loop(tick=app.tick, fps=30)


if __name__ == "__main__":
    main()
