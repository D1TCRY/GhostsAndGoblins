#!/usr/bin/env python3
import unittest
from unittest.mock import Mock, patch

from src.game.core import GraphicalInterface, Camera
from src.game.gui import GUIComponent  # -> solo per creare Dummy


class DummyGUI(GUIComponent):
    """GUI finta per i test."""

    def __init__(self, fixed=True, info=None):
        self._fixed = fixed
        self._info = info or []

    @property
    def name_id(self):
        return "dummy"
    @name_id.setter
    def name_id(self, value) -> None:
        pass

    @property
    def fixed(self):
        return self._fixed
    @fixed.setter
    def fixed(self, value) -> None:
        self._fixed = value

    def render_info(self):
        return self._info


class GraphicalInterfaceTest(unittest.TestCase):

    def setUp(self):
        self.camera = Camera(0, 0, 320, 240)
        self.gui = GraphicalInterface(self.camera)

    # ======== INIT E PROPRIETÀ ========

    def test_init_with_none_camera_creates_default_camera(self):
        """Se passo camera=None, deve crearne una di default."""
        gi = GraphicalInterface(None)
        self.assertIsNotNone(gi.camera)
        self.assertIsInstance(gi.camera, Camera)
        self.assertEqual(gi.gui, [])
        self.assertIsNone(gi.background)

    def test_camera_type_error(self):
        """camera deve essere Camera o None."""
        with self.assertRaises(TypeError):
            self.gui.camera = 123

    def test_gui_type_error(self):
        """gui deve essere list o None."""
        with self.assertRaises(TypeError):
            self.gui.gui = "non-una-list"

    def test_background_type_error(self):
        """background deve essere Sprite, Color o None"""
        with self.assertRaises(TypeError):
            self.gui.background = 123

    # ======== METHODS ========
    def test_add_gui_component_adds_to_list(self):
        comp = DummyGUI()
        self.assertEqual(self.gui.gui, [])  # lista iniziale

        self.gui.add_gui_component(comp)
        self.assertIn(comp, self.gui.gui)

    def test_add_gui_component_type_error(self):
        with self.assertRaises(TypeError):
            self.gui.add_gui_component(123) # type: ignore

    def test_remove_gui_component(self):
        comp1 = DummyGUI()
        comp2 = DummyGUI()
        self.gui.gui = [comp1, comp2]

        self.gui.remove_gui_component(comp1)
        self.assertNotIn(comp1, self.gui.gui)
        self.assertIn(comp2, self.gui.gui)

    def test_remove_gui_component_type_error(self):
        with self.assertRaises(TypeError):
            self.gui.remove_gui_component("abc") # type: ignore

    def test_insert_gui_component(self):
        comp1 = DummyGUI()
        comp2 = DummyGUI()
        comp3 = DummyGUI()
        self.gui.gui = [comp1, comp3]

        self.gui.insert_gui_component(1, comp2)
        self.assertEqual(self.gui.gui, [comp1, comp2, comp3])

    def test_insert_gui_component_type_error(self):
        with self.assertRaises(TypeError):
            self.gui.insert_gui_component(0, 42) # type: ignore

    # ======== RENDER BACKGROUND ========
    def test_render_background_with_tuple_color(self):
        """Se passo un colore (r,g,b) deve chiamare clear_canvas e restituire True."""
        gi = GraphicalInterface(self.camera)

        with patch("src.g2d_lib.g2d.clear_canvas") as mock_clear:
            result = gi.render_background((0, 0, 0))

        mock_clear.assert_called_once()
        self.assertTrue(result)

    def test_render_background_returns_false_with_none_and_no_background(self):
        """Se non ha background e passo None, deve restituire False."""
        gi = GraphicalInterface(self.camera, background=None)

        result = gi.render_background(None)
        self.assertFalse(result)

    # ======== RENDER SPRITES ========
    def test_render_sprites_collects_gui_components_from_actors(self):
        """I componenti gui degli actor (quindi con attributo 'gui') devono finire in __gui_actors_components."""
        gi = GraphicalInterface(self.camera)

        # gioco finto
        game = Mock()
        game.background = None

        actor1 = Mock()
        actor1.sprite.return_value = None
        actor1.gui = [DummyGUI(), DummyGUI()]

        actor2 = Mock()
        actor2.sprite.return_value = None
        actor2.gui = [DummyGUI()]

        game.actors.return_value = [actor1, actor2]

        # patcho clear_canvas E draw_image perché non sono rilevanti qui
        with patch("src.g2d_lib.g2d.clear_canvas"), \
                patch("src.g2d_lib.g2d.draw_image", return_value=None):
            gi.render_sprites(game)

        gui_comps = gi._GraphicalInterface__gui_actors_components  # type: ignore
        self.assertEqual(len(gui_comps), 3)

    # ======== RENDER GUIS ========
    def test_render_guis_draws_rect(self):
        """Un GUIComponent che ritorna un 'rect' deve chiamare draw_rect."""
        info = [{
            "type": "rect",
            "color": (255, 0, 0),
            "pos": (1, 2),
            "size": (3, 4),
        }]
        comp = DummyGUI(fixed=True, info=info)
        self.gui.gui = [comp]
        self.gui._GraphicalInterface__gui_actors_components = []  # type: ignore

        with patch("src.g2d_lib.g2d.clear_canvas"), \
                patch("src.g2d_lib.g2d.set_color") as mock_color, \
                patch("src.g2d_lib.g2d.draw_rect") as mock_rect, \
                patch("src.g2d_lib.g2d.draw_text") as mock_text:
            self.gui.render_guis()

        mock_color.assert_called_once_with((255, 0, 0))
        mock_rect.assert_called_once_with(pos=(1, 2), size=(3, 4))
        mock_text.assert_not_called()

    def test_render_guis_draws_text(self):
        """Un GUIComponent che ritorna un 'text' deve chiamare draw_text."""
        info = [{
            "type": "text",
            "color": (0, 255, 0),
            "text": "Testing",
            "center": (100, 50),
            "font_size": 16,
        }]
        comp = DummyGUI(fixed=True, info=info)
        self.gui.gui = [comp]
        self.gui._GraphicalInterface__gui_actors_components = []  # type: ignore

        with patch("src.g2d_lib.g2d.clear_canvas"), \
                patch("src.g2d_lib.g2d.set_color") as mock_color, \
                patch("src.g2d_lib.g2d.draw_rect") as mock_rect, \
                patch("src.g2d_lib.g2d.draw_text") as mock_text:
            self.gui.render_guis()

        mock_color.assert_called_once_with((0, 255, 0))
        mock_text.assert_called_once_with(text="Testing", center=(100, 50), size=16)
        mock_rect.assert_not_called()


    # ======== RENDER ========
    def test_render_calls_camera_and_subrenders(self):
        """render deve chiamare camera.tick, render_background, render_sprites e render_guis."""
        gi = GraphicalInterface(self.camera)
        game = Mock()

        gi.camera.tick = Mock()

        with patch("src.g2d_lib.g2d.clear_canvas"), \
                patch.object(gi, "render_background") as mock_bg, \
                patch.object(gi, "render_sprites") as mock_spr, \
                patch.object(gi, "render_guis") as mock_gui:
            gi.render(game)

        gi.camera.tick.assert_called_once_with(game)
        mock_bg.assert_called_once()
        mock_spr.assert_called_once_with(game, clear_canvas=False)  # <-- QUI
        mock_gui.assert_called_once()


if __name__ == "__main__":
    unittest.main()
