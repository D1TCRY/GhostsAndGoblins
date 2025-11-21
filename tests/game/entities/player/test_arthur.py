import unittest
from turtledemo.penrose import start
from unittest.mock import Mock, patch

import src.game.entities.player.arthur as arthur_module
from src.game.entities.player import Arthur
from src.game.state import Action, Direction, EntityState


class ArthurTest(unittest.TestCase):

    def setUp(self):
        self.arthur = Arthur(
            name="Arthur",
            x=50,
            y=60,
            width=21,
            height=32,
            speed=5.0,
            gravity=1.0,
            jump_speed=10.0,
            health=80,
            max_health=100,
            throw_interval=10,
        )

    # ======== INIT ========
    def test_init_uses_defaults(self):
        """Arthur deve usare i defaults se non passo i parametri opzionali."""
        self.assertEqual(self.arthur.name, "Arthur")
        self.assertEqual(self.arthur.pos(), (50.0, 60.0))

        self.assertEqual(self.arthur.width, 21)
        self.assertEqual(self.arthur.height, 32)
        self.assertEqual(self.arthur.speed, 5.0)
        self.assertEqual(self.arthur.gravity, 1.0)
        self.assertEqual(self.arthur.jump_speed, 10.0)
        self.assertEqual(self.arthur.max_health, 100.0)
        self.assertEqual(self.arthur.health, 80.0)

        self.assertIsInstance(self.arthur.state, EntityState)
        self.assertEqual(self.arthur.state.action, Action.WALKING)
        self.assertEqual(self.arthur.state.direction, Direction.RIGHT)

    def test_health_cannot_exceed_max_health(self):
        """health deve essere clippata a [0, max_health]."""
        self.arthur.health = 1000
        self.assertEqual(self.arthur.health, self.arthur.max_health)

        self.arthur.health = -10
        self.assertEqual(self.arthur.health, 0.0)

    def test_x_type_error(self):
        with self.assertRaises(TypeError):
            self.arthur.x = "abc"  # type: ignore

    def test_health_type_error(self):
        with self.assertRaises(TypeError):
            self.arthur.health = "abc"  # type: ignore

    # ======== POSITION ========
    def test_pos_and_size_methods(self):
        """pos() e size() devono riflettere x, y, width, height."""
        self.arthur.x = 10
        self.arthur.y = 20
        self.arthur.width = 30
        self.arthur.height = 40

        self.assertEqual(self.arthur.pos(), (10.0, 20.0))
        self.assertEqual(self.arthur.size(), (30, 40))

    # ======== MOVE - GENERIC ========
    def test_move_does_nothing_if_dead(self):
        """Se l'azione è DEAD, move non deve fare niente."""
        arena = Mock()
        arena.current_keys.return_value = []

        old_pos = self.arthur.pos()
        self.arthur.state.action = Action.DEAD

        self.arthur.move(arena)

        arena.current_keys.assert_not_called()
        self.assertEqual(self.arthur.pos(), old_pos)

    def test_move_horizontal_right(self):
        """Con ArrowRight premuto e non crouching, Arthur si muove a destra."""
        arena = Mock()
        arena.current_keys.return_value = ["ArrowRight"]

        self.arthur.grounded = True
        self.arthur.y_step = 0.0
        start_x, start_y = self.arthur.pos()

        self.arthur.move(arena)

        # -> x deve aumentare di speed
        self.assertAlmostEqual(self.arthur.x, start_x + self.arthur.speed)
        # -> y cambia per la gravità
        self.assertAlmostEqual(self.arthur.y, start_y + self.arthur.gravity)
        self.assertEqual(self.arthur.state.direction, Direction.RIGHT)
        self.assertEqual(self.arthur.state.action, Action.WALKING)

    def test_move_jump_with_arrowup(self):
        """Con ArrowUp e grounded Arthur salta."""
        arena = Mock()
        arena.current_keys.return_value = ["ArrowUp"]

        self.arthur.grounded = True
        self.arthur.y_step = 0.0
        start_x, start_y = self.arthur.pos()

        self.arthur.move(arena)

        # -> y_step = -jump_speed + gravity
        expected_y_step = -self.arthur.jump_speed + self.arthur.gravity
        self.assertAlmostEqual(self.arthur.y_step, expected_y_step)
        self.assertAlmostEqual(self.arthur.y, start_y + expected_y_step)
        self.assertEqual(self.arthur.state.action, Action.JUMPING)

    def test_move_jump_and_right_from_top_parametric(self):
        """
        Test parametrico del movimento con ArrowRight + ArrowUp premuti quando Arthur è all'apice della traiettoria (y_step = 0).

        Casi:
        - direzione iniziale: LEFT / RIGHT
        - da terra o in aria: grounded=True / grounded=False
        - su scala o non: laddered=True / laddered=False
        """

        arena = Mock()
        arena.current_keys.return_value = ["ArrowRight", "ArrowUp"]

        start_x, start_y = self.arthur.pos()
        self.arthur.speed = 5.0
        self.arthur.gravity = 1.0

        for start_direction in (Direction.LEFT, Direction.RIGHT):
            for grounded in (False, True):
                for laddered in (False, True):
                    with self.subTest(direction=start_direction,
                                      grounded=grounded,
                                      laddered=laddered):
                        # -> reset Arthur
                        self.arthur.x, self.arthur.y = start_x, start_y
                        self.arthur.x_step = 0.0
                        self.arthur.y_step = 0.0  # -> punto di massimo
                        self.arthur.grounded = grounded
                        self.arthur.laddered = laddered
                        self.arthur._priority_action = None

                        # -> azione iniziale
                        if laddered:
                            self.arthur.state.action = Action.CLIMBING
                        elif grounded:
                            self.arthur.state.action = Action.IDLE
                        else: # -> in aria
                            self.arthur.state.action = Action.JUMPING

                        self.arthur.state.direction = start_direction

                        self.arthur.move(arena)

                        # -> in ogni caso la direzione deve essere Direction.RIGHT e si deve spostare (dato che non è CROUCHING)
                        self.assertEqual(self.arthur.state.direction, Direction.RIGHT)
                        self.assertAlmostEqual(self.arthur.x, start_x + self.arthur.speed)

                        if not laddered:
                            # -> se non è su scala si applica la gravità normalmente

                            if grounded:
                                # -> da terra + ArrowUp -> inizia un salto
                                expected_y_step = -self.arthur.jump_speed + self.arthur.gravity
                                self.assertAlmostEqual(self.arthur.y_step, expected_y_step)
                                self.assertAlmostEqual(self.arthur.y, start_y + expected_y_step)
                                self.assertEqual(self.arthur.state.action, Action.JUMPING)
                            else:
                                # -> in aria + ArrowUp -> non esegue un doppio salto, quindi scende e basta
                                self.assertAlmostEqual(self.arthur.y_step, self.arthur.gravity)
                                self.assertAlmostEqual(self.arthur.y, start_y + self.arthur.gravity)
                                self.assertEqual(self.arthur.state.action, Action.JUMPING)
                        else:
                            # -> se è su scala la gravità non viene applicata
                            self.assertAlmostEqual(self.arthur.y_step, 0.0)
                            # su scala + ArrowUp -> non deve entrare in stato di salto
                            self.assertNotEqual(self.arthur.state.action, Action.JUMPING)


    # ======== MOVE - TORCH, LADDER ========
    def test_move_throw_torch_spawns_torch_and_sets_cooldown(self):
        """Premendo '1' e con cooldown == 0, Arthur lancia una Torch."""
        arena = Mock()
        arena.current_keys.return_value = ["1"]

        self.arthur.laddered = False
        self.arthur.throw_cooldown = 0
        self.arthur.state.action = Action.IDLE
        self.arthur.state.direction = Direction.RIGHT

        with patch.object(arthur_module, "Torch") as MockTorch:
            torch_instance = Mock()
            MockTorch.return_value = torch_instance

            self.arthur.move(arena)

        # -> deve aver creato la Torch e chiamato spawn
        MockTorch.assert_called_once()
        arena.spawn.assert_called_once_with(torch_instance)
        self.assertEqual(self.arthur.throw_cooldown, 10)
        self.assertEqual(self.arthur._priority_action, Action.ATTACKING)

    def test_cannot_throw_torch_while_on_ladder(self):
        """Se Arthur è sulla scala (laddered=True), non deve lanciare la Torch."""
        arena = Mock()
        arena.current_keys.return_value = ["1"]

        self.arthur.laddered = True  # -> dentro la scala
        self.arthur.throw_cooldown = 0
        self.arthur.state.action = Action.IDLE
        self.arthur.state.direction = Direction.RIGHT

        with patch.object(arthur_module, "Torch") as MockTorch:
            self.arthur.move(arena)

        # -> nessuna Torch creata -> quindi nessuno spawn chiamato
        MockTorch.assert_not_called()
        arena.spawn.assert_not_called()
        # -> cooldown e priority_action rimangono uguali
        self.assertEqual(self.arthur.throw_cooldown, 0)
        self.assertIsNone(self.arthur._priority_action)

    def test_can_throw_torch_when_not_on_ladder(self):
        """Se Arthur NON è sulla scala (laddered=False), può lanciare la Torch."""
        arena = Mock()
        arena.current_keys.return_value = ["1"]

        self.arthur.laddered = False  # -> fuori dalla scala
        self.arthur.throw_cooldown = 0
        self.arthur.state.action = Action.IDLE
        self.arthur.state.direction = Direction.RIGHT

        with patch.object(arthur_module, "Torch") as MockTorch:
            torch_instance = Mock()
            MockTorch.return_value = torch_instance

            self.arthur.move(arena)

        # -> deve aver creato la Torch -> quindi lo spawn viene chiamato
        MockTorch.assert_called_once()
        arena.spawn.assert_called_once_with(torch_instance)
        self.assertEqual(self.arthur.throw_cooldown, 10)
        self.assertEqual(self.arthur._priority_action, Action.ATTACKING)

    # ======== SPRITE ========
    def test_sprite_returns_a_sprite_for_walking(self):
        """sprite() deve restituire uno Sprite per stato WALKING RIGHT."""
        self.arthur.state.action = Action.WALKING
        self.arthur.state.direction = Direction.RIGHT
        self.arthur.invincibility_countdown = 0

        spr = self.arthur.sprite()
        # -> controllo che non sia None
        self.assertIsNotNone(spr)
        # -> blinking deve essere False quando countdown == 0
        self.assertFalse(spr.blinking)

    def test_sprite_sets_blinking_when_invincible(self):
        """Se invincibility_countdown > 0, gli sprite devono avere blinking == True."""
        self.arthur.state.action = Action.WALKING
        self.arthur.state.direction = Direction.RIGHT
        self.arthur.invincibility_countdown = int(1e99)

        spr = self.arthur.sprite()
        self.assertIsNotNone(spr)
        self.assertTrue(spr.blinking)

    # ======== GUI ========
    def test_gui_health_bar_updates_with_health(self):
        bar = self.arthur.gui[0]

        # -> health iniziale
        self.assertEqual(bar.value, self.arthur.health)  # type: ignore

        self.arthur.health = 30  # -> new health

        # -> bar.value chiama la funzione associata 'lambda: self.health' che ritorna il valore aggiornato 30
        self.assertEqual(bar.value, 30)  # type: ignore

    # ======== HIT ========
    def test_hit_reduces_health_and_sets_invincibility(self):
        """hit deve togliere vita e settare il countdown di invincibilità."""
        start_health = self.arthur.health
        self.arthur.invincibility_countdown = 0

        self.arthur.hit(10)

        self.assertEqual(self.arthur.health, start_health - 10)
        self.assertEqual(self.arthur.invincibility_countdown, self.arthur.invincibility_time)

    def test_hit_does_nothing_when_invincible(self):
        """Se invincibility_countdown > 0 allora hit non deve togliere vita."""
        start_health = self.arthur.health
        self.arthur.invincibility_countdown = 5

        self.arthur.hit(10)

        self.assertEqual(self.arthur.health, start_health)

    # ======== PLATFORM COLLISION ========
    def test_on_platform_collision_moves_and_sets_grounded(self):
        """Collisione da sopra (Direction.UP) mette grounded=True e applica lo spostamento dx, dy per clampare Arthur."""
        self.arthur.x = 10
        self.arthur.y = 50
        self.arthur.x_step = 3.0
        self.arthur.y_step = -2.0
        self.arthur.grounded = False
        self.arthur.laddered = True  # -> per vedere che viene settato a False

        self.arthur.on_platform_collision(Direction.UP, dx=1.0, dy=-5.0)

        self.assertEqual(self.arthur.x, 11.0)
        self.assertEqual(self.arthur.y, 45.0)
        self.assertEqual(self.arthur.y_step, 0.0)
        self.assertTrue(self.arthur.grounded)
        self.assertFalse(self.arthur.laddered)

    def test_on_platform_collision_horizontal_stops_x_step(self):
        """Collisione da sinistra/destra deve azzerare x_step."""
        self.arthur.x_step = 5.0

        self.arthur.on_platform_collision(Direction.LEFT, dx=-2.0, dy=0.0)
        self.assertEqual(self.arthur.x_step, 0.0)

    # ======== LADDER ========
    def test_on_ladder_collision_dead_does_nothing(self):
        """La collisione con Ladder non modifica laddered se Arthur ha azione DEAD."""
        self.arthur.state.action = Action.DEAD
        self.arthur.laddered = False

        self.arthur.on_ladder_collision(["ArrowUp"], (100, 100), (10, 50))

        # -> non viene modificato
        self.assertFalse(self.arthur.laddered)

    def test_on_ladder_collision_sets_laddered_and_moves(self):
        """Con ArrowUp dentro la scala, Arthur scala verso l'alto."""
        self.arthur.state.action = Action.WALKING
        self.arthur.y = 110  # -> dentro la zona della scala
        self.arthur.height = 32

        keys = ["ArrowUp"]
        ladder_pos = (100, 100)
        ladder_size = (10, 50)

        self.arthur.on_ladder_collision(keys, ladder_pos, ladder_size)

        self.assertTrue(self.arthur.laddered)
        self.assertEqual(self.arthur.y, 108)  # -> 110 - 2
        self.assertIn(self.arthur.state.action, (Action.CLIMBING, Action.CLIMBING_POSE))

    def test_not_on_ladder_collision(self):
        self.arthur.laddered = True
        self.arthur.not_on_ladder_collision()
        self.assertFalse(self.arthur.laddered)

    # ======== SUPPORT METHODS ========
    def test_reset_and_increment_sprite_cycle_counter(self):
        self.arthur.sprite_cycle_counter = 10
        self.arthur.reset_sprite_cycle_counter()
        self.assertEqual(self.arthur.sprite_cycle_counter, 0)

        self.arthur.increment_sprite_cycle_counter()
        self.assertEqual(self.arthur.sprite_cycle_counter, 1)


if __name__ == "__main__":
    unittest.main()
