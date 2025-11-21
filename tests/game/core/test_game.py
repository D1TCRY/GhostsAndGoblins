#!/usr/bin/env python3
import unittest
from unittest.mock import Mock, patch

from src.game.core import Game
from src.game.state import Phase, Direction


class GameTest(unittest.TestCase):
    def setUp(self):
        self.size = (320, 240)
        self.game = Game(self.size)

    # ======== INIT E PROPERTIES ========
    def test_init_default_state(self):
        """Game deve partire in fase PLAYING, senza background."""
        self.assertEqual(self.game.size(), self.size)
        self.assertEqual(self.game.game_phase, Phase.PLAYING)
        self.assertIsNone(self.game.background)

        self.assertIsInstance(self.game._collision_handlers, dict)
        self.assertIsInstance(self.game._collision_free_handlers, dict)

    def test_background_type_error(self):
        """background accetta solo Sprite or None"""
        with self.assertRaises(TypeError):
            self.game.background = 123

    def test_spawn_queue_type_error(self):
        """spawn_queue deve essere list or None."""
        with self.assertRaises(TypeError):
            self.game.spawn_queue = "non-una-list"

    def test_game_phase_type_error(self):
        """game_phase deve essere un Phase."""
        with self.assertRaises(TypeError):
            self.game.game_phase = "GAME_OVER"

    def test_collision_handlers_type_error(self):
        """_collision_handlers deve essere un dict."""
        with self.assertRaises(TypeError):
            self.game._collision_handlers = []

    def test_collision_free_handlers_type_error(self):
        """_collision_free_handlers deve essere un dict."""
        with self.assertRaises(TypeError):
            self.game._collision_free_handlers = ()

    def test_game_over_and_game_won_properties(self):
        """game_over e game_won dipendono da game_phase."""
        self.game.game_phase = Phase.PLAYING
        self.assertFalse(self.game.game_over)
        self.assertFalse(self.game.game_won)

        self.game.game_phase = Phase.GAME_OVER
        self.assertTrue(self.game.game_over)
        self.assertFalse(self.game.game_won)

        self.game.game_phase = Phase.GAME_WON
        self.assertFalse(self.game.game_over)
        self.assertTrue(self.game.game_won)

    # ======== METODI ========
    def test_inside_arena_true_and_false(self):
        """inside_arena deve riconoscere oggetti dentro/fuori i bordi."""
        obj_inside = Mock()
        obj_inside.pos.return_value = (10, 10)
        obj_inside.size.return_value = (20, 20)

        obj_outside = Mock()
        w, h = 50, 50
        obj_outside.pos.return_value = (self.size[0] - w + 1, 10)
        obj_outside.size.return_value = (w, h)

        self.assertTrue(self.game.inside_arena(obj_inside))
        self.assertFalse(self.game.inside_arena(obj_outside))

    def test_distance(self):
        """distance deve calcolare la distanza fra due Actor."""
        o1 = Mock()
        o2 = Mock()
        o1.pos.return_value = (0, 0)
        o2.pos.return_value = (3, 4)  # distanza 5

        dist = self.game.distance(o1, o2)
        self.assertEqual(dist, 5.0)

    def test_empty_queue_spawns_all_actors(self):
        """empty_queue deve spawnare tutti gli attori in spawn_queue (senza Arthur)."""

        class DummyActor: pass

        a1 = DummyActor()
        a2 = DummyActor()

        game2 = Game(self.size)
        game2.spawn = Mock()

        game2.spawn_queue = [a1, a2]
        game2.empty_queue()

        game2.spawn.assert_any_call(a1)
        game2.spawn.assert_any_call(a2)
        self.assertEqual(game2.spawn.call_count, 2)


    # ======== COLLISION HANDLERS ========
    def test_add_collision_handler_symmetry(self):
        """add_collision_handler registra anche la coppia invertita."""

        class A: pass
        class B: pass

        handler = Mock()
        self.game.add_collision_handler(A, B, handler)

        handlers = self.game._collision_handlers

        self.assertIn((A, B), handlers)
        self.assertIn((B, A), handlers)

        a = A()
        b = B()

        handlers[(A, B)](a, b, self.game) # type: ignore
        handlers[(B, A)](a, b, self.game) # type: ignore

        self.assertEqual(handler.call_count, 2)
        handler.assert_any_call(a, b, self.game)
        handler.assert_any_call(b, a, self.game)

    def test_add_collision_free_handler_symmetry(self):
        """add_collision_free_handler registra anche la coppia invertita."""

        class A: pass
        class B: pass

        handler_free = Mock()
        self.game.add_collision_free_handler(A, B, handler_free)

        handlers = self.game._collision_free_handlers

        self.assertIn((A, B), handlers)
        self.assertIn((B, A), handlers)

    def test_generic_damage_only_first_direction(self):
        """Solo a1 ha damage e a2 ha hit, allora chiama solo a2.hit."""
        a1 = Mock()
        a2 = Mock()

        a1.damage = 10
        a2.hit = Mock()

        result = self.game._generic_damage(a1, a2)

        self.assertTrue(result)
        a2.hit.assert_called_once_with(damage=10)

    def test_generic_damage_both_directions(self):
        """Se entrambi hanno damage e hit, li chiama entrambi."""
        a1 = Mock()
        a2 = Mock()

        a1.damage = 5
        a1.hit = Mock()

        a2.damage = 7
        a2.hit = Mock()

        result = Game._generic_damage(a1, a2)

        self.assertTrue(result)
        a2.hit.assert_called_once_with(damage=5)
        a1.hit.assert_called_once_with(damage=7)


    def test_handle_arthur_platform_calls_clamp_and_on_platform_collision(self):
        """_handle_arthur_platform clamp + on_platform_collision."""
        arthur = Mock()
        platform = Mock()
        platform.clamp.return_value = (Direction.UP, 0, -5)

        with patch.object(Game, "_generic_damage", return_value=False) as mock_gd:
            self.game._handle_arthur_platform(arthur, platform, self.game)

        mock_gd.assert_called_once_with(arthur, platform)
        platform.clamp.assert_called_once_with(arthur)
        arthur.on_platform_collision.assert_called_once_with(Direction.UP, 0, -5)

    def test_handle_arthur_platform_no_collision_if_direction_none(self):
        """Se clamp -> (None, ...) non chiama on_platform_collision."""
        arthur = Mock()
        platform = Mock()
        platform.clamp.return_value = (None, 0, 0)

        self.game._handle_arthur_platform(arthur, platform, self.game)

        platform.clamp.assert_called_once_with(arthur)
        arthur.on_platform_collision.assert_not_called()

    def test_handle_arthur_ladder_uses_current_keys(self):
        """_handle_arthur_ladder usa current_keys() del game."""
        arthur = Mock()
        ladder = Mock()
        keys = ["ArrowUp", "ArrowDown"]

        self.game.current_keys = Mock(return_value=keys)

        with patch.object(Game, "_generic_damage", return_value=False):
            self.game._handle_arthur_ladder(arthur, ladder, self.game)

        ladder.pos.assert_called_once()
        ladder.size.assert_called_once()
        arthur.on_ladder_collision.assert_called_once()

    def test_handle_arthur_door(self):
        """_handle_arthur_door chiama door.on_arthur_collision()."""
        arthur = Mock()
        door = Mock()

        Game._handle_arthur_door(arthur, door, self.game)
        door.on_arthur_collision.assert_called_once_with()


    def test_handle_collisions_calls_registered_handler_on_collision(self):
        """Se check_collision è True, chiama il collision handler."""

        class A: pass
        class B: pass

        a1 = A()
        a1.pos = Mock(return_value=(0, 0))
        a1.size = Mock(return_value=(15, 15))

        a2 = B()
        a2.pos = Mock(return_value=(10, 10))
        a2.size = Mock(return_value=(10, 10))

        self.game.actors = Mock(return_value=[a1, a2])
        handler = Mock()
        self.game.add_collision_handler(A, B, handler)

        with patch("src.game.entities.check_collision", return_value=True):
            self.game._handle_collisions()

        handler.assert_called_once_with(a1, a2, self.game)

    def test_handle_collisions_calls_free_handler_when_no_collision(self):
        """Se non ci sono collisioni, chiama il collision_free handler."""
        class A: pass
        class B: pass

        a1 = A()
        a1.pos = Mock(return_value=(0, 0))
        a1.size = Mock(return_value=(5, 5))

        a2 = B()
        a2.pos = Mock(return_value=(10, 10))
        a2.size = Mock(return_value=(10, 10))

        self.game.actors = Mock(return_value=[a1, a2])
        self.game._collision_handlers.clear()
        self.game._collision_free_handlers.clear()

        free_handler = Mock()
        self.game.add_collision_free_handler(A, B, free_handler)

        with patch("src.game.entities.check_collision", return_value=False):
            self.game._handle_collisions()

        free_handler.assert_called_once_with(a1, a2, self.game)


if __name__ == "__main__":
    unittest.main()
