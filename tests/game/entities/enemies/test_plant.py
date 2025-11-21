import unittest
from unittest.mock import Mock, patch

import src.game.entities.enemies.plant as plant_module
from src.game.entities.enemies import Plant

Action = plant_module.Action
Direction = plant_module.Direction
Bar = plant_module.Bar
Range = plant_module.Range
Candidate = plant_module.Candidate


class PlantTest(unittest.TestCase):

    def setUp(self):
        self.plant = Plant(
            x=50,
            y=100,
            health=40,
            damage=10,
            direction=Direction.RIGHT,
            attack_interval=30,
            projectile_speed=2.0,
            projectile_damage=20.0,
            sprite_cycle_speed=4
        )


    # ======== INIT ========
    def test_init(self):
        """Il Plant deve avere gli attributi corretti iniziali."""
        self.assertEqual(self.plant.x, 50.0)
        self.assertEqual(self.plant.y, 100.0)

        self.assertEqual(self.plant.max_health, 40.0)
        self.assertEqual(self.plant.health, 40.0)
        self.assertEqual(self.plant.damage, 10.0)

        self.assertEqual(self.plant.width, 21)
        self.assertEqual(self.plant.height, 32)

        self.assertEqual(self.plant.damage_interval, 60)
        self.assertEqual(self.plant.damage_cooldown, 0)

        self.assertEqual(self.plant.attack_interval, 30)
        self.assertEqual(self.plant.attack_cooldown, 30)

        self.assertEqual(self.plant.projectile_speed, 2.0)
        self.assertEqual(self.plant.projectile_damage, 20.0)

        self.assertEqual(self.plant.state.action, Action.SPAWNING)
        self.assertEqual(self.plant.state.direction, Direction.RIGHT)

        self.assertEqual(self.plant.sprite_cycle_speed, 4)
        self.assertEqual(self.plant.sprite_cycle_counter, 0)
        self.assertEqual(self.plant.sprite_cycle_counter, 0)

    def test_health_clamped_and_sets_dead_when_zero(self):
        """health deve essere compresa tra 0 e max_health, se <=0 mettere lo stato DEAD."""
        self.plant.state.action = Action.IDLE

        # -> salute <= 0
        self.plant.health = -10
        # -> leggere health attiva la logica che può settare DEAD
        value = self.plant.health

        self.assertEqual(value, 0)
        self.assertEqual(self.plant.state.action, Action.DEAD)

    # ======== MOVE - SPAWNING / IDLE / ATTACKING ========
    def test_move_spawning_goes_to_idle_when_anim_finished(self):
        """Partendo da SPAWNING, se l'animazione è finita passa a IDLE."""
        self.plant.state.action = Action.SPAWNING
        arena = Mock()

        with patch.object(self.plant, "_locked_anim_finished", return_value=True) as mock_finished, \
             patch.object(self.plant, "_set_state_action") as mock_set_state:

            self.plant.move(arena)

        mock_finished.assert_called_once()
        mock_set_state.assert_called_once_with(Action.IDLE)

    def test_move_idle_decrements_cooldown_without_attack(self):
        """In azione IDLE con cooldown > 0 non fa nulla, riduce solo attack_cooldown."""
        self.plant.state.action = Action.IDLE
        self.plant.attack_cooldown = 5

        arena = Mock()
        arena.player = Mock()  # -> esiste il player ma cooldown > 0

        with patch.object(self.plant, "_set_state_action") as mock_set_state:
            self.plant.move(arena)

        self.assertEqual(self.plant.attack_cooldown, 4)
        mock_set_state.assert_not_called()

    def test_move_idle_starts_attack_and_sets_direction(self):
        """In IDLE con cooldown 0 setta direction verso Arthur e passa ad ATTACKING."""
        arena = Mock()
        arena.player = Mock()
        self.plant.state.action = Action.IDLE
        self.plant.attack_cooldown = 0

        # -> center del Plant
        plant_cx = self.plant.x + self.plant.width / 2

        # -> due casi: player a destra e a sinistra
        test_cases = [
            ("RIGHT", plant_cx + 20, Direction.RIGHT),
            ("LEFT", plant_cx - 20, Direction.LEFT),
        ]

        for label, player_cx, expected_dir in test_cases:
            with self.subTest(side=label, player_cx=player_cx, expected_dir=expected_dir):
                # -> reset
                self.plant.state.action = Action.IDLE
                self.plant.attack_cooldown = 0
                self.plant.state.direction = Direction.RIGHT  # -> default

                # -> posizione del player
                arena.player.x = player_cx - 10
                arena.player.width = 20
                arena.player.y = 0
                arena.player.height = 30

                with patch.object(self.plant, "_set_state_action") as mock_set_state:
                    self.plant.move(arena)

                # -> direction aggiornata
                self.assertEqual(self.plant.state.direction, expected_dir)
                # -> inizio dello stato ATTACKING
                mock_set_state.assert_called_once_with(Action.ATTACKING)
                # -> cooldown resettato
                self.assertEqual(self.plant.attack_cooldown, self.plant.attack_interval)

    def test_move_attacking_shoots_and_goes_back_to_idle(self):
        """In ATTACKING, quando l'animazione è finita spara EyeBall e torna a IDLE."""
        arena = Mock()
        self.plant.state.action = Action.ATTACKING

        with patch.object(self.plant, "_locked_anim_finished", return_value=True) as mock_finished, \
             patch.object(self.plant, "_shoot_eyeball") as mock_shoot, \
             patch.object(self.plant, "_set_state_action") as mock_set_state:

            self.plant.move(arena)

        mock_finished.assert_called_once()
        # -> spara EyeBall
        mock_shoot.assert_called_once_with(arena)
        # -> torna a IDLE
        mock_set_state.assert_called_once_with(Action.IDLE)

    # ======== HIT ========
    def test_hit_reduces_health_and_sets_dead(self):
        """hit riduce health e se <=0 porta a DEAD."""
        self.plant.state.action = Action.IDLE
        self.plant.health = 10

        self.plant.hit(15)

        self.assertEqual(self.plant.health, 0)
        self.assertEqual(self.plant.state.action, Action.DEAD)

    # ======== COLLISIONS - ARTHUR, PLATFORM ========
    def test_on_arthur_collision_uses_cooldown(self):
        """on_arthur_collision danneggia Arthur <=> cooldown <= 0."""
        arthur = Mock()
        arthur.hit = Mock()
        self.plant.state.action = Action.IDLE

        # -> caso 1: cooldown > 0 -> nessun danno
        self.plant.damage_cooldown = 10

        self.plant.on_arthur_collision(arthur)
        arthur.hit.assert_not_called()

        # -> caso 2: cooldown <= 0 -> danno + reset cooldown
        self.plant.damage_cooldown = 0

        self.plant.on_arthur_collision(arthur)
        arthur.hit.assert_called_once_with(self.plant.damage)
        self.assertEqual(self.plant.damage_cooldown, self.plant.damage_interval)

    def test_on_arthur_collision_ignored_when_spawning_or_dead(self):
        """In SPAWNING o DEAD, on_arthur_collision non fa nulla."""
        arthur = Mock()
        arthur.hit = Mock()

        for action in (Action.SPAWNING, Action.DEAD):
            with self.subTest(action=action):
                self.plant.state.action = action
                self.plant.damage_cooldown = 0
                arthur.hit.reset_mock()

                self.plant.on_arthur_collision(arthur)
                arthur.hit.assert_not_called()

    def test_on_platform_collision_applies_translations(self):
        """on_platform_collision sposta il Plant di dx, dy."""
        self.plant.x = 10
        self.plant.y = 20

        self.plant.on_platform_collision(Direction.UP, dx=3, dy=-5)

        self.assertEqual(self.plant.x, 13)
        self.assertEqual(self.plant.y, 15)

    # ======== GUI ========
    def test_gui_returns_health_bar(self):
        """gui deve ritornare una Bar."""
        gui_list = self.plant.gui

        self.assertEqual(len(gui_list), 1)
        bar = gui_list[0]

        self.assertIsInstance(bar, Bar)

    # ======== SHOOT EYEBALL ========
    def test_shoot_eyeball_spawns_projectile(self):
        """_shoot_eyeball deve creare un EyeBall e chiamare arena.spawn."""
        arena = Mock()
        arena.spawn = Mock()

        self.plant.state.direction = Direction.RIGHT
        self.plant.width = 16
        self.plant.height = 32
        self.plant.x = 100
        self.plant.y = 50

        with patch.object(plant_module, "EyeBall") as MockEyeBall:
            eyeball_instance = Mock()
            MockEyeBall.return_value = eyeball_instance

            self.plant._shoot_eyeball(arena)

        # -> coordinate attese
        # RIGHT: offset_x = width + 5
        expected_spawn_x = self.plant.x + self.plant.width + 5
        expected_spawn_y = self.plant.y + self.plant.height * 0.3

        MockEyeBall.assert_called_once()
        call_args, call_kwargs = MockEyeBall.call_args

        self.assertAlmostEqual(call_kwargs["x"], expected_spawn_x)
        self.assertAlmostEqual(call_kwargs["y"], expected_spawn_y)
        self.assertEqual(call_kwargs["direction"], self.plant.state.direction)
        self.assertEqual(call_kwargs["speed"], self.plant.projectile_speed)
        self.assertEqual(call_kwargs["damage"], self.plant.projectile_damage)

        arena.spawn.assert_called_once_with(eyeball_instance)

    # ======== AUTO_INIT ========
    def test_auto_init_spawn_ranges_on_closest_platform(self):
        """
        auto_init:
        - calcola i range di spawn corretti sulle piattaforme a sinistra e destra,
        - sceglie un Candidate tra le piattaforme selezionate,
        - crea un Plant con x, y, direction coerenti.
        """
        min_dist_x = 50
        max_dist_x = 100

        settings = plant_module.read_settings()
        defaults = settings.get("Plant", {}).get("defaults", {})
        plant_height = defaults.get("height", 32)

        # Player
        player = Mock()
        player.x = 100
        player.y = 50
        player.width = 20   # cx = 110
        player.height = 30  # base_y = 80

        # -> dummy di platform
        class DummyPlatform(plant_module.Platform):
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

        with patch.object(plant_module.random, "choice") as mock_choice, \
             patch.object(plant_module.random, "uniform") as mock_uniform:

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
            spawned_plant = Plant.auto_init(
                player,
                game,
                min_dist_x=min_dist_x,
                max_dist_x=max_dist_x,
            )

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
        chosen_candidate = candidates[0]  # -> return di fake_choice
        self.assertEqual(chosen_candidate.height, platform_close.y)

        # -> CHECK PLANT
        # -> x deve essere l'estremo sinistro del range (fake_uniform ritorna il minimo)
        expected_x = chosen_candidate.range.min
        # -> y = altezza piattaforma - altezza plant
        expected_y = chosen_candidate.height - plant_height

        self.assertIsInstance(spawned_plant, Plant)
        self.assertAlmostEqual(spawned_plant.x, expected_x)
        self.assertAlmostEqual(spawned_plant.y, expected_y)
        self.assertEqual(spawned_plant.state.direction, chosen_candidate.direction)

if __name__ == "__main__":
    unittest.main()
