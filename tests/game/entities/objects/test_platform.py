import unittest
from unittest.mock import Mock

from src.game.entities.objects import platform as platform_module

Platform = platform_module.Platform
Direction = platform_module.Direction
Actor = platform_module.Actor


class PlatformTest(unittest.TestCase):

    def setUp(self):
        self.platform = Platform(
            x=10,
            y=20,
            width=100,
            height=50,
        )

    # ======== INIT ========
    def test_init(self):
        """Platform deve inizializzarsi con i valori passati e contact_surfaces di default."""
        self.assertEqual(self.platform.pos(), (10.0, 20.0))
        self.assertEqual(self.platform.size(), (100, 50))

        self.assertIsInstance(self.platform.contact_surfaces, list)
        self.assertIn(Direction.UP, self.platform.contact_surfaces)
        self.assertIn(Direction.DOWN, self.platform.contact_surfaces)
        self.assertIn(Direction.LEFT, self.platform.contact_surfaces)
        self.assertIn(Direction.RIGHT, self.platform.contact_surfaces)

        self.assertEqual(self.platform.damage, 0.0)
        self.assertEqual(self.platform.name, "Platform")

    def test_contact_surfaces_accepts_list_tuple_and_none(self):
        """contact_surfaces accetta list, tuple o None e li converte in list o None."""
        platform = Platform(0, 0, 10, 10, contact_surfaces=[Direction.UP, Direction.DOWN])
        self.assertIsInstance(platform.contact_surfaces, list)
        self.assertEqual(set(platform.contact_surfaces), {Direction.UP, Direction.DOWN})

        platform.contact_surfaces = (Direction.LEFT, Direction.RIGHT)
        self.assertIsInstance(platform.contact_surfaces, list)
        self.assertEqual(set(platform.contact_surfaces), {Direction.LEFT, Direction.RIGHT})

        platform.contact_surfaces = None
        self.assertIsNone(platform.contact_surfaces)

    # ======== PROPERTIES ========
    def test_x_type_error(self):
        """x accetta solo int o float."""
        with self.assertRaises(TypeError):
            self.platform.x = "not-a-number"  # type: ignore

    def test_y_type_error(self):
        """y accetta solo int o float."""
        with self.assertRaises(TypeError):
            self.platform.y = None  # type: ignore

    def test_width_type_error(self):
        """width accetta solo int."""
        with self.assertRaises(TypeError):
            self.platform.width = 3.5  # type: ignore

    def test_height_type_error(self):
        """height accetta solo int."""
        with self.assertRaises(TypeError):
            self.platform.height = "£$€"  # type: ignore

    def test_contact_surfaces_type_error(self):
        """contact_surfaces accetta solo list, tuple o None."""
        with self.assertRaises(TypeError):
            self.platform.contact_surfaces = 123  # type: ignore

    def test_damage_type_error(self):
        """damage accetta solo int o float."""
        with self.assertRaises(TypeError):
            self.platform.damage = {}  # type: ignore

    def test_name_type_error(self):
        """name deve essere una stringa."""
        with self.assertRaises(TypeError):
            self.platform.name = 42e42  # type: ignore

    # ======== INTERFACE IMPLEMENTATION ========
    def test_pos_and_size_methods(self):
        """pos e size devono restituire (x,y) e (width,height)."""
        self.platform.x = 15
        self.platform.y = 25
        self.platform.width = 80
        self.platform.height = 40

        self.assertEqual(self.platform.pos(), (15.0, 25.0))
        self.assertEqual(self.platform.size(), (80, 40))

    def test_move_does_nothing(self):
        """move non deve modificare la piattaforma."""
        arena = Mock()
        start_pos = self.platform.pos()
        start_size = self.platform.size()

        self.platform.move(arena)

        self.assertEqual(self.platform.pos(), start_pos)
        self.assertEqual(self.platform.size(), start_size)

    def test_sprite_returns_none(self):
        """sprite deve restituire None (Platform non ha sprite grafico in quanto)."""
        self.assertIsNone(self.platform.sprite())

    # ======== CHECK_COLLISION ========
    def test_check_collision_true_when_overlapping(self):
        """check_collision deve restituire True quando c'è sovrapposizione rettangolare."""
        # -> piattaforma: x=10-110, y=20-70
        obj = Mock(spec=Actor)
        obj.pos.return_value = (50, 40)   # -> dentro Platform
        obj.size.return_value = (20, 10)

        self.assertTrue(self.platform.check_collision(obj))

    def test_check_collision_false_when_far_away(self):
        """check_collision deve restituire False quando non c'è overlap."""
        obj = Mock(spec=Actor)
        obj.pos.return_value = (200, 200)  # -> fuori da Platform
        obj.size.return_value = (10, 10)

        self.assertFalse(self.platform.check_collision(obj))

    def test_check_collision_false_when_only_touching_edge(self):
        """check_collision deve restituire False quando l'oggetto tocca solo il bordo senza sovrapporsi."""
        # -> piattaforma: x=10-110, y=20-70
        # -> oggetto appoggiato a destra
        obj = Mock(spec=Actor)
        obj.pos.return_value = (110, 30)   # -> o_left == 110 == p_right
        obj.size.return_value = (20, 20)

        self.assertFalse(self.platform.check_collision(obj))

    # ======== CLAMP ========
    def test_clamp_no_overlap_returns_none(self):
        """Se non c'è overlap, clamp deve restituire (None, 0.0, 0.0)."""
        obj = Mock(spec=Actor)
        obj.pos.return_value = (200, 200)
        obj.size.return_value = (10, 10)

        direction, dx, dy = self.platform.clamp(obj)
        self.assertIsNone(direction)
        self.assertEqual(dx, 0.0)
        self.assertEqual(dy, 0.0)

    def test_clamp_from_left(self):
        """Se l'oggetto entra da sinistra (con overlap orizontale minore dell'overlap verticale), clamp deve restituire LEFT e dx negativo."""
        # piattaforma: x=10-110, y=20-70
        platform = Platform(0, 0, 100, 50)

        obj = Mock(spec=Actor)
        # -> oggetto che interseca da sinistra
        obj.pos.return_value = (-10, 10)   # -> o_left=-10, o_right=5
        obj.size.return_value = (15, 10)   # -> o_top=10, o_bottom=20

        direction, dx, dy = platform.clamp(obj)

        self.assertEqual(direction, Direction.LEFT)
        # -> dx negativo (trasla l'oggetto verso sinistra)
        self.assertLess(dx, 0.0)
        self.assertEqual(dy, 0.0)

    def test_clamp_from_right(self):
        """Se l'oggetto entra da destra (overlap orizontale minore dell'overlap verticale), clamp deve restituire RIGHT e dx positivo."""
        platform = Platform(-100, 0, 100, 50)

        obj = Mock(spec=Actor)
        # -> oggetto che interseca da destra
        obj.pos.return_value = (-5, 10)  # o_left=-5, o_right=10
        obj.size.return_value = (15, 10) # o_top=10, o_bottom=20

        direction, dx, dy = platform.clamp(obj)

        self.assertEqual(direction, Direction.RIGHT)
        self.assertGreater(dx, 0.0)
        self.assertEqual(dy, 0.0)

    def test_clamp_from_top(self):
        """Se l'oggetto entra dall'alto (overlap verticale minore dell'overlap orizontale), clamp deve restituire UP e dy negativo."""
        platform = Platform(-50, 0, 100, 50)

        obj = Mock(spec=Actor)
        # -> oggetto che interseca dall'alto
        obj.pos.return_value = (-5, -10)  # -> o_top=-10, o_bottom=5 (overlap_y=5)
        obj.size.return_value = (10, 15)  # -> o_left=-5, o_right=5 (overlap_x=10)

        direction, dx, dy = platform.clamp(obj)

        self.assertEqual(direction, Direction.UP)
        self.assertEqual(dx, 0.0)
        self.assertLess(dy, 0.0)

    def test_clamp_from_bottom(self):
        """Se l'oggetto entra dal basso, clamp deve restituire DOWN e dy positivo."""
        platform = Platform(-50, -50, 100, 50)

        obj = Mock(spec=Actor)
        # -> oggetto che interseca dal basso
        obj.pos.return_value = (-5, -5)  # -> o_top=-5, o_bottom=15 (overlap_y=5)
        obj.size.return_value = (5, 10) # -> o_left=-5, o_right=5 (overlap_x=10)

        direction, dx, dy = platform.clamp(obj)

        self.assertEqual(direction, Direction.DOWN)
        self.assertEqual(dx, 0.0)
        self.assertGreater(dy, 0.0)

    def test_clamp_respects_contact_surfaces(self):
        """clamp deve restituire (None,0,0) se la direzione non è tra le contact_surfaces."""
        # -> piattaforma che accetta solo collisioni dall'alto (UP)
        platform = Platform(
            x=0,
            y=0,
            width=100,
            height=50,
            contact_surfaces=[Direction.UP],
        )

        # -> oggetto che collide da sinistra (overlap orizzontale < overlap verticale)
        # platform: x=0-100, y=0-50
        # o_left=-10 o_right=5, o_top=10, o_bottom=20
        # overlap_x = 5, overlap_y = 10 -> collisione orizzontale, da sinistra
        obj_left = Mock(spec=Actor)
        obj_left.pos.return_value = (-10, 10)
        obj_left.size.return_value = (15, 10)

        direction, dx, dy = platform.clamp(obj_left)
        # -> direzione sarebbe LEFT, ma non è ammessa -> clamp deve restituire None,0.0,0.0
        self.assertIsNone(direction)
        self.assertEqual(dx, 0.0)
        self.assertEqual(dy, 0.0)

        # -> oggetto che collide dall'alto -> UP è permesso
        # platform: x=0-100, y=0-50
        # o_left=10, o_right=30, o_top=-10, o_bottom=5 -> entra dall'alto
        # overlap_x= 20, overlap_y=5
        obj_top = Mock(spec=Actor)
        obj_top.pos.return_value = (10, -10)
        obj_top.size.return_value = (20, 15)

        direction2, dx2, dy2 = platform.clamp(obj_top)
        self.assertEqual(direction2, Direction.UP)
        self.assertEqual(dx2, 0.0)
        self.assertLess(dy2, 0.0)


if __name__ == "__main__":
    unittest.main()
