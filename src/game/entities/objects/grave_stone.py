# STATE
from ...state import Direction

# OBJECTS
from ..objects import Platform


class GraveStone(Platform):
    def __init__(self,
         x: int | float,
         y: int | float,
         width: int,
         height: int,
         contact_surfaces: list[Direction] | tuple[Direction] | None = (Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT),
         damage: int | float = 0.0,
         *,
         name: str = "GraveStone"
    ) -> None:
        super().__init__(x=x, y=y, width=width, height=height, contact_surfaces=contact_surfaces, damage=damage, name=name)
