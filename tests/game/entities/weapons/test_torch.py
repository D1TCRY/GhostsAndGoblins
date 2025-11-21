import unittest
from unittest.mock import Mock, patch

from src.game.entities.weapons import torch as torch_module

Torch = torch_module.Torch
Action = torch_module.Action
Direction = torch_module.Direction
EntityState = torch_module.EntityState


class TorchTest(unittest.TestCase):

    def setUp(self):
        self.torch = Torch(
            x=10,
            y=20,
            damage=50,
            speed=7.0,
            gravity=0.7,
            sprite_cycle_speed=4,
            action=Action.ATTACKING,
            direction=Direction.RIGHT,
        )

    # ======== INIT ========
    def test_init(self):
        """Torch deve impostare correttamente stato e velocità iniziali."""
        self.assertEqual(self.torch.damage, 50)
        self.assertAlmostEqual(self.torch.speed, 7.0)
        self.assertAlmostEqual(self.torch.gravity, 0.7)
        self.assertEqual(self.torch.sprite_cycle_speed, 4)

        self.assertAlmostEqual(self.torch.x, 10.0)
        self.assertAlmostEqual(self.torch.y, 20.0)

        self.assertIsInstance(self.torch.state, EntityState)
        self.assertEqual(self.torch.state.action, Action.ATTACKING)
        self.assertEqual(self.torch.state.direction, Direction.RIGHT)

        self.assertAlmostEqual(self.torch.x_step, self.torch.speed)
        self.assertAlmostEqual(self.torch.y_step, -5.0)


    # ======== MOVE ========
    def test_move_applies_gravity_and_horizontal_speed(self):
        """move deve applicare gravità e velocità orizzontale."""
        start_x = self.torch.x
        start_y = self.torch.y
        start_vx = self.torch.x_step
        start_vy = self.torch.y_step
        g = self.torch.gravity

        arena = Mock()

        self.torch.move(arena)

        # -> y_step aumenta di gravity
        self.assertAlmostEqual(self.torch.y_step, start_vy + g)
        # -> y cambia di y_step
        expected_y = start_y + start_vy + g
        self.assertAlmostEqual(self.torch.y, expected_y)
        # -> x cambia di x_step
        self.assertAlmostEqual(self.torch.x, start_x + start_vx)

    def test_move_does_nothing_when_dead(self):
        """Se la Torch è DEAD, move non deve modificare posizione."""
        self.torch.state.action = Action.DEAD

        start_pos = self.torch.pos()
        start_vx = self.torch.x_step
        start_vy = self.torch.y_step

        self.torch.move(Mock())

        self.assertEqual(self.torch.pos(), start_pos)
        self.assertEqual(self.torch.x_step, start_vx)
        self.assertEqual(self.torch.y_step, start_vy)

    # ======== SPRITE ========
    def test_sprite_returns_none_when_dead(self):
        """sprite deve restituire None se la Torch è DEAD."""
        self.torch.state.action = Action.DEAD

        self.assertIsNone(self.torch.sprite())

    # ======== COLLISIONS - PLATFORM ========
    def test_on_platform_collision_up_spawns_flame_and_kills(self):
        """
        on_platform_collision con Direction.UP:
        - sposta la Torch di (dx, dy)
        - spawna una Flame
        - imposta lo stato a DEAD.
        """
        self.torch.x = 10
        self.torch.y = 20
        self.torch.width = 16
        self.torch.height = 16

        game = Mock()

        with patch("src.game.entities.weapons.torch.Flame") as MockFlame:
            flame_instance = Mock()
            MockFlame.return_value = flame_instance

            dx, dy = 2, 3
            self.torch.on_platform_collision(Direction.UP, dx, dy, game)

        # -> posizione aggiornata
        self.assertAlmostEqual(self.torch.x, 12)
        self.assertAlmostEqual(self.torch.y, 23)

        # -> coordinate attese della Flame
        expected_flame_x = 12 + self.torch.width / 2
        expected_flame_y = 23 + self.torch.height

        MockFlame.assert_called_once_with(x=expected_flame_x, ground_y=expected_flame_y)
        game.spawn.assert_called_once_with(flame_instance)
        self.assertEqual(self.torch.state.action, Action.DEAD)

    def test_on_platform_collision_side_only_kills(self):
        """
        on_platform_collision con direzione diversa da UP:
        - non sposta la Torch
        - non spawna Flame
        - imposta lo stato a DEAD.
        """
        self.torch.x = 10
        self.torch.y = 20

        game = Mock()

        with patch.object(self.torch, "_spawn_flame") as mock_spawn_flame:
            self.torch.on_platform_collision(Direction.LEFT, dx=5, dy=5, game=game)

        # -> posizione invariata
        self.assertAlmostEqual(self.torch.x, 10)
        self.assertAlmostEqual(self.torch.y, 20)

        mock_spawn_flame.assert_not_called()
        self.assertEqual(self.torch.state.action, Action.DEAD)

    # ======== HIT ========
    def test_hit_sets_state_dead(self):
        """hit deve sempre impostare lo stato a DEAD (indipendentemente dal danno)."""
        self.torch.state.action = Action.ATTACKING

        self.torch.hit(1e64)

        self.assertEqual(self.torch.state.action, Action.DEAD)

    # ======== PROPERTIES ========
    def test_x_type_error(self):
        """x accetta solo int o float."""
        with self.assertRaises(TypeError):
            self.torch.x = "not-a-number"  # type: ignore

    def test_y_step_type_error(self):
        """y_step accetta solo int o float."""
        with self.assertRaises(TypeError):
            self.torch.y_step = "nope"  # type: ignore

    def test_damage_must_be_int(self):
        """damage deve essere int or float."""
        with self.assertRaises(TypeError):
            self.torch.damage = "3.5"  # type: ignore


if __name__ == "__main__":
    unittest.main()
