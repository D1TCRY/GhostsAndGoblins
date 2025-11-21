import unittest
from unittest.mock import patch

from src.game.entities.weapons import eye_ball as eye_ball_module

EyeBall = eye_ball_module.EyeBall
Action = eye_ball_module.Action
Direction = eye_ball_module.Direction
EntityState = eye_ball_module.EntityState


class EyeBallTest(unittest.TestCase):

    def setUp(self):
        self.eye_ball = EyeBall(x=10.0, y=20.0)

    # ======== INIT ========
    def test_init(self):
        """EyeBall deve inizializzarsi con stato action.ATTACKING, direzione valida e sprite corretti."""
        self.assertAlmostEqual(self.eye_ball.x, 10.0)
        self.assertAlmostEqual(self.eye_ball.y, 20.0)

        self.assertIsInstance(self.eye_ball.state, EntityState)
        self.assertEqual(self.eye_ball.state.action, Action.ATTACKING)
        self.assertIsInstance(self.eye_ball.state.direction, Direction)

        key = (Action.ATTACKING, self.eye_ball.state.direction)
        self.assertIn(key, self.eye_ball.sprites)

        first = self.eye_ball.sprites[key][0]
        self.assertEqual(self.eye_ball.width, first.width)
        self.assertEqual(self.eye_ball.height, first.height)

        self.assertAlmostEqual(self.eye_ball.travelled_distance, 0.0)
        self.assertIsInstance(self.eye_ball.max_travel_distance, float)

    # ======== MOVE ========
    def test_move_right_increases_x_and_distance(self):
        """Con direzione RIGHT, move deve aumentare x e travelled_distance."""
        eye = EyeBall(
            x=0.0,
            y=0.0,
            direction=Direction.RIGHT,
            speed=3.0,
            max_travel_distance=3.1,
        )

        start_x = eye.x
        start_dist = eye.travelled_distance

        eye.move(None)  # type: ignore # -> Game non viene usato in move

        # -> si muove a destra
        self.assertAlmostEqual(eye.x, start_x + 3.0)
        # -> distanza accumulata
        self.assertAlmostEqual(eye.travelled_distance, start_dist + 3.0)
        # -> ancora vivo (non ha superato max_travel_distance)
        self.assertEqual(eye.state.action, Action.ATTACKING)

    def test_move_left_decreases_x_and_increases_distance(self):
        """Con direzione LEFT, move deve diminuire x e aumentare travelled_distance."""
        eye = EyeBall(
            x=10.0,
            y=0.0,
            direction=Direction.LEFT,
            speed=2.5,
            max_travel_distance=2.6,
        )

        start_x = eye.x
        start_dist = eye.travelled_distance

        eye.move(None)  # type: ignore

        # -> si muove a sinistra
        self.assertAlmostEqual(eye.x, start_x - 2.5)
        # -> distanza accumulata (positiva)
        self.assertAlmostEqual(
            eye.travelled_distance,
            start_dist + 2.5
        )
        self.assertEqual(eye.state.action, Action.ATTACKING)

    def test_move_dies_after_max_travel_distance(self):
        """Quando travelled_distance >= max_travel_distance allora EyeBall diventa DEAD."""
        eye = EyeBall(
            x=0.0,
            y=0.0,
            direction=Direction.RIGHT,
            speed=2.0,
            max_travel_distance=5.0,
        )

        # -> dopo abbastanza step deve superare la soglia
        for _ in range(3): eye.move(None) # type: ignore

        # -> 3 step da 2 -> travelled_distance = 6 >= 5 -> DEAD
        self.assertGreaterEqual(eye.travelled_distance, eye.max_travel_distance)
        self.assertEqual(eye.state.action, Action.DEAD)

        # -> ulteriori move non devono cambiare x
        x_dead = eye.x
        eye.move(None) # type: ignore
        self.assertEqual(eye.x, x_dead)

    def test_move_does_nothing_when_dead(self):
        """Se la EyeBall è DEAD, move non cambia posizione ne distanza."""
        self.eye_ball.state.action = Action.DEAD
        start_pos = self.eye_ball.pos()
        start_dist = self.eye_ball.travelled_distance

        self.eye_ball.move(None) # type: ignore

        self.assertEqual(self.eye_ball.pos(), start_pos)
        self.assertAlmostEqual(self.eye_ball.travelled_distance, start_dist)

    # ======== SPRITE ========
    def test_sprite_returns_none_when_dead(self):
        """sprite deve restituire None quando lo stato è DEAD."""
        self.eye_ball.state.action = Action.DEAD

        self.assertIsNone(self.eye_ball.sprite())

    # ======== HIT ========
    def test_hit_sets_state_dead(self):
        """hit deve sempre impostare lo stato a DEAD."""
        self.eye_ball.state.action = Action.ATTACKING

        self.eye_ball.hit(1e-16)

        self.assertEqual(self.eye_ball.state.action, Action.DEAD)

    # ======== PROPERTIES ========
    def test_x_type_error(self):
        """x accetta solo int o float."""
        with self.assertRaises(TypeError):
            self.eye_ball.x = "not-a-number"  # type: ignore

    def test_damage_type_error(self):
        """damage accetta solo numeri."""
        with self.assertRaises(TypeError):
            self.eye_ball.damage = "..."  # type: ignore

    def test_travelled_distance_type_error(self):
        """travelled_distance accetta solo numeri."""
        with self.assertRaises(TypeError):
            self.eye_ball.travelled_distance = "§#@"  # type: ignore

    def test_max_travel_distance_type_error(self):
        """max_travel_distance accetta solo numeri."""
        with self.assertRaises(TypeError):
            self.eye_ball.max_travel_distance = None  # type: ignore


if __name__ == "__main__":
    unittest.main()
