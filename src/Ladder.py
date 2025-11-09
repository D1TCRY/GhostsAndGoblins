from status import Action, Direction

from Platform import Platform

class Ladder(Platform):
    def __init__(self,
        x: int | float,
        y: int | float,
        width: int,
        height: int,
        contact_surfaces: list[Direction] | tuple[Direction] | None = (Direction.UP,),
        damage: int | float = 0.0,
        *,
        name: str = "Ladder"
    ) -> None:
        super().__init__(x=x, y=y, width=width, height=height, contact_surfaces=contact_surfaces, damage=damage, name=name)

