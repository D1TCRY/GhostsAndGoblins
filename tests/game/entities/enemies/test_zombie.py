import unittest
from unittest.mock import Mock, patch

import src.game.entities.enemies.zombie as zombie_module
from src.game.entities.enemies.zombie import Zombie, Action, Direction, EntityState


class ZombieTest(unittest.TestCase):

    def setUp(self):
        self.zombie = Zombie(
            name="Zombie",
            x=100,
            y=50,
            health=70.0,
            speed=2.0,
            gravity=1.0,
            min_walk_distance=10.0,
            max_walk_distance=20.0,
            sprite_cycle_speed=3,
            direction=Direction.RIGHT,
            damage=30.0,
            attack_interval=50,
        )

    # ======== INIT ========
    def test_init(self):
        self.assertEqual(self.zombie.name, "Zombie")
        self.assertEqual(self.zombie.pos(), (100.0, 50.0))

        self.assertEqual(self.zombie.max_health, 70.0)
        self.assertEqual(self.zombie.health, 70.0)
        self.assertEqual(self.zombie.speed, 2.0)
        self.assertEqual(self.zombie.gravity, 1.0)

        self.assertIsInstance(self.zombie.state, EntityState)
        self.assertEqual(self.zombie.state.action, Action.EMERGING)
        self.assertEqual(self.zombie.state.direction, Direction.RIGHT)




    # ======== HEALTH ========
    def test_health_clamped_and_sets_dead_when_zero(self):
        """health deve essere contenuta tra 0 e max_health, se arriva a 0 mette lo stato DEAD."""
        # -> clamp sopra max_health
        self.zombie.health = 1000
        self.assertEqual(self.zombie.health, self.zombie.max_health)

        # -> quando va a 0 -> DEAD + reset della distanza
        with patch.object(zombie_module.random, "uniform", return_value=13.0):
            self.zombie.health = 0

        self.assertEqual(self.zombie.health, 0)
        self.assertEqual(self.zombie.state.action, Action.DEAD)
        self.assertEqual(self.zombie.walked_distance, 0.0)
        self.assertEqual(self.zombie.distance_to_walk, 13.0)

    # ======== GUI ========
    def test_gui_returns_bar(self):
        """gui deve restituire un oggetto che eredita da GUIComponent."""
        gui_list = self.zombie.gui

        self.assertEqual(len(gui_list), 1)
        bar = gui_list[0]

        self.assertIsInstance(bar, zombie_module.GUIComponent)

    # ======== POSITION, SIZE ========
    def test_pos_size(self):
        self.zombie.x = 10
        self.zombie.y = 20
        self.zombie.width = 30
        self.zombie.height = 40

        self.assertEqual(self.zombie.pos(), (10.0, 20.0))
        self.assertEqual(self.zombie.size(), (30, 40))

    # ======== MOVE ========
    def test_move_emerging_goes_to_walking_when_anim_finished(self):
        """Se EMERGING e animazione finita, deve passare a WALKING."""
        arena = Mock()

        self.zombie.state.action = Action.EMERGING
        self.zombie.state.direction = Direction.RIGHT
        self.zombie.y_step = 0.0

        with patch.object(Zombie, "_locked_anim_finished", return_value=True), \
             patch.object(Zombie, "_set_state_action") as mock_set_state:
            self.zombie.move(arena)

        # -> nessuna gravità durante EMERGING
        self.assertEqual(self.zombie.y_step, 0.0)
        mock_set_state.assert_called_once_with(Action.WALKING)

    def test_move_walking_moves_and_starts_immersing_after_distance(self):
        """In WALKING si muove, una volta superata distance_to_walk passa all'azione IMMERSING."""
        arena = Mock()

        self.zombie.state.action = Action.WALKING
        self.zombie.state.direction = Direction.RIGHT
        self.zombie.x_step = 0.0
        self.zombie.y_step = 0.0
        self.zombie.grounded = True

        # -> basta camminare pochissimo per cambiare stato
        self.zombie.distance_to_walk = 1.0
        self.zombie.walked_distance = 0.9

        with patch.object(Zombie, "_set_state_action") as mock_set_state:
            self.zombie.move(arena)

        self.assertAlmostEqual(self.zombie.x_step, self.zombie.speed)
        self.assertGreaterEqual(self.zombie.walked_distance, self.zombie.distance_to_walk)
        mock_set_state.assert_called_once_with(Action.IMMERSING)

    def test_move_immersing_sets_dead_when_anim_finished(self):
        """In IMMERSING quando l'animazione è finita diventa DEAD."""
        arena = Mock()

        self.zombie.state.action = Action.IMMERSING

        with patch.object(Zombie, "_locked_anim_finished", return_value=True):
            self.zombie.move(arena)

        self.assertEqual(self.zombie.state.action, Action.DEAD)

    # ======== SPRITE ========
    def test_sprite_returns_sprite_in_walking_and_none_when_dead(self):
        # -> WALKING -> sprite non None
        self.zombie.state.action = Action.WALKING
        self.zombie.state.direction = Direction.RIGHT
        spr = self.zombie.sprite()
        self.assertIsNotNone(spr)

        # -> DEAD -> sprite None
        self.zombie.state.action = Action.DEAD
        spr2 = self.zombie.sprite()
        self.assertIsNone(spr2)

    # ======== ARTHUR COLLISION ========
    def test_on_arthur_collision_does_nothing_when_not_walking(self):
        """In EMERGING/IMMERSING/DEAD non deve colpire Arthur."""
        arthur = Mock()

        for action in (Action.EMERGING, Action.IMMERSING, Action.DEAD):
            with self.subTest(action=action):
                self.zombie.state.action = action
                self.zombie.attack_cooldown = 0
                arthur.hit.reset_mock()

                self.zombie.on_arthur_collision(arthur)
                arthur.hit.assert_not_called()

    def test_on_arthur_collision_hits_when_cooldown_zero(self):
        """In WALKING e cooldown==0 deve chiamare arthur.hit(damage) e settare il cooldown."""
        arthur = Mock()

        self.zombie.state.action = Action.WALKING
        self.zombie.attack_cooldown = 0
        self.zombie.damage = 42.0
        self.zombie.attack_interval = 30

        self.zombie.on_arthur_collision(arthur)

        arthur.hit.assert_called_once_with(42.0)
        self.assertEqual(self.zombie.attack_cooldown, 30)

    def test_on_arthur_collision_ignored_when_cooldown_positive(self):
        """Se il cooldown è >0, non deve colpire Arthur."""
        arthur = Mock()

        self.zombie.state.action = Action.WALKING
        self.zombie.attack_cooldown = 10
        self.zombie.damage = 42.0
        self.zombie.attack_interval = 30

        self.zombie.on_arthur_collision(arthur)

        arthur.hit.assert_not_called()
        self.assertEqual(self.zombie.attack_cooldown, 10)

    # ======== PLATFORM COLLISION ========
    def test_on_platform_collision_updates_position_and_grounded(self):
        """Collisione con piattaforma sistema x, y, direzione e grounded."""
        # -> collisione da sinistra (LEFT)
        self.zombie.x = 10
        self.zombie.y = 20
        self.zombie.y_step = -3.0
        self.zombie.grounded = False
        self.zombie.state.direction = Direction.RIGHT

        self.zombie.on_platform_collision(Direction.LEFT, dx=-2.0, dy=0.0)
        self.assertEqual(self.zombie.x, 8.0)
        self.assertEqual(self.zombie.y, 20.0)
        self.assertEqual(self.zombie.state.direction, Direction.LEFT)

        # -> collisione dall'alto (UP) -> grounded True e y_step azzerata
        self.zombie.y_step = -5.0
        self.zombie.grounded = False
        self.zombie.on_platform_collision(Direction.UP, dx=0.0, dy=-4.0)
        self.assertEqual(self.zombie.y, 16.0)
        self.assertEqual(self.zombie.y_step, 0.0)
        self.assertTrue(self.zombie.grounded)

    # ======== AUTO_INIT ========
    def test_auto_init(self):
        """
        auto_init:
        - calcola i range di spawn corretti sulle piattaforme a sinistra e destra,
        - sceglie un Candidate tra le piattaforme selezionate,
        - crea uno Zombie con x, y, direction coerenti.
        """
        with patch.object(zombie_module, "read_settings") as mock_rs, \
             patch.object(zombie_module.random, "choice") as mock_choice, \
             patch.object(zombie_module.random, "uniform") as mock_uniform:

            mock_rs.return_value = {
                "Zombie": {
                    "defaults": {
                        "width": 21,
                        "height": 32,
                        "spawn_min_dist_x": 50,
                        "spawn_max_dist_x": 100,
                        "max_health": 70.0,
                        "health": 70.0,
                        "speed": 2.0,
                        "gravity": 1.0,
                        "min_walk_distance": 10.0,
                        "max_walk_distance": 20.0,
                        "sprite_cycle_speed": 3,
                        "direction": "RIGHT",
                        "damage": 30.0,
                        "attack_interval": 50,
                    }
                }
            }

            zombie_width = 21
            zombie_height = 32

            # Player
            player = Mock()
            player.x = 100
            player.y = 50
            player.width = 20   # cx = 110
            player.height = 30  # base_y = 80

            # -> dummy di platform
            class DummyPlatform(zombie_module.Platform):
                def __init__(self, x, y, width, height, damage, contact_surfaces):
                    self.x = x
                    self.y = y
                    self.width = width
                    self.height = height
                    self.damage = damage
                    self.contact_surfaces = contact_surfaces

            # piattaforma vicina:
            #   intersezione sinistra: [0, 60]
            #   intersezione destra: [160, 200]
            platform_close = DummyPlatform(
                x=0, y=100, width=200, height=10,
                damage=0,
                contact_surfaces=[Direction.UP],
            )

            # piattaforma più lontana (y=200)
            #   intersezione sinistra: [0, 60]
            #   intersezione destra: [160, 200]
            platform_far = DummyPlatform(
                x=0, y=200, width=200, height=10,
                damage=0,
                contact_surfaces=[Direction.UP],
            )

            game = Mock()
            game.actors.return_value = [platform_close, platform_far]

            # -> salvo i candidati che auto_init passerà a choice in 'captured'
            captured = {}

            def fake_choice(candidates):
                captured["candidates"] = list(candidates)
                # -> dopo il sort, il candidato migliore è il primo
                return candidates[0]

            mock_choice.side_effect = fake_choice

            # uniform(a, b) -> scelgo sempre il minimo
            def fake_uniform(a, b):
                return a

            mock_uniform.side_effect = fake_uniform

            # -> chiamata reale ad auto_init
            spawned_zombie = Zombie.auto_init(player, game)

        # -> CHECK CANDIDATES
        self.assertIn("candidates", captured)
        candidates = captured["candidates"]

        # -> ci devono essere candidati su entrambe le piattaforme
        close_candidates = [c for c in candidates if c.height == platform_close.y]
        far_candidates = [c for c in candidates if c.height == platform_far.y]
        self.assertTrue(close_candidates)
        self.assertTrue(far_candidates)

        # -> tra i candidati sulla piattaforma vicina, troviamo i due lati
        left_close = [
            c for c in close_candidates
            if c.direction == Direction.RIGHT   # -> LEFT range
        ]
        right_close = [
            c for c in close_candidates
            if c.direction == Direction.LEFT    # -> RIGHT range
        ]

        self.assertTrue(left_close)
        self.assertTrue(right_close)

        left_candidate = left_close[0]
        right_candidate = right_close[0]

        # -> range sinistro atteso: [0, 60]
        self.assertAlmostEqual(left_candidate.range.min, 0.0)
        self.assertAlmostEqual(left_candidate.range.max, 60.0)

        # -> range destro atteso: [160, 200]
        self.assertAlmostEqual(right_candidate.range.min, 160.0)
        self.assertAlmostEqual(right_candidate.range.max, 200.0)

        # -> il candidato scelto (dopo il sort) deve stare sulla piattaforma più vicina (imposto da fake_choice)
        chosen_candidate = candidates[0] # -> return di fake_choice
        self.assertEqual(chosen_candidate.height, platform_close.y)

        # -> CHECK ZOMBIE
        # -> x deve essere l'estremo sinistro del range (fake_uniform ritorna il minimo)
        expected_x = chosen_candidate.range.min
        # -> y = altezza piattaforma - altezza zombie
        expected_y = chosen_candidate.height - zombie_height

        self.assertIsInstance(spawned_zombie, Zombie)
        self.assertAlmostEqual(spawned_zombie.x, expected_x)
        self.assertAlmostEqual(spawned_zombie.y, expected_y)
        self.assertEqual(spawned_zombie.state.direction, chosen_candidate.direction)


if __name__ == "__main__":
    unittest.main()
